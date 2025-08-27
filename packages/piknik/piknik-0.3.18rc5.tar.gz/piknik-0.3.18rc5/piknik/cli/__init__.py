# standard imports
import os

# local imports
from piknik import Basket
from piknik.store import FileStoreFactory
from piknik.crypto import PGPSigner

class Context:

    def __init__(self, arg, assembler, mode=0, gpg_home=os.environ.get('GPGHOME'), create=True):
        self.issue_id = arg.issue_id
        self.files_dir = arg.files_dir
        self.alias = getattr(arg, 'alias', None)
        self.show_finished = getattr(arg, 'show_finished', False)
        self.show_states = getattr(arg, 'state', [])
        #self.store_factory = FileStoreFactory(arg.d)
        store_factory = FileStoreFactory(arg.d, create=create)
        self.signer = None
        sign_fn = None
        if hasattr(arg, 's'):
            self.signer = PGPSigner(default_key=arg.s, use_agent=True)
            sign_fn = self.signer.sign
        self.basket = Basket(store_factory, message_wrapper=sign_fn)
        self.gpg_home = gpg_home
        assembler(self, arg)
