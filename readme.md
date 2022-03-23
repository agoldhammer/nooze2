# nooze -- Twitter list accumulator

## Frontend and Backend

The frontend is a separate project, written in Clojurescript and designed as a single-page application.

The frontend consists of the Python app nooze, which can be configured to work with different databases in the backend and to consume different Twitter lists. See [Configuration](#configuration).

Nooze is built on top of `nzdb`, which handles all interfacing with the database. Nooze is a Web service based on `Flask 2.0`.

There is also a graph query engine, nzparse, which runs on node.

The backend is a mongodb database in a Docker container.

Currently using mongo 4.4

### Application details

`nzdb` installs several scripts used by nooze.

`readfeed` processes the Twitter list feed specified in the configuration file.

`storetopics` stores the topic list specified in `xxtopics.txt`, where `xx` designates the appropriate topic file.

`storeauths` stores the author list specified in `xxauthors.txt`.

### Building the container

docker build -t artgoldhammer/nooze310:20220227 .

The tag is constructed from the ISODATE.

### Running on cloud host

Remember to use the NZTAG env variable to specify the correct version
of the containers.

`NZTAG=<tag> docker-compose -f cloud-multi.yaml up -d`
`NZTAG=<tag> docker-compose -f cloud-multi.yaml down`
`NZTAG=<tag> docker-compose -f cloud-multi.yaml logs`

#### Configuration

Congiuration files _must_ be located in the `app/confs` directory of `noozep`.

Here is a sample docker-compose config file:

```yaml
version: "3.7"
services:
  dbhost:
    image: mongo:4.4.4-bionic
    restart: always
    container_name: dbhost
    volumes:
      - $HOME/backup:/warehouse
      - $HOME/data/db:/data/db
    ports:
      - "27018:27017"
    command: mongod --logpath=/dev/null

  usnews:
    depends_on:
      - dbhost
    image: artgoldhammer/nooze310:$NZTAG
    container_name: usnews
    restart: always
    volumes:
      - $HOME/confs:/app/confs
    environment:
      NZDBCONF: /app/confs/cloud-us.conf
    entrypoint: supervisord -n -c supervisor.ini
    ports:
      - "9090:9090"
      - "3031:3031"

  eunews:
    depends_on:
      - dbhost
    image: artgoldhammer/nooze310:$NZTAG
    container_name: eunews
    restart: always
    volumes:
      - $HOME/confs:/app/confs
    environment:
      NZDBCONF: /app/confs/cloud-eu.conf
    entrypoint: supervisord -n -c supervisor.ini
    ports:
      - "9091:9090"
      - "3032:3031"
```

And here is a sample NZDB conf:

```bash


# run database on elite, program on bach
[authentication]

OAUTH_TOKEN = mytoken
OAUTH_TOKEN_SECRET = mysecret
CONSUMER_KEY = myconsumerkey
CONSUMER_SECRET = myconsumersecret

[db]
HOST=mydbhost
DBNAME=mydbname

[authors]
authfile=~/Prog/nooze/confs/usauthors.txt

[topics]
topicsfile=~/Prog/nooze/confs/ustopics.txt

[logging]
logfile=/var/log/nooze/nooze.log
logname=mylogname

[twitter]
owner=mytwitterusername
slug=mylistname
id=myid

[app]
template-dir=~/Prog/nooze/app/templates
static-dir=~/Prog/nooze/app/static
SECRET_KEY=myflasksecret
USERNAME=myusername
PASSWORD=myflaskpassword

```

#### replacing container on website

```bash
ubuntu@ip-172-31-42-130:~$ NZTAG=20220227 docker-compose -f cloud-multi.yaml up -d
Creating network "ubuntu_default" with the default driver
Creating dbhost ... done
Creating usnews ... done
Creating eunews ... done
```

### Running locally

Use the shell script `run-local-[suffix]` in the project root directory. This connects to test backend on the local dev db machine, elite.local.
