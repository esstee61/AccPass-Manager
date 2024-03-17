# AccPass Manager
Python-based offline password manager utilizing cryptography and tkinter modules. 
## How does it work?
This uses <a href='https://cryptography.io/en/latest/fernet/#using-passwords-with-fernet'>Fernet Encryption </a>, to encrypt your passwords with the encryption keys which is derived from the password. All encrypted data is stored in 'encrypted' folder. It's important to keep the 'mainkey' file secure, as losing it would result in losing all the stored passwords. The GUI is based on tkinter and <a href='https://ttkbootstrap.readthedocs.io/en/latest/'>ttkbootstrap</a>.
