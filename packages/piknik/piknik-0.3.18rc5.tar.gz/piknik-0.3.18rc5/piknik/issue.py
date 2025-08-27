# standard imports
import uuid
import json
import datetime

# local imports
from piknik.identity import Identity
from piknik.error import UnknownIdentityError
from piknik.error import ExistsError


def id_generator():
        return str(uuid.uuid4())

class Issue:

    def __init__(self, title, issue_id=None, alias=None, id_generator=id_generator):
        if issue_id == None:
            issue_id = id_generator()
        self.id = issue_id
        self.title = title
        self.assigned = []
        self.assigned_time = []
        self.dependencies = []
        self.alias = alias
        self.owner_idx = 0


    @staticmethod
    def from_str(s):
        r = json.loads(s)
        o = Issue(title=r['title'], issue_id=r['id'])
        for i, k in enumerate(r['assigned'].keys()):
            p = Identity(k)
            o.assigned.append(p)
            t = datetime.datetime.utcfromtimestamp(r['assigned'][k])
            o.assigned_time.append(t)
            if r['owner'] == None or k == r['owner']:
                r['owner'] = k
                o.owner_idx = i
        for v in r['dependencies']:
            o.dep(v)
        o.alias = r.get('alias')
        return o


    def assign(self, identity, t=None):
        if identity in self.assigned:
            raise ExistsError(identity)
        if t == None:
            t = datetime.datetime.utcnow()
        self.assigned.append(identity)
        self.assigned_time.append(t)

    
    def dep(self, dependency_issue_id):
        if dependency_issue_id in self.dependencies:
            raise ExistsError(self.id, dependency_issue_id)
        self.dependencies.append(dependency_issue_id)


    def undep(self, dependency_issue_id=None):
        if dependency_issue_id == None:
            self.dependencies = []
            return
        self.dependencies.remove(dependency_issue_id)


    def get_assigned(self):
        return list(zip(self.assigned, self.assigned_time))


    def get_dependencies(self):
        return self.dependencies


    def unassign(self, identity):
        for i, v in enumerate(self.assigned):
            if v == identity:
                self.assigned.remove(v)
                if i == self.owner_idx:
                    self.owner_idx = 0
                return True
        raise UnknownIdentityError(identity)


    def owner(self):
        try:
            return self.assigned[self.owner_idx]
        except IndexError:
            pass

        raise UnknownIdentityError


    def set_owner(self, identity):
        r = self.owner()
        if identity == r:
            return False

        for i, v in enumerate(self.assigned):
            if v == identity:
                self.owner_idx = i
                return True

        raise UnknownIdentityError(identity)

    
    def __str__(self):
        o = {
            'id': str(self.id),
            'title': self.title,
            'assigned': {},
            'dependencies': self.dependencies,
            'alias': self.alias,
            'owner': None,
            }

        for i, v in enumerate(self.get_assigned()):
            aid = v[0].id()
            o['assigned'][aid] = v[1].timestamp()
            if self.owner_idx == i:
                o['owner'] = aid

        return json.dumps(o)


    def __eq__(self, o):
        if o.id != self.id:
            return False
        if o.title != self.title:
            return False
        if len(self.assigned) != len(o.assigned):
            return False
        for i, v in enumerate(self.assigned):
            if o.assigned[i] != v:
                return False
            
        return True
