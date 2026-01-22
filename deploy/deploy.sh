#!/bin/bash
# 部署脚本 - 测试管理系统

set -e

# 配置变量
PROJECT_DIR="/var/www/testp"
FRONTEND_DIR="$PROJECT_DIR/frontend"
BACKEND_DIR="$PROJECT_DIR/backend"
NGINX_CONF="/etc/nginx/sites-available/testp"
NGINX_ENABLED="/etc/nginx/sites-enabled/testp"
SERVICE_NAME="testp-backend"

echo "========================================="
echo "测试管理系统 - 部署脚本"
echo "========================================="

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# 1. 创建项目目录
echo "创建项目目录..."
mkdir -p "$PROJECT_DIR/frontend"
mkdir -p "$PROJECT_DIR/backend"

# 2. 部署前端
echo "-----------------------------------------"
echo "部署前端..."
echo "-----------------------------------------"

# 复制构建文件
echo "复制前端构建文件..."
cp -r dist/* "$FRONTEND_DIR/"

# 设置权限
chown -R www-data:www-data "$FRONTEND_DIR"
chmod -R 755 "$FRONTEND_DIR"

# 3. 配置 Nginx
echo "-----------------------------------------"
echo "配置 Nginx..."
echo "-----------------------------------------"

# 复制 nginx 配置
cp nginx.conf "$NGINX_CONF"

# 创建符号链接启用站点
ln -sf "$NGINX_CONF" "$NGINX_ENABLED"

# 测试 nginx 配置
nginx -t

# 4. 重启 Nginx
echo "-----------------------------------------"
echo "重启 Nginx..."
echo "-----------------------------------------"
systemctl restart nginx

# 5. 部署后端（可选）
read -p "是否部署后端服务? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "-----------------------------------------"
    echo "部署后端..."
    echo "-----------------------------------------"

    # 复制后端文件
    cp -r ../backend/* "$BACKEND_DIR/"

    # 安装依赖
    cd "$BACKEND_DIR"
    pip3 install -r requirements.txt

    # 创建 systemd 服务文件
    cat > /etc/systemd/system/$SERVICE_NAME.service << EOF
[Unit]
Description=TestP Backend Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=$BACKEND_DIR
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 $BACKEND_DIR/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # 重载并启动服务
    systemctl daemon-reload
    systemctl enable $SERVICE_NAME
    systemctl restart $SERVICE_NAME

    echo "后端服务状态:"
    systemctl status $SERVICE_NAME --no-pager
fi

echo "========================================="
echo "部署完成！"
echo "========================================="
echo "前端目录: $FRONTEND_DIR"
echo "Nginx 配置: $NGINX_CONF"
echo ""
echo "请确保："
echo "1. 已修改 nginx.conf 中的 server_name"
echo "2. 后端服务正在运行"
echo "3. 防火墙已开放 80/443 端口"
echo ""
echo "访问地址: http://your-domain.com"
