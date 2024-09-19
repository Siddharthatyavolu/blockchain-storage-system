import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from user import User
from blockchain import Blockchain
import base64
import os
import time
import webbrowser
import json
import datetime
class MainApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Decentralized File Sharing Application")
        self.blockchain = Blockchain('')
        self.current_user = None
        self.create_login_page()

    def create_login_page(self):
        self.style = ttk.Style()

        # Configure the style for the login page
        self.style.configure('Login.TFrame', background='#2E4053')
        self.style.configure('Login.TLabel', background='#2E4053', foreground='#F7DC6F', font=('Helvetica', 16, 'bold'))
        self.style.configure('Login.TButton', background='#1ABC9C', foreground='#000000', font=('Helvetica', 14, 'bold'), padding=(10, 5))
        self.style.map('Login.TButton', background=[('active', '#16A085')], foreground=[('active', '#000000')])

        self.login_frame = ttk.Frame(self.root, padding="40 40 40 40", style='Login.TFrame')
        self.login_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.login_frame, text="Username:", style='Login.TLabel').grid(row=0, column=0, sticky=tk.W, padx=20, pady=15)
        self.username_entry = ttk.Entry(self.login_frame, width=30, font=('Helvetica', 14))
        self.username_entry.grid(row=0, column=1, padx=20, pady=15)

        ttk.Label(self.login_frame, text="Password:", style='Login.TLabel').grid(row=1, column=0, sticky=tk.W, padx=20, pady=15)
        self.password_entry = ttk.Entry(self.login_frame, width=30, show="*", font=('Helvetica', 14))
        self.password_entry.grid(row=1, column=1, padx=20, pady=15)

        login_button = ttk.Button(self.login_frame, text="Login", command=self.login, style='Login.TButton')
        login_button.grid(row=2, column=0, columnspan=2, pady=20, padx=20, sticky='we')

        signup_button = ttk.Button(self.login_frame, text="Sign Up", command=self.signup, style='Login.TButton')
        signup_button.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky='we')

        # Add a button to view all users
        view_users_button = ttk.Button(self.login_frame, text="View Users", command=self.view_users, style='Login.TButton')
        view_users_button.grid(row=4, column=0, columnspan=2, padx=20, pady=10, sticky='we')

    

        # Green shades
        self.root.configure(bg='#32CD32')  # LimeGreen
       
    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if User.authenticate(username, password):
            self.current_user = User(username, password)
            self.create_user_blockchain()
            self.show_main_menu()
        else:
            messagebox.showerror("Error", "Invalid username or password")

    def signup(self):
        self.login_frame.destroy()
        self.signup_frame = ttk.Frame(self.root, padding="20 20 20 20")
        self.signup_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        ttk.Label(self.signup_frame, text="Username:").grid(row=0, column=0, sticky=tk.W)
        self.new_username_entry = ttk.Entry(self.signup_frame, width=20)
        self.new_username_entry.grid(row=0, column=1)

        ttk.Label(self.signup_frame, text="Password:").grid(row=1, column=0, sticky=tk.W)
        self.new_password_entry = ttk.Entry(self.signup_frame, width=20, show="*")
        self.new_password_entry.grid(row=1, column=1)

        signup_button = ttk.Button(self.signup_frame, text="Sign Up", command=self.create_new_user)
        signup_button.grid(row=2, column=0, columnspan=2, pady=10)

    def create_new_user(self):
        username = self.new_username_entry.get()
        password = self.new_password_entry.get()
        if not User.user_exists(username):
            User.create_user(username, password)
            messagebox.showinfo("Success", "User created successfully! You can now login.")
            self.signup_frame.destroy()
            self.create_login_page()
        else:
            messagebox.showerror("Error", "User already exists. Please choose a different username.")

    def create_user_blockchain(self):
        if self.current_user:
            self.current_user_blockchain = Blockchain(self.current_user.username)

    def show_main_menu(self):
        self.login_frame.destroy()
        self.main_menu_frame = ttk.Frame(self.root, padding="20 20 20 20")
        self.main_menu_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        upload_button = ttk.Button(self.main_menu_frame, text="Upload Files", command=self.upload_files)
        upload_button.grid(row=0, column=0, padx=10, pady=10)

        view_button = ttk.Button(self.main_menu_frame, text="View Uploaded Files", command=self.view_uploaded_files)
        view_button.grid(row=0, column=1, padx=10, pady=10)

    def upload_files(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            file_name = os.path.basename(file_path)
            with open(file_path, 'rb') as file:
                file_data = file.read()
            file_data_str = file_data.decode('latin1')  # Convert binary data to string
            file_hash = self.current_user_blockchain.calculate_hash(file_data_str)  # Pass string data
            
            # Additional information about the file
            owner = self.current_user.username
            
            file_data_base64 = base64.b64encode(file_data).decode('utf-8')
            file_info = {
            'name': file_name,
            'owner':owner,
            'hash': file_hash,
            'data': file_data_base64,
            'type': self.blockchain.get_file_type(file_name),
            'size': len(file_data),
            'upload_time': self.get_human_readable_time(),
            'num_characters': self.blockchain.get_num_characters(file_data)
            }

            
            self.current_user_blockchain.add_file_with_contract(file_info)
            messagebox.showinfo("Success", f"File '{file_name}' uploaded successfully!")


    def view_uploaded_files(self):
        # Get the updated list of files from the blockchain
        self.files = self.current_user_blockchain.get_files()
        if not self.files:
            messagebox.showinfo("Info", "No files uploaded yet.")
            return  # Exit the function if no files are available

        self.files_window = tk.Toplevel(self.root)
        self.files_window.title("Uploaded Files")

        self.files_frame = ttk.Frame(self.files_window, padding="20 20 20 20")
        self.files_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Display each file
        for idx, file_info in enumerate(self.files):
            file_label = ttk.Label(self.files_frame, text=f"Name: {file_info['name']}, Owner: {file_info.get('owner', 'Unknown')}")
            file_label.grid(row=idx, column=0, padx=10, pady=5)

            about_button = ttk.Button(self.files_frame, text="About", command=lambda f=file_info: self.show_file_info(f))
            about_button.grid(row=idx, column=1, padx=10, pady=5)

            download_button = ttk.Button(self.files_frame, text="Download", command=lambda f=file_info: self.download_file(f))
            download_button.grid(row=idx, column=2, padx=10, pady=5)

            view_button = ttk.Button(self.files_frame, text="View", command=lambda f=file_info: self.view_file_content(f))
            view_button.grid(row=idx, column=3, padx=10, pady=5)

            delete_button = ttk.Button(self.files_frame, text="Delete", command=lambda f=file_info: self.delete_file(f))
            delete_button.grid(row=idx, column=4, padx=10, pady=5)

            modify_button = ttk.Button(self.files_frame, text="Modify", command=lambda f=file_info: self.modify_file(f))
            modify_button.grid(row=idx, column=5, padx=10, pady=5)

        # Add a refresh button
        refresh_button = ttk.Button(self.files_frame, text="Refresh", command=self.refresh_files_window)
        refresh_button.grid(row=len(self.files), column=0, columnspan=5, pady=10)

    def show_file_info(self, file_info):
        info_window = tk.Toplevel(self.root)
        info_window.title(f"File Info: {file_info['name']}")

        info_frame = ttk.Frame(info_window, padding="20 20 20 20")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        details = f"""
        Name: {file_info['name']}
        Type: {file_info['type']}
        Owner: {file_info['owner']}
        Size: {file_info['size']} bytes
        Upload Time: {file_info['upload_time']}
        Hash: {file_info['hash']}
        Number of Characters: {file_info['num_characters']}
        """
        details_label = ttk.Label(info_frame, text=details)
        details_label.grid(row=0, column=0, padx=10, pady=10)


    def download_file(self, file_info):
        file_data = base64.b64decode(file_info.get('data', ''))
        file_path = filedialog.asksaveasfilename(defaultextension=file_info.get('type', ''), initialfile=file_info.get('name', ''))
        if file_path:
            with open(file_path, 'wb') as file:
                file.write(file_data)
            messagebox.showinfo("Success", f"File '{file_info.get('name')}' downloaded successfully!")

    def view_file_content(self, file_info):
        content_window = tk.Toplevel(self.root)
        content_window.title(f"View File: {file_info['name']}")

        content_frame = ttk.Frame(content_window, padding="20 20 20 20")
        content_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Decode the base64 encoded file data
        file_data = base64.b64decode(file_info['data'])
        try:
            # Attempt to decode file data as UTF-8 text
            file_content = file_data.decode('utf-8')
        except UnicodeDecodeError:
            # If the file is not a text file, show a message
            file_content = "Cannot display binary file content."

        content_text = tk.Text(content_frame, wrap='word')
        content_text.insert('1.0', file_content)
        content_text.configure(state='disabled')  # Make the text read-only
        content_text.grid(row=0, column=0, padx=10, pady=10)
        
        close_button = ttk.Button(content_frame, text="Close", command=content_window.destroy)
        close_button.grid(row=1, column=0, pady=10)

    def delete_file(self, file_info):
        confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete '{file_info['name']}'?")
        if confirm:
            self.current_user_blockchain.chain = [f for f in self.current_user_blockchain.chain if f['name'] != file_info['name']]
            self.current_user_blockchain.save_blockchain()
            messagebox.showinfo("Success", f"File '{file_info['name']}' deleted successfully!")

    def refresh_files_window(self):
        self.files_window.destroy()
        self.view_uploaded_files()

    def modify_file(self, file_info):
        modify_window = tk.Toplevel(self.root)
        modify_window.title(f"Modify File: {file_info['name']}")

        modify_frame = ttk.Frame(modify_window, padding="20 20 20 20")
        modify_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Decode the base64 encoded file data
        file_data = base64.b64decode(file_info['data'])

        # Create a text widget for editing the file content
        content_text = tk.Text(modify_frame, wrap='word')
        content_text.insert('1.0', file_data.decode('utf-8'))
        content_text.grid(row=0, column=0, padx=10, pady=10)

        # Function to save changes
        def save_changes():
            
            new_content = content_text.get('1.0', 'end-1c')  # Get the modified content
            new_data_base64 = base64.b64encode(new_content.encode('utf-8')).decode('utf-8')
            file_info['data'] = new_data_base64  # Update the file data in the file_info dictionary
            self.current_user_blockchain.save_blockchain()  # Save changes to the blockchain
            messagebox.showinfo("Success", f"Changes saved successfully!")
            modify_window.destroy()

        # Add a button to save changes
        save_button = ttk.Button(modify_frame, text="Save Changes", command=save_changes)
        save_button.grid(row=1, column=0, padx=10, pady=5)

    
    def get_human_readable_time(self):
        # Get the current timestamp and convert it to a human-readable format
        current_time = time.time()
        readable_time = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
        return readable_time
    def view_users(self):
        try:
            with open("users.json", "r") as users_file:
                users = json.load(users_file)

            # Create a new window to display the users
            users_window = tk.Toplevel(self.root)
            users_window.title("User Accounts")

            users_frame = ttk.Frame(users_window, padding="20 20 20 20")
            users_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

            # Function to handle button click and show user details
            def show_user_details_from_button(username):
                gmail = f"{username}@gmail.com"
                file_count = self.get_user_file_count(username)
                self.show_user_details({'username': username, 'gmail': gmail, 'file_count': file_count})

            # Display the list of users
            for idx, username in enumerate(users.keys()):
                # Create a button for each user with username as the text
                user_button = ttk.Button(users_frame, text=username, command=lambda username=username: show_user_details_from_button(username))
                user_button.grid(row=idx, column=0, padx=10, pady=5)

            close_button = ttk.Button(users_frame, text="Close", command=users_window.destroy)
            close_button.grid(row=len(users) + 1, column=0, pady=10)

        except FileNotFoundError:
            messagebox.showerror("Error", "No users found.")

    def get_user_file_count(self, username):
        blockchain_filename = f"{username}_blockchain.json"
        if os.path.exists(blockchain_filename):
            with open(blockchain_filename, 'r') as file:
                data = json.load(file)
                return len(data.get('chain', []))
        return 0
    def get_storage_space_used(self, username):
        blockchain_filename = f"{username}_blockchain.json"
        print(blockchain_filename)
        total_size = 0
        if os.path.exists(blockchain_filename):
            with open(blockchain_filename, 'r') as file:
                data = json.load(file)
                
                for block in data.get('chain', []):
                    if 'size' in block:
                        total_size += block['size']
        return total_size
   

    def show_user_details(self, user):
        details_window = tk.Toplevel(self.root)
        details_window.title(f"User Details: {user['username']}")

        details_frame = ttk.Frame(details_window, padding="20 20 20 20")
        details_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Display username
        ttk.Label(details_frame, text=f"Username: {user['username']}").grid(row=0, column=0, padx=10, pady=5)

        # Display Gmail
        ttk.Label(details_frame, text=f"Gmail: {user['gmail']}").grid(row=1, column=0, padx=10, pady=5)

        # Calculate storage space used
        file_count = self.get_user_file_count(user['username'])
        ttk.Label(details_frame, text=f"Number of files uploaded: {file_count}").grid(row=2, column=0, padx=10, pady=5)

        total_size = self.get_storage_space_used(user['username'])
        ttk.Label(details_frame, text=f"Storage space used: {total_size} bytes").grid(row=3, column=0, padx=10, pady=5)

        close_button = ttk.Button(details_frame, text="Close", command=details_window.destroy)
        close_button.grid(row=4, column=0, pady=10)







    
if __name__ == "__main__":
    root = tk.Tk()
    app = MainApp(root)
    root.mainloop()

