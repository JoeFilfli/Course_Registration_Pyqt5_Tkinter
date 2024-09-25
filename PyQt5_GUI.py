import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QTabWidget, 
                             QComboBox, QMessageBox, QFileDialog, QFormLayout)
from PyQt5.QtCore import Qt
import sqlite3
import csv

class SchoolManagementApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("School Management System")
        self.setGeometry(100, 100, 800, 600)
        self.db_connection = None
        self.cursor = None
        self.setup_database()

        # Setup Tabs
        self.tab_widget = QTabWidget()
        self.setCentralWidget(self.tab_widget)

        self.student_tab = QWidget()
        self.instructor_tab = QWidget()
        self.course_tab = QWidget()
        self.registration_tab = QWidget()
        self.view_tab = QWidget()

        self.tab_widget.addTab(self.student_tab, "Add Student")
        self.tab_widget.addTab(self.instructor_tab, "Add Instructor")
        self.tab_widget.addTab(self.course_tab, "Add Course")
        self.tab_widget.addTab(self.registration_tab, "Register for Course")
        self.tab_widget.addTab(self.view_tab, "View All")

        self.initialize_student_widgets()
        self.initialize_instructor_widgets()
        self.initialize_course_widgets()
        self.initialize_registration_widgets()
        self.initialize_view_widgets()

    def get_database_connection(self):
        if not self.db_connection:
            self.db_connection = sqlite3.connect('school.db')
            self.cursor = self.db_connection.cursor()
        return self.db_connection

    def setup_database(self):
        conn = self.get_database_connection()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            student_id TEXT NOT NULL UNIQUE
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS instructors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            age INTEGER NOT NULL,
            email TEXT NOT NULL,
            instructor_id TEXT NOT NULL UNIQUE
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS courses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course_id TEXT NOT NULL UNIQUE,
            course_name TEXT NOT NULL,
            instructor_id TEXT NOT NULL,
            FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id)
        )""")
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS registrations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            course_id TEXT NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students (student_id),
            FOREIGN KEY (course_id) REFERENCES courses (course_id)
        )""")
        conn.commit()

    def initialize_student_widgets(self):
        layout = QFormLayout()
        self.student_name_input = QLineEdit()
        self.student_age_input = QLineEdit()
        self.student_email_input = QLineEdit()
        self.student_id_input = QLineEdit()

        layout.addRow(QLabel("Name:"), self.student_name_input)
        layout.addRow(QLabel("Age:"), self.student_age_input)
        layout.addRow(QLabel("Email:"), self.student_email_input)
        layout.addRow(QLabel("Student ID:"), self.student_id_input)

        add_btn = QPushButton("Add Student")
        add_btn.clicked.connect(self.add_student_record)
        layout.addWidget(add_btn)

        self.student_tab.setLayout(layout)

    def initialize_instructor_widgets(self):
        layout = QFormLayout()
        self.instructor_name_input = QLineEdit()
        self.instructor_age_input = QLineEdit()
        self.instructor_email_input = QLineEdit()
        self.instructor_id_input = QLineEdit()

        layout.addRow(QLabel("Name:"), self.instructor_name_input)
        layout.addRow(QLabel("Age:"), self.instructor_age_input)
        layout.addRow(QLabel("Email:"), self.instructor_email_input)
        layout.addRow(QLabel("Instructor ID:"), self.instructor_id_input)

        add_btn = QPushButton("Add Instructor")
        add_btn.clicked.connect(self.add_instructor_record)
        layout.addWidget(add_btn)

        self.instructor_tab.setLayout(layout)

    def initialize_course_widgets(self):
        layout = QFormLayout()
        self.course_id_input = QLineEdit()
        self.course_name_input = QLineEdit()
        self.course_instructor_id_input = QLineEdit()

        layout.addRow(QLabel("Course ID:"), self.course_id_input)
        layout.addRow(QLabel("Course Name:"), self.course_name_input)
        layout.addRow(QLabel("Instructor ID:"), self.course_instructor_id_input)

        add_btn = QPushButton("Add Course")
        add_btn.clicked.connect(self.add_course_record)
        layout.addWidget(add_btn)

        self.course_tab.setLayout(layout)

    def initialize_registration_widgets(self):
        layout = QFormLayout()
        self.student_selector = QComboBox()
        self.course_selector = QComboBox()

        layout.addRow(QLabel("Select Student:"), self.student_selector)
        layout.addRow(QLabel("Select Course:"), self.course_selector)

        register_btn = QPushButton("Register")
        register_btn.clicked.connect(self.register_student_for_course)
        layout.addWidget(register_btn)

        self.registration_tab.setLayout(layout)
        self.update_dropdowns()

    def initialize_view_widgets(self):
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(5)
        self.data_table.setHorizontalHeaderLabels(['ID', 'Name', 'Age', 'Email', 'Additional Info'])
        self.data_table.horizontalHeader().setStretchLastSection(True)

        layout = QVBoxLayout()
        layout.addWidget(self.data_table)

        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_table_view)
        layout.addWidget(refresh_btn)

        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.save_to_csv)
        layout.addWidget(export_btn)

        self.view_tab.setLayout(layout)

    def update_dropdowns(self):
        conn = self.get_database_connection()

        self.cursor.execute("SELECT name FROM students")
        students = [row[0] for row in self.cursor.fetchall()]
        self.student_selector.addItems(students)

        self.cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in self.cursor.fetchall()]
        self.course_selector.addItems(courses)

    def add_student_record(self):
        name = self.student_name_input.text()
        age = int(self.student_age_input.text())
        email = self.student_email_input.text()
        student_id = self.student_id_input.text()

        try:
            conn = self.get_database_connection()
            self.cursor.execute("""INSERT INTO students (name, age, email, student_id)
                                  VALUES (?, ?, ?, ?)""", (name, age, email, student_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Student added successfully")
            self.clear_student_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding student: {e}")

    def add_instructor_record(self):
        name = self.instructor_name_input.text()
        age = int(self.instructor_age_input.text())
        email = self.instructor_email_input.text()
        instructor_id = self.instructor_id_input.text()

        try:
            conn = self.get_database_connection()
            self.cursor.execute("""INSERT INTO instructors (name, age, email, instructor_id)
                                  VALUES (?, ?, ?, ?)""", (name, age, email, instructor_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Instructor added successfully")
            self.clear_instructor_inputs()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding instructor: {e}")

    def add_course_record(self):
        course_id = self.course_id_input.text()
        course_name = self.course_name_input.text()
        instructor_id = self.course_instructor_id_input.text()

        try:
            conn = self.get_database_connection()
            self.cursor.execute("""INSERT INTO courses (course_id, course_name, instructor_id)
                                  VALUES (?, ?, ?)""", (course_id, course_name, instructor_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Course added successfully")
            self.clear_course_inputs()
            self.update_dropdowns()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error adding course: {e}")

    def register_student_for_course(self):
        student_name = self.student_selector.currentText()
        course_name = self.course_selector.currentText()

        try:
            conn = self.get_database_connection()
            self.cursor.execute("SELECT student_id FROM students WHERE name = ?", (student_name,))
            student_id = self.cursor.fetchone()[0]

            self.cursor.execute("SELECT course_id FROM courses WHERE course_name = ?", (course_name,))
            course_id = self.cursor.fetchone()[0]

            self.cursor.execute("""INSERT INTO registrations (student_id, course_id)
                                  VALUES (?, ?)""", (student_id, course_id))
            conn.commit()
            QMessageBox.information(self, "Success", "Student registered for course successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error registering student: {e}")

    def refresh_table_view(self):
        self.data_table.setRowCount(0)

        try:
            conn = self.get_database_connection()

            self.cursor.execute("SELECT * FROM students")
            students = self.cursor.fetchall()

            self.cursor.execute("SELECT * FROM instructors")
            instructors = self.cursor.fetchall()

            self.cursor.execute("SELECT * FROM courses")
            courses = self.cursor.fetchall()

            for record in students:
                self.data_table.insertRow(self.data_table.rowCount())
                for i, value in enumerate(record):
                    self.data_table.setItem(self.data_table.rowCount() - 1, i, QTableWidgetItem(str(value)))
                self.data_table.setItem(self.data_table.rowCount() - 1, 4, QTableWidgetItem("Student"))

            for record in instructors:
                self.data_table.insertRow(self.data_table.rowCount())
                for i, value in enumerate(record):
                    self.data_table.setItem(self.data_table.rowCount() - 1, i, QTableWidgetItem(str(value)))
                self.data_table.setItem(self.data_table.rowCount() - 1, 4, QTableWidgetItem("Instructor"))

            for record in courses:
                self.data_table.insertRow(self.data_table.rowCount())
                for i, value in enumerate(record):
                    self.data_table.setItem(self.data_table.rowCount() - 1, i, QTableWidgetItem(str(value)))
                self.data_table.setItem(self.data_table.rowCount() - 1, 4, QTableWidgetItem("Course"))

            QMessageBox.information(self, "Success", "Data refreshed successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing data: {e}")

    def save_to_csv(self):
        try:
            filename = QFileDialog.getSaveFileName(self, "Save CSV", '', "CSV Files (*.csv)")[0]
            if filename:
                with open(filename, 'w', newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Name", "Age", "Email", "Additional Info"])
                    for row in range(self.data_table.rowCount()):
                        row_data = [self.data_table.item(row, col).text() for col in range(self.data_table.columnCount())]
                        writer.writerow(row_data)
                QMessageBox.information(self, "Success", "Data exported successfully")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error exporting data: {e}")

    def clear_student_inputs(self):
        self.student_name_input.clear()
        self.student_age_input.clear()
        self.student_email_input.clear()
        self.student_id_input.clear()

    def clear_instructor_inputs(self):
        self.instructor_name_input.clear()
        self.instructor_age_input.clear()
        self.instructor_email_input.clear()
        self.instructor_id_input.clear()

    def clear_course_inputs(self):
        self.course_id_input.clear()
        self.course_name_input.clear()
        self.course_instructor_id_input.clear()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SchoolManagementApp()
    window.show()
    sys.exit(app.exec_())
