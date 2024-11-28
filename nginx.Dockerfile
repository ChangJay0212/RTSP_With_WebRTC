FROM nginx:latest

# Mapping HLS 
COPY hls /usr/share/nginx/html/hls

# Nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf
