CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_role ENUM('admin','student') NOT NULL
);

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_year INT,
    major VARCHAR(100),
    FOREIGN KEY (student_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_name VARCHAR(100),
    course_code VARCHAR(20) UNIQUE NOT NULL, --course_code is just so that it can be displayed for the frontend
    -- For all intents and purposes, course_id will be used to identify the courses.
    title VARCHAR(100) NOT NULL,
    credits INT NOT NULL
);

CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester VARCHAR(20),
    enrollment_year INT,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    UNIQUE(student_id, course_id, semester, enrollment_year)
);

CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    course_id INT NOT NULL,
    title VARCHAR(100),
    due_date DATE,
    max_marks INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    assignment_id INT NOT NULL,
    student_id INT NOT NULL,
    marks_obtained INT,
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(assignment_id, student_id)
);

CREATE TABLE course_grades(
    course_grade_id INT AUTO_INCREMENT PRIMARY KEY,
    grade VARCHAR(2),
    course_id INT NOT NULL,
    student_id INT NOT NULL,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(course_id, student_id)
);

--We need helper functions to display the total marks secured by a student in a course.
--The total marks will just be the aggregate of all the marks secured in all the assignments for the course.
