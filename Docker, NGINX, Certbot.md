# DOCKER

## Installing docker
https://docs.docker.com/engine/install/debian/
Note - make sure that the distro is correct. The link is for Debian.
When login into the server you can check the distro. Ex:

![image](https://user-images.githubusercontent.com/7826363/134019913-1917f232-659e-4194-99b1-605b65eb6c6e.png)

## Installing docker-compose 
https://docs.docker.com/compose/install/

- Make sure to select Linux

### Testing if installed correctly:
```
docker --version
docker-compose --version
Require sudo privileges
```

### Setting up docker:
Create a folder in /home directory with the following structure: 

![image](https://user-images.githubusercontent.com/7826363/134021049-af84262a-6c67-4b0c-a85e-bbc9777788ac.png)

Ex.
In the addons folder place  is for external addons (optional),
In the config folder odoo.conf file is placed.
Enterprise folder is for the enterprise addons - clone this https://github.com/odoo/enterprise repository with euroblase credentials
Themes  folder s for the external themes (optional)

docker-compose.yml has the following structure:

![image](https://user-images.githubusercontent.com/7826363/134021140-94c0da33-5615-40ca-af62-ff54aef4452b.png)

It this example there is additional mapped folder (home/selenium), which is not needed

``Odoo.conf file``

![image](https://user-images.githubusercontent.com/7826363/134021234-9866e236-e00f-45e6-86d1-75d5e8cc82c5.png)

Note: make sure that xmlrpc_port is the same in the odoo.conf file and in the docker-compos.xml file, make sure that the addons paths are correct too.

For the limit numbers use this https://gist.github.com/sauljabin/21be4f221e6080e76b3e script.

Only need to install bc (apt install bc), give it executable privileges, and run it (./), which will give you the exact number based on the configuration. If a  lot of cron jobs are running in the background make sure to add additional zeros on limit_time_cpu and limit_time_real. For more information check 
https://www.odoo.com/documentation/14.0/administration/install/deploy.html
After all of the above things are set up. Execute docker-compose up -d 
(-d is to run the dockers in the background)


# NGINX
Install Nginx apt-install Nginx
Position to /etc/nginx/sites-available/
Create an empty file and with the same name as the URL that you want the Odoo to be available.
Put this configuration into the file
https://gist.github.com/eneldoserrata/492811cf78b08f6e2e39

In the upstream odoo map the correct port from docker-compose.yml file.
Change the server_name with the URL and save the file.
Execute the following command to map the files in both folders.

```
ln -s /etc/nginx/sites-available/URL /etc/nginx/sites-enabled/
```

Check if Nginx configuration is ok
``nginx -t``

If everything is set up correctly then service nginx restart

# CERTIFICATE

```
	Install certbot apt install python-certbot-nginx 
	Then install the certificate certbot --nginx -d url
	(It is required to enter a mail and allowed to redirect all (2))
	After obtaining the certificate check the Nginx configuration again ( nginx -t )
	And restart Nginx ( service nginx restart )
	To renew the certificate certbot renew
```
