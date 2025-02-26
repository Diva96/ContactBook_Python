# import sqlite3
from tkinter import simpledialog, ttk
import mysql.connector
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import os

# Admin Credentials
ADMIN_LOGIN = "1"
ADMIN_PASSWORD = "1"
USER_LOGIN = "2"
USER_PASSWORD = "2"

# Database Configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "contact_book"
}
# Contact Book Class
class ContactBook:
    def __init__(self):
        try:
            self.db = mysql.connector.connect(**DB_CONFIG)
            self.cursor = self.db.cursor()
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS contacts (
                    student_id CHAR(8) NOT NULL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    phone CHAR(10) NOT NULL,
                    email VARCHAR(255) NOT NULL
                )
            """)
            self.db.commit()
        except mysql.connector.Error as e:
            messagebox.showerror("Database Error", f"Error connecting to database: {e}")
     
    # Add a new contact to the database       
    def add_contact(self, student_id, name, phone, email):
        if not student_id.isdigit() or len(student_id) != 8:
            messagebox.showerror("Error", "Student ID must be an 8-digit number.")
            return
        if not phone.isdigit() or len(phone) != 10:
            messagebox.showerror("Error", "Phone number must be 10 digits (enter without 0).")
            return
        if "@" not in email or not email.endswith(".com"):
            messagebox.showerror("Error", "Invalid email address. It must contain '@' and end with '.com'.")
            return
        
        self.cursor.execute("INSERT INTO contacts (student_id, name, phone, email) VALUES (%s, %s, %s, %s)",
                            (student_id, name, phone, email))
        self.db.commit()
        messagebox.showinfo("Success", f"Contact {name} added successfully!")

    # Search for a contact by name or student ID
    def search_contact(self, name, student_id):
        self.cursor.execute("SELECT * FROM contacts WHERE student_id=%s OR name=%s", (student_id, name))
        contact = self.cursor.fetchone()
        if contact:
            messagebox.showinfo("Contact Found", f"Student ID: {contact[1]}\nName: {contact[2]}\nPhone: {contact[3]}\nEmail: {contact[4]}")
        else:
            messagebox.showerror("Error", "Contact not found.")
            
    # Update contact details
    def update_contact(self, student_id, name=None, phone=None, email=None):
        if not student_id.strip():  # Ensure student ID is entered
            messagebox.showerror("Error", "Please enter the Student ID.")
            return

        if not self._verify_admin():
            return

        self.cursor.execute("SELECT name, phone, email FROM contacts WHERE student_id=%s", (student_id,))
        result = self.cursor.fetchone()

        if not result:
            messagebox.showerror("Error", "Student ID not found!")
            return

        current_name, current_phone, current_email = result

        # Validate phone number (if provided)
        if phone:
            if not phone.isdigit() or len(phone) != 10:
                messagebox.showerror("Error", "Phone number must be 10 digits (enter without 0).")
                return

        # Validate email (if provided)
        if email:
            if "@" not in email or not email.endswith(".com"):
                messagebox.showerror("Error", "Invalid email address. It must contain '@' and end with '.com'.")
                return

        # If no new values are provided, keep the existing values
        new_name = name if name else current_name
        new_phone = phone if phone else current_phone
        new_email = email if email else current_email

        # If no changes are made, notify the user but do not update the database
        if new_name == current_name and new_phone == current_phone and new_email == current_email:
            messagebox.showinfo("No Changes", "No updates were made. Existing details remain the same.")
            return

        # Update the contact details
        self.cursor.execute(
            "UPDATE contacts SET name=%s, phone=%s, email=%s WHERE student_id=%s",
            (new_name, new_phone, new_email, student_id)
        )
        self.db.commit()
        messagebox.showinfo("Success", "Contact updated successfully!")

    # Delete a contact by student ID
    def delete_contact(self, student_id):
        if not student_id.strip():  # Check if student_id is empty
            messagebox.showerror("Error", "Please enter the Student ID.")
            return

        if not self._verify_admin():
            return

        self.cursor.execute("SELECT * FROM contacts WHERE student_id=%s", (student_id,))
        contact = self.cursor.fetchone()  # Check if student ID exists in the database

        if not contact:
            messagebox.showerror("Error", "Student ID not found!")
            return

        self.cursor.execute("DELETE FROM contacts WHERE student_id=%s", (student_id,))
        self.db.commit()
        messagebox.showinfo("Success", "Contact deleted successfully!")
        
    # Verify admin password
    def _verify_admin(self):
        password = simpledialog.askstring("Admin Permission", "Enter admin password:", show='*')
        if password == ADMIN_PASSWORD:
            return True
        else:
            messagebox.showerror("Error", "Incorrect admin password!")
            return False
    
    # Show all contacts in the database    
    def show_all_contacts(self, tree):
        # Clear existing rows
        for row in tree.get_children():
            tree.delete(row)
        
        self.cursor.execute("SELECT * FROM contacts")
        all_contacts = self.cursor.fetchall()
        
        for contact in all_contacts:
            tree.insert("", "end", values=(contact[1], contact[2], contact[3], contact[4])) 
            
# Contact App Class         
class ContactApp:
    def __init__(self, root):
        self.book = ContactBook()
        self.is_admin = False
        self.root = root
        self.root.withdraw()
        self.login_page()
            
# Login Page
    def login_page(self):
        self.login_window = tk.Toplevel()
        self.login_window.title("Login")
        self.login_window.geometry("300x100")
        self.login_window.resizable(False, False)

        # Background Image Handling
        if os.path.exists("login_bg.png"):
            self.bg = ImageTk.PhotoImage(file="login_bg.png")
            bg_label = tk.Label(self.login_window, image=self.bg)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

                
        tk.Label(self.login_window, text="Username:").grid(row=2, column=2, padx=5, pady=5,)
        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.grid(row=2, column=3, padx=5, pady=5,)

        tk.Label(self.login_window, text="Password:").grid(row=3, column=2, padx=5, pady=5,)
        self.password_entry = tk.Entry(self.login_window, show="*")
        self.password_entry.grid(row=3, column=3, padx=5, pady=5,)
        login_button = tk.Button(self.login_window, text="Login", command=self.verify_login)
        login_button.grid(row=4, column=5, pady=10,)
        
        
    # Verify login credentials
    def verify_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == ADMIN_LOGIN and password == ADMIN_PASSWORD:
            self.is_admin = True
            messagebox.showinfo("Login Success", "Admin Access Granted")
        elif username == USER_LOGIN and password == USER_PASSWORD:
            self.is_admin = False
            messagebox.showinfo("Login Success", "User Access Granted")
        else:
            messagebox.showerror("Login Failed", "Invalid credentials")
            return

        self.login_window.destroy()
        self.main_interface()

    # Main Interface
    def main_interface(self):
        self.root.deiconify()
        self.root.title("Contact Book")
        self.root.geometry("600x500")
        
        # Clear all widgets
        for widget in self.root.winfo_children():
            widget.destroy()
        
        #Background Image Handling
        if os.path.exists("login_bg.png"):        
            self.bg_image = Image.open("login_bg.png")  # Keep reference to prevent garbage collection
            self.bg = ImageTk.PhotoImage(self.bg_image)  
            self.bg_label = tk.Label(self.root, image=self.bg)
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

            # Only lower if bg_label was successfully created
            if hasattr(self, 'bg_label'):
                self.bg_label.lower()  # Lower the background image to the bottom
            

        # Form Frame
        form_frame = tk.Frame(self.root)
        form_frame.pack(pady=10)

        tk.Label(form_frame, text="Student ID:").grid(row=0, column=0)
        self.student_id_entry = tk.Entry(form_frame)
        self.student_id_entry.grid(row=0, column=1)
        
        tk.Label(form_frame, text="Name:").grid(row=1, column=0)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1)

        tk.Label(form_frame, text="Phone:").grid(row=2, column=0)
        self.phone_entry = tk.Entry(form_frame)
        self.phone_entry.grid(row=2, column=1)

        tk.Label(form_frame, text="Email:").grid(row=3, column=0)
        self.email_entry = tk.Entry(form_frame)
        self.email_entry.grid(row=3, column=1)

        # Buttons Frame
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=9, fill="x")

        # Button Font
        button_font = ("Arial", 9)
        btn_width = 6

        # Buttons
        tk.Button(btn_frame, text="Add", width=btn_width, font=button_font, bg="green", fg="white", command=self.add_contact).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Search", width=btn_width, font=button_font, bg="blue", fg="white", command=self.search_contact).pack(side="left", padx=5)
        # Only show "Show All" button if admin
        if self.is_admin:
            tk.Button(btn_frame, text="Show all", width=btn_width, font=button_font, bg="black", fg="white", command=self.show_all_contacts).pack(side="left", padx=7)
            tk.Button(btn_frame, text="Delete", width=btn_width, font=button_font, bg="red", fg="white", command=self.delete_contact).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Update", width=btn_width, font=button_font, bg="orange", fg="white", command=self.update_contact).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Clear", width=btn_width, font=button_font, bg="gray", fg="white", command=self.clear_fields).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Quiet", width=btn_width, font=button_font, bg="purple", fg="white", command=self.root.quit).pack(side="left", padx=5)
        
        # Define style
        if self.is_admin:
            style = ttk.Style()
            style.configure("Treeview", background="lightblue", fieldbackground="lightblue", foreground="black")
            style.map("Treeview", background=[('selected', 'blue')])

            # Treeview Frame
            tree_frame = tk.Frame(self.root)
            tree_frame.pack(pady=10, fill="both", expand=True)      
            
            # Scrollbar for Treeview
            tree_scroll = tk.Scrollbar(tree_frame)
            tree_scroll.pack(side="right", fill="y")
                
            # Treeview
            self.tree = ttk.Treeview(tree_frame, columns=("Student ID", "Name", "Phone", "Email"), show="headings")
            self.tree.pack(side="left", fill="both", expand=True)
            tree_scroll.config(command=self.tree.yview)

            self.tree.heading("Student ID", text="Student ID",)
            self.tree.heading("Name", text="Name")
            self.tree.heading("Phone", text="Phone")
            self.tree.heading("Email", text="Email")

            self.tree.column("Student ID", width=100)
            self.tree.column("Name", width=150)
            self.tree.column("Phone", width=100)
            self.tree.column("Email", width=200)
            self.tree.bind("<ButtonRelease-1>", self.select_contact)
        
        
    # Select contact from treeview    
    def add_contact(self):
        self.book.add_contact(self.student_id_entry.get(), self.name_entry.get(), self.phone_entry.get(), self.email_entry.get())
    
    # Search contact from treeview
    def search_contact(self):
        self.book.search_contact(self.name_entry.get(), self.student_id_entry.get())
    
    # Update contact details
    
    def update_contact(self):
        self.book.update_contact(self.student_id_entry.get(), self.name_entry.get(),self.phone_entry.get(), self.email_entry.get())
    
    # Delete contact from treeview
    def delete_contact(self):
        self.book.delete_contact(self.student_id_entry.get())
    
    # Select contact from treeview   
    def clear_fields(self):
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
    
    # Show all contacts in the treeview   
    def show_all_contacts(self):
        if not hasattr(self, "tree"):  # Check if the tree view exists
            messagebox.showerror("Error", "Table view not initialized.")
            return
        
        if self.is_admin:
            # Admin can see all contacts
            self.book.show_all_contacts(self.tree)
        else:
            # User gets a restriction message
            messagebox.showerror("Access Denied", "Only Admin has access to this feature.")
            
    # Select contact from treeview
    def select_contact(self, event):
        selected_item = self.tree.selection()[0]
        values = self.tree.item(selected_item, "values")
        self.student_id_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.student_id_entry.insert(0, values[0])
        self.name_entry.insert(0, values[1])
        self.phone_entry.insert(0, values[2])
        self.email_entry.insert(0, values[3])  
    def __del__(self):
        self.book.db.close()
        self.cursor.close()       
      
# Main
root = tk.Tk()
app = ContactApp(root)
root.mainloop()
