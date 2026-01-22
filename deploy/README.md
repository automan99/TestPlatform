# 生产环境部署指南

## 目录结构

```
testp/
├── frontend/          # 前端项目
│   ├── dist/         # 构建输出目录
│   └── ...
├── backend/          # 后端项目
├── deploy/           # 部署相关文件
│   ├── nginx.conf    # Nginx 配置
│   ├── deploy.sh     # 部署脚本
│   └── README.md     # 本文档
```

## 前端配置

### 环境变量

前端使用环境变量配置 API 地址：

- `.env.development` - 开发环境
- `.env.production` - 生产环境

```bash
# .env.production
VITE_API_BASE_URL=/api
VITE_APP_TITLE=测试管理系统
```

### 如果后端在独立服务器

修改 `.env.production`：

```bash
# 直接指向后端服务器地址
VITE_API_BASE_URL=https://api.your-domain.com
```

同时需要配置后端服务器的 CORS：

```python
# backend/app/__init__.py
CORS(app, resources={
    r"/api/*": {
        "origins": ["https://your-domain.com"],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})
```

### 构建前端

```bash
cd frontend

# 安装依赖
npm install

# 生产构建
npm run build

# 构建输出在 dist/ 目录
```

## Nginx 配置

### 基本配置

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /var/www/testp/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # API 代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

### HTTPS 配置（推荐）

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 部署步骤

### 方式一：使用部署脚本

```bash
cd deploy
sudo bash deploy.sh
```

### 方式二：手动部署

#### 1. 前端部署

```bash
# 构建前端
cd frontend
npm run build

# 复制到服务器
scp -r dist/* user@server:/var/www/testp/frontend/dist/
```

#### 2. 后端部署

```bash
# 复制后端文件
scp -r backend/* user@server:/var/www/testp/backend/

# SSH 登录服务器
ssh user@server

# 安装依赖
cd /var/www/testp/backend
pip3 install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件配置数据库等

# 初始化数据库
flask db upgrade

# 启动服务（使用 systemd）
sudo systemctl start testp-backend
```

#### 3. 配置 Nginx

```bash
# 复制配置文件
sudo cp deploy/nginx.conf /etc/nginx/sites-available/testp

# 编辑配置，修改 server_name
sudo nano /etc/nginx/sites-available/testp

# 启用站点
sudo ln -s /etc/nginx/sites-available/testp /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

## Systemd 服务配置

创建 `/etc/systemd/system/testp-backend.service`：

```ini
[Unit]
Description=TestP Backend Service
After=network.target mysql.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/testp/backend
Environment="PATH=/usr/bin"
ExecStart=/usr/bin/python3 /var/www/testp/backend/run.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl enable testp-backend
sudo systemctl start testp-backend
sudo systemctl status testp-backend
```

## 常见问题

### 1. 刷新页面 404

确保 nginx 配置中包含：

```nginx
try_files $uri $uri/ /index.html;
```

### 2. API 请求失败

检查：

- nginx 代理配置是否正确
- 后端服务是否运行
- 防火墙是否开放端口
- CORS 配置（如果前后端分离）

### 3. 静态资源加载失败

检查：

- 文件路径是否正确
- nginx root 路径配置
- 文件权限（755）

### 4. WebSocket 连接失败

nginx 需要额外配置：

```nginx
proxy_http_version 1.1;
proxy_set_header Upgrade $http_upgrade;
proxy_set_header Connection "upgrade";
```

## 性能优化

### 1. 启用 Gzip 压缩

```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
```

### 2. 静态资源缓存

```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. 启用 HTTP/2

```nginx
listen 443 ssl http2;
```

## 安全建议

1. 使用 HTTPS
2. 启用 HSTS
3. 配置防火墙
4. 定期更新系统
5. 使用强密码
6. 禁用目录浏览
7. 限制请求大小
