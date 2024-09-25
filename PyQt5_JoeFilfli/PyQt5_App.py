#I am Joe Filfli, my teammate is Mansour Allam, i decided to document PyQt5

"""
School Management System Module.

This module provides class definitions for Person, Student, Instructor, and Course. 
It includes functionality for managing student and instructor records, as well as course information.
"""

import sys
import sqlite3
import re
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QTabWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QMessageBox, QTableWidget, QTableWidgetItem,
    QComboBox, QHeaderView, QDialog, QFileDialog
)
import pandas as pd
import os

# ==================== Class Definitions ====================

class Person:
    """
    Represents a person with basic attributes such as name, age, and email.

    :param name: The name of the person.
    :type name: str
    :param age: The age of the person, must be a non-negative integer.
    :type age: int
    :param email: The email address of the person, validated using a regular expression.
    :type email: str
    :raises ValueError: If age is negative or email format is invalid.
    """

    def __init__(self, name, age, email):
        """
        Initializes a new instance of the Person class.

        :param name: The name of the person.
        :param age: The age of the person.
        :param email: The email address of the person.
        """
        self.name = name
        self.age = self._validate_age(age)
        self._email = self._validate_email(email)
    
    def introduce(self):
        """
        Prints an introduction message with the person's name and age.
        """
        print(f"Hello, my name is {self.name} and I am {self.age} years old.")
    
    def _validate_email(self, email):
        """
        Validates the email address format.

        :param email: The email address to be validated.
        :type email: str
        :return: The validated email address if valid.
        :rtype: str
        :raises ValueError: If the email format is invalid.
        """
        pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if re.match(pattern, email):
            return email
        else:
            raise ValueError("Invalid email format.")
    
    def _validate_age(self, age):
        """
        Validates the age to ensure it is a non-negative integer.

        :param age: The age to be validated.
        :type age: int
        :return: The validated age if valid.
        :rtype: int
        :raises ValueError: If the age is negative or not an integer.
        """
        if isinstance(age, int) and age >= 0:
            return age
        else:
            raise ValueError("Age must be a non-negative integer.")


class Student(Person):
    """
    Represents a student, inheriting from the Person class.

    :param name: The name of the student.
    :type name: str
    :param age: The age of the student.
    :type age: int
    :param email: The email address of the student.
    :type email: str
    :param student_id: The unique student ID.
    :type student_id: str
    :param db_id: The database ID for the student (optional).
    :type db_id: int, optional
    """

    def __init__(self, name, age, email, student_id, db_id=None):
        """
        Initializes a new instance of the Student class.

        :param name: The name of the student.
        :param age: The age of the student.
        :param email: The email address of the student.
        :param student_id: The unique student ID.
        :param db_id: The database ID (optional).
        """
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses = []  # List of Course objects
        self.db_id = db_id  # Database ID

    @classmethod
    def from_db_row(cls, row):
        """
        Creates a Student instance from a database row.

        :param row: A tuple containing student data from a database query.
        :type row: tuple
        :return: A new instance of the Student class.
        :rtype: Student
        """
        db_id, name, age, email, student_id = row
        return cls(name, age, email, student_id, db_id)


class Instructor(Person):
    """
    Represents an instructor, inheriting from the Person class.

    :param name: The name of the instructor.
    :type name: str
    :param age: The age of the instructor.
    :type age: int
    :param email: The email address of the instructor.
    :type email: str
    :param instructor_id: The unique instructor ID.
    :type instructor_id: str
    :param db_id: The database ID for the instructor (optional).
    :type db_id: int, optional
    """

    def __init__(self, name, age, email, instructor_id, db_id=None):
        """
        Initializes a new instance of the Instructor class.

        :param name: The name of the instructor.
        :param age: The age of the instructor.
        :param email: The email address of the instructor.
        :param instructor_id: The unique instructor ID.
        :param db_id: The database ID (optional).
        """
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = []  # List of Course objects
        self.db_id = db_id  # Database ID

    @classmethod
    def from_db_row(cls, row):
        """
        Creates an Instructor instance from a database row.

        :param row: A tuple containing instructor data from a database query.
        :type row: tuple
        :return: A new instance of the Instructor class.
        :rtype: Instructor
        """
        db_id, name, age, email, instructor_id = row
        return cls(name, age, email, instructor_id, db_id)


class Course:
    """
    Represents a course in the school system.

    :param course_id: The unique course ID.
    :type course_id: str
    :param course_name: The name of the course.
    :type course_name: str
    :param instructor: The instructor assigned to the course (optional).
    :type instructor: Instructor, optional
    :param db_id: The database ID for the course (optional).
    :type db_id: int, optional
    """

    def __init__(self, course_id, course_name, instructor=None, db_id=None):
        """
        Initializes a new instance of the Course class.

        :param course_id: The unique course ID.
        :param course_name: The name of the course.
        :param instructor: The instructor assigned to the course.
        :param db_id: The database ID (optional).
        """
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor  # Should be an Instructor object
        self.enrolled_students = []   # List of Student objects
        self.db_id = db_id  # Database ID

    @classmethod
    def from_db_row(cls, row):
        """
        Creates a Course instance from a database row.

        :param row: A tuple containing course data from a database query.
        :type row: tuple
        :return: A new instance of the Course class.
        :rtype: Course
        """
        db_id, course_id, course_name, instructor_name = row
        return cls(course_id, course_name, db_id=db_id)

# ==================== Database Setup ====================

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

