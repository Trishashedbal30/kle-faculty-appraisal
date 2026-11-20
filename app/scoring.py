"""Deterministic arithmetic. LLM output never changes scores or policy."""
from decimal import Decimal,ROUND_HALF_UP
D=lambda x:Decimal(str(x))
def rounded(v):return float(v.quantize(Decimal('0.01'),rounding=ROUND_HALF_UP))
def compute(items,policy):
    components=[]
    for rule in policy['rules']:
        rows=[r for r in items if r['kind']==rule['kind'] and r['category']==rule['category']]
        values=[D(r['value']) for r in rows];method=rule['method']
        if method=='count':raw=D(len(rows))
        elif method=='sum':raw=sum(values,D(0))
        elif method=='mean':raw=sum(values,D(0))/D(len(rows)) if rows else D(0)
        else:
            denominator=sum(D(r.get('students',0)) for r in rows)
            raw=sum((D(r['value'])*D(r.get('students',0)) for r in rows),D(0))/denominator if denominator else D(0)
        points=min(raw/D(rule['divisor'])*D(rule['weight']),D(rule['cap']))
        components.append({'kind':rule['kind'],'category':rule['category'],'raw':float(raw),'points':rounded(points),
            'method':method,'formula':f"min(({raw} / {rule['divisor']}) × {rule['weight']}, {rule['cap']})",'policy_citation':rule['citation'],
            'record_ids':[r['id'] for r in rows],'evidence':[{'source_id':r['source_id'],'locator':r['locator'],'sha256':r['source_hash']} for r in rows]})
    total=sum((D(x['points']) for x in components),D(0))
    rating=next(b['label'] for b in sorted(policy['bands'],key=lambda b:b['minimum'],reverse=True) if total>=D(b['minimum']))
    return {'total':float(total),'rating':rating,'components':components,'rounding':'Round each component to 2 decimals, half up; sum rounded components.'}

def acceptance(report,plan,policy,items):
    expected=compute(items,policy)
    evidence_ids={e['record_id'] for e in report.get('evidence',[])}
    checks=[{'name':'Every score cites verified evidence','passed':all(r['id'] in evidence_ids and r.get('evidence',{}).get('status')=='verified' for r in items)},
            {'name':'Weightages and arithmetic match approved policy','passed':report.get('score')==expected},
            {'name':'Locked plan and faculty scope preserved','passed':report.get('faculty_id')==plan['faculty_id'] and report.get('cycle')==plan['cycle'] and report.get('policy_id')==plan['policy_id']},
            {'name':'Rating remains a recommendation before human approval','passed':not report.get('final',False)}]
    return checks
