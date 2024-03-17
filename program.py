import tkinter as tk
from ttkbootstrap import ttk
from ttkbootstrap.dialogs.dialogs import Messagebox
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.window import Window, Toplevel
from os import rename

from person import Person
from accounts import Accounts
from mycrypt import decryedfilenames, encrypt_pw, matchingun

USERNAME_MIN_LEN = 4
PASSWORD_MIN_LEN = 7


def check_invalid_char(x, pw=False):
    if pw:
        charset = " !\"#$ßæ¨~£€´₺½%&'()*+,-/:;<=>?@[\\]^_`{|}"
    else:
        charset = " !\"#$ßæ¨~£€´₺½%&'()*+,/:;<=>?@[\\]^`{|}"

    for c in charset:
        if c in x:
            return c

    return False


class Struct:
    def __init__(self):
        self.username = None  # used in acc name
        self.password = None  # used in both cont pw and acc pw and cont menu pw
        self.cont_name = None  # used in new_cont
        self.cont_is_saved = True  # save before leaving thing
        self.cont = None  # Accounts(object) used in new_cont and cont_menu
        self.auth = None  # used for log in and sign up


class MyApp(Window):
    pw2: bool | str

    def __init__(self, title, themename, size, icon=None):
        super().__init__(title=title, size=size, themename=themename, iconphoto=None)
        self.cframe = None
        self.mframe = None
        self.signup_login_frame = None
        self.iconbitmap(icon)
        self.struct = Struct()

        # self.struct.username = 'admin'

        self.un = tk.StringVar(value=self.struct.username)
        self.pw1 = tk.StringVar()  # value='password')
        self.pw2 = False

        self.signup_login_menu()

        self.after(1000, self.print_window_size)

        self.mainloop()

    def container_menu(self):
        side_on = False

        def side_menu():
            settings_btn.configure(state='disabled')
            nonlocal side_on
            fto = (0.765, 0.9)
            sfto = ((0.21, -0.1),  # rel x
                    (0.888, 0.24),  # rel h
                    (0.208, 0.1),  # rel w
                    (0.085, 0.36))  # rel y
            steps = 56

            def animate(step):
                if not side_on:
                    frame.place_configure(relwidth=fto[0] + (fto[1] - fto[0]) * (step + 1) / steps)
                    side_frame.place_configure(relx=sfto[0][0] + (sfto[0][1] - sfto[0][0]) * (step + 1) / steps,
                                               relheight=sfto[1][0] + (sfto[1][1] - sfto[1][0]) * (step + 1) / steps,
                                               relwidth=sfto[2][0] + (sfto[2][1] - sfto[2][0]) * (step + 1) / steps,
                                               rely=sfto[3][0] + (sfto[3][1] - sfto[3][0]) * (step + 1) / steps)
                else:
                    frame.place_configure(relwidth=fto[1] - (fto[1] - fto[0]) * (step + 1) / steps)
                    side_frame.place_configure(relx=sfto[0][1] - (sfto[0][1] - sfto[0][0]) * (step + 1) / steps,
                                               relheight=sfto[1][1] - (sfto[1][1] - sfto[1][0]) * (step + 1) / steps,
                                               relwidth=sfto[2][1] - (sfto[2][1] - sfto[2][0]) * (step + 1) / steps,
                                               rely=sfto[3][1] - (sfto[3][1] - sfto[3][0]) * (step + 1) / steps)
                if step < steps:
                    if step == 0:
                        self.mframe.after(0, animate, step + 1)
                    else:

                        self.mframe.after(10, animate, step + 1)
                else:
                    settings_btn.configure(state='normal')

            animate(0)
            side_on = not side_on

        def auto_fit():
            table.autofit_columns()
            table.autoalign_columns()
            table.after(2550, auto_fit)

        def renew_table():
            table.pack_forget()
            table.delete_rows()
            for ke, v in self.struct.cont.storage.items():
                val = [ke, *v]
                table.insert_row(values=val)

            table.pack(side='right', fill='both')
            table.reset_table()

        def reset_id(is_deleted=False):
            rows = table.get_rows()
            if rows != sorted(rows, key=lambda row: int(row.values[0])) or is_deleted:
                del_list = []
                new_values = []
                for i, r in enumerate(rows):
                    new_id = i + 10
                    if new_id == r.values[0]:
                        continue
                    new_values.append([new_id] + r.values[1:])
                    del_list.append(r.iid)

                for ind, iid in enumerate(del_list):
                    table.insert_row(values=new_values[ind])
                    try:
                        table.delete_row(iid=iid)
                    except AttributeError:
                        print('attr error')
            else:
                print('There are no changes.')

        def del_items(_):
            rows = table.get_rows(selected=True)
            for r in rows:
                if r == rows[-1]:
                    table.view.selection_set(table.view.next(r.iid))
                table.delete_row(iid=r.iid)
                self.struct.cont.delete_acc(r.values[0])
            self.struct.cont.ordered_storage()
            self.struct.cont_is_saved = False
            print("Deleted the accword! Reordered container.")
            reset_id(True)

        def prntevent(_):
            rows = table.get_rows()

            for row in sorted(rows, key=lambda r: r.values[0]):
                print(row.values)

        def move_row(e):
            if table.get_rows(selected=True) is None or len(table.get_rows(selected=True)) == 0:
                print('121 error ')
                return False
            rows = table.get_rows(selected=True)
            print(*map(lambda x: x.values, rows))
            if e.keysym == 'Up':
                table.move_selected_row_up()
            else:
                table.move_row_down()
            table.view.selection_clear()
            table.after(10, lambda: table.view.selection_set([*map(lambda x: x.iid, rows)]))

        def quit_cont():
            if not self.struct.cont_is_saved:
                yes_no = Messagebox.show_question('Do you want to save changes?', 'Unsaved Progress')
                if yes_no == 'Yes':
                    print("Saving... the container called '{}'".format(self.struct.cont_name))
                    self.struct.cont.store()
                    self.struct.cont_is_saved = True
                    print("Saved and quitted!")
                elif yes_no == 'No':
                    self.struct.cont_is_saved = True
                    print("Quitted without saving!")
                else:
                    print("Not quitted!")
                    return None
            self.cframe.pack_forget()
            self.main_menu()

        def ch_password():
            self.password_input('Container Password',
                                'Type password for the container named "{}"'.format(self.struct.cont_name),
                                'login')

            if not self.pw2:
                return None

            try:
                self.struct.cont = Accounts(self.struct.username, self.struct.cont_name, self.pw2)
            except ValueError:
                Messagebox.show_error(title="Wrong Password!", message='[>197<] Invalid password!')
                return False

            old_pw = self.pw2

            self.password_input('New Password', 'Enter container: {} new password'.format(self.struct.cont_name),
                                'Continue', 'New Password')
            self.pw1.set(self.pw2)
            self.password_input('Password Again',
                                'Please enter container: {} new password again.'.format(self.struct.cont_name), 'Enter',
                                'New Password')

            if self.pw1.get() != self.pw2:
                Messagebox.show_error(title="Passwords don't match!",
                                      message='[>211<] Passwords are not same! Please enter passwords again.')
            elif self.pw2 == old_pw:
                Messagebox.show_error(title="Error!", message='[>213<] New password is same with old password!')
            elif not self.check_username_pw(False):
                pass
            else:
                self.struct.password = self.pw2
                # change password
                temp = self.struct.cont.storage
                self.struct.cont.delete_cont()
                self.struct.cont = Accounts(self.struct.username, self.struct.cont_name, self.struct.password)
                self.struct.cont.storage = temp
                self.struct.cont.store()
                self.struct.cont_is_saved = True
                print("Password changed!")
                Messagebox.show_info('Password changed successfully.', 'Password Changed!')

        def ch_cont_name():
            self.password_input('Container Password', 'Enter container password for change container name', 'continue')
            if not self.pw2:
                return None

            try:
                Accounts(self.struct.username, self.struct.cont_name, self.pw2)
                print("Authenticated!")
            except ValueError:
                Messagebox.show_error(title="Wrong Password!", message='[>237<] Invalid password!')
                return False

            self.password_input('New Container Name', 'Enter new container name', 'Rename', 'Container Name', None)
            if not self.pw2:
                return None

            if self.pw2 in self.struct.auth.containerlist:
                Messagebox.show_error(title="Error", message='[>-245-<] Container name is already taken!')
                return False

            print("Renaming... the container '{}' to '{}'".format(self.struct.cont_name, self.pw2))
            self.struct.cont.rename_cont(self.pw2)
            print("Renamed the container '{}' to '{}'".format(self.struct.cont_name, self.pw2))
            self.struct.cont_name = self.pw2
            self.struct.cont_is_saved = False
            Messagebox.show_info('Container renamed successfully! Dont forget to save.', 'Changed Name')

        def delete_cont():
            self.password_input('Delete Container!', 'Delete Container. Enter your password first.', btn_text='Delete')
            if not self.pw2:
                return False

            try:
                self.struct.cont = Accounts(self.struct.username, self.struct.cont_name, self.pw2)
                print("Correct password")
            except ValueError:
                Messagebox.show_error(title="Wrong Password!", message='[>264<] Invalid password!')
                return False

            yesorno = Messagebox.yesno(
                "Are you sure about delete the container called '{}'?".format(self.struct.cont_name),
                'Delete Container!')

            if yesorno == "Yes":
                bd = self.struct.cont.delete_cont()  # boolen delete
                if bd:
                    print("Deleted the container called '{}' with success!".format(self.struct.cont_name))
                    self.cframe.pack_forget()
                    self.main_menu()
                    Messagebox.show_info(
                        'Container: "{}" is deleted! Quitting main menu.'.format(self.struct.cont_name), 'Deleted!')
                    self.struct.auth.containerlist = self.struct.auth.load_containerlist()
                else:
                    Messagebox.show_error(title="Wrong Password!", message='[>280<] Invalid password!')
                    return False
            elif yesorno == "No":
                pass
            else:
                print('293 error!')

        def save_container():
            self.struct.cont.store()
            self.struct.cont_is_saved = True
            print('Cont saved')

        def add_accpass():
            def btn_click():
                vals = [10 + len(table.get_rows())]
                for var in var_list:  # tk.StringVar object TO str object
                    vals.append(var.get())

                a = self.struct.cont.add_acc(vals[1:])
                if a:
                    print("Added this accword:", vals[1:])
                    self.struct.cont_is_saved = False
                else:
                    Messagebox.show_error(title="Unknown Error!",
                                          message='[>299<] You cant add more than 90 accpasses?!!')
                tl.destroy()
                renew_table()

            input_info = ['Sitename', 'Email', 'Username', 'Password', 'Note']
            var_list = []
            for _ in range(5):
                var_list.append(tk.StringVar())

            tl = Toplevel(title='Add AccPass', minsize=(355, 320), size=(450, 500), maxsize=(775, 675))
            tl.focus_set()
            tl.grid_anchor('center')

            ttk.Label(tl, text='Enter all the information', font='Roboto 12', justify='center').grid(row=0, column=2, columnspan=2)

            for i, info in zip(range(1, 6), input_info):
                ttk.Label(tl, text=info).grid(row=i, column=1, sticky='e')
                ttk.Entry(tl, textvariable=var_list[i - 1]).grid(row=i, column=2, columnspan=2, sticky='ew', pady=4)

            ttk.Button(tl, text='Enter', command=btn_click, cursor='hand2')\
                .grid(row=6, column=2, rowspan=2, columnspan=2, sticky='ew')

            tl.rowconfigure('all', weight=12, uniform='a')
            tl.columnconfigure('all', weight=12, uniform='a')
            tl.columnconfigure(3, weight=4, uniform='a')
            tl.columnconfigure(4, weight=12, uniform='a')

            tl.grab_set()
            tl.wait_window()

        self.minsize(960, 400)
        self.geometry('1625x750')
        self.title('AccPass Manager - Container Menu')

        self.cframe = ttk.Frame(self, relief='solid')
        self.cframe.pack(expand=True, fill='both')

        # side frame
        side_frame = ttk.Frame(self.cframe, relief='solid', style='light')
        side_frame.place(anchor='ne', relheight=.24, relwidth=.1, rely=.36, relx=-0.1)

        settings_btn = ttk.Button(self.cframe, text='S', style='warning', command=side_menu, cursor='hand2')
        settings_btn.place(relx=.055, rely=.15, relwidth=.06, relheight=.1, anchor='center')

        menu_label = ttk.Label(self.cframe, text=self.struct.username + ' - ' + self.struct.cont_name, style='info')
        menu_label.place(relx=.015, rely=.02)

        quit_btn = ttk.Button(side_frame, text='Q', style='danger', command=quit_cont, cursor='hand2')
        quit_btn.place(relx=.80, rely=.0788, relwidth=.294, relheight=.112, anchor='center')

        delete_btn = ttk.Button(side_frame, text='Delete Container', style='secondary', command=delete_cont, cursor='hand2')
        delete_btn.place(rely=0.3387, relx=0.1, relheight=0.1, relwidth=0.8)

        ch_username_btn = ttk.Button(side_frame, text='Change Name', style='secondary', command=ch_cont_name, cursor='hand2')
        ch_username_btn.place(rely=0.5257, relx=0.1, relheight=0.1, relwidth=0.8)
        
        ch_password_btn = ttk.Button(side_frame, text='Container Password', style='secondary', command=ch_password, cursor='hand2')
        ch_password_btn.place(rely=0.7127, relx=0.1, relheight=0.1, relwidth=0.8)

        # frame
        frame = ttk.Frame(self.cframe, relief='solid')
        frame.place(relx=.995, rely=.005, relheight=.99, relwidth=.882, anchor='ne')

        table = Tableview(frame, bootstyle='dark', coldata=['ID', 'Sitename', 'Email', 'Username', 'Password', 'Note'],
                          searchable=True, paginated=True, pagesize=15)

        inner_frame = ttk.Frame(frame)
        inner_frame.pack(side='right', fill='both', expand=True)
        table.pack(side='right', fill='both')

        save_btn = ttk.Button(inner_frame, text='Save changes', style='success', command=save_container, cursor='hand2')
        save_btn.pack(anchor='ne', padx=12, pady=8, ipady=16)

        reset_btn = ttk.Button(inner_frame, text='Reset IDs', style='info', command=reset_id, cursor='hand2')
        reset_btn.pack(fill='x', padx=12, pady=25, anchor='s', expand=True, ipady=5)

        add_btn = ttk.Button(inner_frame, text='Add AccPass', style='info', command=add_accpass, cursor='hand2')
        add_btn.pack(fill='x', padx=12, pady=25, anchor='n', expand=True, ipady=5)

        # table bindings
        table.view.bind('<Delete>', del_items)
        table.view.bind('<ButtonRelease-2>', prntevent)
        table.view.bind('<Delete>', del_items)
        table.view.bind('<Shift-KeyPress-Up>', move_row)
        table.view.bind('<Shift-KeyPress-Down>', move_row)

        table.align_column_center()
        renew_table()
        auto_fit()

    def cont_command(self, cont_name):
        print(cont_name, ' <====')
        # self.struct.cont_name = self.struct.auth.containerlist[i]
        self.struct.cont_name = cont_name
        self.password_input('Container Password',
                            'Type password for the container named "{}"'.format(self.struct.cont_name),
                            'login')

        if not self.pw2:
            return None

        self.struct.password = self.pw2

        try:
            print("Loading container...")
            self.struct.cont = Accounts(self.struct.username, self.struct.cont_name, self.struct.password)
            print("Container has been loaded.")
            self.mframe.pack_forget()
            self.container_menu()
        except ValueError:
            Messagebox.show_error(title="Wrong Password!", message='[>406<] Invalid password!')

    def main_menu(self):
        side_on = False

        def side_menu():
            settings_btn.configure(state='disabled')
            nonlocal side_on
            fto = (0.765, 0.9)
            sfto = ((0.21, -0.1),  # rel x
                    (0.888, 0.24),  # rel h
                    (0.208, 0.1),  # rel w
                    (0.085, 0.36))  # rel y
            
            steps = 56

            def animate(step):
                if not side_on:
                    frame.place_configure(relwidth=fto[0] + (fto[1] - fto[0]) * (step + 1) / steps)
                    side_frame.place_configure(relx=sfto[0][0] + (sfto[0][1] - sfto[0][0]) * (step + 1) / steps,
                                               relheight=sfto[1][0] + (sfto[1][1] - sfto[1][0]) * (step + 1) / steps,
                                               relwidth=sfto[2][0] + (sfto[2][1] - sfto[2][0]) * (step + 1) / steps,
                                               rely=sfto[3][0] + (sfto[3][1] - sfto[3][0]) * (step + 1) / steps)

                else:
                    frame.place_configure(relwidth=fto[1] - (fto[1] - fto[0]) * (step + 1) / steps)
                    side_frame.place_configure(relx=sfto[0][1] - (sfto[0][1] - sfto[0][0]) * (step + 1) / steps,
                                               relheight=sfto[1][1] - (sfto[1][1] - sfto[1][0]) * (step + 1) / steps,
                                               relwidth=sfto[2][1] - (sfto[2][1] - sfto[2][0]) * (step + 1) / steps,
                                               rely=sfto[3][1] - (sfto[3][1] - sfto[3][0]) * (step + 1) / steps)

                if step < steps:
                    if step == 0:
                        self.mframe.after(0, animate, step + 1)
                    else:
                        self.mframe.after(10, animate, step + 1)
                else:
                    settings_btn.configure(state='normal')

            animate(0)
            side_on = not side_on

        def delete_acc():
            self.password_input('Delete Account!',
                                'You should delete all the containers\nbefore deleting account.\n\tEnter your '
                                'password first.',
                                btn_text='Delete')
            if not self.pw2:
                return False

            print("Authenticating...")
            self.struct.auth = Person(self.struct.username, self.pw2)
            if self.struct.auth.loggedin:
                print("Authenticated!")
            else:
                Messagebox.show_error(title="Wrong Password!", message='[>461<] Invalid password!')
                return False

            yesorno = Messagebox.yesno("Are you sure about delete the account called '{}'?"
                                       .format(self.struct.username), 'Delete Account!')

            if yesorno == "Yes":
                try:
                    self.struct.auth.delete_account()
                    print("Deleted the account called '{}'".format(self.struct.username))
                    self.mframe.pack_forget()
                    self.signup_login_menu()
                    Messagebox.show_info('Account is deleted! Quitting login screen.', 'Deleted!')

                except FileExistsError:
                    Messagebox.show_error(title="Cannot Delete!",
                                          message='[>478<] Before delete the account, delete all the containers: {}'
                                          .format(self.struct.auth.containerlist))
            elif yesorno == "No":
                pass
            else:
                print('490 error!')

        def ch_password():
            self.password_input('Password', 'Enter your old password.', btn_text='Continue')

            print("Authenticating...")
            self.struct.auth = Person(self.struct.username, self.pw2)
            if self.struct.auth.loggedin:
                print("Authenticated!")
                old_pw = self.pw2
            else:
                Messagebox.show_error(title="Wrong Password!", message='[>494<] Invalid password!')
                return False

            self.password_input('New Password', 'Enter new password', 'Continue', 'New Password')
            self.pw1.set(self.pw2)
            self.password_input('Password again', 'Please enter new password again.', 'Enter', 'New Password')

            if self.pw1.get() != self.pw2:
                Messagebox.show_error(title="Passwords don't match!",
                                      message='[>503<] Passwords are not same! Please enter passwords again.')
            elif self.pw2 == old_pw:
                Messagebox.show_error(title="Error!", message='[>505<] New password is same with old password!')
            elif not self.check_username_pw(False):
                pass
            else:
                self.struct.password = self.pw2
                self.struct.auth.delete_account(True)
                self.struct.auth = Person(self.struct.username, self.struct.password, True)
                print("Password changed!")
                Messagebox.show_info('Password changed successfully.', 'Password Changed!')

        def ch_username():
            self.password_input('Password', 'Enter your password first.', btn_text='Change Username')
            if not self.pw2:
                return False

            print("Authenticating...")
            self.struct.auth = Person(self.struct.username, self.pw2)
            if self.struct.auth.loggedin:
                print("Authenticated!")
            else:
                Messagebox.show_error(title="Wrong Password!", message='[>525<] Invalid password!')
                return False

            self.password_input('New Username', 'Enter new username', 'Change Username', 'Username:', None)
            self.un.set(self.pw2)
            new_username = self.pw2

            if not self.check_username_pw(False):
                return False
            elif matchingun(new_username)[0]:
                Messagebox.show_error(title="Error", message='[>535<] Username is already taken!')
                return False
            print(self.un.get(), '  ==xxx')
            for enfn, defn in zip(decryedfilenames(self.struct.username),
                                  filter(lambda x: self.struct.username in x, decryedfilenames())):
                print(enfn, defn)
                print(self.struct.username, new_username)
                newun = defn.replace(self.struct.username, new_username)
                rename(enfn, encrypt_pw(newun, self.struct.password, False)[0] + ".key")
            self.struct.username = new_username

            self.mframe.pack_forget()
            print("Changed username!")
            self.signup_login_menu()
            Messagebox.show_info('Username changed sucesfully! Sign in again.', 'Changed!')

        def quit_main_menu():
            self.pw1.set('')
            self.mframe.pack_forget()
            self.signup_login_menu()

        def add_cont():
            title = 'Create Container'
            self.password_input(title, 'Enter name for new container', 'Continue', 'Name:', None)
            if not self.pw2:
                return None
            self.struct.cont_name = self.pw2

            if self.struct.cont_name in self.struct.auth.containerlist:
                Messagebox.show_error(title="Already taken!",
                                      message='[>565<] Cannot create container! There is already a container named {}.'
                                      .format(self.struct.cont_name))
                return False

            if not self.check_username_pw(False, cn=self.struct.cont_name):
                return False

            self.password_input('Container Password', 'Enter the password for new container: ' + self.struct.cont_name,
                                'Continue')

            if not self.pw2:
                return None
            temp = self.pw1.get()
            self.pw1.set(self.pw2)

            if not self.check_username_pw(False):
                self.pw1.set(temp)
                return False

            self.password_input('Container Password Again', 'Please enter password again.', 'Create Container')

            if self.pw1.get() != self.pw2:
                Messagebox.show_error(title="Passwords don't match!",
                                      message='[>588<] Passwords are not same! Please enter passwords again.')
            self.struct.password = self.pw2

            self.struct.cont = Accounts(self.struct.username, self.struct.cont_name, self.struct.password)
            self.struct.cont.store()
            self.struct.auth.containerlist = self.struct.auth.load_containerlist()
            renew()

        self.minsize(575, 330)
        self.geometry('1300x675')
        self.title('AccPass Manager - Main Menu')

        self.mframe = ttk.Frame(self)
        self.mframe.pack(expand=True, fill='both')

        # side frame
        side_frame = ttk.Frame(self.mframe, relief='solid', style='light')
        side_frame.place(anchor='ne', relheight=.24, relwidth=.1, rely=.36, relx=-0.1)

        settings_btn = ttk.Button(self.mframe, text='S', style='warning', command=side_menu, cursor='hand2')
        settings_btn.place(relx=.045, rely=.15, relwidth=.06, relheight=.1, anchor='center')

        menu_label = ttk.Label(self.mframe, text=self.struct.username, style='info')
        menu_label.place(relx=.015, rely=.02)

        quit_btn = ttk.Button(side_frame, text='Q', style='danger', command=quit_main_menu, cursor='hand2')
        quit_btn.place(relx=.80, rely=.0788, relwidth=.294, relheight=.112, anchor='center')  # y: start .0394, end .1514 

        delete_btn = ttk.Button(side_frame, text='Delete Account', style='secondary', command=delete_acc, cursor='hand2')
        delete_btn.place(rely=0.3387, relx=0.1, relheight=0.1, relwidth=0.8)

        ch_username_btn = ttk.Button(side_frame, text='Change Username', style='secondary', command=ch_username, cursor='hand2')
        ch_username_btn.place(rely=0.5257, relx=0.1, relheight=0.1, relwidth=0.8)  # y: start .5257, end .6257

        ch_password_btn = ttk.Button(side_frame, text='Change Password', style='secondary', command=ch_password, cursor='hand2')
        ch_password_btn.place(rely=0.7127, relx=0.1, relheight=0.1, relwidth=0.8)
        # frame
        frame = ttk.Frame(self.mframe, relief='solid')
        frame.grid_anchor('center')

        def renew():
            frame.place_forget()
            frame.place(relx=.995, rely=.005, relheight=.99, relwidth=.9, anchor='ne')

            for i, cont_name in enumerate(self.struct.auth.containerlist):
                ttk.Button(frame, text=cont_name, command=lambda name=cont_name: self.cont_command(name),
                           cursor='hand2').grid(column=i // 2, row=i % 2, sticky='nsew', padx=15, pady=60)
                frame.columnconfigure(i // 2, weight=1, uniform='a')
                frame.rowconfigure(i % 2, weight=1, uniform='a')

                # Add Container
            i = len(self.struct.auth.containerlist)
            if i == 0:
                text = 'There is no container! Add container'
                bstyle = 'warning'
            else:
                text = 'Add container'
                bstyle = 'info'
            ttk.Button(frame, text=text, style=bstyle, command=add_cont, cursor='hand2') \
                .grid(column=i // 2, row=i % 2, sticky='nsew', padx=15, pady=60)
            frame.rowconfigure(i % 2, weight=1, uniform='a')
            frame.columnconfigure(i // 2, weight=1, uniform='a')

        renew()

    def signup_login_menu(self):
        self.title('AccPass Manager - Welcome')
        self.minsize(325, 130)
        self.geometry('900x520')
        self.signup_login_frame = ttk.Frame(self, relief='solid', borderwidth=120)
        self.signup_login_frame.place(anchor='center', relx=.45, rely=.5, x=35,
                                      width=525, height=350, relheight=0.2, relwidth=0.1)

        self.signup_login_frame.grid_anchor('center')
        self.signup_login_frame.focus_set()

        label1 = ttk.Label(self.signup_login_frame, text='Username')
        entry1 = ttk.Entry(self.signup_login_frame, textvariable=self.un)
        entry1.focus_set()

        label2 = ttk.Label(self.signup_login_frame, text='Password')
        entry2 = ttk.Entry(self.signup_login_frame, show='*', textvariable=self.pw1)

        button1 = ttk.Button(self.signup_login_frame, text='Login', command=self.login_click, cursor='hand2')
        button2 = ttk.Button(self.signup_login_frame, text='Sign up', command=self.signup_click, cursor='hand2')

        label1.grid(row=2, column=1, pady=6, sticky='e')
        entry1.grid(row=2, column=3, columnspan=2, sticky='ew', pady=6)

        label2.grid(row=3, column=1, sticky='e')
        entry2.grid(row=3, column=3, columnspan=2, sticky='ew', pady=6)

        button1.grid(row=4, column=2, columnspan=2, rowspan=3, padx=12, pady=6, sticky='we')
        button2.grid(row=4, column=4, columnspan=2, rowspan=3, padx=12, pady=6, sticky='w')

        col_weights = {0: 1, 1: 24, 2: 1, 3: 24, 4: 8, 5: 16}

        for col, w in col_weights.items():
            self.signup_login_frame.columnconfigure(col, weight=w, uniform='a')

        row_weights = {0: 1, 1: 1, 2: 24, 3: 24, 4: 4, 5: 4, 6: 4}
        for row, w in row_weights.items():
            self.signup_login_frame.rowconfigure(row, weight=w, uniform='a')

    def check_username_pw(self, change=True, cn=None):
        pwstr = self.pw1.get()
        if cn is None:
            unstr = self.un.get()
        else:
            unstr = cn
        print(unstr, pwstr)
        if len(unstr) < USERNAME_MIN_LEN:
            Messagebox.show_error(title='Invalid Input!', message='[>700<] Username must be at least {} characters.'
                                  .format(USERNAME_MIN_LEN))
        elif len(pwstr) < PASSWORD_MIN_LEN:
            Messagebox.show_error(title='Invalid Input!', message='[>703<] Password must be at least {} characters.'
                                  .format(PASSWORD_MIN_LEN))
        elif c := check_invalid_char(unstr):
            Messagebox.show_error(title='Invalid Input!', message='[>706<] Invalid character at username: "{}"'
                                  .format(c))
        elif c := check_invalid_char(pwstr, True):
            Messagebox.show_error(title='Invalid Input!', message='[>709<] Invalid character at password: "{}"'
                                  .format(c))
        else:
            if change:
                self.struct.username, self.struct.password = unstr, pwstr
            return True
        return False

    def login_click(self):
        if self.check_username_pw():
            print('legit input')
            print("Authenticating...")
            self.struct.auth = Person(self.struct.username, self.struct.password)
            if self.struct.auth.loggedin:
                self.signup_login_frame.place_forget()
                self.main_menu()
                print("Authenticated!")
            else:
                Messagebox.show_error(title="Wrong Password!", message='[>727<] Invalid username or password!')

    def password_input(self, title: str, message: str, btn_text: str, label: str = 'Password:', show: str | None = '*'):
        def btn_click(_=None):
            self.pw2 = pw2.get()
            tl.destroy()

        self.pw2 = False
        pw2 = tk.StringVar()
        tl = Toplevel(title=title, minsize=(315, 160), size=(350, 300), maxsize=(600, 400))
        tl.bind('<KeyPress-Return>', btn_click)
        ttk.Label(tl, text=message).place(anchor='center', relx=.5, rely=0.3)
        ttk.Label(tl, text=label).place(anchor='center', relx=.2, rely=.5)
        e = ttk.Entry(tl, show=show, textvariable=pw2)
        e.place(anchor='center', relx=.6, rely=.5)
        e.focus_set()
        b = ttk.Button(tl, text=btn_text, command=btn_click, cursor='hand2')
        b.place(anchor='center', relx=.5, rely=.74)

        tl.grab_set()
        tl.wait_window()  # Wait for the Toplevel window to be closed

    def signup_click(self):
        if self.pw1.get() == 'decryptfilenames':
            print(decryedfilenames())
            self.un.set(', '.join(decryedfilenames()))
        elif self.check_username_pw():
            print('legit input')

            self.password_input('Password again', 'Please enter your password again.', 'Register')
            if not self.pw2:
                pass
            elif self.pw2 != self.struct.password:
                Messagebox.show_error(title="Passwords don't match!", message='[>760<] Passwords are not same! Please '
                                                                              'enter passwords again.')
                self.pw1.set('')
            else:
                # create acc
                print('Creating your account...')
                self.struct.password = self.pw1.get()

                self.struct.auth = Person(self.struct.username, self.struct.password, True)
                if self.struct.auth.loggedin:
                    print('Created your account!')
                    self.signup_login_frame.place_forget()
                    self.main_menu()
                else:
                    Messagebox.show_error(title="Already taken!", message='[>774<] Cannot create account! Username '
                                                                          'has already taken. Try another username.')

    def print_window_size(self, *args):
        if len(args) > 0:
            for i in args:
                print(i.winfo_geometry(), ' arg ')
        print(self.winfo_geometry())
        try:
            self.after(8500, lambda: self.print_window_size(*args) if len(args) > 0 else self.print_window_size())
        except tk.TclError:
            print('tclerror prnt window size !')

# TODO option for theme
theme = 'litera'
MyApp('AccPass Manager', theme, size=(900, 520), icon='icon.ico')
