from pymongo.connection import Connection
from pymongo.collection import Collection
from pymongo.binary import Binary

import datetime, uuid, hashlib, random, string

gen_uuid    = lambda: uuid.uuid4().bytes
pretty_hex  = lambda b: str(uuid.UUID(bytes=b))
sha1        = lambda s: hashlib.sha1(s).hexdigest()

String      = lambda min=1, max=6: ''.join(random.sample(string.ascii_lowercase, random.randint(min, max)))
PastDate    = lambda maxdays=180: datetime.datetime.utcnow() - datetime.timedelta(
                days=random.randint(1, maxdays), minutes=random.randint(1,60*24))
TrueFalse   = lambda: random.choice([True, False])

class User(object):
    
    properties = ('name', 'username', 'password', 'email', 'options',
                    'services', 'notifications', 'created', 'status')
    
    def __init__(self, **kw):
        if kw:
            self._init_new(kw)
    
    def _init_new(self, kw):
        for f in ('name', 'username', 'password', 'email'):
            if f in kw:
                self.__setattr__(f, kw.pop(f))
            else:
                self.__setattr__(f, u'')
        
        self.created = datetime.datetime.utcnow()
        self.options = {
            'new_window': True,
            'lang': 'en',
            'private': kw.get('private', False)
        }
        self.services = {}
        self.notifications = []
        self.status = 0

        self.id = gen_uuid()
        
        self.new = self.modified = True
        
    @property
    def should_save(self):
        """True if the user should be saved to db."""
        return self.modified or self.new
    
    def password():
        doc = """Sets user password and auto-crypts it"""
        def fget(self):
            return self._password
        def fset(self, v):
            self._password = sha1(v)
            self.modified = True
        return locals()
    password = property(**password())
    
    def check_password(self, against):
        """Match a user-provided password against the current, encrypted, one"""
        return self._password == sha1(against)
    
    def uuid():
        doc = """Get or set user's UUID"""
        def fget(self):
            return pretty_hex(self.id)
        return locals()
    uuid = property(**uuid())
    
    def as_new_mongo_dict(self):
        values = map(self.__getattribute__, self.properties)
        dic = dict(zip(fields, values))
        dic['_id'] = Binary(self.id, 2)
        return dic
    
    def from_mongo(cls, son):
        u = cls()
        values = map(son.get, u.properties)
        map(u.__setattr__, u.properties, values)
        u._password = son['password']
        return u
    
    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.name)
        
def get_db():
    from pymongo.connection import Connection
    connection = Connection()
    db = connection["testing"]
    return db

def create_users_indexes(coll):
    coll.ensure_index('username', 1)
    coll.ensure_index('created', 1)
    coll.ensure_index('email', 1)

def dummy_user():
    u = User(
        name = 'John Doe',
        email = 'john@doe.org',
        username = String(5, 12),
        password = String(5, 12),
    )
    u.created = PastDate()
    u.options['private'] = TrueFalse()
    u.options['new_window'] = TrueFalse()
    return u

def populate_dummy_users(coll, repeat=1000):
    assert isinstance(coll, Collection), 'Must pass a valid pymongo Collection object'

    dummies = [dummy_user().as_new_mongo_dict() for i in xrange(repeat)]

    results = coll.insert(dummies)

