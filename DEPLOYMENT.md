# DigitalOcean Deployment Guide

This guide walks you through deploying the Order Orchestration system to a DigitalOcean Droplet for demo purposes.

## Prerequisites

- DigitalOcean account (get $200 free credit at digitalocean.com)
- Git installed locally
- SSH client (Terminal on Mac/Linux, PowerShell/WSL on Windows)

---

## Step 1: Create a DigitalOcean Droplet

1. **Sign up for DigitalOcean**
   - Go to https://digitalocean.com
   - Sign up and get $200 free credit (valid for 60 days)

2. **Create a new Droplet**
   - Click "Create" → "Droplets"
   - **Image**: Ubuntu 22.04 LTS x64
   - **Plan**: Basic
   - **CPU Options**: Regular (Disk type: SSD)
   - **Size**: $12/month - 2 GB RAM / 1 CPU / 50 GB SSD
   - **Datacenter**: Choose closest to your users
   - **Authentication**:
     - Choose "SSH Key" (recommended) or "Password"
     - If SSH Key: Add your public key (`cat ~/.ssh/id_rsa.pub`)
   - **Hostname**: order-orchestrator-demo
   - Click "Create Droplet"

3. **Note your Droplet's IP address**
   - It will appear in your dashboard (e.g., `164.90.123.45`)
   - You'll use this to access your app

---

## Step 2: Connect to Your Droplet

Open your terminal and SSH into the droplet:

```bash
ssh root@YOUR_DROPLET_IP
```

Replace `YOUR_DROPLET_IP` with your actual IP address.

---

## Step 3: Install Docker and Docker Compose

Run these commands on your droplet:

```bash
# Update package index
apt update

# Install required packages
apt install -y apt-transport-https ca-certificates curl software-properties-common

# Add Docker GPG key
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

# Add Docker repository
add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"

# Update package index again
apt update

# Install Docker
apt install -y docker-ce docker-ce-cli containerd.io

# Install Docker Compose
apt install -y docker-compose-plugin

# Verify installation
docker --version
docker compose version
```

You should see version output for both Docker and Docker Compose.

---

## Step 4: Clone Your Repository

```bash
# Install git if needed
apt install -y git

# Clone your repository
git clone https://github.com/YOUR_USERNAME/temporal-order-orchestrator.git

# Navigate to the project
cd temporal-order-orchestrator
```

**Alternative**: If your repo is private or you prefer to upload files:

```bash
# On your local machine, create a tarball
tar -czf project.tar.gz temporal-order-orchestrator/

# Upload to droplet
scp project.tar.gz root@YOUR_DROPLET_IP:~

# On droplet, extract
tar -xzf project.tar.gz
cd temporal-order-orchestrator
```

---

## Step 5: Configure Environment Variables

```bash
# Copy the production environment template
cp .env.production .env

# Edit the environment file
nano .env
```

Update the `DB_PASSWORD` to a secure password:

```bash
DB_PASSWORD=your_secure_random_password_here
```

Save and exit (Ctrl+X, then Y, then Enter).

**Security Tip**: Generate a strong password:
```bash
openssl rand -base64 32
```

---

## Step 6: Build and Start All Services

```bash
# Build Docker images (this takes 5-10 minutes first time)
docker compose -f docker-compose.production.yml build

# Start all services in detached mode
docker compose -f docker-compose.production.yml up -d

# Check that all containers are running
docker compose -f docker-compose.production.yml ps
```

You should see 7 containers running:
- `order-db` - Application database
- `temporal-db` - Temporal database
- `temporal` - Temporal server
- `temporal-ui` - Temporal web UI
- `order-worker` - Temporal workers
- `order-api` - FastAPI backend
- `order-frontend` - React frontend with Nginx

---

## Step 7: Setup Search Attributes

Wait 30 seconds for Temporal to fully start, then register search attributes:

```bash
# Wait for Temporal to be ready
sleep 30

# Register search attributes (using docker exec)
docker exec temporal tctl admin cluster add-search-attributes \
  --name CustomerId --type Keyword

docker exec temporal tctl admin cluster add-search-attributes \
  --name CustomerName --type Text

docker exec temporal tctl admin cluster add-search-attributes \
  --name OrderTotal --type Double

docker exec temporal tctl admin cluster add-search-attributes \
  --name Priority --type Keyword

# Verify search attributes
docker exec temporal tctl admin cluster get-search-attributes
```

You should see your custom search attributes listed.

---

## Step 8: Configure Firewall (Optional but Recommended)

```bash
# Install UFW firewall
apt install -y ufw

# Allow SSH (IMPORTANT: do this first!)
ufw allow 22/tcp

# Allow HTTP (frontend)
ufw allow 80/tcp

# Allow Temporal UI (optional, for monitoring)
ufw allow 8080/tcp

# Enable firewall
ufw --force enable

# Check status
ufw status
```

---

## Step 9: Access Your Application

Your application is now live! Access it via:

### **Frontend Dashboard**
```
http://YOUR_DROPLET_IP
```

### **API Documentation**
```
http://YOUR_DROPLET_IP:8000/docs
```

### **Temporal UI** (for monitoring workflows)
```
http://YOUR_DROPLET_IP:8080
```

---

## Step 10: Test the Application

1. **Open the frontend**: `http://YOUR_DROPLET_IP`

2. **Create a customer**:
   - Navigate to "Customers" page
   - Click "Create Customer"
   - Fill in details and submit

