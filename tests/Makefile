.PHONY: all
all: run-tests

.PHONY: build-tester
build-tester:
	docker build --tag falco-test-runner:latest .

.PHONY: run-tests
run-tests: build-tester
	docker run --rm \
		--privileged \
		--name falco-tester \
		-v /dev:/dev:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		falco-test-runner:latest
