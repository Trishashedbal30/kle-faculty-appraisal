"""Cross-platform local project management: python manage.py --help."""
import argparse,os,sys,getpass
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def _demo_password():
    password=os.getenv('KLE_DEMO_PASSWORD','')
    if len(password)<12:
        raise SystemExit('Set KLE_DEMO_PASSWORD to a private synthetic-demo password of at least 12 characters.')
    return password

def _provision_demo(store,password):
    from app.demo import provision_presentation_faculty
    changes=provision_presentation_faculty(store,password)
    if changes:
        print(f'Provisioned {len(changes)} synthetic River/Priya records or account changes.')
    else:
        print('River and Priya are already provisioned; no duplicate data was added.')


def main():
    parser=argparse.ArgumentParser(description='KLE Faculty Appraisal — local development and departmental pilot')
    sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('setup',help='Import supplied records and create the first administrator')
    sub.add_parser('import-check',help='Re-extract source data without modifying originals')
    run=sub.add_parser('run',help='Start on http://127.0.0.1:8000');run.add_argument('--port',type=int,default=8000)
    demo=sub.add_parser('demo',help='Start an isolated synthetic sandbox; no real data or real approvals');demo.add_argument('--port',type=int,default=8001)
    server=sub.add_parser('mcp-server',help='Run the optional MCP server against synthetic demo data only');server.add_argument('--transport',choices=['stdio','sse'],default='stdio');server.add_argument('--port',type=int,default=8002);server.add_argument('--host',default='127.0.0.1');server.add_argument('--db')
    sub.add_parser('mcp-check',help='Run a protocol smoke test for the MCP server and client')
    sub.add_parser('test',help='Run the acceptance and security test suite')
    sub.add_parser('audit-check',help='Verify the local audit hash chain')
    sub.add_parser('demo-provision',help='Safely add River and Priya to the existing synthetic demo sandbox')
    backup=sub.add_parser('backup',help='Create a consistent local SQLite backup');backup.add_argument('destination')
    args=parser.parse_args()
    if args.command=='test':
        import pytest;sys.exit(pytest.main(['-q','tests']))
    if args.command=='mcp-check':
        import asyncio
        from app.mcp_client import probe
        print(asyncio.run(probe()))
        return
    if args.command=='import-check':
        from app.importer import extract
        import json
        d=extract();print(json.dumps({'publications':len(d['research']),'feedback_rows':len(d['feedback']),'faculty_candidates':len(d['profiles']),'issues':d['issues']},indent=2));return
    if args.command=='demo':
        password=_demo_password()
        os.environ['APP_DB']=str(ROOT/'runtime-demo/app.db')
        from app.store import Store
        from app.demo import make_fixture
        store=Store()
        if not store.all('users'):
            make_fixture(store,password_override=password)
            print('Created an isolated synthetic sandbox. Demo accounts use KLE_DEMO_PASSWORD from the local process environment.')
        _provision_demo(store,password)
    if args.command=='demo-provision':
        password=_demo_password()
        os.environ['APP_DB']=str(ROOT/'runtime-demo/app.db')
        from app.store import Store
        store=Store()
        if not store.all('users'):
            raise SystemExit('No existing demo users found. Run `python manage.py demo` once to initialize the synthetic sandbox.')
        _provision_demo(store,password)
        return
    if args.command=='mcp-server':
        from app.mcp_server import run_server
        run_server(args.transport,args.host,args.port,args.db)
        return
    if args.command in ('run','demo'):
        from app.store import Store
        if not Store().all('users'):print('Run python manage.py setup first.');sys.exit(1)
        import uvicorn;uvicorn.run('app.main:app',host='127.0.0.1',port=args.port,workers=1);return
    from app.store import Store
    store=Store()
    if args.command=='setup':
        store.seed()
        if store.all('users'):print('Setup already completed. Manage accounts in the application.');return
        from app.security import create_user
        print('Create the named institutional administrator. No default passwords are installed.')
        username=input('Username: ').strip();name=input('Full name: ').strip();password=getpass.getpass('Password (12+ characters): ')
        if password!=getpass.getpass('Confirm password: '):print('Passwords did not match.');sys.exit(1)
        user=create_user(store,username,name,password,'admin');store.audit(user['id'],'setup.admin',user['id'],{'name':name})
        print('Setup complete. Run: python manage.py run')
    elif args.command=='audit-check':print('PASS' if store.verify_audit() else 'FAIL')
    elif args.command=='backup':
        import sqlite3,shutil
        dest=Path(args.destination)
        if dest.exists():raise ValueError('Choose a new backup directory; existing files are not overwritten.')
        dest.mkdir(parents=True)
        # Stop the application first so app and graph backups are mutually consistent.
        for f in (store.path,store.path.parent/'checkpoints.db'):
            if f.exists():
                with sqlite3.connect(f) as source,sqlite3.connect(dest/f.name) as target:source.backup(target)
        if (store.path.parent/'uploads').exists():shutil.copytree(store.path.parent/'uploads',dest/'uploads')
        print('Backup created. Protect it as confidential institutional data.')
if __name__=='__main__':main()
