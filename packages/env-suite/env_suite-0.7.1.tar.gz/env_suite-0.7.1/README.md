# env_suite

`env_suite` is a package for generating input and submission files for vasp calculations

# Installation via `pip`

Install `env_suite` using `pip` (if using a shared machine, add the `--user` argument after `install`)

```
pip install env_suite
```

# Updating

Update the code using `pip` (if using a shared machine, add the `--user` argument after `install`)

```
pip install env_suite --upgrade
```

# Installation with `pip` editable install

**Only do this if you are developing (i.e. changing) the code.**

Clone a copy of this repository, preferably while within a directory called git

```
mkdir -p git; cd git
git clone https://gitlab.com/chilton-group/env_suite
```

Navigate to the package directory

```
cd env_suite
```

and install the package in editable mode (if using a shared machine, add the `--user` argument after `install`)

```
pip install -e .
```

When you're done developing (i.e. your changes have been merged to the master), 
or if you just want to use the current release version of the package, uninstall using `pip`

```
pip uninstall env_suite
```

and follow the Installation via `pip` instructions above.

# Usage

The `env_suite` command line interface can be invoked with 

```
env_suite -h
```

which prints a list of available subprograms.

Alternatively, the individual submodules can be imported into a python program or script as per usual.

# Building a `.whl` file (Advanced)

**Only do this if you are told to.**

To build a copy of the `vasp_suite` `.whl` file, move to the `package` directory.

Now run

```
./build_binaries.sh
```

Then install the `.whl` file with `pip` (if using a shared machine, add the `--user` argument after `install`)

```
pip install dist/*.whl
```

# Documentation

The [documentation](https://chilton-group.gitlab.io/env_suite/) for this package is hosted by gitlab, and is automatically generated whenever new code is committed to the `main` branch. The automatic generation of this documentation relies on a common layout for comments and docstrings within the code, see [contributing](https://gitlab.com/chilton-group/group-wiki/-/wikis/Contributing:-General) for more information.

# Development

Before making changes to this repository, please follow the steps outlined in the [Chilton group wiki](https://gitlab.com/chilton-group/group-wiki/-/wikis/Contributing:-General).

# Bugs

If you believe you have a bug, *please check that you are using the most up to date version of the code*. 

If that does not fix the problem, please create an issue on GitLab detailing the following:
 - The commands you entered
 - The error message

Remember to simplify the problem as much as possible in order to provide a minimum working example, e.g. an example for a small molecule rather than one with 100000 atoms.

Then, look at the code, try and figure out what you think is wrong if possible, and include this in your issue.
