# 🔐 SSH Security Guide

A comprehensive guide to securing SSH connections and files for the Image Upload Server project.

## 🎯 Overview

This guide covers SSH security best practices, key management, and secure configuration for your development environment.

## 📁 Current SSH Setup

### Generated SSH Keys

```
~/.ssh/
├── id_ed25519          # Private key (600 permissions) - PRIMARY
├── id_ed25519.pub      # Public key (644 permissions) - PRIMARY
├── id_rsa              # Private key (600 permissions) - BACKUP
├── id_rsa.pub          # Public key (644 permissions) - BACKUP
└── config              # SSH configuration (600 permissions)
```

### Your Public Keys

#### ED25519 Key (Primary - More Secure)
```bash
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBDkue9cD5FrkcKWeewrmUayp4LtMng+SulIrW1kiXwQ orangepi@orangepi5max
```

#### RSA Key (Backup - Compatible)
```bash
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCi3r5swCfpfNzgAsmrLw9JIhEF/whZSscqHWVDqrvnw4oDl1eQsGWOoZUPokO9j1Jhq/L5p7WsWuvf34TjdxZAdVJxJZTVAldg0tl1tYG29NTmjO9WLmBK9MrxECehEvQhxVoX1jdZY/i4DPDZ8EnaXi4TaZelqMRHP841+SjdPLiBSuBsFdPGIL7bxtE0qY95p/qNn+cdG6LC4g8xfwEGCdbCeQg67gqo9mQYQkCsFMuN/t/AvT/nolqrl1v6/YOIYjSAkrl/WZUoZuOBsn2ZI4g9vHOiTpgKx3dEO0MvQZsTYibJtTxcIbPEuXErKjg3Bvb+nM+EYcmFrpOJ8xED2kwneotiNiPHHDmwfI8JZFBmt2FVXCUH13Iu/p/f5gXtk1NVQnujaI0Z4G+cDZ/oPAs0APInrRLTCU+5l7sMfcpr3amvKqMf9NYAl5J0aBDsUTUU6DsQW4ST8Ef0wmo210ksi7F7JKzKvJkHPm9ArHUTt53brPMoJP5VDrgE59ig1t8C0KEgc5h36OJamBMaRrTw7ZdvocrhThqoWxF+uY8xrGde80VahMbGbtIvXQUXBW7ZkyjaiqhNZxgxalE1qKdxAv98BU/HRPnrnN5F8OuEHfhzXTDMXYLKma32nvfffjpltWHOTF2H0YQpEbv9GbbuA/fZyAbJ4yaOMVWZzQ== vu.nguyeenngoc@gmail.com
```

### Key Strategy

- **ED25519 Key**: Primary key for new servers and modern systems
- **RSA Key**: Backup key for older servers that don't support ED25519
- **Fallback Order**: SSH will try ED25519 first, then RSA if needed

## 🔒 SSH Security Best Practices

### 1. Key Management

#### ✅ **Secure Key Generation**
```bash
# Generate ED25519 key (recommended)
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519

# Generate RSA key (if needed)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com" -f ~/.ssh/id_rsa
```

#### ✅ **Proper File Permissions**
```bash
# SSH directory
chmod 700 ~/.ssh

# Private keys
chmod 600 ~/.ssh/id_ed25519
chmod 600 ~/.ssh/id_rsa

# Public keys
chmod 644 ~/.ssh/id_ed25519.pub
chmod 644 ~/.ssh/id_rsa.pub

# Config file
chmod 600 ~/.ssh/config
```

### 2. SSH Configuration Security

#### ✅ **Secure Global Settings**
```bash
# ~/.ssh/config
Host *
    # Security settings
    Protocol 2
    HashKnownHosts yes
    GSSAPIAuthentication no
    GSSAPIDelegateCredentials no
    
    # Connection settings
    ServerAliveInterval 60
    ServerAliveCountMax 3
    TCPKeepAlive yes
    
    # Security hardening
    PermitLocalCommand no
    ClearAllForwardings yes
    
    # Key settings
    IdentitiesOnly yes
    IdentityFile ~/.ssh/id_ed25519
```

### 3. Server-Side Security

#### ✅ **SSH Server Configuration**
```bash
# /etc/ssh/sshd_config
# Security settings
Protocol 2
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes
AuthorizedKeysFile .ssh/authorized_keys

# Connection limits
MaxAuthTries 3
MaxSessions 10
ClientAliveInterval 300
ClientAliveCountMax 2

# Disable unused features
X11Forwarding no
AllowTcpForwarding no
PermitTunnel no
```

## 🚀 SSH Usage Examples

### 1. Basic Connection

```bash
# Connect to localhost
ssh localhost

# Connect to remote server
ssh user@remote-server.com

# Connect with specific key
ssh -i ~/.ssh/id_ed25519 user@remote-server.com
```

### 2. Using SSH Config

```bash
# Connect using config alias
ssh production
ssh development
ssh localhost
```

### 3. File Transfer

