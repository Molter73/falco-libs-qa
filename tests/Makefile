.PHONY: all
all: run-tests

.PHONY: build-tester
build-tester:
	docker pull quay.io/mmoltras/falco-test-runner:latest
	docker build \
	--tag quay.io/mmoltras/falco-test-runner:latest \
	--cache-from quay.io/mmoltras/falco-test-runner:latest \
	-f $(CURDIR)/../containers/runner.Dockerfile $(CURDIR)

.PHONY: kmod-tests
kmod-tests: build-tester
	@mkdir -p $(CURDIR)/report/kmod
	docker run --rm \
		--privileged \
		--name falco-tester \
		-v /dev:/dev:ro \
		-v /var/run/docker.sock:/var/run/docker.sock \
		-v $(CURDIR)/report/kmod:/report \
		quay.io/mmoltras/falco-test-runner:latest

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
		quay.io/mmoltras/falco-test-runner:latest

.PHONY: run-tests
run-tests: kmod-tests ebpf-tests
