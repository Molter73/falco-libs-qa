.PHONY: all
all: tests

include $(CURDIR)/constants.mk

.PHONY: pull-caches
pull-caches:
ifndef SINSP_NO_CACHE
	docker pull quay.io/mmoltras/falco-libs-builder:latest
	docker pull quay.io/mmoltras/sinsp-example:latest
endif

.PHONY: builder
builder: pull-caches
	docker build \
		--tag quay.io/mmoltras/falco-libs-builder:$(TAG) \
		--cache-from quay.io/mmoltras/falco-libs-builder:$(TAG) \
		--cache-from quay.io/mmoltras/falco-libs-builder:latest \
		-f $(CURDIR)/containers/builder.Dockerfile $(CURDIR)/containers/

drivers: builder
	@mkdir -p $(CURDIR)/build/driver-build/
	docker run --rm --name kernel-builder \
		-v $(CURDIR)/libs:/libs \
		-v $(CURDIR)/build:/build \
		-v /usr/include/bpf:/usr/include/bpf:ro \
		-v /lib/modules/:/lib/modules/:ro \
		-v /usr/src/:/usr/src/:ro \
		--user $(shell id -u):$(shell id -g) \
		quay.io/mmoltras/falco-libs-builder:$(TAG) "cmake -S /libs \
			-DUSE_BUNDLED_DEPS=OFF \
			-DUSE_BUNDLED_VALIJSON=ON \
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
		quay.io/mmoltras/falco-libs-builder:$(TAG) "cmake -DUSE_BUNDLED_DEPS=OFF \
			-DUSE_BUNDLED_VALIJSON=ON \
			-DCMAKE_CXX_FLAGS_DEBUG="-fsanitize=address" \
			-DCMAKE_C_FLAGS_DEBUG="-fsanitize=address" \
			-DCMAKE_EXE_LINKER_FLAGS="-fsanitize=address" \
			-DCMAKE_SHARED_LINKER_FLAGS="-fsanitize=address" \
			-S /libs \
			-B /build/userspace-build && \
			make -j$(PARALLEL_BUILDS) -C /build/userspace-build/libsinsp/examples sinsp-example"
	@mkdir -p $(CURDIR)/tests/userspace/
	cp $(CURDIR)/build/userspace-build/libsinsp/examples/sinsp-example $(CURDIR)/tests/userspace/sinsp-example
	docker build --tag quay.io/mmoltras/sinsp-example:$(TAG) \
		--cache-from quay.io/mmoltras/sinsp-example:$(TAG) \
		--cache-from quay.io/mmoltras/sinsp-example:latest \
		-f $(CURDIR)/containers/sinsp.Dockerfile $(CURDIR)/tests/

.PHONY: tests
tests: userspace
	make -C tests

.PHONY: clean-drivers
clean-drivers:
	rm -rf $(CURDIR)/libs/driver/bpf/probe.{ll,o}
	rm -rf $(CURDIR)/libs/driver/bpf/.Module.symvers.cmd
	rm -rf $(CURDIR)/libs/driver/bpf/Module.symvers
	rm -rf $(CURDIR)/libs/driver/bpf/.modules.order.cmd
	rm -rf $(CURDIR)/libs/driver/bpf/modules.order
	rm -rf $(CURDIR)/libs/driver/driver_config.h
	rm -rf $(CURDIR)/build/driver-build
	rm -rf $(CURDIR)/tests/driver/

.PHONY: clean
clean:
	docker rmi quay.io/mmoltras/falco-libs-builder:latest \
		quay.io/mmoltras/sinsp-example:latest \
		quay.io/mmoltras/falco-test-runner:latest \
		quay.io/mmoltras/falco-libs-builder:$(TAG) \
		quay.io/mmoltras/sinsp-example:$(TAG) \
		quay.io/mmoltras/falco-test-runner:$(TAG) || true
	rm -rf $(CURDIR)/build/
	rm -rf $(CURDIR)/tests/userspace/
	rm -rf $(CURDIR)/tests/report/
