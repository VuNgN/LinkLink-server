# 🐙 GitHub SSH Setup Guide

A comprehensive guide to safely configure SSH keys for GitHub usage with the Image Upload Server project.

## 🎯 Overview

This guide covers setting up SSH authentication for GitHub, ensuring secure repository access, and best practices for SSH key management.

## ✅ Current Status

### SSH Connection Test
```bash
$ ssh -T git@github.com
Hi VuNgN! You've successfully authenticated, but GitHub does not provide shell access.
```

**Status**: ✅ **SSH connection to GitHub is working!**

### Your SSH Keys

#### ED25519 Key (Primary - Recommended for GitHub)
```bash
# Fingerprint
256 SHA256:vzf3CN8R3/ro/29chU0B7Qo9sZxmtVRqg4/woaVfCMQ orangepi@orangepi5max (ED25519)

# Public Key
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBDkue9cD5FrkcKWeewrmUayp4LtMng+SulIrW1kiXwQ orangepi@orangepi5max
```

#### RSA Key (Backup)
```bash
# Fingerprint
4096 SHA256:R+LNz9qij1wJl8EF9UwddcRX5hONaHh+oytaVrBK1gQ vu.nguyeenngoc@gmail.com (RSA)

# Public Key
ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCi3r5swCfpfNzgAsmrLw9JIhEF/whZSscqHWVDqrvnw4oDl1eQsGWOoZUPokO9j1Jhq/L5p7WsWuvf34TjdxZAdVJxJZTVAldg0tl1tYG29NTmjO9WLmBK9MrxECehEvQhxVoX1jdZY/i4DPDZ8EnaXi4TaZelqMRHP841+SjdPLiBSuBsFdPGIL7bxtE0qY95p/qNn+cdG6LC4g8xfwEGCdbCeQg67gqo9mQYQkCsFMuN/t/AvT/nolqrl1v6/YOIYjSAkrl/WZUoZuOBsn2ZI4g9vHOiTpgKx3dEO0MvQZsTYibJtTxcIbPEuXErKjg3Bvb+nM+EYcmFrpOJ8xED2kwneotiNiPHHDmwfI8JZFBmt2FVXCUH13Iu/p/f5gXtk1NVQnujaI0Z4G+cDZ/oPAs0APInrRLTCU+5l7sMfcpr3amvKqMf9NYAl5J0aBDsUTUU6DsQW4ST8Ef0wmo210ksi7F7JKzKvJkHPm9ArHUTt53brPMoJP5VDrgE59ig1t8C0KEgc5h36OJamBMaRrTw7ZdvocrhThqoWxF+uY8xrGde80VahMbGbtIvXQUXBW7ZkyjaiqhNZxgxalE1qKdxAv98BU/HRPnrnN5F8OuEHfhzXTDMXYLKma32nvfffjpltWHOTF2H0YQpEbv9GbbuA/fZyAbJ4yaOMVWZzQ== vu.nguyeenngoc@gmail.com
```

## 🔧 GitHub SSH Configuration

### 1. SSH Config for GitHub

Your SSH config already includes GitHub configuration:

```bash
# ~/.ssh/config
Host github.com
    HostName github.com
    User git
    IdentityFile ~/.ssh/id_ed25519
    IdentityFile ~/.ssh/id_rsa
    IdentitiesOnly yes
```

### 2. Adding Keys to GitHub

#### Option A: Add ED25519 Key (Recommended)

1. **Copy your ED25519 public key**:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

2. **Add to GitHub**:
   - Go to GitHub.com → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Title: `orangepi5max-ED25519`
   - Key type: `Authentication Key`
   - Paste the public key content
   - Click "Add SSH key"

#### Option B: Add RSA Key (Backup)

1. **Copy your RSA public key**:
   ```bash
   cat ~/.ssh/id_rsa.pub
   ```

