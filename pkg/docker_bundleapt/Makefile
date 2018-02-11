build:
	docker build -t 0xacab.org:4567/leap/docker/bitmask-bundler:latest .
push:
	docker push 0xacab.org:4567/leap/docker/bitmask-bundler:latest
login:
	docker login 0xacab.org:4567

# local tests

bundler:
	docker build -t bundler .
shell:
	docker run -i -t bundler bash
bundle:
	echo "cd /src/leap/bitmask-dev && VIRTUAL_ENV=/usr/local make bundle && cp -r dist/* /dist" | docker run -i -v /srv/bitmask-builds:/dist -w /dist bundler bash

