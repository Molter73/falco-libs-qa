.PHONY: all
all: tests

.PHONY: builder
builder:
	docker build --tag libs-it-builder:latest \
		-f Dockerfile.builder .

scap.ko: builder
	docker run --rm --name kernel-builder \
		-v $(CURDIR)/libs:/libs \
		-v /usr/include/bpf:/usr/include/bpf:ro \
		-v /lib/modules/:/lib/modules/:ro \
		-v /usr/src/kernels/:/usr/src/kernels/:ro \
		libs-it-builder:latest "cmake -S /libs \
		-DUSE_BUNDLED_DEPS=OFF \
		-B /libs/build && \
		make -C /libs/build/driver"
	@mkdir -p $(CURDIR)/tests/driver/scap.ko
	cp $(CURDIR)/libs/build/driver/src/scap.ko $(CURDIR)/tests/driver/scap.ko
	rm -rf $(CURDIR)/libs/build/

.PHONY: userspace
userspace: builder
	docker build --tag sinsp-example:latest \
		-f Dockerfile.sinsp .

.PHONY: tests
tests: userspace scap.ko
	make -C tests

.PHONY: clean
clean:
	docker rmi libs-it-builder:latest \
		sinsp-example:latest \
		falco-test-runner:latest
	rm -rf $(CURDIR)/libs/build
	rm -f $(CURDIR)/tests/driver/scap.ko
