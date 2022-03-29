.PHONY: all
all: run-tests

.PHONY: build-tester
build-tester:
	docker build --tag falco-test-runner:latest .

.PHONY: run-tests
run-tests: build-tester
	@mkdir -p $(CURDIR)/report
	docker run --rm \
		--privileged \
		--name falco-tester \
		-v /dev:/dev:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/report:/report \
		falco-test-runner:latest
