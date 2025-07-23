
from flask import Blueprint, render_template

auth_ui_bp = Blueprint('authui', __name__)

@auth_ui_bp.route('/')
def login_page():
    return render_template('auth_ui/login.html')

@auth_ui_bp.route('/signup')
def signup_page():
    return render_template('auth_ui/signup.html')
