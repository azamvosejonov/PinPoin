#!/bin/bash
# PinPoint deploy script — uzbek-intelligence.uz

set -e

echo "=== 1. Docker tekshirish ==="
if ! command -v docker &> /dev/null; then
    echo "Docker o'rnatilmoqda..."
    curl -fsSL https://get.docker.com | sh
    systemctl start docker
    systemctl enable docker
fi

echo "=== 2. Nginx tekshirish ==="
if ! command -v nginx &> /dev/null; then
    apt update -q && apt install -y nginx certbot python3-certbot-nginx
fi

echo "=== 3. Nginx config ==="
cat > /etc/nginx/sites-available/pinpoint << 'NGINX'
server {
    listen 80;
    server_name uzbek-intelligence.uz www.uzbek-intelligence.uz;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/pinpoint /etc/nginx/sites-enabled/pinpoint
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx
echo "✓ Nginx sozlandi"

echo "=== 4. SSL (HTTPS) ==="
certbot --nginx -d uzbek-intelligence.uz -d www.uzbek-intelligence.uz \
    --non-interactive --agree-tos --email admin@uzbek-intelligence.uz \
    --redirect || echo "SSL keyinroq qo'lda sozlang: certbot --nginx -d uzbek-intelligence.uz"

echo "=== 5. PinPoint ishga tushirish ==="
cd /root/PinPoint 2>/dev/null || cd ~/PinPoint 2>/dev/null || {
    echo "PinPoint papkasi topilmadi! Avval kodni yuklang."
    exit 1
}

docker compose up -d --build

echo ""
echo "✅ Hammasi tayyor!"
echo "   http://uzbek-intelligence.uz"
echo "   https://uzbek-intelligence.uz/docs"
