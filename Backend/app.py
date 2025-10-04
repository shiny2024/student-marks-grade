import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'change-this-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'students.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# -----------------------------
# Database model
# -----------------------------
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    roll_no = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(120), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    course = db.Column(db.String(120), nullable=False)

    def __repr__(self):
        return f"<Student {self.roll_no} - {self.name}>"

# -----------------------------
# Forms
# -----------------------------
class StudentForm(FlaskForm):
    roll_no = StringField('Roll No', validators=[DataRequired()])
    name = StringField('Name', validators=[DataRequired()])
    age = IntegerField('Age', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[DataRequired()])
    course = StringField('Course', validators=[DataRequired()])
    submit = SubmitField('Submit')

# -----------------------------
# Routes
# -----------------------------
@app.route('/')
def index():
    q = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    query = Student.query

    if q:
        like = f"%{q}%"
        query = query.filter(
            (Student.name.ilike(like)) |
            (Student.roll_no.ilike(like)) |
            (Student.course.ilike(like))
        )

    students = query.order_by(Student.id.desc()).paginate(page=page, per_page=8)
    return render_template('index.html', students=students, q=q)

@app.route('/add', methods=['GET', 'POST'])
def add_student():
    form = StudentForm()
    if form.validate_on_submit():
        student = Student(
            roll_no=form.roll_no.data,
            name=form.name.data,
            age=form.age.data,
            gender=form.gender.data,
            course=form.course.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Student added successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_edit.html', form=form, title='Add Student')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
    student = Student.query.get_or_404(id)
    form = StudentForm(obj=student)
    if form.validate_on_submit():
        student.roll_no = form.roll_no.data
        student.name = form.name.data
        student.age = form.age.data
        student.gender = form.gender.data
        student.course = form.course.data
        db.session.commit()
        flash('Student updated successfully!', 'success')
        return redirect(url_for('index'))
    return render_template('add_edit.html', form=form, title='Edit Student')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/view/<int:id>')
def view_student(id):
    student = Student.query.get_or_404(id)
    return render_template('view.html', student=student)

# -----------------------------
# Run server
# -----------------------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='127.0.0.1', port=5000, debug=True)
