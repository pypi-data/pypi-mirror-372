# standard imports
import logging

# external imports
import shep
from shep.error import StateItemNotFound

# local imports
from .error import DeadIssue
from .issue import Issue
from .issue import id_generator
from .msg import IssueMessage
from .identity import Identity

logg = logging.getLogger(__name__)

class Basket:

    def __init__(self, state_factory, message_wrapper=None):
        self.no_resurrect = True
        self.state = state_factory.create_states(default_state='proposed', verifier=self.__check_resurrect)
        self.state.add('backlog')
        self.state.add('pending')
        self.state.add('doing')
        self.state.add('review')
        self.state.add('finished')
        self.state.add('blocked')
        self.state.alias('doingblocked', self.state.DOING | self.state.BLOCKED)
        self.state.alias('pendingblocked', self.state.PENDING | self.state.BLOCKED)
        self.limit = self.state.FINISHED
        self.state.sync()

        self.__tags = state_factory.create_tags()
        self.__tags.sync(ignore_auto=False)

        self.__msg = state_factory.create_messages()
        self.__msg_wrap = message_wrapper

        self.__alias = state_factory.create_aliases()

        self.issues_rev = {}


    def id_generator(self):
        while True:
            issue_id = id_generator()
            issue_alias = issue_id[:5]
            try:
                self.__alias.get(issue_alias)
            except FileNotFoundError:
                return issue_id


    def __check_resurrect(self, st, k, f, t):
        if self.no_resurrect:
            if f & self.state.FINISHED > 0:
                raise DeadIssue(k)


    def add(self, issue):
        issue_id = str(issue.id)
        j = str(issue)
        if issue.alias != None:
            self.__alias.put(issue.alias, issue.id)
        self.state.put(issue_id, contents=j)
        self.__tags.put(issue_id)
        return issue_id


    def get(self, issue_id):
        logg.debug("basket issue get {}".format(issue_id))
        r = self.state.get(issue_id)
        if r == None:
            aliased_issue_id = self.__alias.get(issue_id)
            r = self.state.get(aliased_issue_id)
            logg.debug("resolved issue {} from alias '{}': {}".format(aliased_issue_id, issue_id, r))
        o = Issue.from_str(r)
        return o


    def get_state(self, issue_id):
        o = self.get(issue_id)
        v = self.state.state(o.id)
        return self.state.name(v)


    def list(self, category=None):
        if category == None:
            category = self.state.BACKLOG
        else:
            category = self.state.from_name(category)
        return self.state.list(category)


    def state_pending(self, issue_id):
        o = self.get(issue_id)
        self.state.move(o.id, self.state.PENDING)


    def state_doing(self, issue_id):
        o = self.get(issue_id)
        self.state.move(o.id, self.state.DOING)


    def state_review(self, issue_id):
        o = self.get(issue_id)
        self.state.move(o.id, self.state.REVIEW)


    def state_backlog(self, issue_id):
        o = self.get(issue_id)
        self.state.move(o.id, self.state.BACKLOG)


    def state_finish(self, issue_id):
        o = self.get(issue_id)
        self.state.move(o.id, self.state.FINISHED)
        if o.alias != None:
            self.__alias.purge(o.alias)


    def advance(self, issue_id):
        o = self.get(issue_id)
        if self.state.state(o.id) & self.limit > 0:
            raise DeadIssue(o.id)
        self.unblock(o.id)
        self.state.next(o.id)


    def unblock(self, issue_id):
        o = self.get(issue_id)
        if self.state.state(o.id) & self.state.BLOCKED > 0:
            self.state.unset(o.id, self.state.BLOCKED)


    def block(self, issue_id):
        o = self.get(issue_id)
        self.state.set(o.id, self.state.BLOCKED)


    def blocked(self):
        return self.list('blocked')


    def states(self):
        return self.state.all(pure=True, bit_order=True)


    def tag(self, issue_id, tag):
        v = 0
        try:
            v = self.__tags.from_name(tag)
        except AttributeError:
            self.__tags.add(tag)
            v = self.__tags.from_name(tag)
     
        o = self.get(issue_id)
        move = False
        try:
            r = self.__tags.state(o.id)
            if r == 0:
                move = True
        except shep.error.StateItemNotFound:
            self.__tags.put(o.id)
            move = True

        if move:
            self.__tags.move(o.id, v)
        else:
            self.__tags.set(o.id, v)



    def untag(self, issue_id, tag):
        v = self.__tags.from_name(tag)
        o = self.get(issue_id)
        self.__tags.unset(o.id, v, allow_base=True)


    def tags(self, issue_id):
        o = self.get(issue_id)
        v = None
        try:
            v = self.__tags.state(o.id)
        except StateItemNotFound:
            self.__tags.put(o.id)
            #self.__tags.set(o.id, self.__tags.UNTAGGED)
            v = self.__tags.state(o.id)
        r = self.__tags.elements(v)
        if r == 'UNTAGGED':
            r = '(' + r + ')'
        return shep.state.split_elements(r)


    def __get_msg(self, issue_id, envelope_callback=None, message_callback=None, post_callback=None):
        o = self.get(issue_id)
        try:
            v = self.__msg.get(o.id)
            m = IssueMessage.parse(o, v.decode('utf-8'), envelope_callback=envelope_callback, message_callback=message_callback, post_callback=post_callback)
            return m
        except FileNotFoundError as e:
            logg.debug('instantiating new message log for {} {}'.format(o.id, e))

        return IssueMessage(o)


    def get_msg(self, issue_id, envelope_callback=None, message_callback=None, post_callback=None):
        return self.__get_msg(issue_id, envelope_callback=envelope_callback, message_callback=message_callback, post_callback=post_callback)
 
    
    def dep(self, issue_id, dependency_issue_id):
        o = self.get(issue_id)
        od = self.get(dependency_issue_id)
        r = o.dep(od.id)
        self.state.replace(o.id, contents=str(o))
        return r


    def undep(self, issue_id, dependency_issue_id):
        o = self.get(issue_id)
        self.get(dependency_issue_id)
        r = o.undep(dependency_issue_id)
        self.state.replace(o.id, contents=str(o))
        return r


    def assign(self, issue_id, identity):
        o = self.get(issue_id)
        v = Identity(identity)
        r = o.assign(v)
        self.state.replace(o.id, contents=str(o))
        return r


    def owner(self, issue_id, identity):
        o = self.get(issue_id)
        v = Identity(identity)
        r = o.set_owner(v)
        self.state.replace(o.id, contents=str(o))
        return r


    def unassign(self, issue_id, identity):
        o = self.get(issue_id)
        v = Identity(identity)
        r = o.unassign(v)
        self.state.replace(o.id, contents=str(o))
        return r


    def msg(self, issue_id, *args):
        o = self.get(issue_id)
        m = self.__get_msg(o.id)
        m.add(*args, wrapper=self.__msg_wrap)
        ms = m.as_bytes()
        self.__msg.put(o.id, ms)
        return m
