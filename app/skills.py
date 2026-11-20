"""Case-independent, typed planning and report assembly skills."""
from .contracts import PlanInput
from .store import hashobj,now,uid
from .specialists import REGISTRY
PROFILES={
 'balanced':'Review evidence across all three activity areas.',
 'teaching':'Highlight teaching load, aggregate feedback and learning outcomes.',
 'research':'Highlight publication, project, grant and guidance evidence.',
 'administrative':'Highlight documented institutional duties and service.'}
def plan_skill(data:PlanInput,fingerprint:str,policy:dict):
    body=data.model_dump();body.update({'id':uid(),'created':now(),'status':'draft','fingerprint':fingerprint,
        'policy_hash':hashobj(policy),'specialist':PROFILES[data.profile],
        'budget':{'max_repairs':2,'max_nodes':30,'max_seconds':120},
        'steps':['research','teaching','administrative','evidence_validation','api_calculation','report_generation','acceptance','quality_review','hod_review','release_review','publish']})
    return body

def format_skill(plan,profile,score,checks,items):
    return {'faculty_id':profile['id'],'faculty_name':profile['name'],'department':profile['department'],
        'cycle':plan['cycle'],'profile':plan['profile'],'specialist_focus':PROFILES[plan['profile']],
        'plan_hash':hashobj(plan),'policy_id':plan['policy_id'],'score':score,'checks':checks,
        'summary':f"{profile['name']} — {plan['cycle']}. {len(items)} evidence-reviewed activities included. "
                  f"Calculated API: {score['total']:.2f}. Recommended rating: {score['rating']}. Pending named human review.",
        'highlights':REGISTRY[plan['profile']].highlights(items),
        'evidence':[{'record_id':r['id'],'title':r['title'],'source_id':r['source_id'],'source_name':r['source_name'],'locator':r['locator'],'sha256':r['source_hash'],'review':r['evidence']} for r in items]}
