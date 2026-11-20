import pytest
from fastapi.testclient import TestClient
from app.store import Store
from app.demo import make_fixture
from app.connector import Connector
from app.workflow import Runtime
import app.main as main
@pytest.fixture
def env(tmp_path,monkeypatch):
    store=Store(tmp_path/'app.db');fixture=make_fixture(store,ready=True)
    monkeypatch.setattr(main,'store',store);monkeypatch.setattr(main,'connector',Connector(store));monkeypatch.setattr(main,'runtime',Runtime(store))
    monkeypatch.delenv('OLLAMA_MODEL',raising=False);monkeypatch.delenv('OLLAMA_EMBED_MODEL',raising=False)
    with TestClient(main.app) as client:yield {'store':store,'fixture':fixture,'client':client,'main':main}
def sign(env,role):
    client=env['client'];r=client.post('/api/login',json={'username':'demo-'+role,'password':env['fixture']['password']});assert r.status_code==200,r.text
    client.headers['X-CSRF-Token']=r.json()['csrf'];return client
@pytest.fixture
def start(env):
    def invoke():
        c=sign(env,'faculty');body={'faculty_id':'demo-alex','cycle':'2025-26','profile':'balanced','policy_id':'synthetic-policy','request':'Prepare a complete synthetic appraisal.','completeness':{'research':'Synthetic research is complete.','teaching':'Synthetic teaching is complete.','administrative':'Synthetic service is complete.'}}
        p=c.post('/api/plans',json=body);assert p.status_code==200,p.text
        locked=c.post('/api/plans/'+p.json()['id']+'/lock');assert locked.status_code==200,locked.text
        r=c.post('/api/runs',json={'plan_id':p.json()['id']});assert r.status_code==200,r.text;return r.json()
    return invoke
