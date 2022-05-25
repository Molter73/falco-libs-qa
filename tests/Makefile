.PHONY: all
all: run-tests

.PHONY: build-tester
build-tester:
	docker build --tag falco-test-runner:latest .

.PHONY: kmod-tests
kmod-tests: build-tester
	@mkdir -p $(CURDIR)/report/kmod
	docker run --rm \
		--privileged \
		--name falco-tester \
		-v /dev:/dev:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/report/kmod:/report \
		falco-test-runner:latest

.PHONY: ebpf-tests
ebpf-tests: build-tester
	@mkdir -p $(CURDIR)/report/ebpf
	docker run --rm \
		--privileged \
		--name falco-tester \
		-e BPF_PROBE=/driver/probe.o \
		-v /dev:/dev:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/report/ebpf:/report \
		falco-test-runner:latest

.PHONY: run-tests
run-tests: kmod-tests ebpf-tests
