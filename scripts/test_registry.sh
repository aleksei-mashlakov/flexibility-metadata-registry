#!/bin/sh
docker-compose -f docker-compose-testing.yml build --force-rm --no-cache --pull
docker-compose -f docker-compose-testing.yml up -d
docker logs -f server
