# Validex Security Configuration Guide

This guide explains how to configure the Validex application for secure deployment with network isolation and restricted access.

## 🔒 Security Features

### 1. **Localhost-Only Binding**
- Flask application binds only to `127.0.0.1` (localhost)
- No external network access by default
- Production mode enforces localhost binding

### 2. **Network Security Service**
- URL whitelist for outbound connections
- Domain and IP-based filtering
- Wildcard pattern support
- Configurable blocked domains

### 3. **Firewall Integration**
- Windows Firewall rules (Windows)
- iptables rules (Linux/macOS)
- Outbound connection restrictions
- Localhost exception rules

### 4. **Secure HTTP Client**
- All outbound requests go through security checks
- Automatic URL validation
- Exception handling for blocked requests

## 🚀 Quick Start

### 1. **Configure Security Settings**
```bash
# Run the secure deployment script
python scripts/secure_deployment.py
```

### 2. **Start Application Securely**
```bash
# Windows
start_secure.bat

# Linux/macOS
./start_secure.sh
```

### 3. **Verify Security Configuration**
```bash
# Check current settings
python scripts/configure_network_security.py --show
```

## ⚙️ Configuration

### Network Security Settings

Edit `config/validex_config.json`:

```json
{
  "network_security": {
    "restricted_mode": true,
    "allowed_domains": [
      "trialdablg5.jfrog.io",
      "*.jfrog.io",
      "localhost",
      "127.0.0.1"
    ],
    "allowed_ips": [
      "127.0.0.1",
      "::1"
    ],
    "blocked_domains": [
      "malicious-site.com",
      "*.suspicious-domain.com"
    ]
  }
}
```

### Environment Variables

```bash
# Force localhost binding
export FLASK_HOST=127.0.0.1

# Disable debug mode
export FLASK_DEBUG=false

# Set production environment
export FLASK_ENV=production
```

## 🛠️ Management Commands

### Network Security Management

```bash
# Show current configuration
python scripts/configure_network_security.py --show

# Add allowed domain
python scripts/configure_network_security.py --add-domain "your-artifactory.com"

# Add allowed IP
python scripts/configure_network_security.py --add-ip "192.168.1.100"

# Test connectivity
python scripts/configure_network_security.py --test-url "https://your-artifactory.com"

# Enable/disable restricted mode
python scripts/configure_network_security.py --enable-restricted
python scripts/configure_network_security.py --disable-restricted
```

### Firewall Management (Windows)

```powershell
# Enable firewall restrictions (requires admin)
.\scripts\configure_firewall.ps1 -Enable

# Disable firewall restrictions (requires admin)
.\scripts\configure_firewall.ps1 -Disable

# Show current status
.\scripts\configure_firewall.ps1 -Status
```

## 🔧 Advanced Configuration

### Custom Allowed Domains

To add your Artifactory instance:

```bash
# Add your Artifactory domain
python scripts/configure_network_security.py --add-domain "your-company.jfrog.io"

# Add wildcard for all JFrog instances
python scripts/configure_network_security.py --add-domain "*.jfrog.io"
```

### IP-Based Restrictions

```bash
# Add specific IP addresses
python scripts/configure_network_security.py --add-ip "192.168.1.100"
python scripts/configure_network_security.py --add-ip "10.0.0.50"
```

### Block Malicious Domains

Edit the configuration file to add blocked domains:

```json
{
  "network_security": {
    "blocked_domains": [
      "malicious-site.com",
      "*.suspicious-domain.com",
      "phishing-site.net"
    ]
  }
}
```

## 🧪 Testing Security

### 1. **Test Allowed Connections**
```bash
# Test Artifactory connection
python scripts/configure_network_security.py --test-url "https://trialdablg5.jfrog.io"

# Test localhost connection
python scripts/configure_network_security.py --test-url "http://localhost:8000"
```

### 2. **Test Blocked Connections**
```bash
# This should be blocked
python scripts/configure_network_security.py --test-url "https://example.com"
```

### 3. **Verify Application Binding**
```bash
# Check if app is bound to localhost only
netstat -an | findstr :8000
# Should show: 127.0.0.1:8000
```

## 🚨 Security Best Practices

### 1. **Always Use Localhost Binding**
- Never bind to `0.0.0.0` in production
- Use `127.0.0.1` for localhost-only access
- Consider using a reverse proxy for external access

### 2. **Minimize Allowed Domains**
- Only whitelist necessary domains
- Use specific domains instead of wildcards when possible
- Regularly review and update the whitelist

### 3. **Monitor Network Activity**
- Check security logs regularly
- Monitor for blocked connection attempts
- Review firewall rules periodically

### 4. **Use HTTPS for External Connections**
- Always use HTTPS for Artifactory connections
- Validate SSL certificates
- Consider certificate pinning for critical connections

## 🔍 Troubleshooting

### Common Issues

#### 1. **Application Won't Start**
```bash
# Check if port is already in use
netstat -an | findstr :8000

# Kill existing processes
taskkill /f /im python.exe
```

#### 2. **Network Connections Blocked**
```bash
# Check security configuration
python scripts/configure_network_security.py --show

# Test specific URL
python scripts/configure_network_security.py --test-url "https://your-url.com"
```

#### 3. **Firewall Issues**
```powershell
# Check Windows Firewall status
Get-NetFirewallRule -DisplayName "*Validex*"

# Reset firewall rules
.\scripts\configure_firewall.ps1 -Disable
.\scripts\configure_firewall.ps1 -Enable
```

### Debug Mode

To temporarily disable security for debugging:

```bash
# Disable restricted mode
python scripts/configure_network_security.py --disable-restricted

# Re-enable after debugging
python scripts/configure_network_security.py --enable-restricted
```

## 📊 Security Monitoring

### Security Report

The application generates a security report:

```bash
# View security report
cat security_report.json
```

### Log Files

Check application logs for security events:

```bash
# Look for security-related messages
grep -i "security\|blocked\|allowed" app.log
```

## 🔐 Production Deployment

### 1. **Secure Startup Script**
Use the generated secure startup script:

```bash
# Windows
start_secure.bat

# Linux/macOS
./start_secure.sh
```

### 2. **Environment Variables**
Set these environment variables in production:

```bash
FLASK_HOST=127.0.0.1
FLASK_DEBUG=false
FLASK_ENV=production
```

### 3. **Reverse Proxy (Optional)**
For external access, use a reverse proxy like Nginx:

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 📞 Support

For security-related issues:

1. Check the security report: `security_report.json`
2. Review network security configuration
3. Test connectivity with the management scripts
4. Check firewall rules and logs

Remember: Security is a continuous process. Regularly review and update your security configuration to maintain the highest level of protection.
