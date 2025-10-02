# Windows Firewall Configuration Script for Validex
# This script configures Windows Firewall to restrict network access

param(
    [switch]$Enable,
    [switch]$Disable,
    [switch]$Status,
    [string]$Port = "8000"
)

# Check if running as administrator
function Test-Administrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

# Configure firewall rules
function Set-FirewallRules {
    param([bool]$EnableRules)
    
    if (-not (Test-Administrator)) {
        Write-Error "This script must be run as Administrator"
        return
    }
    
    $ruleName = "Validex-Security-Rule"
    $appPath = (Get-Location).Path + "\run.py"
    
    if ($EnableRules) {
        Write-Host "Enabling firewall restrictions for Validex..."
        
        # Block outbound connections except for allowed domains
        $allowedDomains = @(
            "trialdablg5.jfrog.io",
            "*.jfrog.io"
        )
        
        # Create outbound block rule (will be overridden by allow rules)
        New-NetFirewallRule -DisplayName "$ruleName-Outbound-Block" -Direction Outbound -Action Block -Protocol Any -Program $appPath -ErrorAction SilentlyContinue
        
        # Allow localhost connections
        New-NetFirewallRule -DisplayName "$ruleName-Localhost-Allow" -Direction Outbound -Action Allow -Protocol Any -RemoteAddress "127.0.0.1,::1" -Program $appPath -ErrorAction SilentlyContinue
        
        # Allow specific domains (this is a simplified approach - Windows Firewall doesn't support domain-based rules directly)
        # In practice, you would need to resolve domains to IPs and create IP-based rules
        
        Write-Host "Firewall rules configured successfully"
    } else {
        Write-Host "Disabling firewall restrictions for Validex..."
        
        # Remove all Validex firewall rules
        Get-NetFirewallRule -DisplayName "*$ruleName*" | Remove-NetFirewallRule -ErrorAction SilentlyContinue
        
        Write-Host "Firewall rules removed successfully"
    }
}

# Show current firewall status
function Show-FirewallStatus {
    Write-Host "=== Current Firewall Status ==="
    
    $rules = Get-NetFirewallRule -DisplayName "*Validex*" -ErrorAction SilentlyContinue
    if ($rules) {
        Write-Host "Validex firewall rules found:"
        $rules | ForEach-Object {
            Write-Host "  - $($_.DisplayName): $($_.Action) $($_.Direction)"
        }
    } else {
        Write-Host "No Validex firewall rules found"
    }
    
    Write-Host "`n=== Network Security Configuration ==="
    try {
        python scripts/configure_network_security.py --show
    } catch {
        Write-Host "Could not retrieve network security configuration"
    }
}

# Main execution
if ($Enable) {
    Set-FirewallRules -EnableRules $true
} elseif ($Disable) {
    Set-FirewallRules -EnableRules $false
} elseif ($Status) {
    Show-FirewallStatus
} else {
    Write-Host "Validex Firewall Configuration Script"
    Write-Host "Usage:"
    Write-Host "  .\scripts\configure_firewall.ps1 -Enable    # Enable firewall restrictions"
    Write-Host "  .\scripts\configure_firewall.ps1 -Disable   # Disable firewall restrictions"
    Write-Host "  .\scripts\configure_firewall.ps1 -Status    # Show current status"
    Write-Host ""
    Write-Host "Note: This script must be run as Administrator"
}

