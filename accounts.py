from mycrypt import *
from os import remove
import json


class Accounts:
    def __init__(self, personname, containername, contpw):
        self.personname = personname
        self.containername = containername
        self.contpw = contpw
        self.storage = self.load_storage()

    def __str__(self):
        return json.dumps(self.storage)

    def store(self):
        matchun, filen = matchingun(self.personname + ">-<" + self.containername)
        if matchun:
            remove("encrypted/" + filen)

        cryedun, cryedpwsalt, cryeddict = encrypt_dict(self.personname + ">-<" + self.containername,
                                                       self.contpw, self.storage)

        with open(f"encrypted/{cryedun}.key", "wb") as f:
            f.write(cryedpwsalt + b"\n" + cryeddict)

    def load_storage(self):
        matchun, filen = matchingun(self.personname + ">-<" + self.containername)  # sign in
        if matchun:  # sign in
            signinbool, storage = signin(filen, self.contpw, True)
            if signinbool:
                return storage
            else:
                raise ValueError("WrongPassword!")
        else:
            return {"10": ["sitename", "example@email.com", "username", "password", "note"]}

    def add_acc(self, lis):
        for i in range(10, 100):
            i = str(i)
            if type(self.storage.get(i)) != list:
                self.storage[i] = lis
                return True
        return False

    def delete_acc(self, k):
        self.storage.pop(str(k))

    def edit_acc(self, k, lis):
        self.storage[str(k)] = lis

    def selectid(self, k):
        return self.storage[str(k)]

    def change_pos(self, k1, k2):  # sub
        k1, k2 = str(k1), str(k2)
        try:
            if self.storage[k2] == "1":
                pass
        except KeyError:
            return False  # there is no k2 id

        try:
            temp = self.storage[k1]
        except KeyError:
            self.storage[k1] = self.storage[k2]
            self.delete_acc(k2)
            return True

        self.storage[k1] = self.storage[k2]
        self.storage[k2] = temp
        return True

    def isordered(self):  # sub
        for i, k in enumerate(self.storage.keys()):
            if i + 10 != int(k):
                return False
        return True

    def ordered_storage(self):
        kl = sorted(self.storage)  # key list
        newstorage = {}
        for k in kl:
            newstorage[k] = self.storage[k]
        self.storage = newstorage.copy()
        del newstorage

        while not self.isordered():
            fr, to = [], []
            for i, key in enumerate(self.storage.keys()):
                if int(key) < 10:
                    to.append(int(key) + 10)
                    fr.append(key)
                elif i + 10 != int(key):
                    to.append(int(key) - 1)
                    fr.append(key)
            for i in range(len(fr)):
                self.change_pos(to[i], fr[i])

    def delete_cont(self):
        matchun, filen = matchingun(self.personname + ">-<" + self.containername)
        if matchun:
            remove("encrypted/" + filen)
            return True
        return False

    def rename_cont(self, newname):  # auto save on
        self.delete_cont()
        self.containername = newname
        self.store()

    def sortby(self, ind, r=False):  # (i from 0 to 4)  # id1:[sitename, email, username, password, note]
        st = {}
        for i, l in zip(  # for list of sorted list
                range(1, len(self.storage) + 1),  # for ids
                sorted(self.storage.values(),
                       key=lambda x: x[ind],
                       reverse=r)
        ):

            st[i] = l
        return st

    def filterby(self, ind, filterw):
        valuelist = list(self.storage.values())
        st = {}
        for i, l in zip(
                range(1, len(valuelist) + 1),
                filter(lambda x: x[ind] == filterw.lower(), valuelist)
        ):
            st[i] = l
        return st


"""
fir = Accounts("anangamer", "top secret", "HelloCont1")
for ke, v in fir.storage.items():
    print(ke, ": ", v, sep="")
print()
for ke, v in fir.sortby(0).items():
    print(ke, ":", v)
print()
for ke, v in fir.filterby(0, "reDdiT").items():
    print(ke, ":", v)
"""
