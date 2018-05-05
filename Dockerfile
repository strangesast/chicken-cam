FROM alpine

ENV PATH="/usr/bin:$PATH"

RUN apk add --no-cache git build-base openssl-dev ffmpeg \
    && git clone https://github.com/sergey-dryabzhinsky/nginx-rtmp-module.git /opt/nginx-rtmp-module \
    && apk del git

WORKDIR /tmp

RUN wget ftp://ftp.csx.cam.ac.uk/pub/software/programming/pcre/pcre-8.41.tar.gz
RUN tar xf pcre-8.41.tar.gz
RUN cd pcre-8.41 && ./configure && make && make install

RUN wget -O /tmp/nginx.tar.gz http://nginx.org/download/nginx-1.13.4.tar.gz
RUN tar xf /tmp/nginx.tar.gz -C /opt
WORKDIR /opt/nginx-1.13.4

RUN ./configure --with-http_ssl_module --add-module=../nginx-rtmp-module
RUN make
RUN make install

COPY static /usr/share/nginx/html
COPY nginx-conf /etc/nginx/nginx.conf

EXPOSE 8080
EXPOSE 3000

CMD /usr/local/nginx/sbin/nginx -g 'daemon off;' -c /etc/nginx/nginx.conf \
    & ffmpeg -re -f video4linux2 -i /dev/video0 -vcodec libx264 \
    -vprofile baseline -preset veryfast -acodec aac -strict -2 -f flv -pix_fmt yuv420p -bufsize 6000k rtmp://localhost/show/stream
