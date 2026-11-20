import pytest
from fastapi.testclient import TestClient

import app.main as main
from app.demo import make_fixture, provision_presentation_faculty
from app.security import check_password
from app.store import Store
import manage


def test_demo_password_requires_a_private_environment_value(monkeypatch):
    monkeypatch.delenv('KLE_DEMO_PASSWORD', raising=False)
    with pytest.raises(SystemExit, match='KLE_DEMO_PASSWORD'):
        manage._demo_password()

    monkeypatch.setenv('KLE_DEMO_PASSWORD', 'local-synthetic-password')
    assert manage._demo_password() == 'local-synthetic-password'


def test_presentation_faculty_provisioning_is_safe_to_rerun(tmp_path):
    store = Store(tmp_path / 'demo.db')
    fixture = make_fixture(store, ready=True)
    alex_release = {
        'id': 'alex-existing-release',
        'faculty_id': 'demo-alex',
        'version': 1,
        'report': {'final_rating': 'Good (synthetic)'},
    }
    store.put('releases', alex_release)
    store.put('active', {'id': 'demo-alex', 'release_id': alex_release['id']})

    changes = provision_presentation_faculty(store, fixture['password'])
    assert changes

    users = {user['username']: user for user in store.all('users')}
    assert 'demo-other' not in users
    assert users['demo-river']['faculty_id'] == 'demo-river'
    assert users['demo-priya']['faculty_id'] == 'demo-priya'
    assert check_password(fixture['password'], users['demo-river']['password'])
    assert check_password(fixture['password'], users['demo-priya']['password'])

    for faculty_id in ('demo-river', 'demo-priya'):
        activities = [record for record in store.all('records') if record.get('faculty_id') == faculty_id]
        assert {record['category'] for record in activities} == {'research', 'teaching', 'administrative'}
        for record in activities:
            source = store.get('sources', record['source_id'])
            assert source and source['synthetic']
            assert (tmp_path / 'uploads' / source['id']).is_file()
            assert store.get('evidence', f"{faculty_id}:{record['id']}") is None
            assert store.get('consents', f"{faculty_id}:{source['id']}") is None

    entities_before = {
        kind: len(store.all(kind))
        for kind in ('users', 'profiles', 'sources', 'records', 'consents', 'evidence', 'releases')
    }
    assert provision_presentation_faculty(store, fixture['password']) == []
    assert {
        kind: len(store.all(kind))
        for kind in ('users', 'profiles', 'sources', 'records', 'consents', 'evidence', 'releases')
    } == entities_before
    assert store.get('releases', alex_release['id']) == alex_release
    assert store.get('active', 'demo-alex') == {'id': 'demo-alex', 'release_id': alex_release['id']}


def test_river_and_priya_can_complete_manual_appraisal_flow(env):
    provision_presentation_faculty(env['store'], env['fixture']['password'])

    def login(client, username):
        response = client.post('/api/login', json={
            'username': username,
            'password': env['fixture']['password'],
        })
        assert response.status_code == 200, response.text
        client.headers['X-CSRF-Token'] = response.json()['csrf']
        return client

    with TestClient(main.app) as river_client, TestClient(main.app) as priya_client, \
            TestClient(main.app) as hod_client, TestClient(main.app) as dean_client, \
            TestClient(main.app) as iqac_client:
        for faculty_id, username, client in (
            ('demo-river', 'demo-river', river_client),
            ('demo-priya', 'demo-priya', priya_client),
        ):
            faculty = login(client, username)
            activities = faculty.get(f'/api/faculty/{faculty_id}/records').json()
            assert {record['category'] for record in activities} == {
                'research', 'teaching', 'administrative',
            }
            for record in activities:
                consent = faculty.post(
                    f"/api/faculty/{faculty_id}/consents/{record['source_id']}",
                    json={'granted': True},
                )
                assert consent.status_code == 200, consent.text
                reviewed = login(hod_client, 'demo-hod').post(
                    f"/api/faculty/{faculty_id}/evidence/{record['id']}",
                    json={'status': 'verified', 'note': 'Synthetic source and locator checked by demo HoD.'},
                )
                assert reviewed.status_code == 200, reviewed.text

            plan = faculty.post('/api/plans', json={
                'faculty_id': faculty_id,
                'cycle': '2025-26',
                'profile': 'balanced',
                'policy_id': 'synthetic-policy',
                'request': f'Prepare the complete synthetic appraisal for {username}.',
                'completeness': {
                    'research': 'Synthetic research records declared complete.',
                    'teaching': 'Synthetic aggregate teaching records declared complete.',
                    'administrative': 'Synthetic institutional service records declared complete.',
                },
            })
            assert plan.status_code == 200, plan.text
            plan_id = plan.json()['id']
            assert faculty.post(f'/api/plans/{plan_id}/lock').status_code == 200
            run = faculty.post('/api/runs', json={'plan_id': plan_id})
            assert run.status_code == 200, run.text
            run_id = run.json()['id']
            assert run.json()['status'] == 'awaiting_quality', run.text
            assert not [r for r in env['store'].all('releases') if r['faculty_id'] == faculty_id]

            decisions = (
                (dean_client, 'demo-dean', 'awaiting_hod'),
                (hod_client, 'demo-hod', 'awaiting_release'),
                (iqac_client, 'demo-iqac', 'published'),
            )
            for reviewer_client, reviewer_username, expected_status in decisions:
                response = login(reviewer_client, reviewer_username).post(
                    f'/api/runs/{run_id}/decision',
                    json={
                        'action': 'approve',
                        'note': f'Manual synthetic {reviewer_username} review completed.',
                    },
                )
                assert response.status_code == 200, response.text
                assert response.json()['status'] == expected_status, response.text
                if expected_status != 'published':
                    assert not [r for r in env['store'].all('releases') if r['faculty_id'] == faculty_id]

            releases = faculty.get('/api/releases').json()
            own_release = next(r for r in releases if r['faculty_id'] == faculty_id)
            assert own_release['version'] == 1
            assert own_release['report']['score']['total'] > 0
            assert len(own_release['report']['approvals']) == 3
