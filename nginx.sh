sudo nano /etc/nginx/sites-available/articles.nexuscale.ai 

```
server {
    listen 80;
    listen [::]:80;

    server_name  articles.nexuscale.ai;

    root /var/www/html/myhela;  # Update the path to your website's root directory
    index index.html index.htm;

    location / {
        proxy_pass http://127.0.0.1:7000;  # Update with your application's address
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }


    # Additional configurations can be added here, such as SSL/TLS settings or PHP handling
}

```

sudo rm /etc/nginx/sites-enabled/articles.nexuscale.ai 

sudo ln -s /etc/nginx/sites-available/articles.nexuscale.ai  /etc/nginx/sites-enabled/

sudo certbot --nginx -d articles.nexuscale.ai -d www.articles.nexuscale.ai

sudo nginx -t

sudo systemctl reload nginx

