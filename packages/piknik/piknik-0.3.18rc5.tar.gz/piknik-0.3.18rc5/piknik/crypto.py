# standard imports
import os
import logging
import tempfile
from email.message import Message

# external imports
import gnupg

# local imports
from piknik.error import VerifyError
from piknik.error import UnknownIdentityError
from piknik.error import SignError
from piknik.wrap import Wrapper

logg = logging.getLogger(__name__)
logging.getLogger('gnupg').setLevel(logging.ERROR)


class PGPSigner(Wrapper):

    def __init__(self, home_dir=None, dump_dir=None, default_key=None, passphrase=None, use_agent=False, skip_verify=False):
        super(PGPSigner, self).__init__(dump_dir=dump_dir)
        self.gpg = gnupg.GPG(gnupghome=home_dir)
        self.default_key = default_key
        self.passphrase = passphrase
        self.use_agent = use_agent
        self.sign_material = None
        self.pre_buffer = []
        self.__skip_verify = skip_verify


    def set_from(self, msg, passphrase=None):
        r = None
        for v in self.gpg.list_keys(True):
            if self.default_key == None or v['fingerprint'].upper() == self.default_key.upper():
                r = v['uids'][0]
                break
        if r == None:
            raise UnknownIdentityError('no signing keys found')
        msg.add_header('From', r)


    def sign(self, msg, passphrase=None): # msg = IssueMessage object
        m = Message()
        m.set_type('multipart/relative')
        m.add_header('X-Piknik-Envelope', 'pgp')
        ms = Message()
        ms.set_type('application/pgp-signature')
        fn = '{}.asc'.format(msg.get('X-Piknik-Msg-Id'))
        ms.add_header('Content-Disposition', 'attachment', filename=fn)

        self.set_from(msg, passphrase=passphrase)
        v = msg.as_string()
        sig = self.gpg.sign(v, keyid=self.default_key, detach=True, passphrase=self.passphrase)
        if sig.status != 'signature created':
            raise SignError()
        ms.set_payload(str(sig))
    
        m.attach(msg)
        m.attach(ms)

        return m

    
    def process_envelope(self, msg, env_header):
        self.envelope = None
        if env_header != 'pgp':
            raise VerifyError('expected envelope type "pgp", but got {}'.format(env_header))
        if self.envelope_state > -1 and self.envelope_state < 2:
            raise VerifyError('new envelope before previous was verified ({})'.format(self.envelope_state))
        self.sign_material = None
        super(PGPSigner, self).process_envelope(msg, env_header)
        return self.envelope


    def process_message(self, msg, message_id, message_date):
        if msg.get('From') != None:
            self.envelope.sender = msg.get('From')

        if self.envelope_state == 0:
            self.envelope_state = 1
            self.sign_material = msg
            return (self.envelope, msg,)

        if msg.get('Content-Type') != 'application/pgp-signature':
            self.pre_buffer.append((self.envelope, message_id, msg,))
            return (self.envelope, msg,)

        v = self.sign_material.as_string()

        sig = msg.get_payload()
        (fd, fp) = tempfile.mkstemp()
        f = os.fdopen(fd, 'w')
        f.write(sig)
        f.close()
        r = self.gpg.verify_data(fp, v.encode('utf-8'))
        os.unlink(fp)
        
        if r.key_status != None:
            raise VerifyError('unexpeced key status {}'.format(r.key_status))
        if r.status == 'no public key':
            logg.warning('public key for {} not found, cannot verify'.format(r.fingerprint))
        elif r.status != 'signature valid':
            if self.__skip_verify:
                logg.warning('invalid signature for message {}'.format(message_id))
            else:
                raise VerifyError('invalid signature for message {}'.format(message_id))
        else:
            logg.debug('signature ok from {}'.format(r.fingerprint))
            self.envelope.valid = True
        if self.envelope.sender == None:
            self.envelope.sender = r.fingerprint
        self.envelope_state = 2
        
        while True:
            try:
                v = self.pre_buffer.pop(0)
                self.add(v[0], v[1], v[2])
            except IndexError:
                break

        return (self.envelope, msg,)
