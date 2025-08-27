# 🔬 SVS edit

Editing SVS files (headers) using python module tifftools.


## 📀 Installation

Create a Python virtual environment (to isolate dependencies from other Python packages you may be using), activate it, and then install it. Typically:
```console
$ python3.13 -m venv svs
$ cd svs
$ source bin/activate  # Or source bin/activate.csh for csh/tcsh users
(venv) $ pip install labcas-svsedit
```

This makes the `svs-edit` command-line tool available; run:

    svs-edit --help
  
To see the options.  For example, to replace the `Filename` field with the text `deid` in `input.svs` and write to `output.svs`, run:

    svs-edit --edit-desc Filename=deid input.svs output.svs

You can run on batches of files by wrapping the `svs-edit` invocation in a loop. For example, to replace the `Filename` field with the basename (without extension) of the SVS's file's name:
```bash
$ for f in *.svs; do
> svs-edit --edit-desc Filename=$(basename $f .svs) $f subdir/$f
> done
```
Or in csh/tcsh:
```csh
% foreach f (*.svs)
foreach? svs-edit. --edit-desc Filename=$f:r $f subdir/$f
foreach? end
```

By default the above replaces only those components which have the corresponding tag.

Changes can be tested by dumping the header of the newly written file using:
`tifftools dump subdir/svsfile.svs`


## 🛠️ Development

To develop and debug this software, clone this repository and install the source code into a Python virtual environment in editable mode:
```console
$ git clone https://github.com/jpl-labcas/svs_edit.git
$ cs svs_edit
$ python3.13 -m venv .venv
$ source .venv/bin/activate  # Or source .venv/bin/activate.csh for csh/tcsh users
(venv) $ pip install --editable .
```
The `svs-edit` command now uses the source code under `src/jpl/labacs/svs` and changes made to Python files take effect when the command is next run.


### 🥧 Making Releases

To release the software to the [Python Package Index](https://pypi.org/) use `build` and `twine`:
```console
$ pip install build twine
$ .venv/bin/python3 -m build .
$ twine upload dist/*
```

### 👥 Contributing

Within the JPL Informatics Center, we value the health of our community as much as the code, and that includes participation in creating and refining this software. Towards that end, we ask that you read and practice what's described in these documents:

-   Our [contributor's guide](https://github.com/EDRN/.github/blob/main/CONTRIBUTING.md) delineates the kinds of contributions we accept.
-   Our [code of conduct](https://github.com/EDRN/.github/blob/main/CODE_OF_CONDUCT.md) outlines the standards of behavior we practice and expect by everyone who participates with our software.


### 🔢 Versioning

We use the [SemVer](https://semver.org/) philosophy for versioning this software.


## 📃 License

The project is licensed under the [Apache version 2](LICENSE.md) license.
