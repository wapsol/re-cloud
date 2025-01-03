
# Docker, NGINX, & Certbot Setup Guide

This guide provides a structured and reader-friendly approach to setting up Docker, NGINX, and Certbot for your Odoo deployment. All screenshots have been converted into ASCII representations for easier reference.

---

## Table of Contents

1. [Docker](#docker)
   - [Installing Docker](#installing-docker)
   - [Installing Docker Compose](#installing-docker-compose)
   - [Testing Docker Installation](#testing-docker-installation)
   - [Setting Up Docker](#setting-up-docker)
   - [Configuring Odoo](#configuring-odoo)
   - [Finalizing Docker Setup](#finalizing-docker-setup)
2. [NGINX](#nginx)
   - [Installing NGINX](#installing-nginx)
   - [Configuring NGINX for Odoo](#configuring-nginx-for-odoo)
   - [Enabling NGINX Configuration](#enabling-nginx-configuration)
   - [Testing and Restarting NGINX](#testing-and-restarting-nginx)
3. [Certbot](#certbot)
   - [Installing Certbot](#installing-certbot)
   - [Obtaining SSL Certificate](#obtaining-ssl-certificate)
   - [Renewing SSL Certificate](#renewing-ssl-certificate)

---

## Docker

### Installing Docker

1. **Follow the official Docker installation guide for Debian:**

   [Docker Install on Debian](https://docs.docker.com/engine/install/debian/)

2. **Verify your distribution:**

   Ensure you are using the correct distribution by checking the server. For example:

   ```
   +---------------------------+
   |                           |
   |        Debian Display     |
   |                           |
   +---------------------------+
   ```

### Installing Docker Compose

1. **Follow the official Docker Compose installation guide:**

   [Docker Compose Install](https://docs.docker.com/compose/install/)

2. **Select Linux as your platform.**

### Testing Docker Installation

Ensure Docker and Docker Compose are installed correctly:

```bash
docker --version
docker-compose --version
```

*Note: You may require `sudo` privileges for these commands.*

### Setting Up Docker

1. **Create the necessary directory structure in the `/home` directory:**

   ```
   /home/
   ├── addons/
   │   └── [External addons (optional)]
   ├── config/
   │   └── odoo.conf
   ├── enterprise/
   │   └── [Clone from Odoo Enterprise Repository]
   ├── themes/
   │   └── [External themes (optional)]
   └── downloads/
   ```

   **ASCII Representation:**
   ```
   /home/
   ├── addons/
   ├── config/
   ├── enterprise/
   ├── themes/
   └── downloads/
   ```

2. **Clone the Odoo Enterprise repository using Euroblase credentials:**

   ```bash
   git clone https://github.com/odoo/enterprise.git /home/enterprise
   ```

### Configuring Odoo

1. **Create the `odoo.conf` file in the `config` directory:**

   ```
   [options]
   ; Add your Odoo configurations here
   xmlrpc_port = 8069
   addons_path = /mnt/extra-addons,/mnt/enterprise-addons,/mnt/themes
   ```

   **ASCII Representation:**
   ```
   odoo.conf
   -------------------
   [options]
   xmlrpc_port = 8069
   addons_path = /mnt/extra-addons,/mnt/enterprise-addons,/mnt/themes
   ```

   *Note: Ensure `xmlrpc_port` matches the port specified in `docker-compose.yml`, and verify that all addon paths are correct.*

### Finalizing Docker Setup

1. **Create a `docker-compose.yml` file with the following structure:**

   ````yaml:docker-compose.yml
   version: '3.1'

   services:
     web:
       image: odoo:14
       depends_on:
         - db
       ports:
         - "8099:8099"
         - "8072:8072"
       volumes:
         - odoo-web-data:/var/lib/odoo
         - ./config:/etc/odoo
         - ./addons:/mnt/extra-addons
         - ./enterprise:/mnt/enterprise-addons
         - ./themes:/mnt/themes
         - /home/selenium/downloads:/mnt/downloads
     db:
       image: postgres:13
       environment:
         - POSTGRES_DB=postgres
         - POSTGRES_PASSWORD=odoo
         - POSTGRES_USER=odoo
         - PGDATA=/var/lib/postgresql/data/pgdata
       volumes:
         - odoo-db:/var/lib/postgresql/data

   volumes:
     odoo-db-data: 
     odoo-web-data:
   ````

   *Note: The additional mapped folder `/home/selenium/downloads` is not required and can be removed if unnecessary.*

2. **Set Up Resource Limits:**

   Use the provided script to determine the exact numbers based on your configuration:

   ```bash
   sudo apt install bc
   chmod +x limit_script.sh
   ./limit_script.sh
   ```

   *If multiple cron jobs are running, consider increasing `limit_time_cpu` and `limit_time_real` by adding additional zeros.*

   For more details, refer to the [Odoo Deployment Documentation](https://www.odoo.com/documentation/14.0/administration/install/deploy.html).

3. **Start Docker Containers:**

   ```bash
   docker-compose up -d
   ```

   *The `-d` flag runs the Docker containers in the background.*

---

## NGINX

### Installing NGINX

Install NGINX using the package manager:

```bash
sudo apt install nginx
```

### Configuring NGINX for Odoo

1. **Navigate to the NGINX sites-available directory:**

   ```bash
   cd /etc/nginx/sites-available/
   ```

2. **Create a new configuration file named after your desired URL:**

   ```bash
   sudo touch your_domain.conf
   ```

3. **Add the following configuration to the file:**

   ```nginx:your_domain.conf
   upstream odoo {
       server 127.0.0.1:8069;
   }

   server {
       listen 80;
       server_name your_domain.com;

       access_log /var/log/nginx/odoo_access.log;
       error_log /var/log/nginx/odoo_error.log;

       proxy_buffers 16 64k;
       proxy_buffer_size 128k;

       location / {
           proxy_pass http://odoo;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Host $server_name;
       }

       location /longpolling {
           proxy_pass http://odoo;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Host $server_name;
       }

       # Add other necessary configurations here
   }
   ```

   *Ensure that the `upstream odoo` section maps to the correct port specified in your `docker-compose.yml`.*

### Enabling NGINX Configuration

1. **Create a symbolic link to enable the site:**

   ```bash
   sudo ln -s /etc/nginx/sites-available/your_domain.conf /etc/nginx/sites-enabled/
   ```

### Testing and Restarting NGINX

1. **Test the NGINX configuration for syntax errors:**

   ```bash
   sudo nginx -t
   ```

2. **If the configuration is correct, restart NGINX:**

   ```bash
   sudo service nginx restart
   ```

   **ASCII Representation:**
   ```
   Testing NGINX Configuration:
   +-----------------------+
   | Syntax Ok             |
   | Test Successful       |
   +-----------------------+

   Restarting NGINX:
   +-----------------------+
   | NGINX Restarted       |
   | Service Status: Active|
   +-----------------------+
   ```

---

## Certbot

### Installing Certbot

Install Certbot along with the NGINX plugin:

```bash
sudo apt install python-certbot-nginx
```

### Obtaining SSL Certificate

1. **Run Certbot to obtain and install the SSL certificate:**

   ```bash
   sudo certbot --nginx -d your_domain.com
   ```

2. **Follow the prompts:**

   - **Enter your email address.**
   - **Agree to the terms of service.**
   - **Choose to redirect HTTP traffic to HTTPS (option 2).**

   **ASCII Representation:**
   ```
   Certbot Prompt:
   +-------------------------------------------+
   | Enter Email: user@example.com             |
   | Agree to Terms of Service: [Yes]          |
   | Redirect HTTP to HTTPS: [2]                |
   +-------------------------------------------+
   ```

3. **Verify NGINX Configuration:**

   ```bash
   sudo nginx -t
   ```

4. **Restart NGINX to apply changes:**

   ```bash
   sudo service nginx restart
   ```

### Renewing SSL Certificate

Set up automatic renewal by running:

```bash
sudo certbot renew
```

*It's recommended to add a cron job to automate this process.*

---

# Additional Notes

- **Dependencies:**
  - Ensure all dependencies like `bc` are installed.
  - Maintain proper folder permissions and ownership as required by Docker and Odoo.
  
- **Repository Access:**
  - Clone the Odoo Enterprise repository using valid Euroblase credentials to access enterprise features.

- **Resource Management:**
  - Adjust CPU and real-time limits based on your server's capacity and workload.

- **Security:**
  - Regularly update Docker, NGINX, and Certbot to their latest versions to ensure security patches are applied.

---

# Troubleshooting

- **Docker Issues:**
  - If containers fail to start, check logs using:
    ```bash
    docker-compose logs
    ```
  
- **NGINX Configuration Errors:**
  - Re-examine the `your_domain.conf` file for syntax errors.
  - Ensure that the upstream port matches the one defined in `docker-compose.yml`.

- **SSL Certificate Problems:**
  - Verify that DNS records for your domain are correctly pointing to your server.
  - Ensure that ports 80 and 443 are open and accessible.

---

For more detailed information, refer to the official documentation links provided in each section.