FROM alpine
#FROM node:9-alpine
#FROM resin/raspberry-pi-alpine

ENV PATH="/usr/bin:$PATH"

RUN apk add --no-cache make gcc g++ python linux-headers udev build-base openssl-dev ffmpeg supervisor git \
    && git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git /opt/nginx-rtmp-module \
    && apk del git

WORKDIR /tmp

RUN wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.41.tar.gz
RUN tar xf pcre-8.41.tar.gz
RUN cd pcre-8.41 && ./configure && make && make install

ADD http://nginx.org/download/nginx-1.14.0.tar.gz .
RUN tar xf nginx-1.14.0.tar.gz
RUN mv /tmp/nginx-1.14.0 /opt/

WORKDIR /tmp
ADD https://nodejs.org/dist/v10.0.0/node-v10.0.0-linux-armv7l.tar.xz .
RUN tar xpvf node-v10.0.0-linux-armv7l.tar.xz -C /opt
ENV PATH="/opt/node-v10.0.0-linux-armv7l/bin:$PATH"

WORKDIR /opt/nginx-1.14.0

RUN ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module
RUN make
RUN make install

WORKDIR /opt/node-v10.0.0-linux-armv7l

COPY static /usr/share/nginx/html
COPY nginx-conf /etc/nginx/nginx.conf

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install
COPY server.js .

COPY start-node.sh start-ffmpeg.sh start-nginx.sh /usr/bin/
RUN chmod a+x /usr/bin/start-node.sh \
  && chmod a+x /usr/bin/start-ffmpeg.sh \
  && chmod a+x /usr/bin/start-nginx.sh
RUN mkdir -p /var/log/supervisord/
COPY supervisord.conf /etc/supervisord.conf
EXPOSE 8080

CMD ["supervisord", "--nodaemon", "--configuration", "/etc/supervisord.conf"]
#CMD /usr/local/nginx/sbin/nginx -g 'daemon off;' -c /etc/nginx/nginx.conf \
#    & ffmpeg -re -f video4linux2 -i /dev/video0 -vcodec libx264 \
#    -vprofile baseline -preset veryfast -acodec aac -strict -2 -f flv -pix_fmt yuv420p -bufsize 6000k rtmp://localhost/show/stream
