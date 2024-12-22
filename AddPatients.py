import sqlite3
import datetime
from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import ImageTk, Image
import tkinter as tk
import re
import page_after_login

def add_patient():

    def create_curved_label(canvas, x, y, width, height, text):
        # Create a rounded rectangle
        canvas.create_polygon(x + 10, y, x + width - 10, y, x + width, y + 10, x + width, y + height - 10, 
                            x + width - 10, y + height, x + 10, y + height, x, y + height - 10, x, y + 10, 
                            x + 10, y, fill="blue", outline="blue")

        # Create a text label
        canvas.create_text(x + width // 2, y + height // 2, text=text, fill="white", font=("Arial", 12))

    
    def connection():
        conn = sqlite3.connect("add_patients.db")
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS patients (
                            MOBILE TEXT PRIMARY KEY,
                            NAME TEXT NOT NULL,
                            AGE INTEGER NOT NULL,
                            HISTORY TEXT,
                            MEDICINES TEXT
                        )''')
        conn.commit()
        return conn




    def refreshTable():
        for data in my_tree.get_children():
            my_tree.delete(data)

        for array in read():
            my_tree.insert(parent='', index='end', iid=array, text="", values=(array), tag="orow")

        my_tree.tag_configure('orow', background='#EEEEEE', font=('Arial', 12))
        my_tree.grid(row=8, column=0, columnspan=5, rowspan=11, padx=10, pady=20)

    root = Tk()
    root.title("HOSPITAL EASE")
    root.geometry("1166x718")
    root.resizable(0, 0)
    root.state('zoomed')
    my_tree = ttk.Treeview(root)

    ph1 = tk.StringVar()
    ph2 = tk.StringVar()
    ph3 = tk.StringVar()
    ph4 = tk.StringVar()
    ph5 = tk.StringVar()

    def setph(word, num):
        if num == 1:
            ph1.set(word)
        if num == 2:
            ph2.set(word)
        if num == 3:
            ph3.set(word)
        if num == 4:
            ph4.set(word)
        if num == 5:
            ph5.set(word)

    def read():
        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients")
        results = cursor.fetchall()
        conn.commit()
        conn.close()
        return results

    def open_file_dialog():
        filename = filedialog.askopenfilename(initialdir="/", title="Select Image File", filetypes=(("Image Files", "*.jpg;*.jpeg;*.png"), ("All Files", "*.*")))
        if filename:
            ph5.set(filename)

    def add():
        MOBILE = str(MOBILEEntry.get())
        NAME = str(NAMEEntry.get())
        AGE = str(AGEEntry.get())  # Changed from DOBEntry to AGEEntry
        HISTORY = str(HISTORYEntry.get())
        MEDICINES = str(MEDICINESEntry.get())

        if (MOBILE == "" or MOBILE == " ") or (NAME == "" or NAME == " ") or (AGE == "" or AGE == " ") or (HISTORY == "" or HISTORY == " ") or (MEDICINES == "" or MEDICINES == " "):
            messagebox.showinfo("Error", "Please fill up the blank entry")
            return

        if not re.match(r'^[A-Za-z. ]+$', NAME):
            messagebox.showinfo("Error", "Name should contain only alphabets, spaces, and periods")
            return

        if not MOBILE.isdigit() or len(MOBILE) != 10:
            messagebox.showinfo("Error", "Mobile number should have 10 digits")
            return

        if not AGE.isdigit() or int(AGE) < 0 or int(AGE) > 150:  # Check if AGE is a valid integer within a reasonable range
            messagebox.showinfo("Error", "Invalid age")
            return

        if not HISTORY.isalnum():  # Check if Medical History contains only alphabets and digits
            messagebox.showinfo("Error", "Medical History should contain only alphabets and digits")
            return

        for patient in read():
            if patient[0] == MOBILE and patient[1] == NAME:
                messagebox.showinfo("Error", "Patient with the same name and mobile number already exists")
                return

        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO patients VALUES (?, ?, ?, ?, ?)", (MOBILE, NAME, AGE, HISTORY, MEDICINES))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Patient added successfully")
        except Exception as e:
            print("Error:", e)
            messagebox.showinfo("Error", "An error occurred while adding the patient")
            return

        refreshTable()
        clear_entries()

    def clear_entries():
        MOBILEEntry.delete(0, 'end')
        NAMEEntry.delete(0, 'end')
        AGEEntry.delete(0, 'end')  # Changed from DOBEntry to AGEEntry
        HISTORYEntry.delete(0, 'end')
        MEDICINESEntry.delete(0, 'end')

    def reset():
        decision = messagebox.askquestion("Warning!!", "Delete all data?")
        if decision != "yes":
            return 
        else:
            try:
                conn = connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM patients")
                conn.commit()
                conn.close()
            except:
                messagebox.showinfo("Error", "Sorry an error occured")
                return

            refreshTable()

    def delete():
        if not my_tree.selection():
            messagebox.showinfo("Error", "Please select a data row to delete")
            return 

        decision = messagebox.askquestion("Warning!!", "Delete the selected data?")
        if decision != "yes":
            return 

        selected_item = my_tree.selection()[0]
        deleteData = str(my_tree.item(selected_item)['values'][0])
        try:
            conn = connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM patients WHERE MOBILE=?", (deleteData,))
            conn.commit()
            conn.close()
        except Exception as e:
            print("Error:", e)
            messagebox.showinfo("Error", "Sorry, an error occurred while deleting the data")
            return
        refreshTable()
        clear_entries()

    def search():
        MOBILE = str(MOBILEEntry.get())
        NAME = str(NAMEEntry.get())
        AGE = str(AGEEntry.get())  # Changed from DOBEntry to AGEEntry
        HISTORY = str(HISTORYEntry.get())
        MEDICINES = str(MEDICINESEntry.get())

        conn = connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM patients WHERE MOBILE='"+
        MOBILE+"' or NAME='"+
        NAME+"' or AGE='"+
        AGE+"' or HISTORY='"+
        HISTORY+"' or MEDICINES='"+
        MEDICINES+"' ")

        try:
            result = cursor.fetchall()

            for num in range(0,5):
                setph(result[0][num],(num+1))

            conn.commit()
            conn.close()
        except:
            messagebox.showinfo("Error", "No data found")

    def back():
        root.destroy()
        page_after_login.page_after_login()

    def update():
        selectedMOBILE = ""

        try:
            selected_item = my_tree.selection()[0]
            selectedMOBILE = str(my_tree.item(selected_item)['values'][0])
        except:
            messagebox.showinfo("Error", "Please select a data row")

        MOBILE = str(MOBILEEntry.get())
        NAME = str(NAMEEntry.get())
        AGE = str(AGEEntry.get())
        HISTORY = str(HISTORYEntry.get())
        MEDICINES = str(MEDICINESEntry.get())

        if (MOBILE == "" or MOBILE == " ") or (NAME == "" or NAME == " ") or (AGE == "" or AGE == " ") or (HISTORY == "" or HISTORY == " ") or (MEDICINES == "" or MEDICINES == " "):
            messagebox.showinfo("Error", "Please fill up the blank entry")
            return
        else:
            try:
                conn = connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE patients SET MOBILE='"+
                MOBILE+"', NAME='"+
                NAME+"', AGE='"+
                AGE+"', HISTORY='"+
                HISTORY+"', MEDICINES='"+
                MEDICINES+"' WHERE MOBILE='"+
                selectedMOBILE+"' ")
                conn.commit()
                conn.close()
            except:
                messagebox.showinfo("Error", "Patient already exist")
                return

        refreshTable()
        clear_entries()
    
    label = Label(root, text="PATIENT DATA MANAGEMENT", font=('Arial Bold', 30))
    label.place(x=0, y=0)  # Adjust x and y coordinates as needed

    try:
        # Load the background image
        bg_frame = Image.open('images\\p.png')
        photo = ImageTk.PhotoImage(bg_frame)
        bg_label = Label(root, image=photo)
        bg_label.image = photo
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except Exception as e:
        print("Error loading background image:", e)
        

    my_tree = ttk.Treeview(root)

    ph1 = tk.StringVar()
    ph2 = tk.StringVar()
    ph3 = tk.StringVar()
    ph4 = tk.StringVar()
    ph5 = tk.StringVar()

    # Frame for input fields
    input_frame = Canvas(root, bg='#EEEEEE', bd=0, highlightthickness=0)
    input_frame.place(relx=0.6, rely=0.1, relwidth=0.58, relheight=0.35, anchor="n")

    create_curved_label(input_frame, 0, 0, 120, 30, "Mobile No")
    create_curved_label(input_frame, 0, 50, 120, 30, "Name")
    create_curved_label(input_frame, 0, 100, 120, 30, "Age")
    create_curved_label(input_frame, 0, 150, 120, 30, "Medical History")
    create_curved_label(input_frame, 0, 200, 120, 30, "Medicines")

    MOBILEEntry = Entry(root, width=50, bd=5, font=('Arial', 15), textvariable=ph1, bg="#f3f4ed")
    NAMEEntry = Entry(root, width=50, bd=5, font=('Arial', 15), textvariable=ph2)
    AGEEntry = Entry(root, width=50, bd=5, font=('Arial', 15), textvariable=ph3)
    HISTORYEntry = Entry(root, width=50, bd=5, font=('Arial', 15), textvariable=ph4)
    MEDICINESEntry = Entry(root, width=45, bd=5, font=('Arial', 15), textvariable=ph5)
    browseBtn = Button(root, text="Browse", padx=20, pady=10, font=('Arial', 12),command=open_file_dialog)

    # Place labels and entry fields in the input frame
    MOBILEEntry.place(relx=0.65, rely=0.125, anchor="center")
    NAMEEntry.place(relx=0.65, rely=0.195, anchor="center")
    AGEEntry.place(relx=0.65, rely=0.26, anchor="center")
    HISTORYEntry.place(relx=0.65, rely=0.33, anchor="center")
    MEDICINESEntry.place(relx=0.63, rely=0.4, anchor="center")

    # Place browse button
    browseBtn.place(relx=0.85, rely=0.4, anchor="center")

    

    addBtn = Button(root, text="Add", padx=65, pady=25, width=10, bd=5, font=('Arial', 15), bg="#84F894", command=add)
    updateBtn = Button(root, text="Update", padx=65, pady=25, width=10, bd=5, font=('Arial', 15), bg="#84E8F8", command=update)
    deleteBtn = Button(root, text="Delete", padx=65, pady=25, width=10, bd=5, font=('Arial', 15), bg="#FF9999", command=delete)
    searchBtn = Button(root, text="Search", padx=65, pady=25, width=10, bd=5, font=('Arial', 15), bg="#F4FE82", command=search)
    resetBtn = Button(root, text="Reset", padx=65, pady=25, width=10, bd=5, font=('Arial', 15), bg="#F398FF", command=reset)
    backBtn = Button(root, text="Back", padx=65, pady=25, width=10, bd=5, font=('Arial', 15), bg="#94A1FF", command=back)

    addBtn.grid(row=3, column=0, padx=10, pady=10)
    updateBtn.grid(row=4, column=0, padx=10, pady=10)
    deleteBtn.grid(row=5, column=0, padx=10, pady=10)
    searchBtn.grid(row=6, column=0, padx=10, pady=10)
    resetBtn.grid(row=7, column=0, padx=10, pady=10)
    backBtn.grid(row=8, column=0, padx=10, pady=10)

    

    style = ttk.Style()
    style.configure("Treeview.Heading", font=('Arial Bold', 15))

    # Create a frame for the Treeview widget
    tree_frame = Frame(root)
    tree_frame.place(relx=0.6, rely=0.5, relwidth=0.58, relheight=0.4, anchor="n")

    my_tree = ttk.Treeview(tree_frame)

    

    # Adjust the position of the Treeview widget within the tree_frame
    my_tree.grid(row=0, column=0, sticky="nsew")  # Use sticky to expand the Treeview widget to fill the frame

    my_tree['columns'] = ("Mobile", "Name", "Age", "HISTORY", "MEDICINES")
    
    my_tree.column("#0", width=0, stretch=NO)
    my_tree.column("Mobile", anchor=W, width=120)
    my_tree.column("Name", anchor=W, width=150)
    my_tree.column("Age", anchor=W, width=100)
    my_tree.column("HISTORY", anchor=W, width=150)
    my_tree.column("MEDICINES", anchor=W, width=200)

    my_tree.heading("Mobile", text="Mobile", anchor=W)
    my_tree.heading("Name", text="Name", anchor=W)
    my_tree.heading("Age", text="Age", anchor=W)
    my_tree.heading("HISTORY", text="History", anchor=W)
    my_tree.heading("MEDICINES", text="Medicines", anchor=W)

    refreshTable()

    root.mainloop()

if __name__ == '__main__':
    add_patient()
