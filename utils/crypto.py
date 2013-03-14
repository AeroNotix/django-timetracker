import hashlib
import os
import string
import random

from django.conf import settings

def hasher(string):
    '''Helper method to hash a string to SHA512'''
    h = hashlib.sha512(settings.SECRET_KEY + string).hexdigest()
    for _ in range(settings.HASH_PASSES):
        h = hashlib.sha512(h).hexdigest()
    return h

def get_random_string(length, set=string.ascii_letters+string.digits):
    '''Gets a random string'''
    return ''.join(random.choice(set) for _ in range(length))
