#!/bin/bash

set -e

wget -qO- https://get.docker.com/ | sh

echo -e "[Unit]
Description=Docker Application Container Engine
Documentation=https://docs.docker.com
After=network.target docker.socket
Requires=docker.socket
[Service]
Type=notify
# the default is not to use systemd for cgroups because the delegate issues still
# exists and systemd currently does not support the cgroup feature set required
# for containers run by docker
ExecStart=/usr/bin/docker daemon -H fd:// --dns 8.8.8.8 --dns 8.8.4.4 -H tcp://0.0.0.0:9999
MountFlags=slave
LimitNOFILE=1048576
LimitNPROC=1048576
LimitCORE=infinity
TimeoutStartSec=0
# set delegate yes so that systemd does not reset the cgroups of docker containers
Delegate=yes
[Install]
WantedBy=multi-user.target" | sudo tee -a /lib/systemd/system/docker.service.new


sudo mv /lib/systemd/system/docker.service.new /lib/systemd/system/docker.service
sudo systemctl daemon-reload
sudo systemctl restart docker

docker -H localhost:9999 images
