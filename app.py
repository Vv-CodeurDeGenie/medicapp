from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, TextAreaField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from flask_talisman import Talisman
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from werkzeug.security import generate_password_hash, check_password_hash
import os
import logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///medical_center.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
talisman = Talisman(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
limiter = Limiter(get_remote_address, app=app, default_limits=["200 per day", "50 per hour"])

# Logging configuration
handler = RotatingFileHandler('error.log', maxBytes=10000, backupCount=1)
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Patient(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    medical_history = db.Column(db.String(200))

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(50), nullable=False)
    doctor = db.Column(db.String(50), nullable=False)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    patient = db.relationship('Patient', backref=db.backref('appointments', lazy=True))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class PatientForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=1, max=50)])
    age = IntegerField('Age', validators=[DataRequired(), NumberRange(min=0, max=150)])
    medical_history = TextAreaField('Medical History', validators=[Length(max=200)])
    submit = SubmitField('Submit')

class AppointmentForm(FlaskForm):
    date = StringField('Date', validators=[DataRequired()])
    doctor = StringField('Doctor', validators=[DataRequired(), Length(min=1, max=50)])
    patient_id = IntegerField('Patient ID', validators=[DataRequired()])
    submit = SubmitField('Submit')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

@app.route('/')
@login_required
def index():
    patients = Patient.query.all()
    return render_template('index.html', patients=patients)

@app.route('/add_patient', methods=['GET', 'POST'])
@login_required
def add_patient():
    form = PatientForm()
    if form.validate_on_submit():
        new_patient = Patient(name=form.name.data, age=form.age.data, medical_history=form.medical_history.data)
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_patient.html', form=form)

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
@login_required
def edit_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    form = PatientForm(obj=patient)
    if form.validate_on_submit():
        patient.name = form.name.data
        patient.age = form.age.data
        patient.medical_history = form.medical_history.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_patient.html', form=form)

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
@login_required
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/book_appointment', methods=['GET', 'POST'])
@login_required
def book_appointment():
    form = AppointmentForm()
    patients = Patient.query.all()
    if form.validate_on_submit():
        new_appointment = Appointment(date=form.date.data, doctor=form.doctor.data, patient_id=form.patient_id.data)
        db.session.add(new_appointment)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('book_appointment.html', form=form, patients=patients)

@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def edit_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    form = AppointmentForm(obj=appointment)
    if form.validate_on_submit():
        appointment.date = form.date.data
        appointment.doctor = form.doctor.data
        appointment.patient_id = form.patient_id.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_appointment.html', form=form)

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
@login_required
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/patient_records/<int:patient_id>')
@login_required
def patient_records(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    return render_template('patient_records.html', patient=patient)

@app.route('/login', methods=['GET', 'POST'])
@limiter.limit("5 per minute")
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    if not os.path.exists('medical_center.db'):
        with app.app_context():
            db.create_all()
    app.run(debug=True)
