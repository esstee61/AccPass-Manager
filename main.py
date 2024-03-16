from getpass import getpass
from person import Person
from accounts import Accounts
from mycrypt import decryedfilenames, encrypt_pw, matchingun, createmainkeysalt
from os import rename, system
import time

USERNAME_MIN_LEN = 4
PASSWORD_MIN_LEN = 7
PW_FREQUENCY = 150  # each 150 seconds obligation to enter password


def check_invalchar(x, pw=False):
    if pw:
        charset = " !\"#$ßæ¨~£€´₺½%&'()*+,-/:;<=>?@[\\]^_`{|}"
    else:
        charset = " !\"#$ßæ¨~£€´₺½%&'()*+,/:;<=>?@[\\]^`{|}"

    for c in charset:
        if c in x:
            return c
    return False


class Main:
    def __init__(self):
        self.run = True
        self.openingrun = True
        self.personname = None  # used in acc name
        self.password = None  # used in both cont pw and acc pw and cont menu pw
        self.contname = None  # used in new_cont
        self.contsaved = True  # save before leaving thing
        self.cont = None  # Accounts(object) used in new_cont and cont_menu
        self.auth = None  # used for log in and sign up
        self.showmenucounter = 0
        self.pwgettime = None

    def loop(self):
        while self.run:
            if self.openingrun:
                self.opening()
            if not self.openingrun and self.run:
                self.mainmenu(True)

    def opening(self):  # opening menu
        print("________________________________________________________")
        print("_____Save Your Accounts and Passwords with Security_____")
        print("____Login____")
        print("--exit-Q")
        print("--sign up-0")
        self.personname = input("----username--> ")

        if self.personname.lower() == "q":  # exit program
            self.run = False
        elif self.personname == "decryptfilenames":
            print(decryedfilenames())
        elif self.personname == "createmainkeyiamsure":
            createmainkeysalt()
            print("New main key has been created!!!")

        elif self.personname.lower() == "0":  # __sign up screen__
            print("________________________________________________________")
            print("_____Save Your Accounts and Theirs Informations With Security_____")
            print("____Sign up____")
            print("--exit-Q")
            print("<=> You cannot change your username once you signed up!")

            self.personname = self.inp_personname()  # take username
            if not self.personname:
                return False  # go mainloop

            print("___Sign Up___")
            a = self.inp_password(True)  # take password
            if not a:
                return False  # go mainloop

            print("Creating your account...")
            self.auth = Person(self.personname, self.password, True)
            if self.auth.loggedin:
                print("Created your account!")
                self.openingrun = False
            else:
                print("[>-83-<] Cannot create account! Username already taken. Try another username.")
                return False
        else:
            # check username
            if len(self.personname) < USERNAME_MIN_LEN:
                print("[>-88-<] At least {} charachters! Try again.".format(USERNAME_MIN_LEN))
                return False
            elif check_invalchar(self.personname):
                print("[>-91-<] Invalid charachter({}) in username! Try again.".format(
                    check_invalchar(self.personname)))
                return False

            print("____Log In____")
            a = self.inp_password()
            if not a:
                return False  # go mainloop
            print("Authenticating...")
            self.auth = Person(self.personname, self.password)
            if self.auth.loggedin:
                print("Authenticated!")
                self.openingrun = False
            else:
                print("[>-105-<] Invalid username or password!")
                return False

    def show_menu(self):
        print("________________________________________________________")
        print("_____Save Your Accounts and Passwords with Security_____")
        print("____Main Menu____")
        print("->> Username - {}".format(self.personname))
        print("->> Containers - {}".format(self.auth.containerlist))
        print("--exit-Q")
        print("--delete account-9")
        print("--change username-8")
        print("--change password-7")
        print("--new container-2")
        print("--container-1+[Nth container]")

    def mainmenu(self, show=False):
        if self.showmenucounter % 3 == 0 or show:
            self.show_menu()
        self.showmenucounter += 1
        menuc = input("------>")
        if menuc == "q":
            self.openingrun = True

        elif menuc == "Q":
            self.run = False

        elif menuc == "9":
            print("____Password____")
            a = self.inp_password()
            if not a:
                return False  # go mainloop
            print("Authenticating...")
            self.auth = Person(self.personname, self.password)
            if self.auth.loggedin:
                print("Authenticated!")
            else:
                print("[>-142-<] Invalid username or password!")
                return False

            while not (menuc.lower() == "y" or menuc.lower() == "n"):
                print("<=>Are you sure about delete the account called '{}'?".format(self.personname))
                menuc = input("---(Y/N)--->")
                if menuc.lower() == "y":
                    print("Deleting... the account called '{}'".format(self.personname))
                    try:
                        self.auth.delete_account()
                        print("Deleted the account called '{}'".format(self.personname))
                        self.openingrun = True
                    except FileExistsError:
                        print("[>-155-<] Before delete the account, delete all containers: {}"
                              .format(self.auth.containerlist))
                elif menuc.lower() == "n":
                    break
                else:
                    print("[>-160-<] Invalid value! ({})".format(menuc))

        elif menuc == "7":

            print("___Type current password___")
            a = self.inp_password()
            if not a:
                return False  # go mainloop
            print("Authenticating...")
            self.auth = Person(self.personname, self.password)
            if self.auth.loggedin:
                print("Authenticated!")
                oldpw = self.password
            else:
                print("[>-174-<] Invalid username or password!")
                return False

            print("___Type new password___")
            a = self.inp_password(True)  # new password
            if not a:
                self.password = oldpw
            elif self.password == oldpw:
                print("[>-182-<] You entered the same password with current password!")
            else:  #
                self.auth.delete_account(True)
                self.auth = Person(self.personname, self.password, True)
                print("Password changed!")

        elif menuc == "8":
            a = self.inp_password()
            if not a:
                return False  # go mainloop
            print("Authenticating...")
            self.auth = Person(self.personname, self.password)
            if self.auth.loggedin:
                print("Authenticated!")
            else:
                print("[>-197-<] Invalid username or password!")
                return False

            print("___New Username___")
            newname = self.inp_personname()
            if not newname:
                return False
            elif matchingun(newname)[0]:
                print("[>-205-<] Username is already taken!")
                return False
            print('=================')
            print(self.personname, newname)
            print(decryedfilenames(self.personname))
            print(filter(lambda x: self.personname in x, decryedfilenames()))
            print('=================')
            for enfn, defn in zip(decryedfilenames(self.personname),
                                  filter(lambda x: self.personname in x, decryedfilenames())):
                print(enfn, defn)
                print(self.personname, newname)
                newun = defn.replace(self.personname, newname)
                rename(enfn, encrypt_pw(newun, self.password, False)[0] + ".key")
            self.personname = newname
            self.openingrun = True
            print("Changed username!")

        elif menuc == "2":
            self.inp_cont()

        elif len(menuc) == 2 and menuc[0] == "1" and menuc[1].isdigit():

            size = len(self.auth.containerlist)
            menuc = int(menuc[1])
            if 1 <= menuc <= size:
                self.contmenu(menuc)  # cont menu
            else:
                print("[>-232-<] There is no {}th container!".format(menuc))
                self.mainmenu()

        elif menuc.lower() == "m":
            self.showmenucounter = 0
            self.mainmenu()

        elif menuc == "cls":
            system("cls")

        else:
            print("[>-243-<] Invalid value! '{}'".format(menuc))
            self.mainmenu()

    def contmenu(self, i):
        if i != -1:
            print("____Access Container____")
            print("->> Container named {}".format(self.auth.containerlist[i - 1]))  # container name

        while i + 1:
            a = self.inp_password()
            if not a:
                return False

            self.contname = self.auth.containerlist[i - 1]
            try:
                self.cont = Accounts(self.personname, self.contname, self.password)
                self.pwgettime = time.time()
            except ValueError:
                print("[>-261-<] Invalid password!")
                continue
            print("Loading container...")
            break  # move to actual container menu
        # to container menu
        print("________________________________________________________")
        print("_____Save Your Accounts and Their Informations With Security_____")
        print("____Container Menu____")  # not including edit_acc
        print("<=> Don't left AFK on this menu!")
        print("->> Container: {}".format(self.contname))
        print("--exit-Q")
        print("--delete this container-9")
        print("--rename this container-8")
        print("--save container-7")
        print("--delete accword-6+[accword id]")
        print("--add accword-5")
        print("--change position of-4+[first accword id][second accword id]")
        print("--sort by-3+[any number from 0 to 4][if 0 then reverse]")
        print("--filter-2+[any number from 0 to 4][filterword]")
        print("--show container content-1")
        print("--change container password-0")
        self.contmenuchoose()

    def contmenuchoose(self):
        while True:
            c = input("------>")
            if c.lower() == "q":
                if self.contsaved:
                    print("Quitted!")
                else:
                    c = input("-Do you want to save it before leaving?--(q/y/n)-->")
                    if c.lower() == "y":
                        self.cont.store()
                        self.contsaved = True
                        print("Saved and quitted!")
                    elif c.lower() == "n":
                        self.contsaved = True
                        print("Quitted without saving!")

                if c == "Q":
                    self.run = False
                return False

            elif c == "9":  # delete container

                if time.time() - self.pwgettime > PW_FREQUENCY:
                    print(
                        "[>-308-<] Before delete, you have to show container content! Last enter {} seconds ago".format(
                            time.time() - self.pwgettime))
                    continue

                while not (c.lower() == "y" or c.lower() == "n"):
                    print("<=>Are you sure about delete the container called '{}'?".format(self.contname))
                    c = input("---(Y/N)--->")
                    if c.lower() == "y":
                        print("Deleting... the container called '{}'".format(self.contname))
                        bd = self.cont.delete_cont()  # boolen delete
                        if bd:
                            print("Deleted the container called '{}' with success!".format(self.contname))
                        else:
                            print("[>-321-<] There might have been some unexpected thing!")
                        self.auth.containerlist = self.auth.load_containerlist()
                        return False
                    elif c.lower() == "n":
                        break
                    else:
                        print("[>-327-<] Invalid value! ({})".format(c))

            elif c == "8":  # rename container

                if time.time() - self.pwgettime > PW_FREQUENCY:
                    print(
                        "[>-333-<] Before delete, you have to show container content! Last enter {} seconds ago".format(
                            time.time() - self.pwgettime))
                    continue

                contnewname = self.inp_personname("container name")
                if not contnewname:
                    continue
                elif contnewname in self.auth.containerlist:
                    print("[>-341-<] There is already a container called {}!".format(contnewname))
                    continue
                print("Renaming... the container '{}' to '{}'".format(self.contname, contnewname))
                self.cont.rename_cont(contnewname)
                print("Renamed the container '{}' to '{}'".format(self.contname, contnewname))
                self.contname = contnewname
                self.contsaved = False

            elif c == "7":  # save container

                print("Saving... the container called '{}'".format(self.contname))
                self.cont.store()
                print("Saved the container called '{}'".format(self.contname))
                self.contsaved = True

            elif len(c) == 3 and c[0] == "6" and c[1:].isdigit():  # delete accword 610/699

                if time.time() - self.pwgettime > PW_FREQUENCY:
                    print(
                        "[>-360-<] Before delete, you have to show container content! Last enter {} seconds ago".format(
                            time.time() - self.pwgettime))
                    continue

                c = int(c[1:])
                if 10 <= c:
                    d = "a"
                    while not (d.lower() == "y" and d.lower() == "n"):
                        try:
                            if self.cont.storage[str(c)]:
                                pass
                        except KeyError:
                            print("[>-372-<] There is no id {}!".format(c))
                            break
                        print("<=>Are you sure about delete the accword called '{}'?".format(self.cont.selectid(c)))
                        d = input("---(Y/N)--->")
                        if d.lower() == "y":
                            self.cont.delete_acc(c)
                            print("Deleted the accword! Reordered container.")
                            self.cont.ordered_storage()
                            self.contsaved = False
                            break
                        elif d.lower() == "n":
                            break
                        else:
                            print("[>-385-<] Invalid value! ({})".format(d))
                else:
                    print("[>-387-<] Invalid value for deleting accword! ({})".format(c))

            elif c == "5":  # [sitename, email, username, password, note] to add accword

                sitename = input("-sitename---->")
                if sitename.lower() == "q":
                    continue
                email = input("-email---->")
                if email.lower() == "q":
                    continue
                username = input("-username---->")
                if username.lower() == "q":
                    continue
                passw = input("-password---->")
                if passw.lower() == "q":
                    continue
                note = input("-note---->")
                if note.lower() == "q":
                    continue
                a = self.cont.add_acc([sitename, email, username, passw, note])
                if a:
                    print("Added this accword:", [sitename, email, username, passw, note])
                    self.contsaved = False
                else:
                    print("[>-411-<] Unexpected error! you cant add more than 90 accwords?!")

            elif len(c) == 5 and c == "4" and c[1:].isdigit():  # change pos 41099

                d, c = int(c[1:3]), int(c[3:])
                uplimit = len(self.cont.storage) + 9
                if 10 <= c <= uplimit and 10 <= d <= uplimit and c != d:
                    a = self.cont.change_pos(c, d)
                    if a:
                        print("Changed positions of {} and {}.".format(d, c))
                        self.cont.ordered_storage()
                        self.contsaved = False
                    else:
                        print("[>-424-<] There is no id {}!".format(d))
                else:
                    print("[>-426-<] Must between 10-{} and different! ({},{})".format(uplimit, c, d))

            elif (len(c) == 2 or len(c) == 3) and c[0] == "3" and c[1:].isdigit():  # 30/34 - 300/340

                if time.time() - self.pwgettime > PW_FREQUENCY:
                    print("[>-431-<] Before sort, you have to show container content! Last enter {} seconds ago".format(
                        time.time() - self.pwgettime))
                    continue

                if not (0 <= int(c[1]) <= 4):
                    print("[>-436-<] Must between 30-34!")
                    continue

                if len(c) == 3 and c[2] == "0":
                    h = True
                else:
                    h = False
                by = int(c[1])
                for ke, v in self.cont.sortby(by, h).items():
                    print(ke, ": ", v, sep="")
                if not self.cont.storage:
                    print("This container is empty!")
                continue

            elif len(c) > 2 and c[0] == "2" and c[1].isdigit() and not c[2:].isdigit():  # 20spotify/24main
                if time.time() - self.pwgettime > PW_FREQUENCY:
                    print("[>-452-<] Before filter, you have to show container content! Last enter {} seconds ago"
                          .format(time.time() - self.pwgettime))
                    continue

                if not (0 <= int(c[1]) <= 4):
                    print("[>-457-<] Must between 20-24!")
                    continue

                h = c[2:]
                by = int(c[1])
                for ke, v in self.cont.filterby(by, h).items():
                    print(ke, ": ", v, sep="")
                if not self.cont.storage:
                    print("This container is empty!")
                continue

            elif c == "1":  # show container content
                if type(self.pwgettime) == float and self.pwgettime > time.time() - PW_FREQUENCY:
                    c = "continue"
                while True:
                    if c != "continue":
                        print("___Acces Container Content___")
                        a = self.inp_password()
                        if not a:
                            break
                    try:
                        Accounts(self.personname, self.contname, self.password)
                        if c != "continue":
                            self.pwgettime = time.time()
                    except ValueError:
                        print("[>-482-<] Invalid password!")
                        continue
                    c = "continue second"  # continue after while loop
                    break

                if c == "continue second":
                    for ke, v in self.cont.storage.items():
                        print(ke, ": ", v, sep="")
                    if not self.cont.storage:
                        print("This container is empty!")

            elif c == "0":

                print("___Type current password___")
                oldpw = self.password
                a = self.inp_password()  # current password
                if not a:
                    pass
                elif self.password == oldpw:  # self.password changed to
                    print("___Type new password___")
                    a = self.inp_password(True)  # new password
                    if not a:
                        self.password = oldpw
                    elif self.password == oldpw:
                        print("[>-506-<] You entered the same password with current password!")
                    else:
                        temp = self.cont.storage
                        self.cont.delete_cont()
                        self.cont = Accounts(self.personname, self.contname, self.password)
                        self.cont.storage = temp
                        self.cont.store()
                        self.contsaved = True
                        print("Password changed!")
                else:
                    print("[>-516-<] Wrong password!")
                    self.password = oldpw

            elif c.lower() == "m":
                self.contmenu(-1)
                return False

            elif c == "cls":
                system("cls")

            else:
                print("[>-527-<] Invalid value: '{}'".format(c))

    def inp_cont(self):
        while True:  # input name and pw
            self.contname = self.inp_personname("container name")
            if not self.contname:
                return False
            elif self.contname in self.auth.containerlist:
                print("[>-535-<] There is already a container called {}!".format(self.contname))
                return False

            a = self.inp_password(True)
            if not a:
                return False
            break
        self.cont = Accounts(self.personname, self.contname, self.password)
        self.cont.store()
        self.auth.containerlist = self.auth.load_containerlist()
        return True

    def inp_password(self, pwtwice=False):  # return False if user want to exit else: return nothing
        while True:  # take password
            pw1 = getpass(prompt="---exit-q_type password-->")
            if pw1.lower() == "q":
                return False
            elif len(pw1) < PASSWORD_MIN_LEN:
                print("[>-553-<] At least {} charachters to sign up! Try again.".format(PASSWORD_MIN_LEN))
                continue

            if pwtwice:
                pw2 = getpass(prompt="---type password again-->")
            else:
                pw2 = pw1

            if pw1 != pw2:
                print("[>-562-<] Passwords don't match with each other! Try again.")
            elif check_invalchar(pw1, True):
                print("[>-564-<] Invalid charachter({}) in password! Try again.".format(check_invalchar(pw1, True)))
            else:
                self.password = pw1
                return True

    @staticmethod
    def inp_personname(prom="username"):
        if prom == "container name":
            num = USERNAME_MIN_LEN
        else:
            num = USERNAME_MIN_LEN
        while True:  # take username
            name = input("---exit-q_type {}--> ".format(prom))
            if name.lower() == "q":  # exit to opening
                return False
            elif len(name) < num:
                print("[>-580-<] At least {} charachters to sign up! Try again.".format(num))
            elif check_invalchar(name):
                print("[>-582-<] Invalid char({}) in username! Try again.".format(check_invalchar(name)))
            else:
                return name


program = Main()
program.loop()
