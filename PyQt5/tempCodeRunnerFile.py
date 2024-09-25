import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

class SchoolManagementApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("School Management System")
        self.geometry("600x400")
        self.db_connection = None
        self.db_cursor = None
        self.setup_database()
        
        # Set up the tabs
        self.tab_control = ttk.Notebook(self)
        self.tab_control.pack(expand=1, fill="both")

        self.tab_add_student = ttk.Frame(self.tab_control)
        self.tab_add_instructor = ttk.Frame(self.tab_control)
        self.tab_add_course = ttk.Frame(self.tab_control)
        self.tab_register_course = ttk.Frame(self.tab_control)
        self.tab_view_all = ttk.Frame(self.tab_control)

        self.tab_control.add(self.tab_add_student, text="Add Student")
        self.tab_control.add(self.tab_add_instructor, text="Add Instructor")
        self.tab_control.add(self.tab_add_course, text="Add Course")
        self.tab_control.add(self.tab_register_course, text="Register for Course")
        self.tab_control.add(self.tab_view_all, text="View All")

        # Create widgets for each tab
        self.create_widgets_for_add_student()
        self.create_widgets_for_add_instructor()
        self.create_widgets_for_add_course()
        self.create_widgets_for_register_course()
        self.create_widgets_for_view_all()

    def get_db_connection(self):
        if not self.db_connection:
            self.db_connection = sqlite3.connect('school_management.db')
            self.db_cursor = self.db_connection.cursor()
        return self.db_connection

    def setup_database(self):
        conn = self.get_db_connection()
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL,
                student_id TEXT NOT NULL UNIQUE
            )
        """)
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS instructors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                email TEXT NOT NULL,
                instructor_id TEXT NOT NULL UNIQUE
            )
        """)
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS courses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                course_id TEXT NOT NULL UNIQUE,
                course_name TEXT NOT NULL,
                instructor_id TEXT NOT NULL,
                FOREIGN KEY (instructor_id) REFERENCES instructors (instructor_id)
            )
        """)
        self.db_cursor.execute("""
            CREATE TABLE IF NOT EXISTS registrations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                course_id TEXT NOT NULL,
                FOREIGN KEY (student_id) REFERENCES students (student_id),
                FOREIGN KEY (course_id) REFERENCES courses (course_id)
            )
        """)
        conn.commit()

    def create_widgets_for_add_student(self):
        tk.Label(self.tab_add_student, text="Name:").pack()
        self.student_name_entry = tk.Entry(self.tab_add_student)
        self.student_name_entry.pack()

        tk.Label(self.tab_add_student, text="Age:").pack()
        self.student_age_entry = tk.Entry(self.tab_add_student)
        self.student_age_entry.pack()

        tk.Label(self.tab_add_student, text="Email:").pack()
        self.student_email_entry = tk.Entry(self.tab_add_student)
        self.student_email_entry.pack()

        tk.Label(self.tab_add_student, text="Student ID:").pack()
        self.student_id_entry = tk.Entry(self.tab_add_student)
        self.student_id_entry.pack()

        tk.Button(self.tab_add_student, text="Add Student", command=self.add_student).pack()

    def create_widgets_for_add_instructor(self):
        tk.Label(self.tab_add_instructor, text="Name:").pack()
        self.instructor_name_entry = tk.Entry(self.tab_add_instructor)
        self.instructor_name_entry.pack()

        tk.Label(self.tab_add_instructor, text="Age:").pack()
        self.instructor_age_entry = tk.Entry(self.tab_add_instructor)
        self.instructor_age_entry.pack()

        tk.Label(self.tab_add_instructor, text="Email:").pack()
        self.instructor_email_entry = tk.Entry(self.tab_add_instructor)
        self.instructor_email_entry.pack()

        tk.Label(self.tab_add_instructor, text="Instructor ID:").pack()
        self.instructor_id_entry = tk.Entry(self.tab_add_instructor)
        self.instructor_id_entry.pack()

        tk.Button(self.tab_add_instructor, text="Add Instructor", command=self.add_instructor).pack()

    def create_widgets_for_add_course(self):
        tk.Label(self.tab_add_course, text="Course ID:").pack()
        self.course_id_entry = tk.Entry(self.tab_add_course)
        self.course_id_entry.pack()

        tk.Label(self.tab_add_course, text="Course Name:").pack()
        self.course_name_entry = tk.Entry(self.tab_add_course)
        self.course_name_entry.pack()

        tk.Label(self.tab_add_course, text="Instructor ID:").pack()
        self.course_instructor_id_entry = tk.Entry(self.tab_add_course)
        self.course_instructor_id_entry.pack()

        tk.Button(self.tab_add_course, text="Add Course", command=self.add_course).pack()

    def create_widgets_for_register_course(self):
        tk.Label(self.tab_register_course, text="Select Student:").pack()
        self.student_dropdown = ttk.Combobox(self.tab_register_course)
        self.student_dropdown.pack()

        tk.Label(self.tab_register_course, text="Select Course:").pack()
        self.course_dropdown = ttk.Combobox(self.tab_register_course)
        self.course_dropdown.pack()

        tk.Button(self.tab_register_course, text="Register", command=self.register_for_course).pack()
        self.refresh_dropdowns()

    def create_widgets_for_view_all(self):
        self.view_all_table = ttk.Treeview(self.tab_view_all, columns=("ID", "Name", "Age", "Email", "Additional Info"), show="headings")
        self.view_all_table.heading("ID", text="ID")
        self.view_all_table.heading("Name", text="Name")
        self.view_all_table.heading("Age", text="Age")
        self.view_all_table.heading("Email", text="Email")
        self.view_all_table.heading("Additional Info", text="Additional Info")
        self.view_all_table.pack(expand=1, fill="both")

        tk.Button(self.tab_view_all, text="Refresh", command=self.refresh_view_all).pack()
        tk.Button(self.tab_view_all, text="Export to CSV", command=self.export_to_csv).pack()

    def refresh_dropdowns(self):
        conn = self.get_db_connection()
        self.db_cursor.execute("SELECT name FROM students")
        students = [row[0] for row in self.db_cursor.fetchall()]
        self.student_dropdown['values'] = students

        self.db_cursor.execute("SELECT course_name FROM courses")
        courses = [row[0] for row in self.db_cursor.fetchall()]
        self.course_dropdown['values'] = courses

    def add_student(self):
        name = self.student_name_entry.get()
        age = int(self.student_age_entry.get())
        email = self.student_email_entry.get()
        student_id = self.student_id_entry.get()

        try:
            conn = self.get_db_connection()
            self.db_cursor.execute("""
                INSERT INTO students (name, age, email, student_id)
                VALUES (?, ?, ?, ?)
            """, (name, age, email, student_id))
            conn.commit()
            messagebox.showinfo("Success", "Student added successfully")
            self.clear_student_inputs()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding student: {e}")

    def add_instructor(self):
        name = self.instructor_name_entry.get()
        age = int(self.instructor_age_entry.get())
        email = self.instructor_email_entry.get()
        instructor_id = self.instructor_id_entry.get()

        try:
            conn = self.get_db_connection()
            self.db_cursor.execute("""
                INSERT INTO instructors (name, age, email, instructor_id)
                VALUES (?, ?, ?, ?)
            """, (name, age, email, instructor_id))
            conn.commit()
            messagebox.showinfo("Success", "Instructor added successfully")
            self.clear_instructor_inputs()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding instructor: {e}")

    def add_course(self):
        course_id = self.course_id_entry.get()
        course_name = self.course_name_entry.get()
        instructor_id = self.course_instructor_id_entry.get()

        try:
            conn = self.get_db_connection()
            self.db_cursor.execute("""
                INSERT INTO courses (course_id, course_name, instructor_id)
                VALUES (?, ?, ?)
            """, (course_id, course_name, instructor_id))
            conn.commit()
            messagebox.showinfo("Success", "Course added successfully")
            self.clear_course_inputs()
            self.refresh_dropdowns()
        except Exception as e:
            messagebox.showerror("Error", f"Error adding course: {e}")

    def register_for_course(self):
        student_name = self.student_dropdown.get()
        course_name = self.course_dropdown.get()

        try:
            conn = self.get_db_connection()
            self.db_cursor.execute("SELECT student_id FROM students WHERE name = ?", (student_name,))
            student_id = self.db_cursor.fetchone()[0]

            self.db_cursor.execute("SELECT course_id FROM courses WHERE course_name = ?", (course_name,))
            course_id = self.db_cursor.fetchone()[0]

            self.db_cursor.execute("""
                INSERT INTO registrations (student_id, course_id)
                VALUES (?, ?)
            """, (student_id, course_id))
            conn.commit()
            messagebox.showinfo("Success", "Student registered for course successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error registering course: {e}")

    def refresh_view_all(self):
        self.view_all_table.delete(*self.view_all_table.get_children())

        try:
            conn = self.get_db_connection()

            self.db_cursor.execute("SELECT * FROM students")
            students = self.db_cursor.fetchall()

            self.db_cursor.execute("SELECT * FROM instructors")
            instructors = self.db_cursor.fetchall()

            self.db_cursor.execute("SELECT * FROM courses")
            courses = self.db_cursor.fetchall()

            for record in students:
                self.view_all_table.insert("", "end", values=(*record, "Student"))

            for record in instructors:
                self.view_all_table.insert("", "end", values=(*record, "Instructor"))

            for record in courses:
                self.view_all_table.insert("", "end", values=(*record, "Course"))

            messagebox.showinfo("Success", "Data refreshed successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error refreshing data: {e}")

    def export_to_csv(self):
        try:
            filename = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
            if filename:
                with open(filename, 'w', newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Name", "Age", "Email", "Additional Info"])
                    for row in self.view_all_table.get_children():
                        row_data = self.view_all_table.item(row, 'values')
                        writer.writerow(row_data)
                messagebox.showinfo("Success", "Data exported successfully")
        except Exception as e:
            messagebox.showerror("Error", f"Error exporting data: {e}")

    def clear_student_inputs(self):
        self.student_name_entry.delete(0, tk.END)
        self.student_age_entry.delete(0, tk.END)
        self.student_email_entry.delete(0, tk.END)
        self.student_id_entry.delete(0, tk.END)

    def clear_instructor_inputs(self):
        self.instructor_name_entry.delete(0, tk.END)
        self.instructor_age_entry.delete(0, tk.END)
        self.instructor_email_entry.delete(0, tk.END)
        self.instructor_id_entry.delete(0, tk.END)

    def clear_course_inputs(self):
        self.course_id_entry.delete(0, tk.END)
        self.course_name_entry.delete(0, tk.END)
        self.course_instructor_id_entry.delete(0, tk.END)


if __name__ == "__main__":
    app = SchoolManagementApp()
    app.mainloop()
