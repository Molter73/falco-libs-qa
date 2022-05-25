.PHONY: all
all: tests

.PHONY: builder
builder:
	docker build --tag libs-it-builder:latest \
		-f Dockerfile.builder .

drivers: builder
	docker run --rm --name kernel-builder \
		-v $(CURDIR)/libs:/libs \
		-v /usr/include/bpf:/usr/include/bpf:ro \
		-v /lib/modules/:/lib/modules/:ro \
		-v /usr/src/:/usr/src/:ro \
		libs-it-builder:latest "cmake -S /libs \
		-DUSE_BUNDLED_DEPS=OFF \
		-DBUILD_BPF=ON \
		-B /libs/build && \
		make -C /libs/build/driver"
	@mkdir -p $(CURDIR)/tests/driver/
	cp $(CURDIR)/libs/build/driver/src/scap.ko $(CURDIR)/tests/driver/scap.ko
	cp $(CURDIR)/libs/build/driver/bpf/probe.o $(CURDIR)/tests/driver/probe.o
	rm -rf $(CURDIR)/libs/build/

.PHONY: userspace
userspace: builder drivers
	docker build --tag sinsp-example:latest \
		-f Dockerfile.sinsp .

.PHONY: tests
tests: userspace
	make -C tests

.PHONY: clean
clean:
	docker rmi libs-it-builder:latest \
		sinsp-example:latest \
		falco-test-runner:latest
	rm -rf $(CURDIR)/libs/build
	rm -rf $(CURDIR)/tests/driver/
