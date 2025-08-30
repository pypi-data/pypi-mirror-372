# ClickHouse query tools

Exposes ClickHouse internals to parse and manipulate ClickHouse queries.

Currently made of 1 module, clickhouse-toolset, which includes functionality both for the server and the CLI.

Initially this was published in pypi as `clickhouse-toolset`. After release 0.36 it was moved to `tinybird-toolset` 1.0.0.

## Installing prebuilts

The module is available in pypi:

```bash
pip install tinybird-toolset
```
You need to have access to the API Token, it may be shared from LastPass, if you don't have access request it. 

If we don't have prebuilts for your platform the installation will fail.

## No prebuilts available

To simplify things, the main module source distribution includes only the python code so that installing it is possible,
but it will throw when trying to use it:

```python
>>> from chtoolset import query as chquery
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "/home/raul/.local/lib/python3.9/site-packages/chtoolset/__init__.py", line 1, in <module>
    from . import query
  File "/home/raul/.local/lib/python3.9/site-packages/chtoolset/query.py", line 1, in <module>
    from chtoolset._query import replace_tables, format, tables, table_if_is_simple_query
ModuleNotFoundError: No module named 'chtoolset._query'
```

If you see this in the analytics server that means that your platform isn't supported and needs a prebuilt. If you see
this in the CLI that means that we are not handling the exception as it should (using a remote server).

### Alternative: Use Docker for compilation and testing

If you prefer not to install all dependencies locally, you can use the provided Docker image that contains all necessary tools:

```bash
# Build the Docker image
cd gitlab-runner
docker build -t manylinux_2_27_toolset:latest -f manylinux_2_27_toolset.Dockerfile .

# Run container with your code mounted
cd ..  # Back to project root
docker run -it -v $(pwd):/workspace manylinux_2_27_toolset:latest bash

# Inside the container, compile and test
cd /workspace
make build      # Build for all Python versions
make test       # Run tests for all Python versions

# Or for a specific Python version
make build-3.11 # Build only for Python 3.11
make test-3.11  # Test only for Python 3.11
```

The Docker image includes:
- Clang 17 compiler toolchain
- CMake and Ninja build systems
- Python versions 3.9, 3.10, 3.11, 3.12, and 3.13
- ccache for faster builds
- valgrind for memory testing

This approach ensures a consistent build environment and is the same one used in the CI/CD pipeline.

## Development

### Install pre-requisites (Ubuntu)

```bash
sudo apt-get update
sudo apt-get install git cmake ccache python3 python3-pip ninja-build nasm yasm gawk lsb-release wget software-properties-common gnupg

sudo bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)"

sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.8-dev python3.9-dev python3.10-dev python3.11-dev python3.12-dev python3.13-dev

pip3 install virtualenv
```

### Run tests

First, you need to clone the repo and **its submodules**.

```bash
git clone --recursive git@gitlab.com:tinybird/clickhouse-toolset.git
```

Then, you will compile the dependencies and the module itself. You need a modern compiler (Clang 17) to build it, both under Linux and MacOS (AppleClang is not supported).

The best option is to use the Makefile targets which will use virtualenv to install dependencies, build the packages, install them too and run tests:

```bash
make test-3.9
```

### Generate pre-built packages

You need to install all the necessary python releases so they are available via virtualenv.

#### If you are In MacOS, prepare your environment:

