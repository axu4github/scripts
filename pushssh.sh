#!/bin/bash

if [ ! $1 ]; then
  echo "usage: pushssh.sh user@remoteserver "
  exit
fi

PORT=22

if [ $2 ]; then
   PORT=$2
fi

echo $1 $PORT

# Uploads your id_rsa.pub to the specified host, wrapped for readability

if [ ! -r ${HOME}/.ssh/id_rsa.pub ]; then
  ssh-keygen -b 2048 -t rsa
fi

# Make sure auth file exists and chmod to 600

ssh $1 -p $PORT 0> echo "mkdir ~/.ssh; touch ~/.ssh/authorized_keys; 
chmod u+rw .ssh/authorized_keys"

# Append to the copy on the remote server

cat ~/.ssh/id_rsa.pub | ssh $1 -p $PORT "cat - >> .ssh/authorized_keys"

if [ $? -eq 0 ]; then
 echo "Success"
fi

