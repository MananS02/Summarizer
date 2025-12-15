# Deployment Guide

## Prerequisites

- Node.js 18+ installed
- Python 3.14+ installed
- MongoDB running (local or Atlas)
- Azure OpenAI API access
- PM2 installed globally: `npm install -g pm2`

## Quick Deployment Steps

### 1. Clone and Install

```bash
git clone https://github.com/MananS02/Summarizer.git
cd Summarizer
npm install
```

### 2. Set Up Python Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install pymupdf openai python-dotenv
```

### 3. Configure Environment

```bash
cp .env.example .env
nano .env  # Edit with your credentials
```

**Required variables:**
- `MONGODB_URI` - Your MongoDB connection string
- `AZURE_OPENAI_GPT_ENDPOINT` - Azure OpenAI endpoint
- `AZURE_OPENAI_GPT_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_GPT_DEPLOYMENT` - Deployment name (e.g., gpt-4)

### 4. Create Logs Directory

```bash
mkdir -p logs
```

### 5. Start with PM2

```bash
# Production mode
pm2 start ecosystem.config.js --env production

# View logs
pm2 logs pdf-learning-platform

# Monitor
pm2 monit

# Stop
pm2 stop pdf-learning-platform

# Restart
pm2 restart pdf-learning-platform
```

### 6. Set PM2 to Start on Boot

```bash
pm2 startup
pm2 save
```

## Platform-Specific Deployment

### Heroku

1. **Create Heroku app**
```bash
heroku create your-app-name
```

2. **Add buildpacks**
```bash
heroku buildpacks:add heroku/nodejs
heroku buildpacks:add heroku/python
```

3. **Set environment variables**
```bash
heroku config:set MONGODB_URI=your_mongodb_uri
heroku config:set AZURE_OPENAI_GPT_ENDPOINT=your_endpoint
heroku config:set AZURE_OPENAI_GPT_KEY=your_key
heroku config:set AZURE_OPENAI_GPT_DEPLOYMENT=gpt-4
heroku config:set NODE_ENV=production
```

4. **Deploy**
```bash
git push heroku main
```

### AWS EC2

1. **SSH into instance**
```bash
ssh -i your-key.pem ubuntu@your-instance-ip
```

2. **Install dependencies**
```bash
sudo apt update
sudo apt install -y nodejs npm python3 python3-pip mongodb
```

3. **Clone and setup** (follow Quick Deployment Steps above)

4. **Configure Nginx** (optional, for reverse proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

5. **Enable firewall**
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

### DigitalOcean

1. **Create Droplet** (Ubuntu 22.04)

2. **Follow AWS EC2 steps** (same process)

3. **Optional: Use App Platform**
   - Connect GitHub repo
   - Auto-deploys on push
   - Set environment variables in dashboard

### Vercel (Frontend Only)

Note: Vercel doesn't support Python, so you'll need to:
1. Deploy backend separately (Heroku/AWS)
2. Update API endpoints in frontend
3. Deploy frontend to Vercel

## MongoDB Atlas Setup

1. **Create cluster** at mongodb.com/cloud/atlas

2. **Create database user**
   - Database Access → Add New Database User
   - Set username and password

3. **Whitelist IP**
   - Network Access → Add IP Address
   - For development: Allow from anywhere (0.0.0.0/0)
   - For production: Add your server's IP

4. **Get connection string**
   - Clusters → Connect → Connect your application
   - Copy connection string
   - Replace `<password>` with your password

## Health Checks

The application exposes a health check endpoint:

```bash
curl http://localhost:3000/health
```

Response:
```json
{
  "status": "ok",
  "timestamp": "2025-12-15T11:00:00.000Z",
  "uptime": 12345,
  "mongodb": "connected"
}
```

## Monitoring

### PM2 Monitoring

```bash
# Real-time monitoring
pm2 monit

# List all processes
pm2 list

# View logs
pm2 logs

# Flush logs
pm2 flush
```

### Log Files

Logs are stored in `./logs/`:
- `err.log` - Error logs
- `out.log` - Standard output
- `combined.log` - All logs

## Troubleshooting

### Application won't start

```bash
# Check PM2 logs
pm2 logs pdf-learning-platform --lines 100

# Check if port is in use
lsof -i :3000

# Verify environment variables
pm2 env 0
```

### MongoDB connection issues

```bash
# Test MongoDB connection
mongosh "your_connection_string"

# Check if MongoDB is running
sudo systemctl status mongod
```

### Python script errors

```bash
# Activate virtual environment
source venv/bin/activate

# Test Python dependencies
python3 -c "import fitz; import openai; print('OK')"

# Check Python version
python3 --version  # Should be 3.14+
```

## Security Checklist

- [ ] Change `SESSION_SECRET` in `.env`
- [ ] Use strong MongoDB password
- [ ] Enable MongoDB authentication
- [ ] Set up firewall rules
- [ ] Use HTTPS (SSL certificate)
- [ ] Restrict CORS origins
- [ ] Keep dependencies updated
- [ ] Regular backups of MongoDB
- [ ] Monitor API usage and costs

## Performance Optimization

1. **Enable MongoDB indexing**
```javascript
// In MongoDB shell
db.sections.createIndex({ documentSlug: 1, order: 1 })
db.documents.createIndex({ slug: 1 })
```

2. **Use CDN for static files** (optional)
   - Upload images to S3/Cloudinary
   - Update image URLs

3. **Enable compression**
   - Already configured in server.js

4. **Monitor memory usage**
```bash
pm2 monit
```

## Backup Strategy

### MongoDB Backup

```bash
# Backup
mongodump --uri="your_connection_string" --out=./backups/$(date +%Y%m%d)

# Restore
mongorestore --uri="your_connection_string" ./backups/20251215
```

### Automated Backups (cron)

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * mongodump --uri="your_connection_string" --out=/path/to/backups/$(date +\%Y\%m\%d)
```

## Scaling

### Horizontal Scaling

Update `ecosystem.config.js`:
```javascript
instances: 'max',  // Use all CPU cores
exec_mode: 'cluster'
```

### Load Balancer

Use Nginx or cloud load balancer to distribute traffic across multiple instances.

## Support

For issues, check:
1. PM2 logs: `pm2 logs`
2. MongoDB logs: `/var/log/mongodb/mongod.log`
3. Application logs: `./logs/`

For help, open an issue on GitHub.
