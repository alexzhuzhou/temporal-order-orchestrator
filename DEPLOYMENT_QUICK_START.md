# Quick Start Deployment Guide

## TL;DR - Get Your Demo Running in 15 Minutes

### 1. Create DigitalOcean Droplet
- Sign up at digitalocean.com ($200 free credit)
- Create Droplet: Ubuntu 22.04, 2GB RAM ($12/month)
- Note your IP address

### 2. Connect and Setup
```bash
# SSH into your droplet
ssh root@YOUR_DROPLET_IP

# Install Docker
apt update && apt install -y docker-ce docker-compose-plugin git

# Clone your repo
git clone https://github.com/YOUR_USERNAME/temporal-order-orchestrator.git
cd temporal-order-orchestrator
```

### 3. Configure and Deploy
```bash
# Copy environment template
cp .env.production .env

# Set a secure password
nano .env  # Change DB_PASSWORD

# Run deployment script
chmod +x deploy.sh
./deploy.sh
```

### 4. Access Your App
- **Frontend**: `http://YOUR_DROPLET_IP`
- **API Docs**: `http://YOUR_DROPLET_IP:8000/docs`
- **Temporal UI**: `http://YOUR_DROPLET_IP:8080`

---

## What Gets Deployed

```
Your Single VM (2GB RAM)
├── Frontend (React + Nginx) - Port 80
├── Backend API (FastAPI) - Port 8000
├── Workers (Python) - Internal
├── Temporal Server - Port 7233 (internal)
├── Temporal UI - Port 8080
├── App Database (PostgreSQL) - Internal
└── Temporal Database (PostgreSQL) - Internal
```

---

## Quick Commands

### View Status
```bash
docker compose -f docker-compose.production.yml ps
```

### View Logs
```bash
docker compose -f docker-compose.production.yml logs -f
```

### Restart Everything
```bash
docker compose -f docker-compose.production.yml restart
```

### Stop Everything
```bash
docker compose -f docker-compose.production.yml down
```

### Update After Code Changes
```bash
git pull
docker compose -f docker-compose.production.yml up -d --build
```

---

## Troubleshooting

**Can't access the app?**
```bash
# Check if containers are running
docker ps

# Check firewall
ufw status
ufw allow 80/tcp
```

**Services crashing?**
```bash
# View logs for errors
docker compose -f docker-compose.production.yml logs
```

**Frontend shows 404?**
```bash
# Rebuild frontend
docker compose -f docker-compose.production.yml up -d --build frontend
```

---

## Cost

- **With free credit**: FREE for 16+ months
- **After credit**: $12/month
- **Cancel anytime**: No commitment

---

For detailed instructions, see **DEPLOYMENT.md**