3. **Start an order workflow**:
   - Navigate to "Orders" page
   - Click "Start New Order"
   - Select a customer and enter order details
   - Submit to start the workflow

4. **Approve the order**:
   - The workflow will wait for manual approval
   - Click "Approve" button in the order detail view
   - Watch the workflow progress through the stages

5. **Monitor in Temporal UI**:
   - Go to `http://YOUR_DROPLET_IP:8080`
   - Click "Workflows" to see all running/completed workflows
   - Click on a workflow ID to see detailed execution history

---

## Useful Commands

### View Logs
```bash
# All services
docker compose -f docker-compose.production.yml logs -f

# Specific service
docker compose -f docker-compose.production.yml logs -f api
docker compose -f docker-compose.production.yml logs -f worker
docker compose -f docker-compose.production.yml logs -f frontend
```

### Restart Services
```bash
# Restart all
docker compose -f docker-compose.production.yml restart

# Restart specific service
docker compose -f docker-compose.production.yml restart api
```

### Stop Services
```bash
docker compose -f docker-compose.production.yml down
```

### Rebuild After Code Changes
```bash
# Pull latest code
git pull

# Rebuild and restart
docker compose -f docker-compose.production.yml up -d --build
```

### Check Database
```bash
# Connect to PostgreSQL
docker exec -it order-db psql -U trellis -d trellis

# Run SQL queries
SELECT * FROM customers;
SELECT * FROM orders;
SELECT * FROM payments;
SELECT * FROM events;

# Exit
\q
```

---

## Optional: Add a Custom Domain

### Using a Free Domain (DuckDNS)

1. Go to https://www.duckdns.org
2. Sign in with any account
3. Create a subdomain: `your-demo.duckdns.org`
4. Set the IP to your droplet IP
5. Access your app at: `http://your-demo.duckdns.org`

### Using Your Own Domain

1. **Add DNS A Record**:
   - In your domain registrar (Namecheap, GoDaddy, etc.)
   - Create an A record pointing to your droplet IP
   - Example: `demo.yourdomain.com` → `YOUR_DROPLET_IP`

2. **Wait for DNS propagation** (5-30 minutes)

3. **Access your app**: `http://demo.yourdomain.com`

---

## Troubleshooting

### Services Won't Start

```bash
# Check which services are failing
docker compose -f docker-compose.production.yml ps

# Check logs for errors
docker compose -f docker-compose.production.yml logs
```

### Frontend Shows 404 or Blank Page

```bash
# Check if frontend container is running
docker ps | grep frontend

# Rebuild frontend
docker compose -f docker-compose.production.yml up -d --build frontend
```

### API Not Responding

```bash
# Check API logs
docker compose -f docker-compose.production.yml logs api

# Check if API can connect to Temporal
docker exec order-api curl -s temporal:7233
```

### Workers Not Processing Tasks

```bash
# Check worker logs
docker compose -f docker-compose.production.yml logs worker

# Verify Temporal is healthy
docker exec temporal tctl workflow list
```

### Database Connection Issues

```bash
# Check database is healthy
docker exec order-db pg_isready -U trellis

# Check environment variables
docker compose -f docker-compose.production.yml exec api env | grep DB_
```

### Out of Memory

If you see OOM (Out of Memory) errors:

1. Upgrade to 4GB droplet ($24/month)
2. Or reduce container resource usage by stopping Temporal UI:
   ```bash
   docker stop temporal-ui
   ```

---

## Monitoring and Maintenance

### Check Disk Space
```bash
df -h

# Clean up old Docker images/containers
docker system prune -a
```

### View Resource Usage
```bash
# Install htop
apt install -y htop

# Monitor resources
htop
```

### Backup Database
```bash
# Backup orders database
docker exec order-db pg_dump -U trellis trellis > backup_$(date +%Y%m%d).sql

# Download to local machine
scp root@YOUR_DROPLET_IP:~/backup_*.sql .
```

### Update Application
```bash
# Pull latest changes
cd temporal-order-orchestrator
git pull

# Rebuild and restart
docker compose -f docker-compose.production.yml up -d --build
```

---

## Cost Breakdown

**DigitalOcean Droplet (2GB)**: $12/month

**With $200 free credit**: Free for ~16 months

**After credit expires**: $12/month (cancel anytime)

---

## Security Recommendations

For a production deployment (beyond demo):

1. **Enable HTTPS**:
   - Use Let's Encrypt with Certbot
   - Add SSL certificates to Nginx

2. **Secure passwords**:
   - Use long random passwords
   - Store in environment variables

3. **Database backups**:
   - Set up automated backups
   - DigitalOcean offers automatic backups (+20% cost)

4. **Monitoring**:
   - Set up uptime monitoring
   - Configure log aggregation

5. **Updates**:
   - Keep Docker images updated
   - Apply security patches regularly

---

## Support

If you encounter issues:

1. Check logs: `docker compose -f docker-compose.production.yml logs`
2. Verify all containers are healthy: `docker ps`
3. Check the Temporal UI for workflow errors: `http://YOUR_DROPLET_IP:8080`
4. Review application logs in `/var/log/`

---

## Summary

You've successfully deployed the Order Orchestration system to DigitalOcean!

**Your URLs**:
- Frontend: `http://YOUR_DROPLET_IP`
- API Docs: `http://YOUR_DROPLET_IP:8000/docs`
- Temporal UI: `http://YOUR_DROPLET_IP:8080`

Share the frontend URL with your demo users and they can start creating customers and processing orders!
