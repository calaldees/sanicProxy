DOCKER_IMAGE:=proxy
DOCKER_RUN:=docker run --rm -it --publish 9923:8000 ${DOCKER_IMAGE}

proxy: build
	${DOCKER_RUN}

build:
	docker build --tag ${DOCKER_IMAGE} .

shell:
	${DOCKER_RUN} /bin/sh
