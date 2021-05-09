import base64
from Crypto.Cipher import AES as aes
from Crypto.Util.Padding import pad
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad

key = get_random_bytes(16)
iv = b''
if iv == b'':
    iv = get_random_bytes(16)
print(iv)
# cipher = aes.new(key, aes.MODE_CBC, iv)
# msg = "If you try to encrypt file, you can either use the openSSL or a Python solution using Crypto contributed by Thijs.".encode()

# cipher_txt = cipher.encrypt(pad(msg, aes.block_size))
# print(cipher_txt)

# cc = aes.new(key, aes.MODE_CBC, iv)
# print(unpad(cc.decrypt(cipher_txt), aes.block_size))

def encryptCSV(username, key, iv):
    original_filename = username + '.csv'
    with open(original_filename, 'rb') as f:
        original = f.read()
    cipher = aes.new(key, aes.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(original, aes.block_size))

    enc_filename = username + '.txt'
    with open(enc_filename, 'wb+') as f:
        f.write(encrypted)

def decryptCSV(username, key, iv):
    enc_filename = username + '.txt'
    with open(enc_filename, 'rb') as f:
        enc = f.read()
    cipher = aes.new(key, aes.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(enc), aes.block_size)
    
    with open(enc_filename, 'wb+') as f:
        f.write(decrypted)

def testencryptCSV(username, key, iv):
    filename = username + '.csv'
    # open the unencrypted .csv 
    with open(filename, 'rb') as f:
        original = f.read()
    cipher = aes.new(key, aes.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(original, aes.block_size))

    # replace with an encrypted version of the .csv
    with open(filename, 'wb+') as f:
        f.write(encrypted)

def testdecryptCSV(username, key, iv):
    filename = username + '.csv'
    with open(filename, 'rb') as f:
        enc = f.read()
    cipher = aes.new(key, aes.MODE_CBC, iv)
    decrypted = unpad(cipher.decrypt(enc), aes.block_size)
    
    with open(filename, 'wb+') as f:
        f.write(decrypted)

testencryptCSV('test', key, iv)
testdecryptCSV('test', key, iv)