This repository is a PoC. Its main idea is to leverage the `sinsp-example`
binary from the `falcosecurity/libs` repository and their kernel module as a way
of running integration tests on it. The main components used to achieve this are
the following:

## Builder container
This container is used as the base to compile the `sinsp-example` binary, as
well as the kernel module used with it. The container itself is built from the
`Dockerfile.builder` file.

## sinsp container
A container holding the `sinsp-example` binary. Its entrpoint is set to the
binary, so it can be run in the same way as explained in [this README file](https://github.com/falcosecurity/libs/blob/master/userspace/libsinsp/examples/README.md). The build
for this container is based off of `Dockerfile.sinsp`

## Kernel module
The kernel module used by `sinsp-example` to capture events on the system is
also built as part of this repository. The only requirement for this is to have
the kernel headers for the machine docker is running on installed. There is no
specific dockerfile for this step, instead the builder image is run and the
kernel module is output under `tests/driver/scap.ko`.

## Tester container
This container is in charge of running any tests that are created under the
`tests/` subdirectory. The engine behind it is pytest and, as such, the tests
written need to follow the pattern `test_*/test_*.py` in order for them to be
properly picked up. Additionally, a barebones module called `sinspqa` lives in
`tests/commons/`, it is installed directly to the tester container and is meant
to house any functions/classes that might be useful accross multiple tests. The
dockerfile for this image can be found under `tests/Dockerfile`.

## Running the tests
As with any other repository, start by cloning it with:

```
git clone --recurse-submodules https://github.com/Molter73/falco-libs-qa
```

Running `make` on the root of the repo will trigger all needed steps to:
- Build the builder image.
- Build the `sinsp-example` image.
- Build the `scap.ko` kernel module.
- Build the `falco-test-runner` image.
- Run the tests themselves.

In case the tests need to be re-run without rebuilding all containers,
(i.e: when adding/modifying/debugging tests with no other changes), running
`make` from whithin the `tests/` subdirectory is enough.

## Potential future improvements
Aside from the obvious improvement of adding additional tests, here are some
ideas of things that could be changed to improve the quality of the tests:
- Add a flag to `sinsp-example` in order to enable it to dump events in full as
JSON objects and add a JSON schema validator for those events.
- Enable running tests with the eBPF probe instead of the kernel module.
