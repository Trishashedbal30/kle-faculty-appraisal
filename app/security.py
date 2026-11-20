import hashlib,hmac,secrets,time
from fastapi import HTTPException
from .store import uid,now
ROLES={'admin','faculty','hod','dean','iqac'}
def fail(message,status=400):raise HTTPException(status,message)
def password_hash(password,salt=None):
    salt=salt or secrets.token_hex(16)
    return salt+':'+hashlib.pbkdf2_hmac('sha256',password.encode(),bytes.fromhex(salt),600000).hex()
def check_password(password,value):return hmac.compare_digest(password_hash(password,value.split(':')[0]),value)
def create_user(store,username,name,password,role,faculty_id=None):
    username=username.strip().lower()
    if role not in ROLES or len(password)<12 or not username or len(username)>100 or len(name.strip())<3:fail('Use a valid role, username and a password of at least 12 characters.')
    with store.tx():
        if any(u['username']==username for u in store.all('users')):fail('Username already exists.')
        if role=='faculty':
            p=store.get('profiles',faculty_id)
            if not p or p['identity_status']!='verified':fail('Verify the faculty identity before creating an account.')
            if any(u.get('faculty_id')==faculty_id for u in store.all('users')):fail('A faculty account is already bound to this identity.')
        u={'id':uid(),'username':username,'name':name.strip(),'password':password_hash(password),'role':role,'faculty_id':faculty_id,'active':True,'created':now()}
        return store.put('users',u)
def public_user(u):return {k:v for k,v in u.items() if k!='password'}
def require_role(user,*roles):
    if user['role'] not in roles:fail('This action is not permitted for your role.',403)
def scope(user,fid):
    if user['role']=='faculty' and user.get('faculty_id')!=fid:fail('This faculty record is outside your access scope.',403)
def login(store,username,password):
    name=username.strip().lower();t=time.time()
    with store.tx() as db:
        f=db.execute('SELECT * FROM failures WHERE name=?',(name,)).fetchone()
        if f and f['count']>=8 and f['until']>t:fail('Too many attempts. Try again in 15 minutes.',429)
        u=next((x for x in store.all('users') if x['username']==name and x['active']),None)
        good=check_password(password,u['password']) if u else check_password(password,password_hash('unused-comparison-password'))
        if not u or not good:
            count=(f['count'] if f and f['until']>t else 0)+1
            db.execute('INSERT OR REPLACE INTO failures VALUES(?,?,?)',(name,count,t+900))
            # Return a sentinel; raising inside the transaction would undo the attempt counter.
            return None
        db.execute('DELETE FROM failures WHERE name=?',(name,))
        token=secrets.token_urlsafe(40);csrf=secrets.token_urlsafe(30)
        db.execute('INSERT INTO sessions VALUES(?,?,?,?)',(hashlib.sha256(token.encode()).hexdigest(),u['id'],csrf,t+8*3600))
        store.audit(u['id'],'auth.login',u['id'],{})
        return token,csrf,u
