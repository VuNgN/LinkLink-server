#!/bin/bash

# SSH Agent Setup Script for GitHub
# This script sets up persistent SSH authentication

echo "🔐 Setting up SSH Agent for GitHub..."

# Start SSH agent if not running
if [ -z "$SSH_AUTH_SOCK" ]; then
    echo "Starting SSH agent..."
    eval $(ssh-agent -s)
    echo "SSH Agent started with PID: $SSH_AGENT_PID"
else
    echo "SSH Agent already running"
fi

# Add SSH keys to agent
echo "Adding SSH keys to agent..."

# Add ED25519 key (primary)
if ssh-add -l | grep -q "orangepi@orangepi5max"; then
    echo "✅ ED25519 key already loaded"
else
    ssh-add ~/.ssh/id_ed25519
    echo "✅ ED25519 key added"
fi

# Add RSA key (backup)
if ssh-add -l | grep -q "vu.nguyeenngoc@gmail.com"; then
    echo "✅ RSA key already loaded"
else
    ssh-add ~/.ssh/id_rsa
    echo "✅ RSA key added"
fi

# Test GitHub connection
echo "Testing GitHub connection..."
if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
    echo "✅ GitHub SSH connection successful!"
    echo "You can now push to GitHub without entering passwords"
else
    echo "❌ GitHub SSH connection failed"
    echo "Please check your SSH keys and GitHub configuration"
fi

# Show loaded keys
echo ""
echo "📋 Loaded SSH Keys:"
ssh-add -l

echo ""
echo "🚀 SSH Agent setup complete!"
echo "You can now use git push without authentication prompts" 