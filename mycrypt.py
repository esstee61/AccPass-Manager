from base64 import urlsafe_b64encode
from os import urandom, listdir, mkdir
import json
import cryptography.fernet
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def createmainkeysalt():  # new main key
    salt = urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=480000)
    main_key = urlsafe_b64encode(kdf.derive("AOY4bh0kk7Sh".encode()))
    fer = Fernet(main_key)
    salt = fer.encrypt(salt)
    try:
        with open("encrypted/key.mainkey", "wb") as fi:
            fi.write(main_key + b"\n" + salt)
    except FileNotFoundError:
        if 'encrypted' not in listdir():
            mkdir('encrypted')
            createmainkeysalt()


def loadmainkeysalt():  # load main key
    # return type bytes
    # return main key and main salt
    try:
        with open("encrypted/key.mainkey", "rb") as fi:
            key, salt = fi.read().split(b"\n")
    except FileNotFoundError:
        createmainkeysalt()
        with open("encrypted/key.mainkey", "rb") as fi:
            key, salt = fi.read().split(b"\n")

    fer = Fernet(key)
    salt = fer.decrypt(salt)
    return key, salt


def decryedfilenames(un=""):  # Is there matching username file?
    filenames = []
    main_key = loadmainkeysalt()[0]
    for filen in listdir("encrypted/"):
        if ".key" in filen:
            # mainkey for check is there matching username
            fer = Fernet(main_key)
            # File's username
            fn = filen[:-4].encode()
            fn = fer.decrypt(fn).decode()
            if not un:
                filenames.append(fn)
            else:
                if un == fn or un == fn[:len(un)]:  # anan, anan>-< ; anan
                    filenames.append(filen)
    return filenames


def matchingun(un):  # Is there matching username file?
    contnames = []
    main_key = loadmainkeysalt()[0]
    for fn in listdir("encrypted"):
        if ".key" in fn:
            # mainkey for check is there matching username
            fer = Fernet(main_key)
            # File's username
            fun = fn[:-4].encode()
            fun = fer.decrypt(fun).decode()
            if fun == un:
                return True, fn
            elif un in fun:
                contnames.append(fun)  # fun[len(un):]
    return False, contnames


def encrypt_pw(un, pw, e=True):  # return one-step encrypted username and two-step encrypted password
    if matchingun(un)[0] and e:
        raise ValueError("This Username Is Already Taken!")
    un = un.encode()
    pw = pw.encode()
    salt = urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=480000)
    # 1st encrypt with own-special key
    key = urlsafe_b64encode(kdf.derive(pw))
    fer = Fernet(key)
    pw = fer.encrypt(pw)
    # 2nd encrypt with main key
    key = loadmainkeysalt()[0]
    fer = Fernet(key)
    pw = fer.encrypt(pw)
    un = fer.encrypt(un)
    salt = fer.encrypt(salt)
    return un.decode(), pw + b"\n" + salt


def gen_samekey(pw, salt):  # regenerate the same key if password true
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=480000)
    skey = urlsafe_b64encode(kdf.derive(pw.encode()))
    return skey


def signin(fn, passw, checkdic=False):  # check is sign in password true
    with open("encrypted/"+fn, "rb") as fi:
        if checkdic:
            pw, salt, dic = fi.read().split(b"\n")
        else:
            dic = None
            pw, salt = fi.read().split(b"\n")

    # 1st decrypt with mainkey
    main_key = loadmainkeysalt()[0]
    fer = Fernet(main_key)
    salt = fer.decrypt(salt)
    pw = fer.decrypt(pw)
    if checkdic:
        dic = fer.decrypt(dic)
    # 2nd decrypt with own-special key
    samekey = gen_samekey(passw, salt)
    fer = Fernet(samekey)
    try:
        pw = fer.decrypt(pw).decode()
        if checkdic:
            dic = json.loads(fer.decrypt(dic).decode())
    except cryptography.fernet.InvalidToken:
        return False, dic
    if passw == pw:
        return True, dic
    return False, dic


def encrypt_dict(un, pw, dic):
    un = un.encode()
    pw = pw.encode()
    dic = json.dumps(dic).encode()
    salt = urandom(16)
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(),
                     length=32,
                     salt=salt,
                     iterations=480000)
    # 1st encrypt with own-special key
    key = urlsafe_b64encode(kdf.derive(pw))
    fer = Fernet(key)
    pw = fer.encrypt(pw)
    dic = fer.encrypt(dic)
    # 2nd encrypt with main key
    key = loadmainkeysalt()[0]
    fer = Fernet(key)
    pw = fer.encrypt(pw)
    un = fer.encrypt(un)
    dic = fer.encrypt(dic)
    salt = fer.encrypt(salt)
    return un.decode(), pw + b"\n" + salt, dic
