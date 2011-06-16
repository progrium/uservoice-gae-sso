import array
import base64
import hashlib
import urllib
import operator

from django.utils import simplejson

try:
    from Crypto.Cipher import AES
except ImportError:
    # Just pass through in dev mode
    class AES:
        MODE_CBC = 0
        new = classmethod(lambda k,x,y,z: AES)
        encrypt = classmethod(lambda k,x: x)
        decrypt = classmethod(lambda k,x: x)

def token(message, account_key, api_key):
    block_size = 16
    mode = AES.MODE_CBC
    
    iv = "OpenSSL for Ruby"
    
    json = simplejson.dumps(message, separators=(',',':'))
    
    salted = api_key+account_key
    saltedHash = hashlib.sha1(salted).digest()[:16]
    
    json_bytes = array.array('b', json[0 : len(json)]) 
    iv_bytes = array.array('b', iv[0 : len(iv)])
    
    # # xor the iv into the first 16 bytes.
    for i in range(0, 16):
    	json_bytes[i] = operator.xor(json_bytes[i], iv_bytes[i])
    
    pad = block_size - len(json_bytes.tostring()) % block_size
    data = json_bytes.tostring() + pad * chr(pad)
    aes = AES.new(saltedHash, mode, iv)
    encrypted_bytes = aes.encrypt(data)
    
    return base64.b64encode(encrypted_bytes)