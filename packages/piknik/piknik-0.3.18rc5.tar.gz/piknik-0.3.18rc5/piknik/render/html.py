# standard imports
import sys
import os
import logging

# external imports
import dominate
from dominate.tags import div, p, a, meta, ul, ol, li, h1, h2, link, dl, dd, dt, img
from mimeparse import parse_mime_type

# local imports
from .base import Renderer as BaseRenderer

logg = logging.getLogger(__name__)


class Accumulator:

    def __init__(self, w=sys.stdout):
        self.doc = None
        self.category = ul(_id='state_list')
        self.category_content = None
        self.issue = None
        self.msg = None
        #self.envelope_content = None
        self.envelope = None
        self.w = w
        self.last_v = None
        self.issues = []


    def add(self, v, w=None):
        if w == None:
            w = self.w
        if len(v) == 0:
            if self.envelope != None:
                self.msg.add(self.envelope)
            if self.msg != None:
                self.category.add(self.msg)
                #self.doc.add(self.msg)
            if self.last_v != None:
                self.category.add(li(self.last_v))
            self.doc.add(self.category)
            w.write(self.doc.render())
            self.last_v = None

        v_id = getattr(v, 'id', '')
        logg.debug('add id {}'.format(v_id))
        if len(v_id) > 1:
            if v_id[0] == 's':
                self.last_v = v
            if v_id[:2] == 's_':
                if self.issue != None:
                    self.category_content.add(self.issue)
                    self.category.add(li(self.category_content))
                self.category_content = v
                self.issue = ul(_id='issue_list_' + v_id[2:])
            elif v_id[:2] == 'i_':
                logg.debug('issue now')
                self.issue.add(v)
                self.issues.append(v_id[2:])
            elif v_id[:4] == 'd_i_':
                self.category = v
                self.issue = v
                self.msg = ol(_id='message_list')
                self.issues.append(v_id[2:])
            elif v_id[:4] == 'd_c_':
                self.issue.add(v)
            elif v_id[:2] == 'm_':
                if self.envelope != None:
                    self.msg.add(self.envelope)
                #self.envelope_content = v
                self.envelope = li(v)
            elif v_id[:4] == 'd_m_':
                self.envelope.add(v)
        else:
            self.doc = v
            self.last_v = None


class Renderer(BaseRenderer):

    def __init__(self, basket, accumulator=None, wrapper=None, outdir=None, states_include=[], states_skip=[]):
        if accumulator == None:
            accumulator = Accumulator().add
        super(Renderer, self).__init__(basket, accumulator=accumulator, wrapper=wrapper, states_include=states_include, states_skip=states_skip)
        self.outdir = outdir


    def apply_state(self, state, accumulator=None):
        self.render_mode = 1
        v = div(_id='s_' + state.lower())
        v.add(h2(state))
        self.add(v)
        super(Renderer, self).apply_state(state, accumulator=accumulator)


    def apply_issue(self, state, issue, tags, accumulator=None):
        if self.render_mode == 1:
            s = issue.title
            u = a(s, href=issue.id + '.html')
            return li(u, _id='i_' + issue.id)

        r = div(_id='d_i_' + issue.id)

        s = h1(issue.title)
        r.add(s)
        
        s = dd()
        s.add(dt('issue id'))
        s.add(dd(issue.id))

        s.add(dt('state'))
        s.add(dd(state))

        s.add(dt('tags'))
        if len(tags) == 1 and tags[0] == '(UNTAGGED)':
                s.add(dd(tags[0]))
        else:
            r_d = ul()
            for v in tags:
                r_d.add(li(v))
            s.add(dd(r_d))
    
        assigned = issue.get_assigned()
        s.add(dt('assigned to'))
        if len(assigned) == 0:
            s.add(dd('(not assigned)'))
        else:
            owner = issue.owner()
            r_r = ul()
            for v in assigned:
                o = v[0]
                ss = o.id()
                if o == owner:
                    ss += ' (owner)'
                r_r.add(li(ss))
            s.add(dd(r_r))

        #r.add(s)

        deps = issue.get_dependencies()
        s.add(dt('depends on'))
        if len(deps) == 0:
            s.add(dd('no dependencies'))
        else:
            r_r = ul()
            for v in deps:
                r_r.add(dd(v))
            s.add(dd(r_r))
    
        r.add(s)

        self.add(r)

        r = self.apply_issue_mid(state, issue, tags, accumulator=accumulator)
        self.add(r)

        super(Renderer, self).apply_issue(state, issue, tags, accumulator=accumulator)

    
    def apply_message(self, state, issue, tags, envelope, message, message_id, message_date, accumulator=None):
        r = div(_id='m_' + message_id)

        s = dd()
        s.add(dt('Date'))
        s.add(dd(str(message_date)))

        v = envelope.sender
        if v == None:
            v = '(unknown)'
        else:
            if envelope.valid:
                v += ' (!!)'
            else:
                v += ' (??)'
        s.add(dt('By'))
        s.add(dd(v))
        r.add(s)

        self.add(r)
       

    def apply_message_part(self, state, issue, tags, envelope, message, message_date, message_content, accumulator=None):
        logg.debug('env {}'.format(envelope.sender))
        r = None
        if message_content['filename'] != None:
            s = 'data:{}/{};base64,{}'.format(
                    message_content['type'][0],
                    message_content['type'][1],
                    message_content['contents'],
                    )
            r = None
            if message_content['type'][0] == 'image':
                r = img(src=s)
            else:
                v = os.path.basename(message_content['filename'])
                r = a(v, href=s)
            
        else:
            r = message_content['contents']

        m_id = 'd_m_{}_{}'.format(
                    message_content['id'],
                    message_content['idx'],
                    )

        return div(r, _id=m_id)


    def apply_begin(self, accumulator=None):
        r = dominate.document(title='issues for ...')
        r.head.add(meta(name='generator', content='piknik'))
        r.head.add(link(rel='stylesheet', href='style.css'))
        self.add(r)


    def apply_end(self, accumulator=None):
        self.add(())
        return None


    def apply_issue_mid(self, state, issue, tags, accumulator=None):
        logg.debug('>>>>>>>> foo')
        return h2('comments', _id='d_c_{}'.format(issue.id))
