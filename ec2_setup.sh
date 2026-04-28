#!/bash/bin
# 🧠 CustomerIQ — AWS EC2 Setup Script (Ubuntu 22.04 LTS)
# Usage: curl -sSL https://raw.githubusercontent.com/user/repo/main/ec2_setup.sh | bash

set -e # Exit on error

echo "🚀 Starting CustomerIQ Enterprise Deployment..."

# 1. Update system
sudo apt-get update -y
sudo apt-get upgrade -y

# 2. Install Docker
if ! command -v docker &> /dev/null; then
    echo "🐳 Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
fi

# 3. Install Docker Compose
if ! command -v docker-compose &> /dev/null; then
    echo "📦 Installing Docker Compose..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

# 4. Clone Repository (User should replace with actual URL)
if [ ! -d "customeriq" ]; then
    echo "📂 Cloning Repository..."
    # Replace the URL below with your actual private/public repository URL
    # git clone https://github.com/yourusername/customeriq.git
    mkdir -p customeriq
fi

cd customeriq

# 5. Create .env template (if not exists)
if [ ! -f ".env" ]; then
    echo "📝 Creating .env template... PLEASE EDIT THIS FILE MANUALLY!"
    cat <<EOF > .env
# Database
DATABASE_URL=postgresql://user:pass@host:5432/postgres

# Supabase
SUPABASE_URL=https://your-proj.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_JWT_SECRET=your-jwt-secret

# Application
API_BASE_URL=http://localhost/api/v1
REDIS_URL=redis://redis:6379/0
LOG_JSON=true
DEBUG=false
EOF
fi

# 6. Launch Platform
echo "🚢 Launching CustomerIQ via Docker Compose..."
sudo docker-compose up -d --build

echo "✅ Deployment Complete!"
echo "Dashboard: http://\$(curl -s ifconfig.me)"
echo "Next Steps: Edit the .env file with production credentials and run 'docker-compose restart'"
