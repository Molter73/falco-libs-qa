.PHONY: all
all: tests

PARALLEL_BUILDS ?= 6

.PHONY: builder
builder:
	docker pull quay.io/mmoltras/falco-libs-builder:latest
	docker build \
		--tag quay.io/mmoltras/falco-libs-builder:latest \
		--cache-from quay.io/mmoltras/falco-libs-builder:latest \
		-f $(CURDIR)/containers/Dockerfile.builder $(CURDIR)/containers/

drivers: builder
	@mkdir -p $(CURDIR)/build/driver-build/
	docker run --rm --name kernel-builder \
		-v $(CURDIR)/libs:/libs \
		-v $(CURDIR)/build:/build \
		-v /usr/include/bpf:/usr/include/bpf:ro \
		-v /lib/modules/:/lib/modules/:ro \
		-v /usr/src/:/usr/src/:ro \
		--user $(shell id -u):$(shell id -g) \
		quay.io/mmoltras/falco-libs-builder:latest "cmake -S /libs \
		-DUSE_BUNDLED_DEPS=OFF \
		-DBUILD_BPF=ON \
		-B /build/driver-build && \
		make -j$(PARALLEL_BUILDS) -C /build/driver-build/driver"
	@mkdir -p $(CURDIR)/tests/driver/
	cp $(CURDIR)/build/driver-build/driver/src/scap.ko $(CURDIR)/tests/driver/scap.ko
	cp $(CURDIR)/build/driver-build/driver/bpf/probe.o $(CURDIR)/tests/driver/probe.o

.PHONY: userspace
userspace: builder drivers
	@mkdir -p $(CURDIR)/build/userspace-build/
	docker run --rm --name userspace-builder \
		-v $(CURDIR)/libs:/libs \
		-v $(CURDIR)/build:/build \
		--user $(shell id -u):$(shell id -g) \
		quay.io/mmoltras/falco-libs-builder:latest "cmake -DUSE_BUNDLED_DEPS=OFF \
			-DCMAKE_CXX_FLAGS_DEBUG="-fsanitize=address" \
			-DCMAKE_C_FLAGS_DEBUG="-fsanitize=address" \
			-DCMAKE_EXE_LINKER_FLAGS="-fsanitize=address" \
			-DCMAKE_SHARED_LINKER_FLAGS="-fsanitize=address" \
			-S /libs \
			-B /build/userspace-build && \
		make -j$(PARALLEL_BUILDS) -C /build/userspace-build/libsinsp/examples sinsp-example"
	@mkdir -p $(CURDIR)/tests/userspace/
	cp $(CURDIR)/build/userspace-build/libsinsp/examples/sinsp-example $(CURDIR)/tests/userspace/sinsp-example
	docker build --tag sinsp-example:latest \
		-f sinsp.Dockerfile $(CURDIR)/tests/

.PHONY: tests
tests: userspace
	make -C tests

.PHONY: clean
clean:
	docker rmi quay.io/mmoltras/falco-libs-builder:latest \
		sinsp-example:latest \
		quay.io/mmoltras/falco-test-runner:latest || true
	rm -rf $(CURDIR)/build/
	rm -rf $(CURDIR)/tests/driver/
	rm -rf $(CURDIR)/tests/userspace/
	rm -rf $(CURDIR)/tests/report/
	rm -rf $(CURDIR)/libs/driver/bpf/probe.{ll,o}
	rm -rf $(CURDIR)/libs/driver/bpf/.Module.symvers.cmd
	rm -rf $(CURDIR)/libs/driver/bpf/Module.symvers
	rm -rf $(CURDIR)/libs/driver/bpf/.modules.order.cmd
	rm -rf $(CURDIR)/libs/driver/bpf/modules.order
	rm -rf $(CURDIR)/libs/driver/driver_config.h
