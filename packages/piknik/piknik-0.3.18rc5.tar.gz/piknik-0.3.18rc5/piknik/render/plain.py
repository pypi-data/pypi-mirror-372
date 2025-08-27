# standard imports
import logging
import tempfile
import os
import sys

# external imports
from mimeparse import parse_mime_type

# local imports
from .base import Renderer as BaseRenderer
from .base import stream_accumulator

logg = logging.getLogger(__name__)

def to_suffixed_file(d, s, data):
    (v, ext) = os.path.splitext(s)
    r = tempfile.mkstemp(suffix=ext, dir=d)

    f = os.fdopen(r[0], 'wb')
    try:
        f.write(data)
    except TypeError:
        f.write(data.encode('utf-8'))
    f.close()

    return r[1]


class Accumulator:

    def __init__(self, w=sys.stdout):
        self.w = w


    def add(self, v):
        stream_accumulator(v, w=self.w)


class Renderer(BaseRenderer):

    def __init__(self, basket, dump_dir=None, accumulator=None, **kwargs):
        if accumulator == None:
            accumulator = Accumulator().add
        super(Renderer, self).__init__(basket, accumulator=accumulator, **kwargs)
        self.dump_dir = dump_dir


    def apply_issue(self, state, issue, tags, accumulator=None):
        if self.render_mode == 0:
            return self.apply_issue_standalone(state, issue, tags, accumulator=accumulator)

        s = '{}\t{}\t{}'.format(
                issue.title,
                ','.join(tags),
                issue.id,
                )
        if issue.alias != None:
            s += " (" + issue.alias + ")"
        s += "\n"
        self.add(s, accumulator=accumulator)
        super(Renderer, self).apply_issue(state, issue, tags, accumulator=accumulator)


    def apply_issue_standalone(self, state, issue, tags, accumulator=None):
        s = """title: {}
id: {}
state: {}
tags: {}
""".format(
        issue.title,
        issue.id,
        state,
        ', '.join(tags),
            )
        self.add(s, accumulator=accumulator)

        assigned = issue.get_assigned()

        assigns = [] 
        s = 'assigned to: '
        if len(assigned) == 0:
            assigns.append('(not assigned)')
        else:
            owner = issue.owner()
            for v in assigned:
                o = v[0]
                ss = o.id()
                if o == owner:
                    ss += ' (owner)'
                #s = '\t' + str(s) + '\n'
                assigns.append(ss)
        s += ', '.join(assigns) + '\n'

        if len(issue.dependencies) > 0:
            s += 'depends on: '
            s += ', '.join(issue.dependencies) + '\n'
        self.add(s, accumulator=accumulator)

        super(Renderer, self).apply_issue(state, issue, tags, accumulator=accumulator)


    def apply_message(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        s = '\nmessage {} from {} {} - {}\n'.format(
            message_date,
            envelope.sender,
            envelope.valid,
            message_id,
            )
        return s


    def apply_message_part(self, state, issue, tags, envelope, message, message_date, message_content, accumulator=None):
        if message_content['filename'] != None:
            if self.dump_dir != None:
                filename = to_suffixed_file(self.dump_dir, message_content['filename'], message_content['contents'])
            sz = message_content['size']
            if sz == -1:
                sz = 'unknown'
            v = '[file: {}, type {}/{}, size: {}]'.format(
                    message_content['filename'],
                    message_content['type'][0],
                    message_content['type'][1],
                    sz,
                    )
        else:
            v = message_content['contents']

        s = '\n\t' + v + '\n'
        return s


    def apply_state(self, state, accumulator=None):
        s = '[' + state + ']\n'
        self.add(s, accumulator=accumulator) 
        super(Renderer, self).apply_state(state, accumulator=accumulator)


    def apply_state_post(self, state, accumulator=None):
        self.add('\n', accumulator=accumulator)
