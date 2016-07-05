#!/bin/bash

set -e

wget -qO- https://get.docker.com/ | sh
echo "DONE"

cp /etc/default/docker /tmp/docker
cat > /tmp/docker << END
    DOCKER_OPTS="--dns 8.8.8.8 --dns 8.8.4.4"
    DOCKER_OPTS="-H tcp://0.0.0.0:9999"
END
sudo mv /tmp/docker /etc/default/docker
sudo service docker restart
docker -H localhost:9999 images
