# standard imports
import logging
import sys

# local imports
from piknik.msg import MessageEnvelope

logg = logging.getLogger(__name__)


def stream_accumulator(v, w=sys.stdout):
    w.write(v)


class Renderer:

    def __init__(self, basket, accumulator=None, wrapper=None, states_include=[], states_skip=[]):
        self.b = basket
        self.a = accumulator
        self.w = wrapper
        if self.w == None:
            logg.info('no wrapper defined. no message parts will be output')
        self.render_mode = 0
        self.states = []
        self.__make_state_filter(states_include, states_skip)
       

    def __make_state_filter(self, include, skip):
        have_include = False
        for i in range(len(include)):
            include[i] = include[i].upper()
            have_include = True
        for i in range(len(skip)):
            skip[i] = skip[i].upper()
        for state in self.b.states():
            if have_include:
                if state not in include:
                    continue
            elif state in skip:
                continue
            self.states.append(state)


    def add(self, v, accumulator=None):
        if accumulator == None:
            accumulator = self.a
        if accumulator != None:
            if v != None:
                r = accumulator(v)


    def apply_envelope_pre(self, state, issue, tags, envelope, accumulator=None):
        pass


    def apply_envelope_post(self, state, issue, tags, envelope, accumulator=None):
        pass

    
    def apply_envelope(self, state, issue, tags, envelope, accumulator=None):
        pass


    def apply_message_pre(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        pass


    def apply_message_post(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        pass

 
    def apply_message_post(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        pass

   
    def apply_message(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        pass


    def apply_message_part(self, state, issue, tags, envelope, message, message_date, message_content, accumulator=None):
        pass


    def apply_issue_pre(self, state, issue, tags, accumulator=None):
        pass


    def apply_issue_post(self, state, issue, tags, accumulator=None):
        pass


    def apply_issue_mid(self, state, issue, tags, accumulator=None):
        pass


    def apply_issue(self, state, issue, tags, accumulator=None):

        def envelope_callback(envelope, envelope_type):
            if self.w != None:
                envelope = self.w.process_envelope(envelope, envelope_type)
            else:
                envelope = MessageEnvelope(envelope)
            r = self.apply_envelope_pre(state, issue, tags, envelope, accumulator=accumulator)
            self.add(r)
            r = self.apply_envelope(state, issue, tags, envelope, accumulator=accumulator)
            self.add(r)
            r = self.apply_envelope_post(state, issue, tags, envelope, accumulator=accumulator)
            self.add(r)
            return envelope

        def message_callback(message, message_id, message_date):
            envelope = None
            if self.w == None:
                return (envelope, message,)

            (envelope, message) = self.w.process_message(message, message_id, message_date)

            initial = True
            while True:
                v = self.w.pop()
                if v == None:
                    break
                if initial:
                    r = self.apply_message_pre(state, issue, tags, envelope, message, message_id, message_date, accumulator=accumulator)
                    self.add(r)
                    r = self.apply_message(state, issue, tags, envelope, message, message_id, message_date, accumulator=accumulator)
                    self.add(r)
                    r = self.apply_message_post(state, issue, tags, envelope, message, message_id, message_date, accumulator=accumulator)
                    self.add(r)
                    initial = False

                r = self.apply_message_part(state, issue, tags, envelope, message, message_date, v)
                self.add(r)

            return (envelope, message,)

        self.b.get_msg(issue.id, envelope_callback=envelope_callback, message_callback=message_callback)


    def apply_state_pre(self, state, accumulator=None):
        self.render_mode = 1


    def apply_state_post(self, state, accumulator=None):
        pass


    def apply_state(self, state, accumulator=None):
        for issue_id in self.b.list(category=state):
            issue = self.b.get(issue_id)
            tags = self.b.tags(issue_id=issue_id)
            r = self.apply_issue_pre(state, issue, tags)
            self.add(r)
            r = self.apply_issue(state, issue, tags)
            self.add(r)
            r = self.apply_issue_post(state, issue, tags)
            self.add(r)


    def apply_begin(self, accumulator=None):
        pass


    def apply_end(self, accumulator=None):
        pass


    def apply(self, accumulator=None):
        r = self.apply_begin()
        self.add(r)

        #for state in self.b.states():
        for state in self.states:
            r = self.apply_state_pre(state)
            self.add(r)
            r = self.apply_state(state)
            self.add(r)
            r = self.apply_state_post(state)
            self.add(r)

        r = self.apply_end()
        self.add(r)
