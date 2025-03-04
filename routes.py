from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.exc import IntegrityError
from app import app, db
from models import User, Schedule
from forms import LoginForm, RegisterForm, ScheduleForm
from ai_scheduler import generate_schedule

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid email or password. Please try again.', 'error')
        except Exception as e:
            flash('An error occurred during login. Please try again.', 'error')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except IntegrityError:
            db.session.rollback()
            flash('An account with this email or username already exists.', 'error')
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    schedules = Schedule.query.filter_by(user_id=current_user.id).order_by(Schedule.created_at.desc()).all()
    return render_template('dashboard.html', schedules=schedules)

@app.route('/create_schedule', methods=['GET', 'POST'])
@login_required
def create_schedule():
    form = ScheduleForm()
    if form.validate_on_submit():
        try:
            schedule_data = generate_schedule(form.preferences.data)
            schedule = Schedule(
                title=form.title.data,
                content=schedule_data,
                user_id=current_user.id
            )
            db.session.add(schedule)
            db.session.commit()
            return redirect(url_for('view_schedule', schedule_id=schedule.id))
        except Exception as e:
            db.session.rollback()
            flash(f'Error generating schedule: {str(e)}', 'error')
    return render_template('create_schedule.html', form=form)

@app.route('/schedule/<int:schedule_id>')
@login_required
def view_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
    return render_template('view_schedule.html', schedule=schedule)

@app.route('/schedule/<int:schedule_id>/delete', methods=['POST'])
@login_required
def delete_schedule(schedule_id):
    schedule = Schedule.query.get_or_404(schedule_id)
    if schedule.user_id != current_user.id:
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))

    db.session.delete(schedule)
    db.session.commit()
    flash('Schedule deleted successfully')
    return redirect(url_for('dashboard'))