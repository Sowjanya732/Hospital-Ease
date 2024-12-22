import datetime
from tkinter import *
from PIL import Image, ImageTk
import tkinter.messagebox as mb
from tkinter import ttk
from tkcalendar import DateEntry
import sqlite3
import random
import page_after_login

def book_appointment():
    global tree
    global name_strvar, contact_strvar, age_strvar, symptoms_strvar, gender_strvar, date_of_appointment, stream_strvar

    # Initialize the GUI window
    main = Tk()
    main.title('APPOINTMENT MANAGEMENT SYSTEM')
    main.geometry('1166x718')
    main.resizable(0, 0)
    main.state('zoomed')

    # Creating the universal font variables
    headlabelfont = ("Noto Sans CJK TC", 15, 'bold')
    labelfont = ('Garamond', 14)
    entryfont = ('Garamond', 12)

    # Connecting to the Database where all information will be stored
    connector = sqlite3.connect('Appointment.db')
    cursor = connector.cursor()
    connector.execute(
        "CREATE TABLE IF NOT EXISTS APPOINTMENT_MANAGEMENT (PATIENT_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, NAME TEXT, PHONE_NO TEXT, AGE INTEGER, SYMPTOMS TEXT, GENDER TEXT, DATE_OF_APPOINTMENT TEXT, STREAM TEXT, DOCTOR_NAME TEXT)"
    )

    # List of available doctor names
    doctor_names = ["Dr. John Doe", "Dr. Jane Smith", "Dr. Robert Johnson", "Dr. Emily Davis", "Dr. Michael Wilson"]

    # Creating the functions
    def reset_fields():
        global name_strvar, contact_strvar, age_strvar, symptoms_strvar, gender_strvar, date_of_appointment, stream_strvar
        for i in ['name_strvar', 'contact_strvar', 'age_strvar', 'symptoms_strvar', 'gender_strvar', 'stream_strvar']:
            exec(f"{i}.set('')")
        date_of_appointment.set_date(datetime.datetime.now().date())

    def reset_form():
        global tree
        tree.delete(*tree.get_children())
        reset_fields()

    def display_records():
        tree.delete(*tree.get_children())
        curr = connector.execute('SELECT * FROM APPOINTMENT_MANAGEMENT')
        for records in curr.fetchall():
            tree.insert('', END, values=(records[0], records[1], records[2], records[3], records[4], records[5], records[6], records[7], records[8]))

    # Define the function to get an available doctor based on symptoms and age
    def get_available_doctor(symptoms, age):
        # Define mappings of symptoms and age ranges to doctors
        doctor_mapping = {
            "Dr. John Doe": {"age_range": (0, 40), "symptoms": ["Fever", "Cold"]},
            "Dr. Jane Smith": {"age_range": (0, 120), "symptoms": ["Headache", "Migraine"]},
            "Dr. Robert Johnson": {"age_range": (18, 60), "symptoms": ["Back pain", "Muscle strain"]},
            "Dr. Emily Davis": {"age_range": (0, 100), "symptoms": ["Allergy", "Skin rash"]},
            "Dr. Michael Wilson": {"age_range": (30, 120), "symptoms": ["Hypertension", "Diabetes"]}
        }

        # Find a doctor that matches the symptoms and age
        for doctor, info in doctor_mapping.items():
            if age in range(info["age_range"][0], info["age_range"][1] + 1) and symptoms in info["symptoms"]:
                return doctor

        # Default to a random doctor if no specific match is found
        return random.choice(list(doctor_mapping.keys()))

    def add_record():
        global name_strvar, contact_strvar, age_strvar, symptoms_strvar, gender_strvar, date_of_appointment, stream_strvar

        # Get user input
        patient_name = name_strvar.get()
        contact = contact_strvar.get()
        age = age_strvar.get()
        symptoms = symptoms_strvar.get()
        gender = gender_strvar.get()
        DATE_OF_APPOINTMENT = date_of_appointment.get_date()
        stream_input = stream_strvar.get()

        # Validate patient's name
        if not patient_name or not patient_name.isalpha():
            mb.showerror('Error!', "Please enter a valid name with alphabets only.")
            return

        if not contact or not contact.isdigit() or len(contact) != 10:
            mb.showerror('Error!', "Please enter a valid 10-digit contact number.")
            return

        # Check if age is within the specified range
        if not 1 <= int(age) <= 150:
            mb.showerror('Error!', "Please enter a valid age between 1 and 150.")
            return

        if not symptoms:
            mb.showerror('Error!', "Please enter the symptoms.")
            return

        if not gender:
            mb.showerror('Error!', "Please select gender.")
            return

        if not DATE_OF_APPOINTMENT or not stream_input:
            mb.showerror('Error!', "Please fill all the missing fields.")
            return

        # Check if the appointment date is in the future
        if DATE_OF_APPOINTMENT < datetime.datetime.now().date():
            mb.showerror('Error!', "Please select a date in the future for the appointment.")
            return

        # Check if the appointment time is valid (in hh:mm format)
        try:
            hours, minutes = map(int, stream_input.split(':'))
            if not (0 <= hours < 24 and 0 <= minutes < 60):
                raise ValueError("Invalid time format")
        except ValueError:
            mb.showerror('Error!', "Please enter a valid time in hh:mm format.")
            return

        # Check if the appointment time is in the future
        current_time = datetime.datetime.now().time()
        if DATE_OF_APPOINTMENT == datetime.datetime.now().date() and (hours < current_time.hour or (hours == current_time.hour and minutes <= current_time.minute)):
            mb.showerror('Error!', "Please select a time in the future for the appointment.")
            return

        # Check if the patient already has an appointment at the selected date and time
        existing_appointment = connector.execute(
            "SELECT * FROM APPOINTMENT_MANAGEMENT WHERE (NAME=? OR PHONE_NO=?) AND DATE_OF_APPOINTMENT=? AND STREAM=?",
            (patient_name, contact, DATE_OF_APPOINTMENT, stream_input)
        ).fetchone()

        if existing_appointment:
            mb.showerror('Error!', f"{patient_name} with contact number {contact} already has an appointment at the selected date and time.")
            return


        # Get an available doctor
        doctor_name = get_available_doctor(symptoms, age)

        # Get the last inserted appointment ID
        last_id = connector.execute("SELECT MAX(PATIENT_ID) FROM APPOINTMENT_MANAGEMENT").fetchone()[0]
        # If there are no previous records, start from ID 1
        if last_id is None:
            last_id = 0

        # Increment the appointment ID
        new_id = last_id + 1
        try:
            # Insert the record into the database with the selected doctor's name
            connector.execute(
                'INSERT INTO APPOINTMENT_MANAGEMENT (NAME, PHONE_NO, AGE, SYMPTOMS, GENDER, DATE_OF_APPOINTMENT , STREAM, DOCTOR_NAME) VALUES (?,?,?,?,?,?,?,?)',
                (patient_name, contact, age, symptoms, gender, DATE_OF_APPOINTMENT, stream_input, doctor_name)
            )
            connector.commit()
            mb.showinfo('Record added', f"Record of {patient_name} was successfully added with Doctor: {doctor_name}")
            reset_fields()
            display_records()
        except Exception as e:
            mb.showerror('Error', f'An error occurred: {e}')

    def back():
        main.destroy()
        page_after_login.page_after_login()

    def remove_record():
        global tree
        if not tree.selection():
            mb.showerror('Error!', 'Please select an item from the database')
        else:
            current_item = tree.focus()
            values = tree.item(current_item)
            selection = values["values"]

            # Get the patient ID to be removed
            patient_id = selection[0]

            # Delete the selected record from the database
            connector.execute('DELETE FROM APPOINTMENT_MANAGEMENT WHERE PATIENT_ID=?', (patient_id,))
            connector.commit()

            # Fetch all records from the database
            curr = connector.execute('SELECT * FROM APPOINTMENT_MANAGEMENT')
            records = curr.fetchall()

            # Update patient IDs starting from 1
            for index, record in enumerate(records, start=1):
                old_patient_id = record[0]
                if old_patient_id != index:
                    # Update the patient ID in the database
                    connector.execute('UPDATE APPOINTMENT_MANAGEMENT SET PATIENT_ID=? WHERE PATIENT_ID=?', (index, old_patient_id))
            connector.commit()

            mb.showinfo('Done', 'The record you wanted deleted was successfully deleted.')
            display_records()


    def view_record():
        global name_strvar, contact_strvar, age_strvar, symptoms_strvar, gender_strvar, date_of_appointment, stream_strvar
        if not tree.selection():
            mb.showerror('Error!', 'Please select a record to view')
        else:
            current_item = tree.focus()
            values = tree.item(current_item)
            selection = values["values"]

            name_strvar.set(selection[1])
            contact_strvar.set(selection[2])
            age_strvar.set(selection[3])
            symptoms_strvar.set(selection[4])
            gender_strvar.set(selection[5])
            date = datetime.date(int(selection[6][:4]), int(selection[6][5:7]), int(selection[6][8:]))
            date_of_appointment.set_date(date)
            stream_strvar.set(selection[7])

    # Placing the components in the main window
    Label(main, text="HOSPITAL EASE", font=headlabelfont, bg='sky blue').pack(side=TOP, fill=X)

    # Appointment management form
    appointment_frame = Frame(main, bg='palegreen')
    appointment_frame.pack(fill=X, padx=20, pady=10)
    
    # Placing components in the appointment management form
    Label(appointment_frame, text="Name", font=('Arial', 15)).grid(row=0, column=1, sticky='e', padx=(10, 5))
    Label(appointment_frame, text="Contact Number", font=('Arial', 15)).grid(row=1, column=1, sticky='e', padx=(10, 5))
    Label(appointment_frame, text="Age", font=('Arial', 15)).grid(row=2, column=1, sticky='e', padx=(10, 5))
    Label(appointment_frame, text="Symptoms", font=('Arial', 15)).grid(row=3, column=1, sticky='e', padx=(10, 5))
    Label(appointment_frame, text="Gender", font=('Arial', 15)).grid(row=4, column=1, sticky='e', padx=(10, 5))
    Label(appointment_frame, text="Date of Appointment", font=('Arial', 15)).grid(row=5, column=1, sticky='e', padx=(10, 5))
    Label(appointment_frame, text="Time(HH:MM) 24hrs", font=('Arial', 15)).grid(row=6, column=1, sticky='e', padx=(10, 5))

    name_strvar = StringVar()
    contact_strvar = StringVar()
    age_strvar = StringVar()
    symptoms_strvar = StringVar()
    gender_strvar = StringVar()
    stream_strvar = StringVar()

    Entry(appointment_frame, width=25, textvariable=name_strvar, font=('Arial', 11)).grid(row=0, column=2, pady=5)
    Entry(appointment_frame, width=25, textvariable=contact_strvar, font=('Arial', 11)).grid(row=1, column=2, pady=5)
    Entry(appointment_frame, width=25, textvariable=age_strvar, font=('Arial', 11)).grid(row=2, column=2, pady=5)
    Entry(appointment_frame, width=25, textvariable=symptoms_strvar, font=('Arial', 11)).grid(row=3, column=2, pady=5)
    OptionMenu(appointment_frame, gender_strvar, 'Male', 'Female').grid(row=4, column=2, pady=5)
    date_of_appointment = DateEntry(appointment_frame, font=("Arial", 15), width=15)
    date_of_appointment.grid(row=5, column=2, padx=10, pady=5)
    Entry(appointment_frame, width=25, textvariable=stream_strvar, font=('Arial', 11)).grid(row=6, column=2, pady=5)

    # Buttons frame
    buttons_frame = Frame(appointment_frame,bg='palegreen')
    buttons_frame.grid(row=0, column=3, rowspan=7, padx=(20, 0), pady=10)

    # Buttons for form actions
    Button(buttons_frame, text='Book Appointment', font=('Arial', 15), command=add_record, width=15).grid(row=0, column=0, pady=10)
    Button(buttons_frame, text='View Appointment', font=('Arial', 15), command=view_record, width=15).grid(row=1, column=0, pady=10)
    Button(buttons_frame, text='Reset Fields', font=('Arial', 15), command=reset_fields, width=15).grid(row=2, column=0, pady=10)
    Button(buttons_frame, text='Cancel Appointment', font=('Arial', 15), command=remove_record, width=15).grid(row=3, column=0, pady=10)
    Button(buttons_frame, text='Back', font=('Arial', 15), command=back, width=15).grid(row=4, column=0, pady=10)

    # Image frame
    image_frame = Frame(appointment_frame, bg='white')
    image_frame.grid(row=0, column=0, rowspan=7, padx=(20, 0), pady=10)

    # Load the image
    image_path = 'images\\download.jpg'  # Replace 'path_to_your_image.jpg' with the actual path to your image
    image = Image.open(image_path)
    image = image.resize((600, 300))  # Adjust the size as needed
    photo = ImageTk.PhotoImage(image)

    # Display the image
    image_label = Label(image_frame, image=photo)
    image_label.image = photo
    image_label.pack()



    # Appointment record display
    record_frame = Frame(main, bg='PaleGreen')
    record_frame.pack(fill=BOTH, expand=YES, padx=20, pady=(10, 20))

    Label(record_frame, text='Appointment Record', font=headlabelfont, bg='PaleGreen', fg='DarkGreen').pack(side=TOP, fill=X)
    tree = ttk.Treeview(record_frame, height=15, selectmode=BROWSE,
                        columns=('Patient ID', "Name", "Contact Number", "Age", "Symptoms", "Gender", "Date of Appointment", "Time", "Doctor Name"))
    X_scroller = Scrollbar(tree, orient=HORIZONTAL, command=tree.xview)
    Y_scroller = Scrollbar(tree, orient=VERTICAL, command=tree.yview)
    X_scroller.pack(side=BOTTOM, fill=X)
    Y_scroller.pack(side=RIGHT, fill=Y)
    tree.config(yscrollcommand=Y_scroller.set, xscrollcommand=X_scroller.set)
    tree.heading('Patient ID', text='ID', anchor=CENTER)
    tree.heading('Name', text='Name', anchor=CENTER)
    tree.heading('Contact Number', text='Phone No', anchor=CENTER)
    tree.heading('Age', text='Age', anchor=CENTER)
    tree.heading('Symptoms', text='Symptoms', anchor=CENTER)
    tree.heading('Gender', text='Gender', anchor=CENTER)
    tree.heading('Date of Appointment', text='Date', anchor=CENTER)
    tree.heading('Time', text='Time', anchor=CENTER)
    tree.heading('Doctor Name', text='Doctor Name', anchor=CENTER)  
    tree.column('#0', width=0, stretch=NO)
    tree.column('#1', width=60, stretch=NO)
    tree.column('#2', width=220, stretch=NO)
    tree.column('#3', width=120, stretch=NO)
    tree.column('#4', width=60, stretch=NO)
    tree.column('#5', width=200, stretch=NO)
    tree.column('#6', width=100, stretch=NO)  # Adjusted width here
    tree.column('#7', width=80, stretch=NO)
    tree.column('#8', width=100, stretch=NO)
    tree.pack(side=LEFT, fill=BOTH, expand=YES)
    display_records()

    # Finalizing the GUI window
    main.mainloop()

if __name__ == '__main__':
    book_appointment()
