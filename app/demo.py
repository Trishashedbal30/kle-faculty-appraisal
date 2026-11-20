"""Synthetic sandbox only. Never infer approvals or scores for supplied real records."""
import hashlib,secrets
from .store import now,hashobj
from .security import create_user


PRESENTATION_FACULTY = (
    {
        'id': 'demo-river',
        'username': 'demo-river',
        'name': 'River Demo',
        'activities': (
            ('research', 'conference', 'Synthetic conference paper on resilient campus networks', 1, 0,
             'River Demo; Synthetic Proceedings of Responsible Computing, 2026; paper 14.'),
            ('teaching', 'feedback_summative', 'Synthetic aggregated student feedback for Data Systems', 86, 34,
             'River Demo; Data Systems; 34 synthetic responses; cycle summary, page 2.'),
            ('administrative', 'committee', 'Synthetic curriculum review committee service', 2, 0,
             'River Demo; curriculum review appointment; term summary, page 1.'),
        ),
    },
    {
        'id': 'demo-priya',
        'username': 'demo-priya',
        'name': 'Priya Demo',
        'activities': (
            ('research', 'conference', 'Synthetic conference paper on accessible learning analytics', 1, 0,
             'Priya Demo; Synthetic Proceedings of Inclusive Technology, 2026; paper 8.'),
            ('teaching', 'feedback_summative', 'Synthetic aggregated student feedback for Human Computer Interaction', 92, 28,
             'Priya Demo; Human Computer Interaction; 28 synthetic responses; cycle summary, page 3.'),
            ('administrative', 'committee', 'Synthetic accessibility and inclusion committee service', 1, 0,
             'Priya Demo; accessibility committee appointment; term summary, page 2.'),
        ),
    },
)


def make_fixture(store,ready=False,password_override=None):
    if store.all('users'):raise ValueError('Sandbox must be empty. Existing data is never overwritten.')
    store.put('meta',{'id':'import','cycle':'2025-26','notes':['SYNTHETIC SANDBOX: invented activities and rubric. Not institutional or UGC policy.'],'issues':[]})
    folder=store.path.parent/'uploads';folder.mkdir(parents=True,exist_ok=True)
    for cat in ['research','teaching','administrative','policy']:
        sid='synthetic-'+cat;content=f'SYNTHETIC TEST EVIDENCE ONLY\nAlex Demo\nCycle 2025-26\nCategory {cat}\nNot a real institutional record.\n'.encode();(folder/sid).write_bytes(content)
        store.put('sources',{'id':sid,'name':sid+'.txt','kind':cat,'sha256':hashlib.sha256(content).hexdigest(),'bytes':len(content),'uploaded':True,'owner':'synthetic'})
    for fid,n in [('demo-alex','Alex Demo'),('demo-river','River Demo')]:store.put('profiles',{'id':fid,'name':n,'department':'Synthetic Demonstration Department','identity_status':'verified','aliases':[n]})
    password=secrets.token_urlsafe(14);users={}
    password=password_override or password
    if len(password)<12:
        raise ValueError('The synthetic demo password must be at least 12 characters.')
    for role in ['admin','faculty','hod','dean','iqac']:
        users[role]=create_user(store,'demo-'+role,'Demo '+role.title(),password,role,'demo-alex' if role=='faculty' else None)
    users['other']=create_user(store,'demo-other','River Demo',password,'faculty','demo-river')
    for cat,kind,value in [('research','conference',1),('teaching','feedback_summative',90),('administrative','committee',1)]:
        r={'id':'demo-'+cat,'category':cat,'kind':kind,'faculty_id':'demo-alex','title':'Synthetic '+cat+' activity','value':value,'students':20,'year':2026,'month':6,'authors':['Alex Demo'],'source_id':'synthetic-'+cat,'locator':'Synthetic evidence, line 2','raw':{'synthetic':True}}
        store.put('records',r)
        if ready:
            store.put('consents',{'id':'demo-alex:'+r['source_id'],'faculty_id':'demo-alex','source_id':r['source_id'],'granted':True,'actor':users['faculty']['id'],'at':now()})
            store.put('evidence',{'id':'demo-alex:'+r['id'],'faculty_id':'demo-alex','record_id':r['id'],'status':'verified','note':'Synthetic test fixture verification','record_hash':hashobj(r),'actor':users['hod']['id'],'reviewer':'Demo Hod','at':now()})
    p={'id':'synthetic-policy','name':'SYNTHETIC training rubric — not institutional policy','cycle':'2025-26','profile':'balanced','source_id':'synthetic-policy','reference':'SYNTHETIC TEST FIXTURE ONLY','status':'approved' if ready else 'draft','created_by':users['dean']['id'],
        'rules':[{'kind':'conference','category':'research','method':'count','weight':10,'divisor':1,'cap':40,'citation':'Synthetic example clause 1'},
        {'kind':'feedback_summative','category':'teaching','method':'weighted_mean','weight':50,'divisor':100,'cap':50,'citation':'Synthetic example clause 2'},
        {'kind':'committee','category':'administrative','method':'sum','weight':5,'divisor':1,'cap':10,'citation':'Synthetic example clause 3'}],
        'bands':[{'minimum':0,'label':'Developing (synthetic)'},{'minimum':50,'label':'Good (synthetic)'},{'minimum':80,'label':'Excellent (synthetic)'}]}
    store.put('policies',p);store.audit('synthetic-fixture','sandbox.create','demo-alex',{'ready_for_tests':ready})
    return {'users':users,'password':password,'policy':p,'faculty_id':'demo-alex'}


