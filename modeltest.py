import datetime, uuid, hashlib, random, string

gen_uuid    = lambda: uuid.uuid4().bytes
pretty_hex  = lambda b: str(uuid.UUID(bytes=b))
sha1        = lambda s: hashlib.sha1(s).hexdigest()

class User(object):
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
        fields = ('name', 'username', 'password', 'email', 'options', 'services', 'notifications', 'created', 'status')
        values = map(self.__getattribute__, fields)
        
        dic = dict(zip(fields, values))
        
        dic['_id'] = self.id
        
        # instead of doing binary for mongo.. for testing first
        dic['_id'] = self.uuid
        
        return dic
    
    def __repr__(self):
        return "<User('%s', '%s')>" % (self.username, self.name)
        
    
