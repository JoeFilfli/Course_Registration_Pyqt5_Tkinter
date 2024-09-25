"""
School Management System
========================

This module provides a GUI-based school management system using Tkinter and SQLite. 
It allows management of students, instructors, and courses.

Classes
-------
Person
    Represents a person with a name, age, and email.
Student(Person)
    Represents a student, inheriting from Person.
Instructor(Person)
    Represents an instructor, inheriting from Person.
Course
    Represents a course with a course ID, name, and optional instructor.

Functions
---------
create_tables()
    Creates the necessary tables in the SQLite database.
validate_email(email)
    Validates the format of an email address.
validate_age(age)
    Validates that the age is a non-negative integer.
add_student()
    Adds a student to the database and refreshes the student tree view.
refresh_student_tree()
    Refreshes the student tree view with the current data from the database.
delete_student()
    Deletes the selected student from the database and refreshes the student tree view.

Main Application
----------------
A Tkinter-based GUI application with tabs for managing students, instructors, and courses.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import re
import pandas as pd
import os

# ==================== Class Definitions ====================

class Person:
    """
    A class used to represent a Person.
    
    Attributes
    ----------
    name : str
        The name of the person.
    age : int
        The age of the person.
    email : str
        The email address of the person.
    
    Methods
    -------
    introduce()
        Prints an introduction message with the person's name and age.
    _validate_email(email)
        Validates the email format.
    _validate_age(age)
        Validates that the age is a non-negative integer.
    """
    
    def __init__(self, name, age, email):
        """
        Parameters
        ----------
        name : str
            The name of the person.
        age : int
            The age of the person.
        email : str
            The email address of the person.
        """
        self.name = name
        self.age = self._validate_age(age)
        self._email = self._validate_email(email)
    
    def introduce(self):
        """Prints an introduction message with the person's name and age."""
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")
    
    def _validate_email(self, email):
        """
        Validates the email format.

        Parameters
        ----------
        email : str
            The email address to validate.

        Returns
        -------
        str
            The validated email address.

        Raises
        ------
        ValueError
            If the email format is invalid.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return email
        else:
            raise ValueError("Invalid email format.")
    
    def _validate_age(self, age):
        """
        Validates that the age is a non-negative integer.

        Parameters
        ----------
        age : int
            The age to validate.

        Returns
        -------
        int
            The validated age.

        Raises
        ------
        ValueError
            If the age is not a non-negative integer.
        """
        if isinstance(age, int) and age >= 0:
            return age
        else:
            raise ValueError("Age must be a non-negative integer.")

class Student(Person):
    """
    A class used to represent a Student, inheriting from Person.
    
    Attributes
    ----------
    student_id : str
        The student's unique ID.
    registered_courses : list
        List of Course objects the student is registered in.
    db_id : int, optional
        The database ID of the student (default is None).

    Methods
    -------
    from_db_row(cls, row)
        Creates a Student object from a database row.
    """
    
    def __init__(self, name, age, email, student_id, db_id=None):
        """
        Parameters
        ----------
        name : str
            The name of the student.
        age : int
            The age of the student.
        email : str
            The email address of the student.
        student_id : str
            The student's unique ID.
        db_id : int, optional
            The database ID of the student (default is None).
        """
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses = []  # List of Course objects
        self.db_id = db_id  # Database ID

    @classmethod
    def from_db_row(cls, row):
        """
        Creates a Student object from a database row.

        Parameters
        ----------
        row : tuple
            A tuple containing student data from the database.

        Returns
        -------
        Student
            A Student object created from the database row.
        """
        db_id, name, age, email, student_id = row
        return cls(name, age, email, student_id, db_id)

class Instructor(Person):
    """
    A class used to represent an Instructor, inheriting from Person.
    
    Attributes
    ----------
    instructor_id : str
        The instructor's unique ID.
    assigned_courses : list
        List of Course objects the instructor is assigned to.
    db_id : int, optional
        The database ID of the instructor (default is None).

    Methods
    -------
    from_db_row(cls, row)
        Creates an Instructor object from a database row.
    """
    
    def __init__(self, name, age, email, instructor_id, db_id=None):
        """
        Parameters
        ----------
        name : str
            The name of the instructor.
        age : int
            The age of the instructor.
        email : str
            The email address of the instructor.
        instructor_id : str
            The instructor's unique ID.
        db_id : int, optional
            The database ID of the instructor (default is None).
        """
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = []  # List of Course objects
        self.db_id = db_id  # Database ID

    @classmethod
    def from_db_row(cls, row):
        """
        Creates an Instructor object from a database row.

        Parameters
        ----------
        row : tuple
            A tuple containing instructor data from the database.

        Returns
        -------
        Instructor
            An Instructor object created from the database row.
        """
        db_id, name, age, email, instructor_id = row
        return cls(name, age, email, instructor_id, db_id)

class Course:
    """
    A class used to represent a Course.
    
    Attributes
    ----------
    course_id : str
        The unique ID of the course.
    course_name : str
        The name of the course.
    instructor : Instructor, optional
        The instructor assigned to the course (default is None).
    enrolled_students : list
        List of Student objects enrolled in the course.
    db_id : int, optional
        The database ID of the course (default is None).

    Methods
    -------
    from_db_row(cls, row)
        Creates a Course object from a database row.
    """
    
    def __init__(self, course_id, course_name, instructor=None, db_id=None):
        """
        Parameters
        ----------
        course_id : str
            The unique ID of the course.
        course_name : str
            The name of the course.
        instructor : Instructor, optional
            The instructor assigned to the course (default is None).
        db_id : int, optional
            The database ID of the course (default is None).
        """
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor  # Should be an Instructor object
        self.enrolled_students = []   # List of Student objects
        self.db_id = db_id  # Database ID

    @classmethod
    def from_db_row(cls, row):
        """
        Creates a Course object from a database row.

        Parameters
        ----------
        row : tuple
            A tuple containing course data from the database.

        Returns
        -------
        Course
            A Course object created from the database row.
        """
        db_id, course_id, course_name, instructor_name = row
        return cls(course_id, course_name, db_id=db_id)

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

def create_tables():
    """
    Creates the necessary tables in the SQLite database.
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            email TEXT NOT NULL UNIQUE,
            student_id TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            email TEXT NOT NULL UNIQUE,
            instructor_id TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL UNIQUE,
            course_name TEXT NOT NULL,
            instructor_id INTEGER,
            FOREIGN KEY(instructor_id) REFERENCES instructors(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            student_id INTEGER,
            course_id INTEGER,
            PRIMARY KEY(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')
    conn.commit()

create_tables()

def validate_email(email):
    """
    Validates the format of an email address.

    Parameters
    ----------
    email : str
        The email address to validate.

    Returns
    -------
    str
        The validated email address.

    Raises
    ------
    ValueError
        If the email format is invalid.
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if re.match(pattern, email):
        return email
    else:
        raise ValueError("Invalid email format.")

def validate_age(age):
    """
    Validates that the age is a non-negative integer.

    Parameters
    ----------
    age : str
        The age to validate.

    Returns
    -------
    int
        The validated age.

    Raises
    ------
    ValueError
        If the age is not a non-negative integer.
    """
    if age.isdigit() and int(age) >= 0:
        return int(age)
    else:
        raise ValueError("Age must be a non-negative integer.")

# Main application window
root = tk.Tk()
root.title("School Management System")
root.geometry("1000x700")

# Create Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill='both')

# Frames for Students, Instructors, and Courses
student_frame = ttk.Frame(notebook)
instructor_frame = ttk.Frame(notebook)
course_frame = ttk.Frame(notebook)

notebook.add(student_frame, text='Students')
notebook.add(instructor_frame, text='Instructors')
notebook.add(course_frame, text='Courses')

# ==================== Student Tab ====================

# Variables for student form
student_name_var = tk.StringVar()
student_age_var = tk.StringVar()
student_email_var = tk.StringVar()
student_id_var = tk.StringVar()

# Student Form
tk.Label(student_frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(student_frame, textvariable=student_name_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(student_frame, text="Age").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(student_frame, textvariable=student_age_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(student_frame, text="Email").grid(row=2, column=0, padx=5, pady=5)
tk.Entry(student_frame, textvariable=student_email_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(student_frame, text="Student ID").grid(row=3, column=0, padx=5, pady=5)
tk.Entry(student_frame, textvariable=student_id_var).grid(row=3, column=1, padx=5, pady=5)

def add_student():
    """
    Adds a student to the database and refreshes the student tree view.
    
    This function retrieves the data entered in the student form, validates it, 
    and inserts it into the database. If the data is valid and the insertion is successful,
    the student tree view is refreshed to display the new student.
    
    Raises
    ------
    ValueError
        If the entered age or email is invalid.
    sqlite3.IntegrityError
        If the student ID or email is not unique.
    """
    name = student_name_var.get()
    age = student_age_var.get()
    email = student_email_var.get()
    student_id = student_id_var.get()
    try:
        age = validate_age(age)
        email = validate_email(email)
        cursor.execute('''
            INSERT INTO students (name, age, email, student_id)
            VALUES (?, ?, ?, ?)
        ''', (name, age, email, student_id))
        conn.commit()
        messagebox.showinfo("Success", "Student added to the database.")
        refresh_student_tree()
        # Clear form fields
        student_name_var.set('')
        student_age_var.set('')
        student_email_var.set('')
        student_id_var.set('')
    except ValueError as ve:
        messagebox.showerror("Validation Error", str(ve))
    except sqlite3.IntegrityError as ie:
        messagebox.showerror("Database Error", "Student ID or Email must be unique.")

tk.Button(student_frame, text="Add Student", command=add_student).grid(row=4, column=1, padx=5, pady=5)

# Treeview to display students
student_tree = ttk.Treeview(student_frame, columns=('ID', 'Name', 'Age', 'Email', 'Student ID'), show='headings')
student_tree.heading('ID', text='ID')
student_tree.heading('Name', text='Name')
student_tree.heading('Age', text='Age')
student_tree.heading('Email', text='Email')
student_tree.heading('Student ID', text='Student ID')
student_tree.column('ID', width=30)
student_tree.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

def refresh_student_tree():
    """
    Refreshes the student tree view with the current data from the database.
    
    This function retrieves the current data from the 'students' table in the database 
    and updates the student tree view to display this data.
    """
    for row in student_tree.get_children():
        student_tree.delete(row)
    cursor.execute('SELECT id, name, age, email, student_id FROM students')
    for student in cursor.fetchall():
        student_tree.insert('', 'end', values=student)

refresh_student_tree()

def delete_student():
    """
    Deletes the selected student from the database and refreshes the student tree view.
    
    This function retrieves the selected student from the student tree view, deletes it 
    from the 'students' table in the database, and refreshes the tree view.
    
    Raises
    ------
    messagebox.showerror
        If no student is selected.
    """
    selected_item = student_tree.selection()
    if selected_item:
        student_id = student_tree.item(selected_item)['values'][0]
        cursor.execute('DELETE FROM students WHERE id = ?', (student_id,))
        conn.commit()
        refresh_student_tree()
        messagebox.showinfo("Success", "Student deleted.")
    else:
        messagebox.showerror("Error", "No student selected.")

tk.Button(student_frame, text="Delete Student", command=delete_student).grid(row=4, column=2, padx=5, pady=5)
# ==================== Instructor Tab ====================

# Variables for instructor form
instructor_name_var = tk.StringVar()
instructor_age_var = tk.StringVar()
instructor_email_var = tk.StringVar()
instructor_id_var = tk.StringVar()

# Instructor Form
tk.Label(instructor_frame, text="Name").grid(row=0, column=0, padx=5, pady=5)
tk.Entry(instructor_frame, textvariable=instructor_name_var).grid(row=0, column=1, padx=5, pady=5)

tk.Label(instructor_frame, text="Age").grid(row=1, column=0, padx=5, pady=5)
tk.Entry(instructor_frame, textvariable=instructor_age_var).grid(row=1, column=1, padx=5, pady=5)

tk.Label(instructor_frame, text="Email").grid(row=2, column=0, padx=5, pady=5)
tk.Entry(instructor_frame, textvariable=instructor_email_var).grid(row=2, column=1, padx=5, pady=5)

tk.Label(instructor_frame, text="Instructor ID").grid(row=3, column=0, padx=5, pady=5)
tk.Entry(instructor_frame, textvariable=instructor_id_var).grid(row=3, column=1, padx=5, pady=5)

def add_instructor():
    """
    Adds an instructor to the database and refreshes the instructor tree view.
    
    This function retrieves the data entered in the instructor form, validates it, 
    and inserts it into the database. If the data is valid and the insertion is successful,
    the instructor tree view is refreshed to display the new instructor.

    Raises
    ------
    ValueError
        If the entered age or email is invalid.
    sqlite3.IntegrityError
        If the instructor ID or email is not unique.
    """
    name = instructor_name_var.get()
    age = instructor_age_var.get()
    email = instructor_email_var.get()
    instructor_id = instructor_id_var.get()
    try:
        age = validate_age(age)
        email = validate_email(email)
        cursor.execute('''
            INSERT INTO instructors (name, age, email, instructor_id)
            VALUES (?, ?, ?, ?)
        ''', (name, age, email, instructor_id))
        conn.commit()
        messagebox.showinfo("Success", "Instructor added to the database.")
        refresh_instructor_tree()
        # Clear form fields
        instructor_name_var.set('')
        instructor_age_var.set('')
        instructor_email_var.set('')
        instructor_id_var.set('')
    except ValueError as ve:
        messagebox.showerror("Validation Error", str(ve))
    except sqlite3.IntegrityError as ie:
        messagebox.showerror("Database Error", "Instructor ID or Email must be unique.")

tk.Button(instructor_frame, text="Add Instructor", command=add_instructor).grid(row=4, column=1, padx=5, pady=5)

# Treeview to display instructors
instructor_tree = ttk.Treeview(instructor_frame, columns=('ID', 'Name', 'Age', 'Email', 'Instructor ID'), show='headings')
instructor_tree.heading('ID', text='ID')
instructor_tree.heading('Name', text='Name')
instructor_tree.heading('Age', text='Age')
instructor_tree.heading('Email', text='Email')
instructor_tree.heading('Instructor ID', text='Instructor ID')
instructor_tree.column('ID', width=30)
instructor_tree.grid(row=5, column=0, columnspan=4, padx=5, pady=5)

def refresh_instructor_tree():
    """
    Refreshes the instructor tree view with the current data from the database.
    
    This function retrieves the current data from the 'instructors' table in the database 
    and updates the instructor tree view to display this data.
    """
    for row in instructor_tree.get_children():
        instructor_tree.delete(row)
    cursor.execute('SELECT id, name, age, email, instructor_id FROM instructors')
    for instructor in cursor.fetchall():
        instructor_tree.insert('', 'end', values=instructor)

refresh_instructor_tree()

def delete_instructor():
    """
    Deletes the selected instructor from the database and refreshes the instructor tree view.
    
    This function retrieves the selected instructor from the instructor tree view, deletes it 
    from the 'instructors' table in the database, and refreshes the tree view. 
    It also sets the instructor_id to NULL in the courses table where this instructor is assigned.

    Raises
    ------
    messagebox.showerror
        If no instructor is selected.
    """
    selected_item = instructor_tree.selection()
    if selected_item:
        instructor_id = instructor_tree.item(selected_item)['values'][0]
        
        # Ask for confirmation
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this instructor? This will remove them from any assigned courses.")
        if not confirm:
            return
        
        try:
            # Set instructor_id to NULL in courses where this instructor is assigned
            cursor.execute('UPDATE courses SET instructor_id = NULL WHERE instructor_id = ?', (instructor_id,))
            conn.commit()
            
            # Delete the instructor
            cursor.execute('DELETE FROM instructors WHERE id = ?', (instructor_id,))
            conn.commit()
            
            refresh_instructor_tree()
            refresh_course_tree()
            messagebox.showinfo("Success", "Instructor deleted and courses updated.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
    else:
        messagebox.showerror("Error", "No instructor selected.")

tk.Button(instructor_frame, text="Delete Instructor", command=delete_instructor).grid(row=4, column=2, padx=5, pady=5)

# ==================== Course Tab ====================

# Variables for course form
course_id_var = tk.StringVar()
course_name_var = tk.StringVar()
course_instructor_var = tk.StringVar()
search_course_var = tk.StringVar()

# Function to add a course
def add_course():
    """
    Adds a course to the database and refreshes the course tree view.
    
    This function retrieves the data entered in the course form, validates it,
    and inserts it into the database. If the data is valid and the insertion is successful,
    the course tree view is refreshed to display the new course.

    Raises
    ------
    sqlite3.IntegrityError
        If the course ID is not unique.
    Exception
        If any other error occurs during insertion.
    """
    course_id = course_id_var.get()
    course_name = course_name_var.get()
    instructor_info = course_instructor_var.get()
    try:
        if instructor_info and instructor_info != 'None':
            instructor_id = int(instructor_info.split(':')[0])
        else:
            instructor_id = None
        cursor.execute('''
            INSERT INTO courses (course_id, course_name, instructor_id)
            VALUES (?, ?, ?)
        ''', (course_id, course_name, instructor_id))
        conn.commit()
        messagebox.showinfo("Success", "Course added to the database.")
        refresh_course_tree()
        # Clear form fields
        course_id_var.set('')
        course_name_var.set('')
        course_instructor_var.set('')
    except sqlite3.IntegrityError:
        messagebox.showerror("Database Error", "Course ID must be unique.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# Function to delete a course
def delete_course():
    """
    Deletes the selected course from the database and refreshes the course tree view.
    
    This function retrieves the selected course from the course tree view, deletes it 
    from the 'courses' table in the database, and refreshes the tree view.

    Raises
    ------
    messagebox.showerror
        If no course is selected.
    """
    selected_item = course_tree.selection()
    if selected_item:
        course_id = course_tree.item(selected_item)['values'][0]
        cursor.execute('DELETE FROM courses WHERE id = ?', (course_id,))
        conn.commit()
        refresh_course_tree()
        messagebox.showinfo("Success", "Course deleted.")
    else:
        messagebox.showerror("Error", "No course selected.")

# Course Form Labels and Entries
tk.Label(course_frame, text="Course ID").grid(row=0, column=0, padx=5, pady=5, sticky='e')
tk.Entry(course_frame, textvariable=course_id_var).grid(row=0, column=1, padx=5, pady=5, sticky='w')

tk.Label(course_frame, text="Course Name").grid(row=1, column=0, padx=5, pady=5, sticky='e')
tk.Entry(course_frame, textvariable=course_name_var).grid(row=1, column=1, padx=5, pady=5, sticky='w')

tk.Label(course_frame, text="Instructor").grid(row=2, column=0, padx=5, pady=5, sticky='e')
course_instructor_dropdown = ttk.Combobox(course_frame, textvariable=course_instructor_var)
course_instructor_dropdown.grid(row=2, column=1, padx=5, pady=5, sticky='w')

def update_course_instructor_options():
    """
    Updates the options in the instructor dropdown menu for the course form.
    
    This function retrieves the current instructors from the 'instructors' table in the database 
    and updates the dropdown menu options to include these instructors.
    """
    cursor.execute('SELECT id, name FROM instructors')
    instructors = cursor.fetchall()
    instructor_options = ['None'] + [f"{i[0]}: {i[1]}" for i in instructors]
    course_instructor_dropdown['values'] = instructor_options

course_instructor_dropdown.bind("<Button-1>", lambda e: update_course_instructor_options())

# Place the "Add Course" and "Delete Course" buttons
tk.Button(course_frame, text="Add Course", command=add_course).grid(row=3, column=0, padx=5, pady=5, sticky='e')
tk.Button(course_frame, text="Delete Course", command=delete_course).grid(row=3, column=1, padx=5, pady=5, sticky='w')

# Treeview to display courses
course_tree = ttk.Treeview(course_frame, columns=('ID', 'Course ID', 'Course Name', 'Instructor'), show='headings')
course_tree.heading('ID', text='ID')
course_tree.heading('Course ID', text='Course ID')
course_tree.heading('Course Name', text='Course Name')
course_tree.heading('Instructor', text='Instructor')
course_tree.column('ID', width=30)
course_tree.grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky='nsew')

# Configure the grid to make the treeview expand
course_frame.grid_columnconfigure(0, weight=0)
course_frame.grid_columnconfigure(1, weight=1)
course_frame.grid_columnconfigure(2, weight=0)
course_frame.grid_rowconfigure(4, weight=1)

def refresh_course_tree():
    """
    Refreshes the course tree view with the current data from the database.
    
    This function retrieves the current data from the 'courses' table in the database 
    and updates the course tree view to display this data.
    """
    for row in course_tree.get_children():
        course_tree.delete(row)
    cursor.execute('''
        SELECT courses.id, courses.course_id, courses.course_name, IFNULL(instructors.name, 'None')
        FROM courses
        LEFT JOIN instructors ON courses.instructor_id = instructors.id
    ''')
    for course in cursor.fetchall():
        course_tree.insert('', 'end', values=course)

refresh_course_tree()

# ==================== Student Registration for Courses ====================

# Registration Section in Student Tab
tk.Label(student_frame, text="Register Student for Course").grid(row=6, column=0, padx=5, pady=10, columnspan=2)

selected_student_var = tk.StringVar()
selected_course_var = tk.StringVar()

def update_student_options():
    """
    Updates the student dropdown menu with current student options from the database.
    
    This function retrieves the current students from the 'students' table in the database
    and updates the dropdown menu options to include these students.
    """
    cursor.execute('SELECT id, name FROM students')
    students = cursor.fetchall()
    student_options = [f"{s[0]}: {s[1]}" for s in students]
    selected_student_var.set('')
    student_dropdown['values'] = student_options

def update_course_options():
    """
    Updates the course dropdown menu with current course options from the database.
    
    This function retrieves the current courses from the 'courses' table in the database
    and updates the dropdown menu options to include these courses.
    """
    cursor.execute('SELECT id, course_name FROM courses')
    courses = cursor.fetchall()
    course_options = [f"{c[0]}: {c[1]}" for c in courses]
    selected_course_var.set('')
    course_dropdown['values'] = course_options

tk.Label(student_frame, text="Select Student").grid(row=7, column=0, padx=5, pady=5)
student_dropdown = ttk.Combobox(student_frame, textvariable=selected_student_var, postcommand=update_student_options)
student_dropdown.grid(row=7, column=1, padx=5, pady=5)

tk.Label(student_frame, text="Select Course").grid(row=8, column=0, padx=5, pady=5)
course_dropdown = ttk.Combobox(student_frame, textvariable=selected_course_var, postcommand=update_course_options)
course_dropdown.grid(row=8, column=1, padx=5, pady=5)

def register_student_for_course():
    """
    Registers a student for a selected course in the database.
    
    This function retrieves the selected student and course from the dropdown menus,
    inserts a new registration record into the 'registrations' table, and commits the changes.

    Raises
    ------
    messagebox.showerror
        If an error occurs during registration.
    """
    student_info = selected_student_var.get()
    course_info = selected_course_var.get()
    try:
        student_id = int(student_info.split(':')[0])
        course_id = int(course_info.split(':')[0])
        cursor.execute('''
            INSERT INTO registrations (student_id, course_id)
            VALUES (?, ?)
        ''', (student_id, course_id))
        conn.commit()
        messagebox.showinfo("Success", "Student registered for course.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(student_frame, text="Register", command=register_student_for_course).grid(row=9, column=1, padx=5, pady=5)

# ==================== Instructor Assignment to Courses ====================

# Assignment Section in Instructor Tab
tk.Label(instructor_frame, text="Assign Instructor to Course").grid(row=6, column=0, padx=5, pady=10, columnspan=2)

assign_instructor_var = tk.StringVar()
assign_course_var = tk.StringVar()

def update_instructor_options():
    """
    Updates the instructor dropdown menu with current instructor options from the database.
    
    This function retrieves the current instructors from the 'instructors' table in the database
    and updates the dropdown menu options to include these instructors.
    """
    cursor.execute('SELECT id, name FROM instructors')
    instructors = cursor.fetchall()
    instructor_options = [f"{i[0]}: {i[1]}" for i in instructors]
    assign_instructor_var.set('')
    instructor_dropdown['values'] = instructor_options

def update_assign_course_options():
    """
    Updates the course dropdown menu with current unassigned course options from the database.
    
    This function retrieves the current courses from the 'courses' table in the database
    where the instructor is not assigned, and updates the dropdown menu options to include these courses.
    """
    cursor.execute('SELECT id, course_name FROM courses WHERE instructor_id IS NULL')
    courses = cursor.fetchall()
    course_options = []
    for c in courses:
        course_id = c[0]
        course_name = c[1] if c[1] else '[No Name]'
        course_options.append(f"{course_id}: {course_name}")
    assign_course_var.set('')
    assign_course_dropdown['values'] = course_options

tk.Label(instructor_frame, text="Select Instructor").grid(row=7, column=0, padx=5, pady=5)
instructor_dropdown = ttk.Combobox(instructor_frame, textvariable=assign_instructor_var, postcommand=update_instructor_options)
instructor_dropdown.grid(row=7, column=1, padx=5, pady=5)

tk.Label(instructor_frame, text="Select Course").grid(row=8, column=0, padx=5, pady=5)
assign_course_dropdown = ttk.Combobox(instructor_frame, textvariable=assign_course_var, postcommand=update_assign_course_options)
assign_course_dropdown.grid(row=8, column=1, padx=5, pady=5)

def assign_instructor_to_course():
    """
    Assigns an instructor to a selected course in the database.
    
    This function retrieves the selected instructor and course from the dropdown menus,
    updates the course record in the 'courses' table with the selected instructor,
    and commits the changes.

    Raises
    ------
    messagebox.showerror
        If an error occurs during the assignment or if selections are invalid.
    """
    instructor_info = assign_instructor_var.get()
    course_info = assign_course_var.get()

    if not instructor_info or not course_info:
        messagebox.showerror("Error", "Please select both an instructor and a course.")
        return

    try:
        instructor_id = int(instructor_info.split(':')[0])
        course_id = int(course_info.split(':')[0])

        cursor.execute('''
            UPDATE courses SET instructor_id = ? WHERE id = ?
        ''', (instructor_id, course_id))
        conn.commit()
        messagebox.showinfo("Success", "Instructor assigned to course.")
        refresh_course_tree()
    except ValueError:
        messagebox.showerror("Error", "Invalid selection. Please select a valid instructor and course.")
    except Exception as e:
        messagebox.showerror("Error", str(e))

tk.Button(instructor_frame, text="Assign", command=assign_instructor_to_course).grid(row=9, column=1, padx=5, pady=5)

# ==================== Search Functionality ====================

# Search in Student Tab
search_student_var = tk.StringVar()

tk.Label(student_frame, text="Search Students").grid(row=10, column=0, padx=5, pady=5)
tk.Entry(student_frame, textvariable=search_student_var).grid(row=10, column=1, padx=5, pady=5)

def search_students():
    """
    Searches and displays students based on the query entered in the search box.
    
    This function retrieves students from the 'students' table in the database whose name or 
    student ID matches the search query, and updates the student tree view to display these students.
    """
    query = search_student_var.get()
    for row in student_tree.get_children():
        student_tree.delete(row)
    cursor.execute('''
        SELECT id, name, age, email, student_id FROM students
        WHERE name LIKE ? OR student_id LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    for student in cursor.fetchall():
        student_tree.insert('', 'end', values=student)

tk.Button(student_frame, text="Search", command=search_students).grid(row=10, column=2, padx=5, pady=5)

# Search in Instructor Tab
search_instructor_var = tk.StringVar()

tk.Label(instructor_frame, text="Search Instructors").grid(row=10, column=0, padx=5, pady=5)
tk.Entry(instructor_frame, textvariable=search_instructor_var).grid(row=10, column=1, padx=5, pady=5)

def search_instructors():
    """
    Searches and displays instructors based on the query entered in the search box.
    
    This function retrieves instructors from the 'instructors' table in the database whose name or 
    instructor ID matches the search query, and updates the instructor tree view to display these instructors.
    """
    query = search_instructor_var.get()
    for row in instructor_tree.get_children():
        instructor_tree.delete(row)
    cursor.execute('''
        SELECT id, name, age, email, instructor_id FROM instructors
        WHERE name LIKE ? OR instructor_id LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    for instructor in cursor.fetchall():
        instructor_tree.insert('', 'end', values=instructor)

tk.Button(instructor_frame, text="Search", command=search_instructors).grid(row=10, column=2, padx=5, pady=5)

def search_courses():
    """
    Searches and displays courses based on the query entered in the search box.
    
    This function retrieves courses from the 'courses' table in the database whose name or 
    course ID matches the search query, and updates the course tree view to display these courses.
    """
    query = search_course_var.get()
    for row in course_tree.get_children():
        course_tree.delete(row)
    cursor.execute('''
        SELECT courses.id, courses.course_id, courses.course_name, IFNULL(instructors.name, 'None')
        FROM courses
        LEFT JOIN instructors ON courses.instructor_id = instructors.id
        WHERE courses.course_name LIKE ? OR courses.course_id LIKE ?
    ''', (f'%{query}%', f'%{query}%'))
    for course in cursor.fetchall():
        course_tree.insert('', 'end', values=course)

# Search in Course Tab
search_course_var = tk.StringVar()

# Search Functionality
tk.Label(course_frame, text="Search Courses").grid(row=5, column=0, padx=5, pady=5, sticky='e')
tk.Entry(course_frame, textvariable=search_course_var).grid(row=5, column=1, padx=5, pady=5, sticky='w')
tk.Button(course_frame, text="Search", command=search_courses).grid(row=5, column=2, padx=5, pady=5, sticky='w')

# ==================== Database Backup ====================

def backup_database():
    """
    Create a backup of the database.

    This function performs the following steps:
    
    1. Commit any pending transactions.
    2. Open a file dialog to select the save location.
    3. Read data from each table into pandas DataFrames.
    4. Save each DataFrame to a CSV file in the selected folder.
    5. Show a success message upon completion.

    If any exception occurs, an error message is displayed.

    Raises
    ------
    messagebox.showerror
        If an error occurs during the backup process.
    """
    try:
        conn.commit()
        folder_path = filedialog.askdirectory(title="Select Backup Folder")
        if folder_path:
            students_df = pd.read_sql_query("SELECT * FROM students", conn)
            instructors_df = pd.read_sql_query("SELECT * FROM instructors", conn)
            courses_df = pd.read_sql_query("SELECT * FROM courses", conn)
            registrations_df = pd.read_sql_query("SELECT * FROM registrations", conn)

            students_csv = os.path.join(folder_path, 'students_backup.csv')
            instructors_csv = os.path.join(folder_path, 'instructors_backup.csv')
            courses_csv = os.path.join(folder_path, 'courses_backup.csv')
            registrations_csv = os.path.join(folder_path, 'registrations_backup.csv')

            students_df.to_csv(students_csv, index=False)
            instructors_df.to_csv(instructors_csv, index=False)
            courses_df.to_csv(courses_csv, index=False)
            registrations_df.to_csv(registrations_csv, index=False)

            messagebox.showinfo("Success", f"Database backup saved to {folder_path}.")
    except Exception as e:
        messagebox.showerror("Error", str(e))


def show_enrolled_students(event):
    """
    Display enrolled students for the selected course.

    This function retrieves the students enrolled in the selected course
    and displays them in a new window.

    Parameters
    ----------
    event : tk.Event
        The event object containing information about the double-click event.

    Raises
    ------
    messagebox.showerror
        If no course is selected or an error occurs while fetching the data.
    """
    selected_item = course_tree.selection()
    if selected_item:
        course_id = course_tree.item(selected_item)['values'][0]
        cursor.execute('''
            SELECT students.id, students.name, students.student_id
            FROM registrations
            JOIN students ON registrations.student_id = students.id
            WHERE registrations.course_id = ?
        ''', (course_id,))
        students = cursor.fetchall()
        display_students_window = tk.Toplevel(root)
        display_students_window.title("Enrolled Students")
        tree = ttk.Treeview(display_students_window, columns=('ID', 'Name', 'Student ID'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Name', text='Name')
        tree.heading('Student ID', text='Student ID')
        tree.pack(fill='both', expand=True)
        for student in students:
            tree.insert('', 'end', values=student)
    else:
        messagebox.showerror("Error", "No course selected.")

course_tree.bind("<Double-1>", show_enrolled_students)


def show_assigned_courses(event):
    """
    Display courses taught by the selected instructor.

    This function retrieves the courses assigned to the selected instructor
    and displays them in a new window.

    Parameters
    ----------
    event : tk.Event
        The event object containing information about the double-click event.

    Raises
    ------
    messagebox.showerror
        If no instructor is selected or an error occurs while fetching the data.
    """
    selected_item = instructor_tree.selection()
    if selected_item:
        instructor_id = instructor_tree.item(selected_item)['values'][0]
        cursor.execute('''
            SELECT courses.id, courses.course_id, courses.course_name
            FROM courses
            WHERE instructor_id = ?
        ''', (instructor_id,))
        courses = cursor.fetchall()
        display_courses_window = tk.Toplevel(root)
        display_courses_window.title("Assigned Courses")
        tree = ttk.Treeview(display_courses_window, columns=('ID', 'Course ID', 'Course Name'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Course ID', text='Course ID')
        tree.heading('Course Name', text='Course Name')
        tree.pack(fill='both', expand=True)
        for course in courses:
            tree.insert('', 'end', values=course)
    else:
        messagebox.showerror("Error", "No instructor selected.")

instructor_tree.bind("<Double-1>", show_assigned_courses)


def show_student_courses(event):
    """
    Display courses enrolled by the selected student.

    This function retrieves the courses enrolled by the selected student
    and displays them in a new window.

    Parameters
    ----------
    event : tk.Event
        The event object containing information about the double-click event.

    Raises
    ------
    messagebox.showerror
        If no student is selected or an error occurs while fetching the data.
    """
    selected_item = student_tree.selection()
    if selected_item:
        student_id = student_tree.item(selected_item)['values'][0]
        cursor.execute('''
            SELECT courses.id, courses.course_id, courses.course_name
            FROM registrations
            JOIN courses ON registrations.course_id = courses.id
            WHERE registrations.student_id = ?
        ''', (student_id,))
        courses = cursor.fetchall()
        display_courses_window = tk.Toplevel(root)
        display_courses_window.title("Enrolled Courses")
        tree = ttk.Treeview(display_courses_window, columns=('ID', 'Course ID', 'Course Name'), show='headings')
        tree.heading('ID', text='ID')
        tree.heading('Course ID', text='Course ID')
        tree.heading('Course Name', text='Course Name')
        tree.pack(fill='both', expand=True)
        for course in courses:
            tree.insert('', 'end', values=course)
    else:
        messagebox.showerror("Error", "No student selected.")

student_tree.bind("<Double-1>", show_student_courses)


def load_database():
    """
    Load the database from backup CSV files.

    This function performs the following steps:
    
    1. Open a file dialog to select the folder containing the backup CSV files.
    2. Check if all necessary CSV files are present in the selected folder.
    3. Read each CSV into a DataFrame.
    4. Begin a transaction and disable foreign key checks.
    5. Delete existing data and reset sequences.
    6. Insert data from DataFrames into the corresponding database tables.
    7. Re-enable foreign key checks and commit the transaction.
    8. Refresh the tree views to display the updated data.
    9. Show a success message upon completion.

    If any exception occurs, the transaction is rolled back and an error message is displayed.

    Raises
    ------
    messagebox.showerror
        If an error occurs during the load process or if the backup files are not found.
    """
    try:
        folder_path = filedialog.askdirectory(title="Select Backup Folder")
        if folder_path:
            students_csv = os.path.join(folder_path, 'students_backup.csv')
            instructors_csv = os.path.join(folder_path, 'instructors_backup.csv')
            courses_csv = os.path.join(folder_path, 'courses_backup.csv')
            registrations_csv = os.path.join(folder_path, 'registrations_backup.csv')

            if not all(os.path.exists(f) for f in [students_csv, instructors_csv, courses_csv, registrations_csv]):
                messagebox.showerror("Error", "Backup files not found in the selected folder.")
                return

            students_df = pd.read_csv(students_csv)
            instructors_df = pd.read_csv(instructors_csv)
            courses_df = pd.read_csv(courses_csv)
            registrations_df = pd.read_csv(registrations_csv)

            conn.execute("BEGIN TRANSACTION;")
            conn.execute("PRAGMA foreign_keys = OFF;")
            cursor.execute("DELETE FROM registrations;")
            cursor.execute("DELETE FROM courses;")
            cursor.execute("DELETE FROM instructors;")
            cursor.execute("DELETE FROM students;")
            conn.commit()

            cursor.execute("DELETE FROM sqlite_sequence WHERE name='students';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='instructors';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='courses';")
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='registrations';")
            conn.commit()

            instructors_df.to_sql('instructors', conn, if_exists='append', index=False)
            courses_df.to_sql('courses', conn, if_exists='append', index=False)
            students_df.to_sql('students', conn, if_exists='append', index=False)
            registrations_df.to_sql('registrations', conn, if_exists='append', index=False)

            conn.execute("PRAGMA foreign_keys = ON;")
            conn.commit()

            refresh_instructor_tree()
            refresh_course_tree()
            refresh_student_tree()

            messagebox.showinfo("Success", "Database loaded from backup.")
    except Exception as e:
        conn.rollback()
        messagebox.showerror("Error", f"An error occurred while loading the database: {str(e)}")


tk.Button(root, text="Backup Database", command=backup_database).pack(side='bottom', pady=5)
tk.Button(root, text="Load Database", command=load_database).pack(side='bottom', pady=5)

root.mainloop()
conn.close()

