from mycrypt import *
from os import remove


class Person:
    def __init__(self, personname, password, signing=False):
        self.personname = personname
        self.password = password
        self.signing = signing
        if self.signing:
            self.loggedin = self.signup()
        else:
            self.loggedin = self.login()
        self.containerlist = self.load_containerlist()

    def __str__(self):
        return str(self.loggedin)

    def load_containerlist(self):
        matchun, contl = matchingun(self.personname + ">-<")
        ncontl = []
        if not matchun:
            for contn in contl:
                ncontl.append(contn[len(self.personname)+3:])

            return ncontl
        return []

    def signup(self):
        try:
            cryedun, cryedpwsalt = encrypt_pw(self.personname, self.password)  # sign up
        except ValueError:  # if username already taken
            return False
        with open(f"encrypted/{cryedun}.key", "wb") as f:
            f.write(cryedpwsalt)
        return True

    def login(self):
        matchun, filen = matchingun(self.personname)  # sign in
        if matchun:  # signing
            if signin(filen, self.password)[0]:
                return True  # print("Signed in!")
            else:
                return False  # print("Invalid username or password! Please try again.")
        else:
            return False  # print("Invalid username or password! Please try again.")

    def delete_account(self, force=False):
        if len(self.containerlist) == 0 or force:
            matchun, filen = matchingun(self.personname)
            if matchun:
                remove("encrypted/" + filen)
                return True
            return False
        else:
            raise FileExistsError("Before delete account, delete all containers: {}".format(self.containerlist))


"""
pers = Person("esstee", "HelloWorld")
print(pers)"""
