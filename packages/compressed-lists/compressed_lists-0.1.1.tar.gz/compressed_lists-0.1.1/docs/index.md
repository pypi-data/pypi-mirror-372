# compressed-lists

A Python implementation of the `CompressedList` class from R/Bioconductor for memory-efficient list-like objects.

`CompressedList` is a memory-efficient container for list-like objects. Instead of storing each list element separately, it concatenates all elements into a single vector-like object and maintains information about where each original element begins and ends. This approach is significantly more memory-efficient than standard lists, especially when dealing with many list elements.

## Install

To get started, install the package from [PyPI](https://pypi.org/project/compressed-lists/)

```bash
pip install compressed-lists
```


## Contents

```{toctree}
:maxdepth: 2

Overview <readme>
Tutorial <tutorial>
Contributions & Help <contributing>
License <license>
Authors <authors>
Changelog <changelog>
Module Reference <api/modules>
```

## Indices and tables

* {ref}`genindex`
* {ref}`modindex`
* {ref}`search`

[Sphinx]: http://www.sphinx-doc.org/
[Markdown]: https://daringfireball.net/projects/markdown/
[reStructuredText]: http://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html
[MyST]: https://myst-parser.readthedocs.io/en/latest/