# Create tables if they don't already exist
def create_tables():
    """
    Creates tables in the SQLite database for managing students, instructors, courses, 
    and registrations if they do not already exist.

    - `students`: Contains `id`, `name`, `age`, `email`, and `student_id` fields.
    - `instructors`: Contains `id`, `name`, `age`, `email`, and `instructor_id` fields.
    - `courses`: Contains `id`, `course_id`, `course_name`, and a foreign key `instructor_id`.
    - `registrations`: Links students and courses in a many-to-many relationship, 
       containing `student_id` and `course_id` foreign keys.
    
    Each table includes necessary constraints, such as `PRIMARY KEY` and `FOREIGN KEY`, 
    to ensure data integrity.
    
    The tables created are:
    
    - `students`: Stores student data.
    - `instructors`: Stores instructor data.
    - `courses`: Stores course data.
    - `registrations`: Links students with their registered courses.
    
    After executing the queries, the changes are committed to the database.
    
    """
    # Create `students` table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            email TEXT NOT NULL UNIQUE,
            student_id TEXT NOT NULL UNIQUE
        )
    ''')

    # Create `instructors` table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL CHECK(age >= 0),
            email TEXT NOT NULL UNIQUE,
            instructor_id TEXT NOT NULL UNIQUE
        )
    ''')

    # Create `courses` table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL UNIQUE,
            course_name TEXT NOT NULL,
            instructor_id INTEGER,
            FOREIGN KEY(instructor_id) REFERENCES instructors(id)
        )
    ''')

    # Create `registrations` table if it does not exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            student_id INTEGER,
            course_id INTEGER,
            PRIMARY KEY(student_id, course_id),
            FOREIGN KEY(student_id) REFERENCES students(id),
            FOREIGN KEY(course_id) REFERENCES courses(id)
        )
    ''')

    # Commit the transaction to save changes
    conn.commit()

# Create tables if they don't already exist
create_tables()

# ==================== PyQt5 Application ====================

