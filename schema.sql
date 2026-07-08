CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    user_name VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    user_role ENUM('admin','student', 'instructor') NOT NULL
);

CREATE TABLE students (
    student_id INT PRIMARY KEY,
    student_name VARCHAR(100),
    student_year INT,
    major VARCHAR(100),
    FOREIGN KEY (student_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE instructors(
    instructor_id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_name VARCHAR(100),
    FOREIGN KEY (instructor_id) REFERENCES users(user_id) ON DELETE CASCADE
);

CREATE TABLE courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) UNIQUE NOT NULL, --course_code is just so that it can be displayed for the frontend
    -- For all intents and purposes, course_id will be used to identify the courses.
    title VARCHAR(100) NOT NULL,
    credits INT NOT NULL
);

CREATE TABLE course_offerings (
    offering_id INT AUTO_INCREMENT PRIMARY KEY,
    instructor_id INT NOT NULL,
    course_id INT NOT NULL,
    offering_year INT,
    semester ENUM('Spring', 'Summer', 'Fall'),
    max_seats INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (instructor_id) REFERENCES instructors(instructor_id)
);

CREATE TABLE course_prerequisites (
    course_id INT,
    prereq_id INT,
    FOREIGN KEY (course_id) REFERENCES courses(course_id),
    FOREIGN KEY (prereq_id) REFERENCES courses(course_id),
    PRIMARY KEY (course_id, prereq_id)
);

CREATE TABLE enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    offering_id INT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id),
    UNIQUE(student_id, offering_id)
);

CREATE TABLE assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    offering_id INT NOT NULL,
    title VARCHAR(100),
    due_date DATE,
    max_marks INT,
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id)
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
    offering_id INT NOT NULL,
    student_id INT NOT NULL,
    FOREIGN KEY (offering_id) REFERENCES course_offerings(offering_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(offering_id, student_id)
);

CREATE TABLE waitlist (
    waitlist_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    offering_id INT NOT NULL,
    waitlist_position INT,
    UNIQUE(student_id, offering_id)
);

--We need helper functions to display the total marks secured by a student in a course.
--The total marks will just be the aggregate of all the marks secured in all the assignments for the course.

CREATE TABLE assignment_submissions (
    submission_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    assignment_id INT NOT NULL,
    filepath VARCHAR(500) NOT NULL,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(student_id, assignment_id),
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    FOREIGN KEY (assignment_id) REFERENCES assignments(assignment_id)
);
