import logging
from django.db import models
from django.conf import settings
from traceback import format_exc


class EncryptedTextField(models.Field):
    description = "Encrypted text fields using aes"
    
    def __init__(self, *args, secret_key: str = None, **kwargs):
        self.secret_key = secret_key or getattr(settings, "DEFAULT_ENCRYPTED_TEXT_FIELD_SECRET_KEY", None)
        if self.secret_key is None:
            raise Exception("set secret_key or DEFAULT_ENCRYPTED_TEXT_FIELD_SECRET_KEY")
        super().__init__(*args, **kwargs)

    def get_internal_type(self):
        return "TextField"

    def _decrypt(self, value):
        from morest.utils.aes import AESCipherManager
        try:
            return AESCipherManager(self.secret_key).decrypt(value)
        except Exception as e:
            logging.error(format_exc())
            return None
        
    def _encrypt(self, value): 
        from morest.utils.aes import AESCipherManager
        return AESCipherManager(self.secret_key).encrypt(value)
    
    def from_db_value(self, value, *_args):
        if value is None or value == '':
            return value
        return self._decrypt(value)
    
    def to_python(self, value):
        if value is None or value == '':
            return value
        return value

    def get_prep_value(self, value):
        if value is None or value == '':
            return None
        return self._encrypt(value)

    @property
    def non_db_attrs(self):
        return super().non_db_attrs + ("secret_key",)
