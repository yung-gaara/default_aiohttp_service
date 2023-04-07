# default_aiohttp_service
Default aiohttp service template

## Requirements
  * Python 3.10
  * Packages from ./src/server/requirements.txt and ./src/worker/requirements.txt
  * Docker
  * Docker compose

## Build images
  There is run CLI commands at project directory 
  
    docker build -t {server_name}:{tag} -f ./src/server/Dockerfile .
    docker build -t {worker_name}:{tag} -f ./src/worker/Dockerfile .

## Deploy
  There is set environment variables at .env file
  
  There is run CLI command at deploy directory

    docker-compose up -d
