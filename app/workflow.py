"""AURA coordinator: parallel specialists, evidence hard gate, repair and human interrupts."""
from typing import TypedDict
import threading,time
from langgraph.graph import StateGraph,START,END
from langgraph.types import interrupt,Command
from langgraph.checkpoint.sqlite import SqliteSaver
from .connector import Connector
from .store import hashobj,now,uid
from .scoring import compute,acceptance
from .skills import format_skill
from .memory import narrative
from .security import fail
class State(TypedDict,total=False):
    run_id:str
    plan:dict
    research:dict
    teaching:dict
    administrative:dict
    items:list
    excluded:list
    errors:list
    score:dict
    report:dict
    checks:list
    repairs:int
    quality:dict
    hod:dict
    release:dict
    outcome:str

class Runtime:
    def __init__(self,store):self.store=store;self.connector=Connector(store);self.locks={};self.guard=threading.Lock()
    def lock(self,rid):
        with self.guard:return self.locks.setdefault(rid,threading.RLock())
    def build(self,checkpointer,rid):
        store=self.store;c=self.connector;run=store.get('runs',rid);owner=store.get('users',run['owner']);start=time.monotonic()
        def record(node,inputs,outputs):
            with store.tx():
                current=store.get('runs',rid);current['node_count']=current.get('node_count',0)+1
                if current['node_count']>current['plan']['budget']['max_nodes']:raise RuntimeError('Node budget exhausted; human investigation required.')
                if time.monotonic()-start>current['plan']['budget']['max_seconds']:raise RuntimeError('Run time budget exhausted; resume after investigation.')
                current['last_node']=node;store.put('runs',current)
                store.audit(owner['id'],'agent.'+node,rid,{'inputs':inputs,'outputs':outputs})
        def save_status(status,**kwargs):
            with store.tx():
                current=store.get('runs',rid);current.update(status=status,updated=now(),**kwargs);store.put('runs',current)
        def collector(category):
            def node(s):
                result=c.collect(owner,s['plan']['faculty_id'],category,rid)
                record(category,{'plan_hash':hashobj(s['plan'])},{'ids':[i['id'] for i in result['items']],'errors':result['errors']})
                return {category:result}
            return node
        def validate(s):
            plan=s['plan'];errors=[];valid=[];excluded=[]
            if c.fingerprint(owner,plan['faculty_id'])!=plan['fingerprint']:errors.append({'reason':'Inputs changed after plan lock. Create a revised plan.'})
            p=c.profile(owner,plan['faculty_id'])
            if p['identity_status']!='verified':errors.append({'reason':'Faculty identity is not verified.'})
            for category in ('research','teaching','administrative'):
                errors.extend(s[category]['errors'])
                if not plan['completeness'].get(category):errors.append({'reason':f'{category}: missing completeness declaration'})
                for r in s[category]['items']:
                    ev=r.get('evidence') or {}
                    if ev.get('record_hash')!=hashobj({k:v for k,v in r.items() if k not in ('evidence','source_hash','source_name')}):errors.append({'id':r['id'],'reason':'Evidence decision is missing or stale'});continue
                    if ev.get('status')=='excluded':excluded.append({'id':r['id'],'reason':ev['note']});continue
                    if ev.get('status')!='verified':errors.append({'id':r['id'],'reason':'Evidence requires human verification'});continue
                    if not c.intact(r['source_id']):errors.append({'id':r['id'],'reason':'Evidence file is missing or its checksum changed'});continue
                    if not r.get('locator'):errors.append({'id':r['id'],'reason':'Evidence locator missing'});continue
                    date=f"{int(r['year']):04d}-{int(r['month']):02d}"
                    if not '2025-08'<=date<='2026-07':errors.append({'id':r['id'],'reason':'Activity outside appraisal cycle'});continue
                    if r['kind']=='preprint':errors.append({'id':r['id'],'reason':'Preprints must be excluded or corrected to an evidenced published record'});continue
                    valid.append(r)
            policy=c.policy(plan['policy_id'])
            if hashobj(policy)!=plan['policy_hash']:errors.append({'reason':'Policy version changed after plan lock'})
            kinds={(r['category'],r['kind']) for r in policy['rules']}
            for r in valid:
                if (r['category'],r['kind']) not in kinds:errors.append({'id':r['id'],'reason':'No approved scoring rule for this activity kind; configure policy or explicitly exclude.'})
            seen={}
            for r in valid:
                rule=next((x for x in policy['rules'] if x['kind']==r['kind'] and x['category']==r['category']),None)
                if rule and rule['method']=='weighted_mean' and r.get('students',0)<=0:
                    errors.append({'id':r['id'],'reason':'Weighted feedback needs a positive response count.'})
                if r['category']=='research':
                    natural=(r.get('doi') or r['title']).strip().lower().removeprefix('https://doi.org/')
                    if natural in seen:errors.append({'id':r['id'],'reason':'Possible duplicate of '+seen[natural]+'. Review and explicitly exclude duplicate claims.'})
                    seen[natural]=r['id']
            if not valid:errors.append({'reason':'No verified, consented activities to appraise.'})
            record('evidence_validation',{'records':sum(len(s[k]['items']) for k in ('research','teaching','administrative'))},{'verified':[r['id'] for r in valid],'excluded':excluded,'errors':errors})
            if errors:save_status('blocked',errors=errors)
            return {'items':valid,'excluded':excluded,'errors':errors}
        def score(s):
            result=compute(s['items'],c.policy(s['plan']['policy_id']));record('api_calculation',{'policy_id':s['plan']['policy_id'],'record_ids':[r['id'] for r in s['items']]},result)
            return {'score':result}
        def assemble(s):
            report=format_skill(s['plan'],c.profile(owner,s['plan']['faculty_id']),s['score'],[],s['items']);report['excluded']=s['excluded'];report['completeness']=s['plan']['completeness'];report['narrative']=narrative(report)
            record('report_generation',{'score_hash':hashobj(s['score'])},{'report_hash':hashobj(report)})
            return {'report':report,'repairs':0}
        def check(s):
            checks=acceptance(s['report'],s['plan'],c.policy(s['plan']['policy_id']),s['items']);checks.append({'name':'Audit integrity and appeals trail preserved','passed':store.verify_audit()});record('acceptance',{'report_hash':hashobj(s['report'])},checks)
            if not all(x['passed'] for x in checks) and s.get('repairs',0)>=2:save_status('blocked',errors=[{'reason':x['name']} for x in checks if not x['passed']])
            return {'checks':checks}
        def repair(s):
            report=dict(s['report']);fixes=[]
            for x in s['checks']:
                if x['passed']:continue
                if x['name']=='Weightages and arithmetic match approved policy':report['score']=compute(s['items'],c.policy(s['plan']['policy_id']));fixes.append('Recomputed numeric components')
                elif x['name']=='Every score cites verified evidence':
                    report['evidence']=format_skill(s['plan'],c.profile(owner,s['plan']['faculty_id']),s['score'],[],s['items'])['evidence'];fixes.append('Restored source citations from verified records')
            record('targeted_repair',{'failed':[x['name'] for x in s['checks'] if not x['passed']]},{'fixes':fixes})
            return {'report':report,'repairs':s.get('repairs',0)+1}
        def gate(stage,roles):
            def node(s):
                # Persist only idempotent review projection before interrupt (node restarts on resume).
                report={**s['report'],'checks':s['checks'],'review_history':[s[k] for k in ('quality','hod','release') if k in s]}
                save_status('awaiting_'+stage,report=report,checks=s['checks'],errors=[])
                decision=interrupt({'stage':stage,'run_id':rid,'report_hash':hashobj(report),'allowed_roles':roles})
                actor=store.get('users',decision.get('actor'))
                if not actor or not actor['active'] or actor['role'] not in roles:raise ValueError('Invalid human authority')
                if decision['action']=='return':save_status('returned',return_note=decision['note'])
                record(stage,{'report_hash':hashobj(report)},decision)
                return {stage:decision}
            return node
        def publish(s):
            with store.tx():
                current=store.get('runs',rid)
                if current.get('release_id'):return {'outcome':'published'}
                if c.fingerprint(owner,s['plan']['faculty_id'])!=s['plan']['fingerprint']:save_status('blocked',errors=[{'reason':'Inputs or consent changed during review. Build a new run.'}]);return {'outcome':'blocked'}
                if hashobj(c.policy(s['plan']['policy_id']))!=s['plan']['policy_hash']:raise ValueError('Policy changed before release')
                if not all(c.intact(r['source_id']) for r in s['items']):raise ValueError('Evidence changed before release')
                if not store.verify_audit():raise ValueError('Audit integrity failed before release')
                if not all(x['passed'] for x in acceptance(s['report'],s['plan'],c.policy(s['plan']['policy_id']),s['items'])):raise ValueError('Acceptance gate failed before release')
                if not all(s[k]['action'] in ('approve','override') for k in ('quality','hod','release')):raise ValueError('All human approvals are required')
                report={**s['report'],'checks':s['checks'],'final':True}
                overrides=[s[k] for k in ('quality','hod','release') if s[k].get('rating_override')]
                report['final_rating']=overrides[-1]['rating_override'] if overrides else report['score']['rating']
                report['approvals']=[s[k] for k in ('quality','hod','release')]
                fid=s['plan']['faculty_id'];versions=[v for v in store.all('releases') if v['faculty_id']==fid]
                release={'id':uid(),'run_id':rid,'faculty_id':fid,'cycle':s['plan']['cycle'],'version':len(versions)+1,'created':now(),'report':report,'hash':hashobj(report)}
                store.put('releases',release);store.put('active',{'id':fid,'release_id':release['id']})
                store.audit(s['release']['actor'],'release.publish',fid,{'release_id':release['id'],'version':release['version'],'report_hash':release['hash'],'approvals':report['approvals']})
                save_status('published',release_id=release['id'],report=report)
            return {'outcome':'published'}
        graph=StateGraph(State)
        for name in ('research','teaching','administrative'):graph.add_node(name,collector(name));graph.add_edge(START,name)
        graph.add_node('validate',validate);graph.add_edge(['research','teaching','administrative'],'validate')
        for name,node in [('score',score),('assemble',assemble),('check',check),('repair',repair),('quality',gate('quality',['dean','iqac'])),('hod',gate('hod',['hod'])),('release',gate('release',['dean','iqac'])),('publish',publish)]:graph.add_node(name,node)
        graph.add_conditional_edges('validate',lambda s:END if s['errors'] else 'score')
        graph.add_edge('score','assemble');graph.add_edge('assemble','check')
        graph.add_conditional_edges('check',lambda s:'quality' if all(c['passed'] for c in s['checks']) else ('repair' if s.get('repairs',0)<2 else END))
        graph.add_edge('repair','check')
        for stage,nxt in [('quality','hod'),('hod','release'),('release','publish')]:graph.add_conditional_edges(stage,lambda s,k=stage,n=nxt:END if s[k]['action']=='return' else n)
        graph.add_edge('publish',END)
        return graph.compile(checkpointer=checkpointer)
    def drive(self,rid,decision=None,resume=False):
        with self.lock(rid):
            run=self.store.get('runs',rid)
            with SqliteSaver.from_conn_string(str(self.store.path.parent/'checkpoints.db')) as cp:
                graph=self.build(cp,rid)
                try:
                    graph.invoke(Command(resume=decision) if decision else None if resume else {'run_id':rid,'plan':run['plan'],'repairs':0}, {'configurable':{'thread_id':rid},'recursion_limit':40})
                except Exception as e:
                    with self.store.tx():
                        current=self.store.get('runs',rid);current.update(status='failed',error=str(e),updated=now());self.store.put('runs',current);self.store.audit('system','run.failed',rid,{'error':str(e)})
                    raise
        return self.store.get('runs',rid)
