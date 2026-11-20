"""Reproducible synthetic latency benchmark; never touches the real database."""
import sys,tempfile,time,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from app.store import Store,uid,now,hashobj
from app.demo import make_fixture
from app.workflow import Runtime
from app.skills import plan_skill
from app.contracts import PlanInput
from app.batch import run_batch

def benchmark():
    with tempfile.TemporaryDirectory() as tmp:
        store=Store(Path(tmp)/'app.db');fixture=make_fixture(store,ready=True);runtime=Runtime(store);plans=[]
        for i in range(3):
            fid=f'benchmark-{i}';store.put('profiles',{'id':fid,'name':f'Synthetic Faculty {i}','department':'Synthetic','aliases':[],'identity_status':'verified'})
            actor={**fixture['users']['faculty'],'id':uid(),'faculty_id':fid};store.put('users',actor)
            for category in ('research','teaching','administrative'):
                record={**store.get('records','demo-'+category),'id':fid+'-'+category,'faculty_id':fid};store.put('records',record)
                store.put('consents',{'id':fid+':'+record['source_id'],'faculty_id':fid,'source_id':record['source_id'],'granted':True,'actor':actor['id'],'at':now()})
                review={**store.get('evidence','demo-alex:demo-'+category),'id':fid+':'+record['id'],'faculty_id':fid,'record_id':record['id'],'record_hash':hashobj(record)};store.put('evidence',review)
            data=PlanInput(faculty_id=fid,policy_id='synthetic-policy',request='Benchmark synthetic complete appraisal.',completeness={k:'Synthetic data complete.' for k in ('research','teaching','administrative')})
            p=plan_skill(data,runtime.connector.fingerprint(actor,fid),fixture['policy']);p.update(owner=actor['id'],status='locked');store.put('plans',p);plans.append(p)
        collect=runtime.connector.collect
        def delayed(*args,**kwargs):
            time.sleep(.10) # Explicitly simulated connector latency; no production performance claim.
            return collect(*args,**kwargs)
        runtime.connector.collect=delayed
        t=time.perf_counter();serial=[]
        for p in plans:
            r={'id':uid(),'plan':p,'faculty_id':p['faculty_id'],'owner':p['owner'],'status':'running','created':now(),'node_count':0};store.put('runs',r);serial.append(runtime.drive(r['id']))
        serial_seconds=time.perf_counter()-t
        t=time.perf_counter();parallel,rejected=run_batch(store,runtime,runtime.connector,plans,fixture['users']['hod']);parallel_seconds=time.perf_counter()-t
        equal=sorted((r['faculty_id'],r['report']['score']['total'],r['checks']) for r in serial)==sorted((r['faculty_id'],r['report']['score']['total'],r['checks']) for r in parallel)
        return {'workload':'3 synthetic faculty; 100 ms simulated latency per collector; real LangGraph/SQLite pipeline','sequential_seconds':round(serial_seconds,3),'parallel_seconds':round(parallel_seconds,3),'equal_scores_and_checks':equal,'rejected':rejected,'speedup':round(serial_seconds/parallel_seconds,2)}
if __name__=='__main__':print(json.dumps(benchmark(),indent=2))
