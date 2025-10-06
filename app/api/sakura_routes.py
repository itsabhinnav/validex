from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.database_service import DatabaseService
from app.services.file_service import FileService
from app.utils.text_config import get_text

# Create Sakura blueprint
sakura_bp = Blueprint('sakura', __name__)

@sakura_bp.route('/sakura')
def sakura_dashboard():
    """Sakura dashboard - main entry point for Sakura app"""
    return render_template('sakura/dashboard.html')

@sakura_bp.route('/sakura/automation')
def automation():
    """Test automation management"""
    return render_template('sakura/automation.html')

@sakura_bp.route('/sakura/orchestration')
def orchestration():
    """Test orchestration and scheduling"""
    return render_template('sakura/orchestration.html')

@sakura_bp.route('/sakura/monitoring')
def monitoring():
    """Real-time test monitoring"""
    return render_template('sakura/monitoring.html')

@sakura_bp.route('/sakura/insights')
def insights():
    """AI-powered insights and analytics"""
    return render_template('sakura/insights.html')

@sakura_bp.route('/sakura/browse-requirements')
def browse_requirements():
    """Browse and manage requirements"""
    return render_template('sakura/browse_requirements.html')