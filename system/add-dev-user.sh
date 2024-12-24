#!/bin/bash
if [ -z "$1" ] || [ -z "$2" ]
then
  read -p "Username: " NAME
  read -p "Publickey: " PUBKEY
else
  NAME=$1
  PUBKEY=$2
fi

echo "Creating and adding permission for user $NAME"
sudo adduser --shell /bin/bash --gecos "" --disabled-password $NAME
sudo -u $NAME mkdir -p /home/$NAME/.ssh
sudo -u $NAME echo $PUBKEY > /home/$NAME/.ssh/authorized_keys
sudo -i echo "$NAME ALL=(ALL) NOPASSWD: /usr/bin/docker" > /etc/sudoers.d/$NAME
sudo -i chown $NAME:$NAME /home/$NAME/.ssh/authorized_keys