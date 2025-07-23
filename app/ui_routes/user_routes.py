
from flask import Blueprint, render_template

user_ui_bp = Blueprint('usui', __name__)

@user_ui_bp.route('/dashboard')
def dashboard():
    return render_template('user_ui/book_cr.html')

@user_ui_bp.route('/manage/books')
def manage_books():
    return render_template('user_ui/book_rudf.html')

@user_ui_bp.route('/recover')
def recover_deleted_books():
    return render_template('user_ui/recovery.html')

@user_ui_bp.route('/view/all')
def show_favourite_and_deleted():
    return render_template('user_ui/showfav.html')
