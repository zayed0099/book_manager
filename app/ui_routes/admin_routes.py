
from flask import Blueprint, render_template

admin_ui_bp = Blueprint('adminui', __name__)

@admin_ui_bp.route('/manage/admin')
def manage_admin():
    return render_template('admin_ui/admin.html')

@admin_ui_bp.route('/manage/user')
def manage_user():
    return render_template('admin_ui/user.html')

