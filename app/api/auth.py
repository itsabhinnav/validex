"""
Authentication routes for Test Case Management System
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash

# Create blueprint
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login')
def login():
    """Login page"""
    return render_template('login.html')

@auth_bp.route('/authenticate', methods=['POST'])
def authenticate():
    """Authenticate user"""
    username = request.form.get('username')
    password = request.form.get('password')
    
    # Simple authentication (implement proper auth as needed)
    if username and password:
        session['user'] = username
        return redirect(url_for('main.dashboard'))
    else:
        flash('Invalid credentials')
        return redirect(url_for('auth.login'))

@auth_bp.route('/logout')
def logout():
    """Logout user"""
    session.pop('user', None)
    return redirect(url_for('main.index'))

