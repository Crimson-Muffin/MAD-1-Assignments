import os
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
current_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{
    os.path.join(current_dir, 'database.sqlite3')}"

db = SQLAlchemy()
db.init_app(app)
app.app_context().push()


class Student(db.Model):
    __tablename__ = "student"
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    roll_number = db.Column(db.String, unique=True, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String)


class Course(db.Model):
    __tablename__ = "course"
    course_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    course_code = db.Column(db.String, unique=True, nullable=False)
    course_name = db.Column(db.String, nullable=False)
    course_description = db.Column(db.String)
    student = db.relationship("Student", secondary="enrollments")


class Enrollments(db.Model):
    __tablename__ = "enrollments"
    enrollment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    estudent_id = db.Column(db.Integer, db.ForeignKey(
        'student.student_id'), nullable=False)
    ecourse_id = db.Column(db.Integer, db.ForeignKey(
        'course.course_id'), nullable=False)


@app.route('/', methods=['GET', 'POST'])
def home():
    students = Student.query.all()
    return render_template('home.html', students=students, len=len(students))


@app.route('/student/create', methods=['GET', 'POST'])
def create_student():
    if request.method == "GET":
        courses = Course.query.all()
        return render_template('create_student.html',courses=courses)
    elif request.method == "POST":
        roll_number = request.form['roll']
        first_name = request.form['f_name']
        last_name = request.form['l_name']
        enrolled_courses = request.form.getlist('courses')

        existing_student = Student.query.filter(
            Student.roll_number == roll_number).first()

        if existing_student:
            return render_template('existing_student.html')
        new_student = Student(roll_number=roll_number,
                              first_name=first_name, last_name=last_name)
        db.session.add(new_student)
        db.session.commit()

        for enrolled_course in enrolled_courses:
            course_id = enrolled_course
            new_enrollment = Enrollments(
                estudent_id=new_student.student_id, ecourse_id=course_id)
            db.session.add(new_enrollment)
            db.session.commit()

        return redirect(url_for('home'))


@app.route('/student/<int:student_id>/update', methods=['GET', 'POST'])
def update_student(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    courses = Course.query.all()
    if request.method == "GET":
        return render_template('update_student_mine.html', student=student, courses=courses)
    elif request.method == "POST":
        student.first_name = request.form['f_name']
        student.last_name = request.form['l_name']

        updated_enrollment = request.form.getlist('courses')
        Enrollments.query.filter(
            Enrollments.estudent_id == student_id).delete()

        for course in updated_enrollment:
            course_id = course
            enroll = Enrollments(estudent_id=student_id, ecourse_id=course_id)
            db.session.add(enroll)

        db.session.commit()

        return redirect(url_for('home'))


@app.route('/student/<int:student_id>/delete')
def delete_student(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    if student:
        Enrollments.query.filter(
            Enrollments.estudent_id == student_id).delete()
        db.session.delete(student)
        db.session.commit()

    return redirect(url_for('home'))


# @app.route('/student/<int:student_id>')
# def get_student(student_id):
#     student = Student.query.filter(Student.student_id == student_id).first()
#     enrolled_courses = Course.query.join(Enrollments).filter(
#         Enrollments.estudent_id == student_id).all()

#     return render_template('student_courses.html', student=student, enrolled_courses=enrolled_courses)

@app.route('/student/<int:student_id>')
def get_student_detail(student_id):
    student = Student.query.filter(Student.student_id == student_id).first()
    enrolled_courses = Course.query.join(Enrollments).filter(
        Enrollments.estudent_id == student_id).all()
    return render_template('student_courses.html', student=student, enrolled_courses=enrolled_courses)


if __name__ == '__main__':
    db.create_all()
    app.run(debug=True)
