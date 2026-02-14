#!/bin/bash

echo "🛡️  Installing Sentinel Agent..."

# 1. Setup Directories
mkdir -p /etc/sentinel
cp sentinel-wrapper.sh /usr/local/bin/sentinel-docker
chmod +x /usr/local/bin/sentinel-docker

# 2. Setup Alias (The "Hook")
# We add this to the global bashrc so it applies to all users (admins)
PROFILE_FILE="/etc/bash.bashrc"

if ! grep -q "sentinel-docker" "$PROFILE_FILE"; then
    echo "
# Sentinel Agent Hook
alias docker='/usr/local/bin/sentinel-docker'
" >> "$PROFILE_FILE"
    echo "✅ Alias added to $PROFILE_FILE"
else
    echo "ℹ️  Alias already exists."
fi

echo "🎉 Installation Complete!"
echo "Please restart your shell or run 'source /etc/bash.bashrc'"
