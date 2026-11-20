from app import reports


def test_report_pdf_renders_without_local_logo(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, 'ROOT', tmp_path)
    release = {
        'version': 1,
        'created': '2026-01-01T00:00:00+00:00',
        'hash': 'synthetic-hash',
        'id': 'synthetic-release',
        'report': {
            'cycle': '2025-26',
            'faculty_name': 'Synthetic Faculty',
            'department': 'Synthetic Department',
            'score': {'total': 0, 'components': [], 'rounding': 'Synthetic test'},
            'final_rating': 'Synthetic',
            'summary': 'Synthetic report.',
            'approvals': [],
            'evidence': [],
            'checks': [],
            'completeness': {},
            'excluded': [],
        },
    }

    assert reports.render_pdf(release).startswith(b'%PDF')
