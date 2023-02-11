
FROM nginx:latest

COPY ./docker_containers/nginx/app/conf/default.template2 /etc/nginx/conf.d/default.template2
COPY ./docker_containers/nginx/app/certs/localhost.crt /etc/nginx/localhost.crt
COPY ./docker_containers/nginx/app/certs/localhost.key /etc/nginx/localhost.key
RUN cat /etc/nginx/conf.d/default.template2 > /etc/nginx/nginx.conf
CMD nginx -g 'daemon off;'