class SchoolManagementSystem(QMainWindow):
    """
    A PyQt5-based GUI application for managing students, instructors, and courses in a school system.
    
    The application provides functionalities for:
    - Adding, deleting, and searching students and instructors.
    - Registering students for courses.
    - Backing up and restoring the database.
    - Viewing enrolled students and assigned courses.
    """
    def __init__(self):
        """
        Initializes the `SchoolManagementSystem` window.

        This method sets up the main window properties, such as the title and window size, and 
        establishes a connection to the SQLite database. It also adds buttons for backing up 
        the database to CSV and loading the database from a backup. Additionally, it initializes 
        the user interface (UI) components of the application.

        The following operations are performed:
        
        - Sets the window title to "School Management System".
        - Defines the geometry of the window (100x100 for position, 1000x700 for width and height).
        - Connects the `conn` and `cursor` objects to the SQLite database.
        - Adds a "Backup Database to CSV" button to the status bar, which calls `backup_database_to_csv`.
        - Adds a "Load Database" button to the status bar, which calls `load_database`.
        - Calls the `initUI` method to initialize the user interface and create tabs for students, instructors, and courses.
        """
        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 1000, 700)
        
        # Set up database connection and cursor
        self.conn = conn
        self.cursor = cursor

        # Create the Backup button
        backup_button = QPushButton("Backup Database to CSV")
        backup_button.clicked.connect(self.backup_database_to_csv)
        self.statusBar().addPermanentWidget(backup_button)

        # Create the Load Database button
        load_button = QPushButton('Load Database', self)
        load_button.clicked.connect(self.load_database)
        self.statusBar().addPermanentWidget(load_button)

        # Initialize the UI
    
        self.initUI()


    def initUI(self):
        """
        Initializes the user interface (UI) for the `SchoolManagementSystem` application.

        This method sets up the main UI components of the application, which includes:
        
        - Creating a tabbed layout with separate tabs for managing students, instructors, and courses.
        - Initializing and adding three tabs: "Students", "Instructors", and "Courses" to the main window.
        - Calling specific methods (`init_student_tab`, `init_instructor_tab`, and `init_course_tab`) to 
        populate each tab with its respective content, forms, and functionality.
        
        Steps:
        
        1. A `QTabWidget` is created to manage multiple tabs.
        2. Three `QWidget` instances (`student_tab`, `instructor_tab`, `course_tab`) are created to represent 
        the tabs for students, instructors, and courses.
        3. Each tab is added to the `QTabWidget` with appropriate labels: "Students", "Instructors", and "Courses".
        4. Calls are made to initialize the content of each tab via the `init_student_tab`, `init_instructor_tab`, 
        and `init_course_tab` methods.
        
        This method does not take any parameters or return any values.
        """
        
        # Create the tab widget
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Student, Instructor, and Course tabs
        self.student_tab = QWidget()
        self.instructor_tab = QWidget()
        self.course_tab = QWidget()

        # Add the tabs to the tab widget
        self.tabs.addTab(self.student_tab, "Students")
        self.tabs.addTab(self.instructor_tab, "Instructors")
        self.tabs.addTab(self.course_tab, "Courses")

        # Initialize each tab
        self.init_student_tab()
        self.init_instructor_tab()
        self.init_course_tab()


    def backup_database_to_csv(self):
        """
        Backs up the current state of the database to CSV files.

        This method allows the user to back up the `students`, `instructors`, `courses`, and `registrations` 
        tables from the SQLite database to CSV files. The user is prompted to select a directory to save 
        the backup files, and if successful, the data from each table is exported into separate CSV files.

        Steps:
        
        1. Prompts the user to choose a directory using a `QFileDialog`.
        2. Reads the data from the database tables (`students`, `instructors`, `courses`, `registrations`) 
        into `pandas` DataFrames.
        3. Defines the filenames for each backup CSV based on the selected folder.
        4. Saves each table's DataFrame as a CSV file in the selected directory.
        5. Displays a success message if the operation is successful.
        6. If an error occurs during the process, an error message is shown to the user.

        Exceptions:
            Exception: If any error occurs during the backup process, it will be caught, 
            and a warning message will be shown to the user.

        Example Usage:
            To back up the database, the user would click the "Backup Database to CSV" button, 
            which triggers this method to perform the backup.

        Raises:
            Exception: If any error occurs while reading from the database or writing to the CSV files.

        """
        try:
            # Prompt the user to select a directory to save the backup files
            options = QFileDialog.Options()
            folder_path = QFileDialog.getExistingDirectory(self, "Select Backup Folder", options=options)

            if folder_path:
                # Read data from each table into pandas DataFrames
                students_df = pd.read_sql_query("SELECT * FROM students", self.conn)
                instructors_df = pd.read_sql_query("SELECT * FROM instructors", self.conn)
                courses_df = pd.read_sql_query("SELECT * FROM courses", self.conn)
                registrations_df = pd.read_sql_query("SELECT * FROM registrations", self.conn)

                # Define filenames for each CSV
                students_csv = os.path.join(folder_path, 'students_backup.csv')
                instructors_csv = os.path.join(folder_path, 'instructors_backup.csv')
                courses_csv = os.path.join(folder_path, 'courses_backup.csv')
                registrations_csv = os.path.join(folder_path, 'registrations_backup.csv')

                # Save each DataFrame to a CSV file
                students_df.to_csv(students_csv, index=False)
                instructors_df.to_csv(instructors_csv, index=False)
                courses_df.to_csv(courses_csv, index=False)
                registrations_df.to_csv(registrations_csv, index=False)

                # Show success message
                QMessageBox.information(self, "Success", f"Database backup saved to {folder_path}.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))



    def init_student_tab(self):
        """
        Initializes the student management tab in the `SchoolManagementSystem` UI.

        This method sets up the layout and functionality for managing student records, allowing the user 
        to add, delete, search, and register students for courses. The tab includes a form to input student 
        information, a table to display student data, and a section for searching and registering students 
        for courses.

        Layout Details:
        
        1. **Left Side: Form to Add Students**
        - **Name**: A `QLabel` and `QLineEdit` to input the student's name.
        - **Age**: A `QLabel` and `QLineEdit` to input the student's age.
        - **Email**: A `QLabel` and `QLineEdit` to input the student's email.
        - **Student ID**: A `QLabel` and `QLineEdit` to input the student's unique ID.
        - **Add Student Button**: A `QPushButton` that calls the `add_student` method when clicked.
        - **Delete Student Button**: A `QPushButton` that calls the `delete_student` method when clicked.
        
        2. **Right Side: Table to Display Students**
        - A `QTableWidget` to display the student list with columns for ID, Name, Age, Email, and Student ID.
        - The table is read-only (via `NoEditTriggers`) and supports row selection.
        - Double-clicking a row calls the `show_student_courses` method to display the student's registered courses.
        
        3. **Search Section**
        - **Search Bar**: A `QLabel` and `QLineEdit` for entering search queries to filter students by name or student ID.
        - **Search Button**: A `QPushButton` that calls the `search_students` method when clicked.
        
        4. **Registration Section**
        - **Student ComboBox**: A `QComboBox` populated with students using the `update_student_options` method.
        - **Course ComboBox**: A `QComboBox` populated with available courses using the `update_course_options` method.
        - **Register Button**: A `QPushButton` that calls the `register_student_for_course` method when clicked.

        Finally, the student tab layout is set, and the student table is refreshed by calling `refresh_student_table`.

        """
        # Layout for the student tab
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Left side: Form to add students
        form_group = QWidget()
        form_group_layout = QVBoxLayout()

        # Name input
        name_label = QLabel("Name:")
        self.student_name_input = QLineEdit()
        form_group_layout.addWidget(name_label)
        form_group_layout.addWidget(self.student_name_input)

        # Age input
        age_label = QLabel("Age:")
        self.student_age_input = QLineEdit()
        form_group_layout.addWidget(age_label)
        form_group_layout.addWidget(self.student_age_input)

        # Email input
        email_label = QLabel("Email:")
        self.student_email_input = QLineEdit()
        form_group_layout.addWidget(email_label)
        form_group_layout.addWidget(self.student_email_input)

        # Student ID input
        student_id_label = QLabel("Student ID:")
        self.student_id_input = QLineEdit()
        form_group_layout.addWidget(student_id_label)
        form_group_layout.addWidget(self.student_id_input)

        # Add and delete student buttons
        add_student_button = QPushButton("Add Student")
        add_student_button.clicked.connect(self.add_student)
        form_group_layout.addWidget(add_student_button)

        delete_student_button = QPushButton("Delete Student")
        delete_student_button.clicked.connect(self.delete_student)
        form_group_layout.addWidget(delete_student_button)

        form_group.setLayout(form_group_layout)
        form_layout.addWidget(form_group)

        # Right side: Table to display students
        self.student_table = QTableWidget()
        self.student_table.setColumnCount(5)
        self.student_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Student ID'])
        self.student_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.student_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.student_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.student_table.doubleClicked.connect(self.show_student_courses)
        form_layout.addWidget(self.student_table)

        layout.addLayout(form_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Students:")
        self.student_search_input = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_students)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.student_search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Registration section
        registration_layout = QVBoxLayout()
        registration_label = QLabel("Register Student for Course")
        registration_layout.addWidget(registration_label)

        reg_form_layout = QHBoxLayout()

        # Student ComboBox
        self.registration_student_combo = QComboBox()
        self.update_student_options()
        reg_form_layout.addWidget(QLabel("Select Student:"))
        reg_form_layout.addWidget(self.registration_student_combo)

        # Course ComboBox
        self.registration_course_combo = QComboBox()
        self.update_course_options()
        reg_form_layout.addWidget(QLabel("Select Course:"))
        reg_form_layout.addWidget(self.registration_course_combo)

        # Register button
        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register_student_for_course)
        reg_form_layout.addWidget(register_button)

        registration_layout.addLayout(reg_form_layout)
        layout.addLayout(registration_layout)

        # Set the layout for the student tab and refresh the table
        self.student_tab.setLayout(layout)
        self.refresh_student_table()

    def init_instructor_tab(self):
        """
        Initializes the instructor management tab in the `SchoolManagementSystem` UI.

        This method sets up the layout and functionality for managing instructor records, allowing the user 
        to add, delete, search for, and assign instructors to courses. The tab includes a form to input 
        instructor information, a table to display instructor data, and sections for searching instructors 
        and assigning them to courses.

        Layout Details:
        
        1. **Left Side: Form to Add Instructors**
        - **Name**: A `QLabel` and `QLineEdit` to input the instructor's name.
        - **Age**: A `QLabel` and `QLineEdit` to input the instructor's age.
        - **Email**: A `QLabel` and `QLineEdit` to input the instructor's email.
        - **Instructor ID**: A `QLabel` and `QLineEdit` to input the unique instructor ID.
        - **Add Instructor Button**: A `QPushButton` that triggers the `add_instructor` method when clicked.
        - **Delete Instructor Button**: A `QPushButton` that triggers the `delete_instructor` method when clicked.

        2. **Right Side: Table to Display Instructors**
        - A `QTableWidget` to display the instructor list with columns for ID, Name, Age, Email, and Instructor ID.
        - The table is read-only (via `NoEditTriggers`) and supports row selection.
        - Double-clicking a row calls the `show_assigned_courses` method to display the courses assigned to the instructor.

        3. **Search Section**
        - **Search Bar**: A `QLabel` and `QLineEdit` for entering search queries to filter instructors by name or ID.
        - **Search Button**: A `QPushButton` that triggers the `search_instructors` method when clicked.

        4. **Assignment Section**
        - **Instructor ComboBox**: A `QComboBox` populated with instructors using the `update_instructor_options` method.
        - **Course ComboBox**: A `QComboBox` populated with available courses using the `update_unassigned_course_options` method.
        - **Assign Button**: A `QPushButton` that triggers the `assign_instructor_to_course` method when clicked.

        After setting up the instructor tab layout, the instructor table is refreshed by calling `refresh_instructor_table`.

        """
        # Layout for the instructor tab
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Left side: Form to add instructors
        form_group = QWidget()
        form_group_layout = QVBoxLayout()

        # Name input
        name_label = QLabel("Name:")
        self.instructor_name_input = QLineEdit()
        form_group_layout.addWidget(name_label)
        form_group_layout.addWidget(self.instructor_name_input)

        # Age input
        age_label = QLabel("Age:")
        self.instructor_age_input = QLineEdit()
        form_group_layout.addWidget(age_label)
        form_group_layout.addWidget(self.instructor_age_input)

        # Email input
        email_label = QLabel("Email:")
        self.instructor_email_input = QLineEdit()
        form_group_layout.addWidget(email_label)
        form_group_layout.addWidget(self.instructor_email_input)

        # Instructor ID input
        instructor_id_label = QLabel("Instructor ID:")
        self.instructor_id_input = QLineEdit()
        form_group_layout.addWidget(instructor_id_label)
        form_group_layout.addWidget(self.instructor_id_input)

        # Add and delete instructor buttons
        add_instructor_button = QPushButton("Add Instructor")
        add_instructor_button.clicked.connect(self.add_instructor)
        form_group_layout.addWidget(add_instructor_button)

        delete_instructor_button = QPushButton("Delete Instructor")
        delete_instructor_button.clicked.connect(self.delete_instructor)
        form_group_layout.addWidget(delete_instructor_button)

        form_group.setLayout(form_group_layout)
        form_layout.addWidget(form_group)

        # Right side: Table to display instructors
        self.instructor_table = QTableWidget()
        self.instructor_table.setColumnCount(5)
        self.instructor_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Instructor ID'])
        self.instructor_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.instructor_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.instructor_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.instructor_table.doubleClicked.connect(self.show_assigned_courses)
        form_layout.addWidget(self.instructor_table)

        layout.addLayout(form_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Instructors:")
        self.instructor_search_input = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_instructors)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.instructor_search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        # Assignment section
        assignment_layout = QVBoxLayout()
        assignment_label = QLabel("Assign Instructor to Course")
        assignment_layout.addWidget(assignment_label)

        assign_form_layout = QHBoxLayout()

        # Instructor ComboBox
        self.assignment_instructor_combo = QComboBox()
        self.update_instructor_options()
        assign_form_layout.addWidget(QLabel("Select Instructor:"))
        assign_form_layout.addWidget(self.assignment_instructor_combo)

        # Course ComboBox
        self.assignment_course_combo = QComboBox()
        self.update_unassigned_course_options()
        assign_form_layout.addWidget(QLabel("Select Course:"))
        assign_form_layout.addWidget(self.assignment_course_combo)

        # Assign button
        assign_button = QPushButton("Assign")
        assign_button.clicked.connect(self.assign_instructor_to_course)
        assign_form_layout.addWidget(assign_button)

        assignment_layout.addLayout(assign_form_layout)
        layout.addLayout(assignment_layout)

        # Set the layout for the instructor tab and refresh the table
        self.instructor_tab.setLayout(layout)
        self.refresh_instructor_table()


    def init_course_tab(self):
        """
        Initializes the course management tab in the `SchoolManagementSystem` UI.

        This method sets up the layout and functionality for managing courses. The tab includes a form for 
        adding and deleting courses, a table for displaying course data, a search bar for filtering courses, 
        and functionality to view enrolled students.

        Layout Details:
        - **Left Side**: A form with inputs for the course ID, course name, and instructor.
        - **Right Side**: A table displaying the course list with columns for ID, Course ID, Course Name, and Instructor.
        - **Search Bar**: Allows searching courses by name or ID.
        - **Add and Delete Buttons**: Buttons to add or delete courses, connected to their respective methods.
        """
        # Layout for the course tab
        layout = QVBoxLayout()
        form_layout = QHBoxLayout()

        # Left side: Form to add courses
        form_group = QWidget()
        form_group_layout = QVBoxLayout()

        # Course ID input
        course_id_label = QLabel("Course ID:")
        self.course_id_input = QLineEdit()
        form_group_layout.addWidget(course_id_label)
        form_group_layout.addWidget(self.course_id_input)

        # Course Name input
        course_name_label = QLabel("Course Name:")
        self.course_name_input = QLineEdit()
        form_group_layout.addWidget(course_name_label)
        form_group_layout.addWidget(self.course_name_input)

        # Instructor input
        instructor_label = QLabel("Instructor:")
        self.course_instructor_combo = QComboBox()
        self.update_course_instructor_options()
        form_group_layout.addWidget(instructor_label)
        form_group_layout.addWidget(self.course_instructor_combo)

        # Add and delete course buttons
        add_course_button = QPushButton("Add Course")
        add_course_button.clicked.connect(self.add_course)
        form_group_layout.addWidget(add_course_button)

        delete_course_button = QPushButton("Delete Course")
        delete_course_button.clicked.connect(self.delete_course)
        form_group_layout.addWidget(delete_course_button)

        form_group.setLayout(form_group_layout)
        form_layout.addWidget(form_group)

        # Right side: Table to display courses
        self.course_table = QTableWidget()
        self.course_table.setColumnCount(4)
        self.course_table.setHorizontalHeaderLabels(['ID', 'Course ID', 'Course Name', 'Instructor'])
        self.course_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.course_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.course_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.course_table.doubleClicked.connect(self.show_enrolled_students)
        form_layout.addWidget(self.course_table)

        layout.addLayout(form_layout)

        # Search bar
        search_layout = QHBoxLayout()
        search_label = QLabel("Search Courses:")
        self.course_search_input = QLineEdit()
        search_button = QPushButton("Search")
        search_button.clicked.connect(self.search_courses)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.course_search_input)
        search_layout.addWidget(search_button)
        layout.addLayout(search_layout)

        self.course_tab.setLayout(layout)
        self.refresh_course_table()


    # ==================== Student Tab Methods ====================

    def add_student(self):
        """
        Adds a new student to the database.

        Retrieves the student's name, age, email, and student ID from the respective input fields,
        validates the inputs, and inserts the new student into the `students` table in the database.
        After adding the student, it refreshes the student table and clears the input fields.

        Raises:
            ValueError: If the age input is not a valid integer.
            sqlite3.IntegrityError: If the student ID or email is not unique.

        Displays:
            - A success message if the student is added successfully.
            - A validation error message if there is an issue with the input.
            - A database error message if there is a uniqueness constraint violation.
        """
        name = self.student_name_input.text()
        age_str = self.student_age_input.text()
        email = self.student_email_input.text()
        student_id = self.student_id_input.text()
        try:
            age = int(age_str)
            student = Student(name, age, email, student_id)
            # Save to database
            self.cursor.execute('''
                INSERT INTO students (name, age, email, student_id)
                VALUES (?, ?, ?, ?)
            ''', (student.name, student.age, student._email, student.student_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Student added to the database.")
            self.refresh_student_table()
            # Clear form fields
            self.student_name_input.clear()
            self.student_age_input.clear()
            self.student_email_input.clear()
            self.student_id_input.clear()
            self.update_student_options()
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Database Error", "Student ID or Email must be unique.")


    def delete_student(self):
        """
        Deletes the selected student from the database.

        Identifies the selected student from the table, deletes them from the `students` table,
        and refreshes the student table afterward.

        Displays:
            - A success message if the student is deleted successfully.
            - An error message if no student is selected.
        """
        selected_rows = self.student_table.selectionModel().selectedRows()
        if selected_rows:
            db_id = int(self.student_table.item(selected_rows[0].row(), 0).text())
            self.cursor.execute('DELETE FROM students WHERE id = ?', (db_id,))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Student deleted.")
            self.refresh_student_table()
            self.update_student_options()
        else:
            QMessageBox.warning(self, "Error", "No student selected.")


    def refresh_student_table(self):
        """
        Refreshes the student table by retrieving all students from the database.

        This method fetches all student records from the `students` table and displays them in the
        student table widget.
        """
        self.student_table.setRowCount(0)
        self.cursor.execute('SELECT id, name, age, email, student_id FROM students')
        students = self.cursor.fetchall()
        for student_row in students:
            row_position = self.student_table.rowCount()
            self.student_table.insertRow(row_position)
            for column, data in enumerate(student_row):
                self.student_table.setItem(row_position, column, QTableWidgetItem(str(data)))


    def search_students(self):
        """
        Searches for students based on the input query.

        Retrieves the search query from the search input, fetches students from the database
        whose name or student ID matches the query, and updates the student table with the results.
        """
        query = self.student_search_input.text()
        self.student_table.setRowCount(0)
        self.cursor.execute('''
            SELECT id, name, age, email, student_id FROM students
            WHERE name LIKE ? OR student_id LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        students = self.cursor.fetchall()
        for student_row in students:
            row_position = self.student_table.rowCount()
            self.student_table.insertRow(row_position)
            for column, data in enumerate(student_row):
                self.student_table.setItem(row_position, column, QTableWidgetItem(str(data)))


    def update_student_options(self):
        """
        Updates the student dropdown options in the registration form.

        Retrieves all students from the `students` table and populates the dropdown
        that allows selecting a student for course registration.
        """
        self.registration_student_combo.clear()
        self.cursor.execute('SELECT id, name FROM students')
        students = self.cursor.fetchall()
        for student in students:
            self.registration_student_combo.addItem(f"{student[0]}: {student[1]}")


    def update_course_options(self):
        """
        Updates the course dropdown options in the registration form.

        Retrieves all courses from the `courses` table and populates the dropdown
        that allows selecting a course for student registration.
        """
        self.registration_course_combo.clear()
        self.cursor.execute('SELECT id, course_name FROM courses')
        courses = self.cursor.fetchall()
        for course in courses:
            self.registration_course_combo.addItem(f"{course[0]}: {course[1]}")


    def register_student_for_course(self):
        """
        Registers a student for a selected course.

        Fetches the selected student and course from the dropdown menus and registers
        the student for the course in the `registrations` table.

        Raises:
            sqlite3.IntegrityError: If the student is already registered for the course.

        Displays:
            - A success message if registration is successful.
            - An error message if the student is already registered for the course or if another error occurs.
        """
        student_info = self.registration_student_combo.currentText()
        course_info = self.registration_course_combo.currentText()
        try:
            student_db_id = int(student_info.split(':')[0])
            course_db_id = int(course_info.split(':')[0])
            self.cursor.execute('''
                INSERT INTO registrations (student_id, course_id)
                VALUES (?, ?)
            ''', (student_db_id, course_db_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Student registered for course.")
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Error", "Student is already registered for this course.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def show_student_courses(self):
        """
        Displays the courses that a selected student is registered in.

        When a student is selected from the student table, this method fetches the courses
        they are registered for from the `registrations` table and displays them in a dialog.

        Displays:
            - A dialog showing the courses the selected student is enrolled in.
            - An error message if no student is selected.
        """
        selected_rows = self.student_table.selectionModel().selectedRows()
        if selected_rows:
            db_id = int(self.student_table.item(selected_rows[0].row(), 0).text())
            self.cursor.execute('''
                SELECT courses.id, courses.course_id, courses.course_name
                FROM registrations
                JOIN courses ON registrations.course_id = courses.id
                WHERE registrations.student_id = ?
            ''', (db_id,))
            courses = self.cursor.fetchall()
            # Display the courses in a new dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Enrolled Courses")
            layout = QVBoxLayout()
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(['ID', 'Course ID', 'Course Name'])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setRowCount(len(courses))
            for row_num, course in enumerate(courses):
                for col_num, data in enumerate(course):
                    table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            layout.addWidget(table)
            dialog.setLayout(layout)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No student selected.")


    # ==================== Instructor Tab Methods ====================

    def add_instructor(self):
        """
        Adds a new instructor to the database.

        Retrieves the instructor's name, age, email, and instructor ID from the respective input fields,
        validates the inputs, and inserts the new instructor into the `instructors` table in the database.
        After adding the instructor, it refreshes the instructor table and clears the input fields.

        Raises:
            ValueError: If the age input is not a valid integer.
            sqlite3.IntegrityError: If the instructor ID or email is not unique.

        Displays:
            - A success message if the instructor is added successfully.
            - A validation error message if there is an issue with the input.
            - A database error message if there is a uniqueness constraint violation.
        """
        name = self.instructor_name_input.text()
        age_str = self.instructor_age_input.text()
        email = self.instructor_email_input.text()
        instructor_id = self.instructor_id_input.text()
        try:
            age = int(age_str)
            instructor = Instructor(name, age, email, instructor_id)
            # Save to database
            self.cursor.execute('''
                INSERT INTO instructors (name, age, email, instructor_id)
                VALUES (?, ?, ?, ?)
            ''', (instructor.name, instructor.age, instructor._email, instructor.instructor_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Instructor added to the database.")
            self.refresh_instructor_table()
            # Clear form fields
            self.instructor_name_input.clear()
            self.instructor_age_input.clear()
            self.instructor_email_input.clear()
            self.instructor_id_input.clear()
            self.update_instructor_options()
            self.update_course_instructor_options()
        except ValueError as ve:
            QMessageBox.warning(self, "Validation Error", str(ve))
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Database Error", "Instructor ID or Email must be unique.")


    def delete_instructor(self):
        """
        Deletes the selected instructor from the database.

        Identifies the selected instructor from the table, deletes them from the `instructors` table,
        and refreshes the instructor table afterward.

        Displays:
            - A success message if the instructor is deleted successfully.
            - An error message if no instructor is selected.
        """
        selected_rows = self.instructor_table.selectionModel().selectedRows()
        if selected_rows:
            db_id = int(self.instructor_table.item(selected_rows[0].row(), 0).text())
            self.cursor.execute('DELETE FROM instructors WHERE id = ?', (db_id,))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Instructor deleted.")
            self.refresh_instructor_table()
            self.update_instructor_options()
            self.update_course_instructor_options()
        else:
            QMessageBox.warning(self, "Error", "No instructor selected.")


    def refresh_instructor_table(self):
        """
        Refreshes the instructor table by retrieving all instructors from the database.

        This method fetches all instructor records from the `instructors` table and displays them
        in the instructor table widget.
        """
        self.instructor_table.setRowCount(0)
        self.cursor.execute('SELECT id, name, age, email, instructor_id FROM instructors')
        instructors = self.cursor.fetchall()
        for instructor_row in instructors:
            row_position = self.instructor_table.rowCount()
            self.instructor_table.insertRow(row_position)
            for column, data in enumerate(instructor_row):
                self.instructor_table.setItem(row_position, column, QTableWidgetItem(str(data)))


    def search_instructors(self):
        """
        Searches for instructors based on the input query.

        Retrieves the search query from the search input, fetches instructors from the database
        whose name or instructor ID matches the query, and updates the instructor table with the results.
        """
        query = self.instructor_search_input.text()
        self.instructor_table.setRowCount(0)
        self.cursor.execute('''
            SELECT id, name, age, email, instructor_id FROM instructors
            WHERE name LIKE ? OR instructor_id LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        instructors = self.cursor.fetchall()
        for instructor_row in instructors:
            row_position = self.instructor_table.rowCount()
            self.instructor_table.insertRow(row_position)
            for column, data in enumerate(instructor_row):
                self.instructor_table.setItem(row_position, column, QTableWidgetItem(str(data)))


    def update_instructor_options(self):
        """
        Updates the instructor dropdown options for course assignment.

        Retrieves all instructors from the `instructors` table and populates the dropdown
        that allows selecting an instructor for course assignment.
        """
        self.assignment_instructor_combo.clear()
        self.cursor.execute('SELECT id, name FROM instructors')
        instructors = self.cursor.fetchall()
        for instructor in instructors:
            self.assignment_instructor_combo.addItem(f"{instructor[0]}: {instructor[1]}")


    def update_unassigned_course_options(self):
        """
        Updates the course dropdown options for instructor assignment.

        Retrieves all courses from the `courses` table that do not have an assigned instructor,
        and populates the dropdown that allows selecting a course for assignment.
        """
        self.assignment_course_combo.clear()
        self.cursor.execute('SELECT id, course_name FROM courses WHERE instructor_id IS NULL')
        courses = self.cursor.fetchall()
        for course in courses:
            self.assignment_course_combo.addItem(f"{course[0]}: {course[1]}")


    def assign_instructor_to_course(self):
        """
        Assigns an instructor to a selected course.

        Fetches the selected instructor and course from the dropdown menus and updates the
        `courses` table to assign the selected instructor to the selected course.

        Displays:
            - A success message if the assignment is successful.
            - An error message if an exception occurs.
        """
        instructor_info = self.assignment_instructor_combo.currentText()
        course_info = self.assignment_course_combo.currentText()
        try:
            instructor_db_id = int(instructor_info.split(':')[0])
            course_db_id = int(course_info.split(':')[0])
            self.cursor.execute('''
                UPDATE courses SET instructor_id = ? WHERE id = ?
            ''', (instructor_db_id, course_db_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Instructor assigned to course.")
            self.refresh_course_table()
            self.update_unassigned_course_options()
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def show_assigned_courses(self):
        """
        Displays the courses assigned to a selected instructor.

        When an instructor is selected from the instructor table, this method fetches the courses
        they are assigned to from the `courses` table and displays them in a dialog.

        Displays:
            - A dialog showing the courses the selected instructor is assigned to.
            - An error message if no instructor is selected.
        """
        selected_rows = self.instructor_table.selectionModel().selectedRows()
        if selected_rows:
            db_id = int(self.instructor_table.item(selected_rows[0].row(), 0).text())
            self.cursor.execute('''
                SELECT courses.id, courses.course_id, courses.course_name
                FROM courses
                WHERE instructor_id = ?
            ''', (db_id,))
            courses = self.cursor.fetchall()
            # Display the courses in a new dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Assigned Courses")
            layout = QVBoxLayout()
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(['ID', 'Course ID', 'Course Name'])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setRowCount(len(courses))
            for row_num, course in enumerate(courses):
                for col_num, data in enumerate(course):
                    table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            layout.addWidget(table)
            dialog.setLayout(layout)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No instructor selected.")


    # ==================== Course Tab Methods ====================

    def add_course(self):
        """
        Adds a new course to the database.

        Retrieves the course ID, course name, and optionally the instructor from the input fields.
        Inserts the course into the `courses` table and assigns an instructor if specified.
        
        Clears the input fields and refreshes the course table after a successful operation.

        Raises:
            - sqlite3.IntegrityError: If the course ID is not unique.
            - Exception: Handles any other database-related errors.
        """
        course_id = self.course_id_input.text()
        course_name = self.course_name_input.text()
        instructor_info = self.course_instructor_combo.currentText()
        try:
            if instructor_info and instructor_info != 'None':
                instructor_db_id = int(instructor_info.split(':')[0])
                self.cursor.execute('SELECT id FROM instructors WHERE id = ?', (instructor_db_id,))
                if self.cursor.fetchone() is None:
                    QMessageBox.warning(self, "Error", "Selected instructor does not exist.")
                    return
            else:
                instructor_db_id = None
            course = Course(course_id, course_name)
            # Save to database
            self.cursor.execute('''
                INSERT INTO courses (course_id, course_name, instructor_id)
                VALUES (?, ?, ?)
            ''', (course.course_id, course.course_name, instructor_db_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Course added to the database.")
            self.refresh_course_table()
            # Clear form fields
            self.course_id_input.clear()
            self.course_name_input.clear()
            self.course_instructor_combo.setCurrentIndex(0)
            self.update_course_options()
            self.update_unassigned_course_options()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "Database Error", "Course ID must be unique.")
        except Exception as e:
            QMessageBox.warning(self, "Error", str(e))


    def delete_course(self):
        """
        Deletes the selected course from the database.

        Identifies the selected course in the course table and deletes it from the `courses` table.
        
        Refreshes the course table and updates the course and instructor options.
        
        Displays:
            - A success message if the course is deleted successfully.
            - An error message if no course is selected.
        """
        selected_rows = self.course_table.selectionModel().selectedRows()
        if selected_rows:
            db_id = int(self.course_table.item(selected_rows[0].row(), 0).text())
            self.cursor.execute('DELETE FROM courses WHERE id = ?', (db_id,))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Course deleted.")
            self.refresh_course_table()
            self.update_course_options()
            self.update_unassigned_course_options()
        else:
            QMessageBox.warning(self, "Error", "No course selected.")


    def refresh_course_table(self):
        """
        Refreshes the course table by retrieving all courses from the database.

        Fetches courses from the `courses` table, including the associated instructor, and displays them in the course table.
        """
        self.course_table.setRowCount(0)
        self.cursor.execute('''
            SELECT courses.id, courses.course_id, courses.course_name, IFNULL(instructors.name, 'None')
            FROM courses
            LEFT JOIN instructors ON courses.instructor_id = instructors.id
        ''')
        courses = self.cursor.fetchall()
        for course_row in courses:
            row_position = self.course_table.rowCount()
            self.course_table.insertRow(row_position)
            for column, data in enumerate(course_row):
                self.course_table.setItem(row_position, column, QTableWidgetItem(str(data)))


    def search_courses(self):
        """
        Searches for courses based on the input query.

        Fetches courses whose name or course ID matches the query from the database and updates the course table with the results.
        """
        query = self.course_search_input.text()
        self.course_table.setRowCount(0)
        self.cursor.execute('''
            SELECT courses.id, courses.course_id, courses.course_name, IFNULL(instructors.name, 'None')
            FROM courses
            LEFT JOIN instructors ON courses.instructor_id = instructors.id
            WHERE courses.course_name LIKE ? OR courses.course_id LIKE ?
        ''', (f'%{query}%', f'%{query}%'))
        courses = self.cursor.fetchall()
        for course_row in courses:
            row_position = self.course_table.rowCount()
            self.course_table.insertRow(row_position)
            for column, data in enumerate(course_row):
                self.course_table.setItem(row_position, column, QTableWidgetItem(str(data)))


    def update_course_instructor_options(self):
        """
        Updates the instructor options in the course form.

        Retrieves all instructors from the `instructors` table and populates the dropdown menu for selecting a course instructor.
        """
        self.course_instructor_combo.clear()
        self.course_instructor_combo.addItem('None')
        self.cursor.execute('SELECT id, name FROM instructors')
        instructors = self.cursor.fetchall()
        for instructor in instructors:
            self.course_instructor_combo.addItem(f"{instructor[0]}: {instructor[1]}")


    def show_enrolled_students(self):
        """
        Displays students enrolled in a selected course.

        Retrieves students registered for the selected course from the `registrations` table
        and displays the list in a new dialog window.
        """
        selected_rows = self.course_table.selectionModel().selectedRows()
        if selected_rows:
            db_id = int(self.course_table.item(selected_rows[0].row(), 0).text())
            self.cursor.execute('''
                SELECT students.id, students.name, students.student_id
                FROM registrations
                JOIN students ON registrations.student_id = students.id
                WHERE registrations.course_id = ?
            ''', (db_id,))
            students = self.cursor.fetchall()
            # Display the students in a new dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Enrolled Students")
            layout = QVBoxLayout()
            table = QTableWidget()
            table.setColumnCount(3)
            table.setHorizontalHeaderLabels(['ID', 'Name', 'Student ID'])
            table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            table.setRowCount(len(students))
            for row_num, student in enumerate(students):
                for col_num, data in enumerate(student):
                    table.setItem(row_num, col_num, QTableWidgetItem(str(data)))
            layout.addWidget(table)
            dialog.setLayout(layout)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Error", "No course selected.")


    def load_database(self):
        """
        Loads a backup of the database from CSV files.

        Prompts the user to select a folder containing backup CSV files, loads the data from the
        `students`, `instructors`, `courses`, and `registrations` tables, and restores the data into the database.
        
        It first deletes existing data, then imports the backup data. A confirmation is required before proceeding.
        
        Displays:
            - A success message if the database is loaded successfully.
            - An error message if any issues arise during the process.
        """
        try:
            folder_path = QFileDialog.getExistingDirectory(self, "Select Backup Folder")
            if folder_path:
                students_csv = os.path.join(folder_path, 'students_backup.csv')
                instructors_csv = os.path.join(folder_path, 'instructors_backup.csv')
                courses_csv = os.path.join(folder_path, 'courses_backup.csv')
                registrations_csv = os.path.join(folder_path, 'registrations_backup.csv')

                if not all(os.path.exists(f) for f in [students_csv, instructors_csv, courses_csv, registrations_csv]):
                    QMessageBox.critical(self, "Error", "Backup files not found in the selected folder.")
                    return

                students_df = pd.read_csv(students_csv)
                instructors_df = pd.read_csv(instructors_csv)
                courses_df = pd.read_csv(courses_csv)
                registrations_df = pd.read_csv(registrations_csv)

                confirm = QMessageBox.question(
                    self, "Confirm Load",
                    "Loading a backup will overwrite existing data. Do you want to continue?",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if confirm != QMessageBox.Yes:
                    return

                self.conn.execute("BEGIN TRANSACTION;")
                self.conn.execute("PRAGMA foreign_keys = OFF;")

                self.cursor.execute("DELETE FROM registrations;")
                self.cursor.execute("DELETE FROM courses;")
                self.cursor.execute("DELETE FROM instructors;")
                self.cursor.execute("DELETE FROM students;")
                self.conn.commit()

                self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='students';")
                self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='instructors';")
                self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='courses';")
                self.cursor.execute("DELETE FROM sqlite_sequence WHERE name='registrations';")
                self.conn.commit()

                instructors_df.to_sql('instructors', self.conn, if_exists='append', index=False)
                courses_df.to_sql('courses', self.conn, if_exists='append', index=False)
                students_df.to_sql('students', self.conn, if_exists='append', index=False)
                registrations_df.to_sql('registrations', self.conn, if_exists='append', index=False)

                self.conn.execute("PRAGMA foreign_keys = ON;")
                self.conn.commit()

                self.refresh_instructor_table()
                self.refresh_course_table()
                self.refresh_student_table()

                QMessageBox.information(self, "Success", "Database loaded from backup.")
        except Exception as e:
            self.conn.rollback()
            QMessageBox.critical(self, "Error", f"An error occurred while loading the database: {str(e)}")


    def closeEvent(self, event):
        """
        Closes the database connection when the application window is closed.
        
        Ensures that the connection to the SQLite database is properly closed when the application exits.
        """
        self.conn.close()
        event.accept()

# ==================== Run the Application ====================

def main():
    app = QApplication(sys.argv)
    window = SchoolManagementSystem()
    window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
