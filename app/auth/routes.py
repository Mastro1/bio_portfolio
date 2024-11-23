from flask import Blueprint, redirect, url_for
from app import oauth  # Import the already initialized OAuth object
from flask import render_template, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from app.database_setup import User, Session
from flask_login import login_user, logout_user

auth = Blueprint("auth", __name__)

# Register the Google provider
google = oauth.register(
    name="google",
    client_id="your-client-id",
    client_secret="your-client-secret",
    access_token_url="https://oauth2.googleapis.com/token",
    access_token_params=None,
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    authorize_params=None,
    api_base_url="https://www.googleapis.com/oauth2/v1/",
    client_kwargs={"scope": "openid email profile"},
)

@auth.route("/login")
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        session = Session()
        user = session.query(User).filter_by(email=email).first()
        session.close()

        if not user or not check_password_hash(user.password, password):
            flash('Invalid credentials.', 'danger')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash('Logged in successfully.', 'success')
        return redirect(url_for('main.index'))

    return render_template('login.html')

@auth.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        session = Session()
        user = session.query(User).filter_by(email=email).first()

        if user:
            flash('Email already exists.', 'danger')
            return redirect(url_for('auth.signup'))

        new_user = User(username=username, email=email, password=password)
        session.add(new_user)
        session.commit()
        session.close()

        flash('Signup successful! Please log in.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('signup.html')


@auth.route('/logout')
def logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))