2. **Add to GitHub**:
   - Go to GitHub.com → Settings → SSH and GPG keys
   - Click "New SSH key"
   - Title: `orangepi5max-RSA`
   - Key type: `Authentication Key`
   - Paste the public key content
   - Click "Add SSH key"

## 🚀 Using SSH with GitHub

### 1. Clone Repository

```bash
# Clone using SSH
git clone git@github.com:VuNgN/image-upload-server.git

# Or for existing repository, change remote URL
git remote set-url origin git@github.com:VuNgN/image-upload-server.git
```

### 2. Push to GitHub

```bash
# Add files
git add .

# Commit changes
git commit -m "Add SSH security configuration"

# Push to GitHub
git push origin main
```

### 3. Test Connection

```bash
# Test SSH connection
ssh -T git@github.com

# Expected output:
# Hi VuNgN! You've successfully authenticated, but GitHub does not provide shell access.
```

## 🔒 Security Best Practices

### 1. Key Management

#### ✅ **Do This**
- Use ED25519 keys for new repositories
- Keep RSA keys as backup
- Regularly rotate keys
- Use descriptive key titles in GitHub
- Monitor key usage

#### ❌ **Don't Do This**
- Share private keys
- Use the same key for multiple services
- Store keys in public repositories
- Use weak passphrases
- Ignore security warnings

### 2. Repository Security

#### ✅ **Safe for Public Repositories**
- ✅ Source code
- ✅ Documentation
- ✅ Configuration examples
- ✅ README files
- ✅ License files

#### ❌ **Never Commit to Public Repositories**
- ❌ Private SSH keys
- ❌ API keys and secrets
- ❌ Database passwords
- ❌ Environment files (.env)
- ❌ Personal information

### 3. Environment Variables

Create a `.env.example` file for public repositories:

```bash
# .env.example (safe to commit)
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

```bash
# .env (never commit)
DATABASE_URL=postgresql+asyncpg://realuser:realpass@realhost:5432/realdb
SECRET_KEY=actual-secret-key-value
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
```

## 📋 GitHub SSH Checklist

### ✅ **Setup Complete**
- [x] SSH keys generated (ED25519 + RSA)
- [x] Keys moved to secure location
- [x] Proper permissions set
- [x] SSH config configured
- [x] GitHub connection tested
- [x] Keys added to GitHub account

### 🔄 **Before Pushing to GitHub**
- [ ] Review all files for sensitive data
- [ ] Check for hardcoded passwords
- [ ] Verify .gitignore includes sensitive files
- [ ] Test SSH connection
- [ ] Review commit history

### 🛡️ **Security Review**
- [ ] No private keys in repository
- [ ] No API keys in code
- [ ] No database credentials
- [ ] No personal information
- [ ] Environment variables externalized

## 🔍 Troubleshooting

### 1. SSH Connection Issues

```bash
# Test connection with verbose output
ssh -vT git@github.com

# Check SSH agent
ssh-add -l

# Restart SSH agent
eval $(ssh-agent)
ssh-add ~/.ssh/id_ed25519
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

### 3. Git Configuration

```bash
# Set Git user
git config --global user.name "VuNgN"
git config --global user.email "vu.nguyeenngoc@gmail.com"

# Check Git configuration
git config --list
```

## 🚀 Quick Commands

### **Test GitHub Connection**
```bash
ssh -T git@github.com
```

### **Clone Repository**
```bash
git clone git@github.com:VuNgN/image-upload-server.git
```

### **Change Remote URL**
```bash
git remote set-url origin git@github.com:VuNgN/image-upload-server.git
```

### **Push to GitHub**
```bash
git add .
git commit -m "Your commit message"
git push origin main
```

### **Check Remote URL**
```bash
git remote -v
```

## 📚 Additional Resources

- [GitHub SSH Documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh)
- [GitHub Security Best Practices](https://docs.github.com/en/github/authenticating-to-github/keeping-your-account-and-data-secure)
- [SSH Key Management](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

---

**🐙 Your SSH setup is ready for secure GitHub usage!** 