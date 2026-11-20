import json
from app.store import ROOT
from app.importer import extract,key
from app.scoring import compute
from app.skills import plan_skill
from app.contracts import PolicyInput

def test_supplied_source_reconciliation():
    source_dir = ROOT / 'data' / 'source'
    if not source_dir.is_dir():
        import pytest
        pytest.skip('Requires the private source bundle, which is not distributed.')
    data=extract();assert len(data['research'])==234;assert len(data['feedback'])==159;assert len(data['profiles'])==43;assert not data['issues']
    assert sum(len(r['provenance']) for r in data['research'])==382
    row=next(r for r in data['feedback'] if r['id']=='summative-CS,4A-1');assert row['value']==82.82;assert row['students']==45;assert row['locator']=='Page 7, CS,4A, row 1'
    assert all(len(r['questions'])==14 for r in data['feedback'])

def test_unicode_name_normalization():assert key(' Dr. Sunitha\u200b  Hiremath ')==key('Sunitha Hiremath')

def test_weighted_mean_cap_rounding():
    policy={'rules':[{'kind':'feedback','category':'teaching','method':'weighted_mean','weight':50,'divisor':100,'cap':40,'citation':'test'}],'bands':[{'minimum':0,'label':'Example'}]}
    base={'kind':'feedback','category':'teaching','source_id':'s','locator':'p1','source_hash':'hash'}
    rows=[{**base,'id':'a','value':80,'students':10},{**base,'id':'b','value':100,'students':30}]
    result=compute(rows,policy);assert result['components'][0]['raw']==95;assert result['total']==40

def test_policy_schema_rejects_nan_and_bad_divisor():
    import pytest
    from pydantic import ValidationError
    from app.contracts import Rule
    with pytest.raises(ValidationError):Rule(kind='feedback',category='teaching',method='mean',weight=float('nan'),divisor=0,cap=100,citation='test')
