#!/bin/bash
# =============================================================================
# ec2_bootstrap.sh — run ONCE on a fresh EC2 to provision the box
# =============================================================================
# Usage:
#   chmod +x ec2_bootstrap.sh && sudo ./ec2_bootstrap.sh
#
# What it does:
#   1. Installs Docker CE + Compose plugin (official Docker repo)
#   2. Adds `ubuntu` user to the `docker` group (no sudo needed)
#   3. Creates 2 GB swap file and persists in /etc/fstab
#   4. Sets vm.swappiness=10 (don't swap unless memory is tight)
#
# After reboot (or re-login):
#   docker --version
#   docker compose version
# =============================================================================
set -eu

# ---- Fail-fast if not running as root ----
if [ "$(id -u)" -ne 0 ]; then
    echo "ERROR: This script must be run as root (use sudo)." >&2
    exit 1
fi

echo "==> ec2_bootstrap: starting at $(date -u)"

# =============================================================================
# Phase 1 — Install Docker CE + Compose plugin
# =============================================================================
echo "==> Installing Docker..."

apt-get update -qq
apt-get install -y -qq ca-certificates curl

# Add Docker's official GPG key
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc

# Add the stable repository
UBUNTU_CODENAME=$(. /etc/os-release && echo "$VERSION_CODENAME")
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc]" \
    "https://download.docker.com/linux/ubuntu $UBUNTU_CODENAME stable" \
    > /etc/apt/sources.list.d/docker.list

apt-get update -qq
apt-get install -y -qq docker-ce docker-ce-cli containerd.io \
    docker-buildx-plugin docker-compose-plugin

# Let the ubuntu user run docker without sudo
usermod -aG docker ubuntu

echo "Docker $(docker --version) installed."
echo "Compose plugin: $(docker compose version)."

# =============================================================================
# Phase 2 — Swap (t3.micro has only 1 GB RAM)
# =============================================================================
echo "==> Creating 2 GB swap..."

if [ -f /swapfile ]; then
    echo "  /swapfile already exists, skipping."
else
    fallocate -l 2G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    echo "  2 GB swap created and persisted in /etc/fstab."
fi

# =============================================================================
# Phase 3 — Swappiness (avoid swapping unless necessary)
# =============================================================================
SYSCTL_SWAP="/etc/sysctl.d/99-swappiness.conf"
if [ -f "$SYSCTL_SWAP" ]; then
    echo "  Swappiness config already exists, skipping."
else
    echo 'vm.swappiness=10' > "$SYSCTL_SWAP"
    sysctl -w vm.swappiness=10
    echo "  vm.swappiness=10 set."
fi

# =============================================================================
# Phase 4 — Verify
# =============================================================================
echo ""
echo "==> Summary"
echo "  Docker         : $(docker --version 2>/dev/null || echo 'FAIL')"
echo "  Compose plugin : $(docker compose version 2>/dev/null || echo 'FAIL')"
echo "  Swap           : $(swapon --show 2>/dev/null | tail -1 || echo 'none')"
echo ""
echo "==> ec2_bootstrap: complete."
echo ""
echo "IMPORTANT: Log out and back in (or 'newgrp docker') so the 'ubuntu'"
echo "user can run docker without sudo."