You need to be able to compile ClickHouse for MacOS so we follow [their guide](https://github.com/ClickHouse/ClickHouse/blob/master/docs/en/development/build-osx.md) to install the necessary packages:

* Install Homebrew
* Install Xcode and Command Line Tools
* Install the necessary tools (cmake ninja libtool gettext llvm@16 gcc ccache findutils grep)
* Make sure your local clang is pointing to the llvm installation and to the default from OSX / Xcode.  You can check it by running these commands. You should see a similar output
```bash
➜  clickhouse-toolset git:(master) ✗ clang --version
Homebrew clang version 16.0.6
Target: x86_64-apple-darwin22.5.0
Thread model: posix
InstalledDir: /usr/local/opt/llvm/bin
➜  clickhouse-toolset git:(master) ✗ llvm-as --version
Homebrew LLVM version 16.0.6
  Optimized build.
* Follow the normal build (`make build`)
```

#### Clean environment if you already did some compilation before
To clean your environment you need to make sure that the repository is clean and updated with the expected values. To do that you can use:

```bash
make distclean
git clean -fdx
```

#### Make sure you have the expeted version from the submodules
```bash
git submodule sync && git submodule update --init --recursive

# If it fails because of changes inside the ClickHouse folder related to the patchs we apply, just reset all the changes in that directory so these patchs can be reaplied in the next step.
cd clickhouse
git reset --hard
```

#### Compile and generate the new .whl files
Use:

```bash
make build
```

```
Disclaimer: The MacOS package for 3.8 will be generated but it will not work and tests fill fail. We have not been using that version since 0.27.dev0 and no-one has requested it so we'll deprecate the generation for this version soon. You can continue with the process, just don't push that version to Pypi.
```

Note that to reduce the version of the dependencies in the binary wheel, it is better if generated on an old Linux distribution, and it's best to use the CI.

#### Tip: re-compiling and debugging

A couple of environment variables can be defined with a non-empty value to help retrying the compilation and debugging:

* `OMIT_PATCHES` prevents the application of the ClickHouse patches: this is useful if you've already applied them to avoid having to restore the original source code, since some patches may not re-apply cleanly.
* `DEBUG_SYMBOLS` triggers the generation of debug symbols for the python extension code (query.cpp and the C++ functions, but not for the ClickHouse code).

#### Finish preparation of Linux packages

In order to improve compatibility for Linux packages you need to use auditwheel to "repair" them  before the upload to pypi:

```bash
for i in $(ls /tmp/artifacts/*whl); do auditwheel repair --plat manylinux2014_x86_64 $i; done
```

This will check and rename them to `manylinux2014` or `manylinux_2_17` (provided they have been compiled correctly). If auditwheel fails, or the result is still `linux_x86_64`, then **don't upload them** as they won't be compatible with older Linux releases.

#### Finish preparation of MacOS packages

In the case of MacOS we need to check the dependencies of the generated wheel using [delocate](https://github.com/matthew-brett/delocate). Use `delocate-listdeps` to check that there aren't any external dependencies and `delocate-wheel` if there are.

Problems may arise depending on the version of Python and delocate used. At the time of releasing tinybird-clickhouse 1.0.0 version 3.13 of Python and 0.13.0 of `delocate-wheel`.

You can use it by running:
```bash
# Install it
pip install delocate

# Execute it for each .whl generated
delocate-listdeps ./dist/clickhousetinybird_toolset-1.0.0-cp313-cp313-macosx_14_0_arm64.whl
```

In addition, to increase compatibility of the generated packages we need to rename them to the oldest release with binary compatibility (based on python tags), which we decided on 11.0:

If you're executing in from Linux, run:
```bash
find . -type f -name \*macosx_*_*_x86\* | perl -pe 'print $_; s/macosx_.._.+_x86/macosx_11_0_x86/' | xargs -d "\n" -n2 mv
find . -type f -name \*macosx_*_*_arm64\* | perl -pe 'print $_; s/macosx_.._.+_arm64/macosx_11_0_arm64/' | xargs -d "\n" -n2 mv
```

If you're executing in from MacOS, run:
```bash
find -E . -type f -regex '.*macosx_.._._x86.*' | perl -pe 'print $_; s/macosx_.._.+_x86/macosx_11_0_x86/' | xargs -n2 mv
find -E . -type f -regex '.*macosx_.._._arm64.*' | perl -pe 'print $_; s/macosx_.._.+_arm64/macosx_11_0_arm64/' | xargs -n2 mv
```

## Examples

Check tests directory

## Publish

1. Update VERSION in `setup.py`

2. Publish the source package for the version you want to use to the **test repository** (if you don't have permissions to do that, upload the generated `.whl` packages to [the compiled package's GCP bucket](https://console.cloud.google.com/storage/browser/tinybird-bdist_wheels?pageState=(%22StorageObjectListTable%22:(%22f%22:%22%255B%255D%22))&prefix=&) and ask for help):


In general, use the most recent versions of Python and `twine` to avoid problems, at the time of the 1.0.0 release Python 3.13 and `twine` 6.1 worked well.

```
twine upload --repository-url https://test.pypi.org/legacy/ dist/tinybird-toolset-1.0.0.tar.gz
```

3. Publish the whl packages (wheelhouse/ is generated by auditwheel):

```
twine upload --repository-url https://test.pypi.org/legacy/ wheelhouse/*
```
