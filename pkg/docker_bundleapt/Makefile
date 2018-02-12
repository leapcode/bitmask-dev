IMAGE=bitmask-bundler-apt

# for leap registry

build:
	docker build -t 0xacab.org:4567/leap/docker/$(IMAGE):latest .
push:
	docker push 0xacab.org:4567/leap/docker/$(IMAGE):latest
login:
	docker login 0xacab.org:4567

# for local tests

bundler:
	docker build -t $(IMAGE) .
shell:
	docker run -i -t $(IMAGE) bash
bundle:
	echo "cd /src/leap/bitmask-dev && VIRTUAL_ENV=/usr/local make bundle && cp -r dist/* /dist" | docker run -i -v /srv/bitmask-builds:/dist -w /dist $(IMAGE) bash