```bash
# Copy file to remote server
scp file.txt user@remote-server.com:/path/to/destination/

# Copy file from remote server
scp user@remote-server.com:/path/to/file.txt ./

# Copy directory
scp -r local-directory/ user@remote-server.com:/path/to/destination/
```

### 4. Port Forwarding

```bash
# Local port forwarding
ssh -L 8080:localhost:8000 user@remote-server.com

# Remote port forwarding
ssh -R 8080:localhost:8000 user@remote-server.com
```

## 🔧 SSH Key Management

### 1. Adding Keys to Servers

```bash
# Copy public key to server
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@remote-server.com

# Manual method
cat ~/.ssh/id_ed25519.pub | ssh user@remote-server.com "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

### 2. Key Rotation

```bash
# Generate new key
ssh-keygen -t ed25519 -C "new-key@example.com" -f ~/.ssh/id_ed25519_new

# Update authorized_keys on servers
ssh-copy-id -i ~/.ssh/id_ed25519_new.pub user@remote-server.com

# Remove old key from servers
ssh user@remote-server.com "sed -i '/old-key-fingerprint/d' ~/.ssh/authorized_keys"
```

### 3. Key Backup

```bash
# Backup SSH keys (encrypted)
tar -czf ssh-backup.tar.gz ~/.ssh/
gpg -c ssh-backup.tar.gz

# Restore from backup
gpg ssh-backup.tar.gz.gpg
tar -xzf ssh-backup.tar.gz
```

## 🛡️ Security Hardening

### 1. SSH Agent

```bash
# Start SSH agent
eval $(ssh-agent)

# Add key to agent
ssh-add ~/.ssh/id_ed25519

# List loaded keys
ssh-add -l

# Remove key from agent
ssh-add -d ~/.ssh/id_ed25519
```

### 2. Key Passphrases

```bash
# Generate key with passphrase
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519

# Add passphrase to existing key
ssh-keygen -p -f ~/.ssh/id_ed25519
```

### 3. Host Key Verification

```bash
# Check known hosts
ssh-keygen -l -f ~/.ssh/known_hosts

# Remove host from known_hosts
ssh-keygen -R hostname.com
```

## 🔍 SSH Troubleshooting

### 1. Connection Issues

```bash
# Verbose connection for debugging
ssh -v user@remote-server.com

# Test connection with specific key
ssh -i ~/.ssh/id_ed25519 -v user@remote-server.com

# Check SSH agent
ssh-add -l
```

### 2. Permission Issues

```bash
# Check file permissions
ls -la ~/.ssh/

# Fix permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_ed25519
chmod 644 ~/.ssh/id_ed25519.pub
chmod 600 ~/.ssh/config
```

### 3. Server Connection Issues

```bash
# Test server connectivity
ping remote-server.com

# Test SSH port
telnet remote-server.com 22

# Check server SSH configuration
ssh -T user@remote-server.com
```

## 📋 Security Checklist

### ✅ **Key Security**
- [ ] Use ED25519 or RSA 4096-bit keys
- [ ] Set proper file permissions (600 for private, 644 for public)
- [ ] Use strong passphrases
- [ ] Regularly rotate keys
- [ ] Backup keys securely

### ✅ **Configuration Security**
- [ ] Disable root login
- [ ] Disable password authentication
- [ ] Enable key-based authentication
- [ ] Limit connection attempts
- [ ] Use non-standard SSH port (optional)

### ✅ **Network Security**
- [ ] Use firewall rules
- [ ] Implement fail2ban
- [ ] Monitor SSH logs
- [ ] Use VPN for remote access
- [ ] Restrict SSH access to specific IPs

### ✅ **Monitoring**
- [ ] Monitor SSH logs
- [ ] Set up intrusion detection
- [ ] Regular security audits
- [ ] Keep SSH software updated

## 🚨 Security Warnings

### ❌ **Never Do This**
- Share private keys
- Use default SSH keys
- Store keys in public repositories
- Use weak passphrases
- Allow root SSH access
- Use password authentication

### ⚠️ **Security Risks**
- Key compromise
- Brute force attacks
- Man-in-the-middle attacks
- Privilege escalation
- Data exfiltration

## 📚 Additional Resources

- [OpenSSH Documentation](https://www.openssh.com/manual.html)
- [SSH Key Management](https://www.ssh.com/ssh/key/)
- [SSH Security Best Practices](https://www.ssh.com/ssh/security/)
- [Fail2ban Documentation](https://www.fail2ban.org/)

## 🔧 Quick Commands

### **Generate New Key**
```bash
ssh-keygen -t ed25519 -C "your-email@example.com" -f ~/.ssh/id_ed25519
```

### **Copy Key to Server**
```bash
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@remote-server.com
```

### **Test Connection**
```bash
ssh -T user@remote-server.com
```

### **Check Permissions**
```bash
ls -la ~/.ssh/
```

### **Start SSH Agent**
```bash
eval $(ssh-agent) && ssh-add ~/.ssh/id_ed25519
```

---

**🔐 Keep your SSH keys secure and regularly audit your SSH configuration!** 