#!/bin/sh
docker-compose -f docker-compose-registry.yml build --force-rm --no-cache --pull
docker-compose -f docker-compose-registry.yml up -d
docker logs -f server
