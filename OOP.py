import json
import re

# Helper function for email validation
def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(pattern, email)

# Helper function for non-negative age validation
def is_valid_age(age):
    return isinstance(age, int) and age >= 0

# Person class definition
class Person:
    def __init__(self, name, age, email):
        if not is_valid_age(age):
            raise ValueError("Age must be a non-negative integer.")
        if not is_valid_email(email):
            raise ValueError("Invalid email format.")
        self.name = name
        self.age = age
        self._email = email  # Private email attribute

    def introduce(self):
        print(f"Hello, my name is {self.name}, and I am {self.age} years old.")

# Student subclass definition
class Student(Person):
    def __init__(self, name, age, email, student_id):
        super().__init__(name, age, email)
        self.student_id = student_id
        self.registered_courses = []

    def enroll_in_course(self, course):
        if isinstance(course, Course):
            self.registered_courses.append(course)
            course.add_student(self)
        else:
            raise ValueError("Invalid course object.")

# Instructor subclass definition
class Instructor(Person):
    def __init__(self, name, age, email, instructor_id):
        super().__init__(name, age, email)
        self.instructor_id = instructor_id
        self.assigned_courses = []

    def assign_course(self, course):
        if isinstance(course, Course):
            self.assigned_courses.append(course)
        else:
            raise ValueError("Invalid course object.")

# Course class definition
class Course:
    def __init__(self, course_id, course_name, instructor):
        if not isinstance(instructor, Instructor):
            raise ValueError("Instructor must be an instance of the Instructor class.")
        self.course_id = course_id
        self.course_name = course_name
        self.instructor = instructor
        self.enrolled_students = []

    def add_student(self, student):
        if isinstance(student, Student):
            self.enrolled_students.append(student)
        else:
            raise ValueError("Invalid student object.")

# Serialization: Flatten objects and save data to a JSON file
def save_to_file(instructor, courses, students, filename):
    data = {
        "instructor": {
            "name": instructor.name,
            "age": instructor.age,
            "_email": instructor._email,
            "instructor_id": instructor.instructor_id,
            "assigned_courses": [course.course_id for course in instructor.assigned_courses]
        },
        "courses": [
            {
                "course_id": course.course_id,
                "course_name": course.course_name,
                "instructor_id": course.instructor.instructor_id,
                "enrolled_students": [student.student_id for student in course.enrolled_students]
            } for course in courses
        ],
        "students": [
            {
                "name": student.name,
                "age": student.age,
                "_email": student._email,
                "student_id": student.student_id,
                "registered_courses": [course.course_id for course in student.registered_courses]
            } for student in students
        ]
    }
    with open(filename, 'w') as file:
        json.dump(data, file, indent=4)

# Deserialization: Rebuild the objects from the JSON file
def load_from_file(filename):
    with open(filename, 'r') as file:
        data = json.load(file)

    instructor_data = data["instructor"]
    instructor = Instructor(instructor_data["name"], instructor_data["age"], instructor_data["_email"], instructor_data["instructor_id"])

    course_dict = {}
    for course_data in data["courses"]:
        course = Course(course_data["course_id"], course_data["course_name"], instructor)
        course_dict[course.course_id] = course

    student_dict = {}
    for student_data in data["students"]:
        student = Student(student_data["name"], student_data["age"], student_data["_email"], student_data["student_id"])
        student_dict[student.student_id] = student
        for course_id in student_data["registered_courses"]:
            if course_id in course_dict:
                student.enroll_in_course(course_dict[course_id])

    for course_id in instructor_data["assigned_courses"]:
        if course_id in course_dict:
            instructor.assign_course(course_dict[course_id])

    return instructor, course_dict, student_dict

# Example usage
if __name__ == "__main__":
    instructor = Instructor("Louay Bazzi", 40, "louaybazzi@mail.aub.edu", "97738")
    course1 = Course("EECE 230", "Introduction to Programming", instructor)
    course2 = Course("EECE 330", "Data Structures", instructor)
    instructor.assign_course(course1)
    instructor.assign_course(course2)

    student = Student("Mansour", 19, "mxa14@mail.aub.edu", "293292")
    student.enroll_in_course(course1)

    save_to_file(instructor, [course1, course2], [student], 'school_data.json')
    print("Data saved to school_data.json")

    instructor, courses, students = load_from_file('school_data.json')
    print(f"Instructor: {instructor.name}, Assigned Courses: {[course.course_name for course in instructor.assigned_courses]}")
    for student_id, student in students.items():
        print(f"Student: {student.name}, Registered Courses: {[course.course_name for course in student.registered_courses]}")
