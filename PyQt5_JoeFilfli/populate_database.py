import sqlite3
import random
import string

# Connect to the SQLite database (it should already exist with the required tables)
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

# Function to generate random email addresses
def generate_email(name):
    domains = ['example.com', 'school.edu', 'mail.com']
    domain = random.choice(domains)
    email = f"{name.lower().replace(' ', '')}@{domain}"
    return email

# Function to generate a random age between 18 and 65
def generate_age():
    return random.randint(18, 65)

# Function to generate a random ID
def generate_id(prefix, length=6):
    return prefix + ''.join(random.choices(string.digits, k=length))

# Sample data
student_names = [
    'Alice Johnson', 'Bob Smith', 'Carol Williams', 'David Brown',
    'Eva Davis', 'Frank Miller', 'Grace Wilson', 'Henry Moore',
    'Isabella Taylor', 'Jack Anderson', 'Karen Thomas', 'Leo Jackson',
    'Mia White', 'Nathan Harris', 'Olivia Martin', 'Peter Thompson',
    'Queen Robinson', 'Ryan Clark', 'Sophia Lewis', 'Thomas Lee'
]

instructor_names = [
    'Dr. Emily Walker', 'Prof. Daniel Hall', 'Dr. Fiona Allen',
    'Prof. George Young', 'Dr. Hannah King', 'Prof. Ian Wright',
    'Dr. Julia Scott', 'Prof. Kevin Green', 'Dr. Laura Baker',
    'Prof. Michael Adams'
]

course_data = [
    ('CS101', 'Introduction to Computer Science'),
    ('MATH201', 'Calculus I'),
    ('ENG301', 'English Literature'),
    ('PHY101', 'General Physics'),
    ('CHEM101', 'General Chemistry'),
    ('BIO201', 'Cell Biology'),
    ('HIST101', 'World History'),
    ('ART201', 'Modern Art'),
    ('PSY101', 'Introduction to Psychology'),
    ('ECON201', 'Microeconomics')
]

# Clear existing data (optional)
def clear_tables():
    cursor.execute('DELETE FROM registrations')
    cursor.execute('DELETE FROM students')
    cursor.execute('DELETE FROM instructors')
    cursor.execute('DELETE FROM courses')
    conn.commit()
    print("Existing data cleared.")

# Uncomment the following line if you want to clear existing data
# clear_tables()

# Populate instructors
def populate_instructors():
    print("Populating instructors...")
    for name in instructor_names:
        age = generate_age()
        email = generate_email(name)
        instructor_id = generate_id('INST')
        try:
            cursor.execute('''
                INSERT INTO instructors (name, age, email, instructor_id)
                VALUES (?, ?, ?, ?)
            ''', (name, age, email, instructor_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error inserting instructor {name}: {e}")
    print("Instructors populated.")

# Populate courses and assign instructors
def populate_courses():
    print("Populating courses and assigning instructors...")
    cursor.execute('SELECT id FROM instructors')
    instructor_ids = [row[0] for row in cursor.fetchall()]
    for course_id, course_name in course_data:
        instructor_id = random.choice(instructor_ids)
        try:
            cursor.execute('''
                INSERT INTO courses (course_id, course_name, instructor_id)
                VALUES (?, ?, ?)
            ''', (course_id, course_name, instructor_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error inserting course {course_id}: {e}")
    print("Courses populated and instructors assigned.")

# Populate students
def populate_students():
    print("Populating students...")
    for name in student_names:
        age = generate_age()
        email = generate_email(name)
        student_id = generate_id('STU')
        try:
            cursor.execute('''
                INSERT INTO students (name, age, email, student_id)
                VALUES (?, ?, ?, ?)
            ''', (name, age, email, student_id))
            conn.commit()
        except sqlite3.IntegrityError as e:
            print(f"Error inserting student {name}: {e}")
    print("Students populated.")

# Register students for courses
def register_students():
    print("Registering students for courses...")
    cursor.execute('SELECT id FROM students')
    student_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute('SELECT id FROM courses')
    course_ids = [row[0] for row in cursor.fetchall()]
    for student_id in student_ids:
        # Each student registers for 3 random courses
        courses = random.sample(course_ids, 3)
        for course_id in courses:
            try:
                cursor.execute('''
                    INSERT INTO registrations (student_id, course_id)
                    VALUES (?, ?)
                ''', (student_id, course_id))
                conn.commit()
            except sqlite3.IntegrityError as e:
                print(f"Error registering student {student_id} for course {course_id}: {e}")
    print("Students registered for courses.")

# Main function to populate the database
def populate_database():
    populate_instructors()
    populate_courses()
    populate_students()
    register_students()
    print("Database population complete.")

# Run the population script
if __name__ == '__main__':
    populate_database()
    # Close the database connection
    conn.close()
