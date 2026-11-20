"""Per-faculty fan-out with an explicit plan-alignment selector."""
from concurrent.futures import ThreadPoolExecutor
from .store import uid,now,hashobj
from .security import fail

def select_aligned(results,plans):
    expected={p['id']:hashobj(p) for p in plans};selected={};rejected=[]
    for run in results:
        p=run['plan'];aligned=expected.get(p['id'])==hashobj(p)
        key=(run['faculty_id'],p['cycle'])
        # Deterministic precedence: passing human-review draft > blocked > failed; then newest.
        rank=(int(run['status'].startswith('awaiting_') or run['status']=='published'),int(run['status'] not in ('failed','running')),run['created'])
        if not aligned:rejected.append({'run_id':run['id'],'reason':'Plan mismatch'});continue
        old=selected.get(key)
        if old is None or rank>old[0]:
            if old:rejected.append({'run_id':old[1]['id'],'reason':'Lower-alignment candidate for the same unit'})
            selected[key]=(rank,run)
        else:rejected.append({'run_id':run['id'],'reason':'Lower-alignment candidate for the same unit'})
    return [v[1] for v in selected.values()],rejected

def run_batch(store,runtime,connector,plans,initiator):
    if not 1<=len(plans)<=10:fail('A batch contains one to ten locked plans.')
    prepared=[]
    for plan in plans:
        if plan['status']!='locked':fail('Every batch plan must be locked by its faculty owner.')
        owner=store.get('users',plan['owner'])
        if not owner or not owner['active']:fail('Plan owner is not active.')
        if connector.fingerprint(owner,plan['faculty_id'])!=plan['fingerprint']:fail('A plan is stale; revise it before batch execution.',409)
        r={'id':uid(),'plan':plan,'faculty_id':plan['faculty_id'],'owner':plan['owner'],'status':'running','created':now(),'node_count':0}
        store.put('runs',r);prepared.append(r)
    def work(r):
        try:return runtime.drive(r['id'])
        except Exception:return store.get('runs',r['id'])
    with ThreadPoolExecutor(max_workers=3) as pool:results=list(pool.map(work,prepared))
    merged,rejected=select_aligned(results,plans)
    store.audit(initiator['id'],'batch.merge','batch',{'plan_ids':[p['id'] for p in plans],'selected':[r['id'] for r in merged],'rejected':rejected})
    return merged,rejected
