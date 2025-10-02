# 🚀 Validex Deployment Guide

This directory contains all deployment-related files and documentation for the Validex Test Case Management System.

## 📁 Directory Structure

```
deployment/
├── README.md                           # This file
├── PRODUCTION_DEPLOYMENT.md           # Comprehensive production guide
├── DEPLOYMENT_README.md                  # Quick start deployment options
└── scripts/                          # Deployment scripts
    ├── production_setup.sh           # Linux/macOS automated setup
    ├── setup_windows.ps1            # Windows automated setup
    └── quick_start.sh               # Development quick start
```

## 🚀 Quick Start

### Automated Deployment
```bash
# Linux/macOS
chmod +x scripts/production_setup.sh
./scripts/production_setup.sh

# Windows PowerShell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\scripts\setup_windows.ps1
```

### Docker Deployment
```bash
# Using Docker Compose
docker-compose up -d
```

### Manual Deployment
Follow the detailed steps in `PRODUCTION_DEPLOYMENT.md`

## 📋 Deployment Options

1. **Automated Scripts** - Recommended for most users
2. **Docker Deployment** - For containerized environments
3. **Manual Setup** - For custom configurations
4. **Cloud Deployment** - AWS, GCP, Azure specific guides

## 🔧 Configuration

All configuration files are located in the `config/` directory:
- `config/production/settings.py` - Production settings
- `config/production/env.example` - Environment variables template

## 📊 Monitoring

The deployment includes:
- Health check scripts
- Backup automation
- Log rotation
- Performance monitoring

## 🆘 Support

For deployment issues:
1. Check the logs in `logs/` directory
2. Review the troubleshooting section in `PRODUCTION_DEPLOYMENT.md`
3. Verify system requirements
4. Check network connectivity

---

**Ready to deploy? Start with the automated scripts for the easiest setup!**

