# Docker Guide For BookdlBot 🐳 #

Credits for guide: [megadlbot](https://github.com/eyaadh/megadlbot_oss/blob/master/DockerReadme.md) project

## Install docker ##

- Follow the official docker [installation guide](https://docs.docker.com/engine/install/)

## Install Docker-compose ##

- Easiest way to install docker-compose is <br>
```sudo pip install docker-compose```
- Also you can check other official methods of installing docker-compose [here](https://docs.docker.com/compose/install/)

## Run Bookdlbot ##

- We dont need to clone the repo (yeah Docker-compose does that for us)
- Setup configs (the 2 files in `docker` folder)
    - Download the sample config file <br>
        - ```mkdir bookdlbot && cd bookdlbot``` <br> Create and change to a working directory
        - ```wget https://github.com/Samfun75/bookdlbot/raw/master/docker/docker-config.ini.sample -O docker-config.ini``` <br> Download docker-config.ini file
        - ```vim docker-config.ini``` <br> Fill all the variables witht correct values and save

    - Download the yml file for docker-compose
        - ```wget https://github.com/Samfun75/bookdlbot/raw/master/docker/docker-compose.yml``` <br> Download docker-comose.yml
- Finally start the bot <br>
```docker-compose up -d```
- Voila !! The bot should be running now <br>
Check logs with ```docker-compose logs -f```

## How to stop the bot ##
- Stop Command
    - ```docker-compose stop``` <br> This will just stop the containers. Built images won't be removed. <br> So next time you can start with ``docker-compose start`` command and it will start up quickly.

- Down command
    - ```docker-compose down``` <br> This will stop and delete the built images. So next time you have to do ``docker-compose up -d`` to start the build and start the bot.
