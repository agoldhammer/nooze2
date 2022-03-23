
#! /bin/bash
export NZDBCONF=~/Prog/nooze/confs/bach.conf
docker run --name dbhost -d -p 27017:27017 -v ~/data:/data/db mongo
