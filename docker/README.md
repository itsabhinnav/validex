# 🐳 Validex Docker Deployment

This directory contains Docker-related files for containerized deployment of the Validex Test Case Management System.

## 📁 Files

- `Dockerfile` - Main application container
- `docker-compose.yml` - Multi-container orchestration
- `nginx.conf` - Nginx reverse proxy configuration

## 🚀 Quick Start

### Using Docker Compose (Recommended)
```bash
# Copy environment file
cp ../config/production/env.example .env

# Edit environment variables
nano .env

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f validex
```

### Using Docker Only
```bash
# Build image
docker build -t validex .

# Run container
docker run -d \
  --name validex-app \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  -e FLASK_ENV=production \
  -e SECRET_KEY=your-secret-key \
  validex
```

## 🏗️ Architecture

The Docker setup includes:

- **validex** - Main application container
- **nginx** - Reverse proxy and static file server
- **redis** - Caching and session storage
- **postgres** - Database (optional, SQLite by default)

## 🔧 Configuration

### Environment Variables
Create a `.env` file with:
```bash
SECRET_KEY=your-super-secret-key
POSTGRES_PASSWORD=your-db-password
```

### SSL/TLS Setup
1. Place SSL certificates in `ssl/` directory
2. Update `nginx.conf` with certificate paths
3. Restart containers: `docker-compose restart`

## 📊 Monitoring

### Health Checks
```bash
# Check application health
curl http://localhost:8000/health

# Check container status
docker-compose ps

# View logs
docker-compose logs -f
```

### Backup
```bash
# Backup database
docker-compose exec validex sqlite3 /app/data/test_cases.db ".backup /app/backups/backup.db"

# Backup volumes
docker run --rm -v validex_data:/data -v $(pwd)/backups:/backup alpine tar czf /backup/data.tar.gz -C /data .
```

## 🔄 Updates

### Update Application
```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Update Dependencies
```bash
# Update requirements.txt
# Rebuild container
docker-compose build --no-cache validex
docker-compose up -d
```

## 🚨 Troubleshooting

### Common Issues

1. **Container won't start**
```bash
# Check logs
docker-compose logs validex

# Check configuration
docker-compose config
```

2. **Database issues**
```bash
# Access database
docker-compose exec validex sqlite3 /app/data/test_cases.db

# Reset database
docker-compose exec validex rm /app/data/test_cases.db
docker-compose restart validex
```

3. **Permission issues**
```bash
# Fix permissions
docker-compose exec validex chown -R validex:validex /app/data
```

### Performance Optimization

1. **Resource Limits**
```yaml
# In docker-compose.yml
services:
  validex:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
```

2. **Database Optimization**
```bash
# Optimize SQLite
docker-compose exec validex sqlite3 /app/data/test_cases.db "PRAGMA optimize;"
```

## 📈 Scaling

### Horizontal Scaling
```bash
# Scale application
docker-compose up -d --scale validex=3

# Load balancer configuration needed
```

### Vertical Scaling
```bash
# Increase resources in docker-compose.yml
# Restart services
docker-compose up -d
```

---

**🐳 Your Validex application is now running in Docker!**

