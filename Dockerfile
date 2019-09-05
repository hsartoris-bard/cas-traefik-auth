FROM python:3.7-alpine

ENV INSTALL_PATH /bip
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY . .
RUN apk add --no-cache --virtual .build-deps build-base \
	&& pip install -r requirements.txt \
	&& find /usr/local \
		\( -type d -a -name test -o -name tests \) \
		-o \( -type f -a -name '*.pyc' -o -name '*.pyo' \) \
		-exec rm -rf '{}' + \
	&& runDeps="$( \
		scanelf --needed --nobanner --recursive /usr/local \
			| awk '{ gsub(/,/, "\nso:", $2); print "so:" $2}' \
			| sort -u \
			| xargs -r apk info --installed \
			| sort -u \
		)" \
	&& apk add --virtual .rundeps $runDeps \
	&& apk del .build-deps

ENTRYPOINT gunicorn -w 1 -b 0.0.0.0:8080 app:app