def provision_presentation_faculty(store, password):
    """Idempotently stage River and Priya without approving or consenting for them."""
    if len(password) < 12:
        raise ValueError('The synthetic demo password must be at least 12 characters.')

    users = store.all('users')
    user_by_username = {user['username']: user for user in users}
    profiles = {profile['id']: profile for profile in store.all('profiles')}
    folder = store.path.parent / 'uploads'
    folder.mkdir(parents=True, exist_ok=True)
    changes = []

    for faculty in PRESENTATION_FACULTY:
        fid = faculty['id']
        profile = profiles.get(fid)
        if profile is None:
            profile = {
                'id': fid,
                'name': faculty['name'],
                'department': 'Synthetic Demonstration Department',
                'identity_status': 'verified',
                'aliases': [faculty['name']],
                'synthetic': True,
            }
            store.put('profiles', profile)
            profiles[fid] = profile
            changes.append({'entity': 'profile', 'id': fid, 'change': 'created'})
        elif profile.get('name') != faculty['name']:
            raise ValueError(f'Synthetic profile ID {fid!r} is already assigned to a different name.')

        candidates = [
            user for user in store.all('users')
            if user.get('username') == faculty['username'] or user.get('faculty_id') == fid
            or (fid == 'demo-river' and user.get('username') == 'demo-other'
                and user.get('faculty_id') == fid)
        ]
        if len({user['id'] for user in candidates}) > 1:
            raise ValueError(f'Multiple accounts are bound to synthetic faculty {fid!r}; resolve them manually.')
        account = candidates[0] if candidates else None
        username_owner = user_by_username.get(faculty['username'])
        if username_owner and (account is None or username_owner['id'] != account['id']):
            raise ValueError(f"Username {faculty['username']!r} is already assigned to another account.")

        if account is None:
            account = create_user(
                store, faculty['username'], faculty['name'], password, 'faculty', fid
            )
            changes.append({'entity': 'user', 'id': account['id'], 'change': 'created', 'faculty_id': fid})
        else:
            if account.get('role') != 'faculty':
                raise ValueError(f"Account {account['username']!r} is not a faculty account.")
            if account.get('faculty_id') != fid and account.get('faculty_id') is not None:
                raise ValueError(f"Account {account['username']!r} is bound to another faculty profile.")
            updated = dict(account)
            updated.update(username=faculty['username'], name=faculty['name'], faculty_id=fid)
            if not _password_matches(password, account.get('password', '')):
                from .security import password_hash
                updated['password'] = password_hash(password)
            if updated != account:
                store.put('users', updated)
                changes.append({'entity': 'user', 'id': account['id'], 'change': 'repaired', 'faculty_id': fid})
                account = updated
        user_by_username[faculty['username']] = account

        for category, kind, title, value, students, citation in faculty['activities']:
            source_id = f'{fid}-source-{category}'
            source_name = f'{faculty["name"].split()[0].lower()}-{category}.txt'
            body = (
                'SYNTHETIC PRESENTATION EVIDENCE — NOT AN INSTITUTIONAL RECORD\n'
                f'Faculty: {faculty["name"]}\n'
                'Academic cycle: 2025-26\n'
                f'Category: {category}\n'
                f'Claim: {title}\n'
                f'Citation: {citation}\n'
            ).encode('utf-8')
            digest = hashlib.sha256(body).hexdigest()
            source_path = folder / source_id
            if source_path.exists():
                if hashlib.sha256(source_path.read_bytes()).hexdigest() != digest:
                    raise ValueError(f'Synthetic source file {source_id!r} changed; refusing to overwrite it.')
            else:
                with source_path.open('xb') as source_file:
                    source_file.write(body)
            expected_source = {
                'id': source_id, 'name': source_name, 'kind': category, 'sha256': digest,
                'bytes': len(body), 'owner': account['id'], 'uploaded': True, 'synthetic': True,
            }
            existing_source = store.get('sources', source_id)
            if existing_source:
                if any(existing_source.get(key) != value for key, value in expected_source.items()):
                    raise ValueError(f'Synthetic source metadata {source_id!r} conflicts with existing data.')
            else:
                store.put('sources', {**expected_source, 'created': now()})
                changes.append({'entity': 'source', 'id': source_id, 'change': 'created'})

            record_id = f'{fid}-{category}'
            expected_record = {
                'id': record_id, 'faculty_id': fid, 'category': category, 'kind': kind,
                'title': title, 'value': value, 'students': students, 'year': 2026, 'month': 6,
                'authors': [faculty['name']], 'source_id': source_id,
                'locator': citation, 'synthetic': True,
            }
            existing_record = store.get('records', record_id)
            if existing_record:
                if any(existing_record.get(key) != value for key, value in expected_record.items()):
                    raise ValueError(f'Synthetic activity {record_id!r} conflicts with existing data.')
            else:
                store.put('records', {**expected_record, 'raw': {'synthetic': True}, 'created': now()})
                changes.append({'entity': 'activity', 'id': record_id, 'change': 'staged'})

    if changes:
        store.audit('synthetic-fixture', 'demo.faculty.provision', 'presentation-faculty', {
            'changes': changes,
            'consent_and_evidence_reviews_required': True,
        })
    return changes


def _password_matches(password, encoded):
    from .security import check_password
    try:
        return check_password(password, encoded)
    except (ValueError, TypeError, IndexError):
        return False
