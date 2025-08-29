# Obfuscator

Utility to obfuscate Python code

### Installation

```bash
pip install localstack-obfuscator
```

### Usage

You need to have a config file in the project you want to obfuscate.

An example config file is given below:

```yml
custom_patches: false # if true, will use custom patches for dataclasses. Default is false.

# custom parameters for python_minifier
minify:
  remove_literal_statements: true

# list of files to exclude from obfuscation
exclude:
  - "constants.py"
  - "routes.py"

# list of files to remove from resulting build
remove:
  - ".venv"
  - "build"

target_dir: "outages" # relative to the build directory. The default is the same as current dir name
build_dir: "build" # relative to the current dir. The default is "build".
```

Note that the `exclude` and `remove` lists perform different functions:
- The exclusion works on a per-file basis and is for files that should be kept in the package but not obfuscated.
- The removal is for files and directories that should not be in the final build at all.
  This is, e.g., useful for the virtual environment directory or the build directory itself.
  It also improves the performance because the files are not even copied to the build directory in the first place.

To perform the obfuscation, run the obfuscator against the project directory.

```bash
localstack-obfuscator .
```
