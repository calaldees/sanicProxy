DOCKER_IMAGE:=proxy
DOCKER_RUN:=docker run --rm -it --publish 9100:8000 ${DOCKER_IMAGE}

proxy: build
	${DOCKER_RUN}

shell:
	${DOCKER_RUN} /bin/sh

build:
	docker build --tag ${DOCKER_IMAGE} .

run:
	python3 -m http.server 8002
