# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['speakeasy2']

package_data = \
{'': ['*']}

install_requires = \
['igraph>=0.11.0,<0.12.0', 'numpy>=2.0.0,<3.0.0']

setup_kwargs = {
    'name': 'speakeasy2',
    'version': '0.1.6',
    'description': 'SpeakEasy2 community detection algorithm',
    'long_description': '# Python SpeakEasy2 package\n\n![PyPI - Version](https://img.shields.io/pypi/v/speakeasy2)\n![PyPI - Python Version](https://img.shields.io/pypi/pyversions/speakeasy2)\n\n\nProvides the SpeakEasy2 community detection algorithm to cluster graph\'s stored as igraph\'s data type. The algorithm is described in the [Genome Biology article](https://genomebiology.biomedcentral.com/articles/10.1186/s13059-023-03062-0).\n\nThis uses a rewrite of the algorithm used in the publication, to see a comparison to the original implementation see [the benchmarks](https://github.com/SpeakEasy-2/libspeakeasy2/tree/master/benchmarks)\n\nExample:\n\n```python\n import igraph as ig\n import speakeasy2 as se2\n\n g = ig.Graph.Famous("Zachary")\n memb = se2.cluster(g)\n```\n\nMembership is returned as an `igraph.clustering.VertexClustering` object.\nUse `print` to view the membership:\n\n```python\nprint(memb)\n```\n\n```python\nClustering with 34 elements and 9 clusters\n[0] 0, 1, 2, 3, 7, 12, 13, 17, 19, 21\n[1] 14, 15, 18, 20, 22, 32, 33\n[2] 8, 30\n[3] 26, 29\n[4] 11\n[5] 23, 24, 25, 27, 31\n[6] 9\n[7] 28\n[8] 4, 5, 6, 10, 16\n```\n\nOr to convert to a python list for use outside of `igraph` run `memb.membership`.\n\nFrom the results, a node ordering can be computed to group nodes in a community together. This can be used as an index and works to display the community structure using a heatmap to view the adjacency matrix.\n\n```python\nordering = se2.order_nodes(g, memb)\n```\n\nSpeakEasy 2 can work with weighted graphs by either passing weights as a list with length equal to the number of edges or by using the igraph attribute table.\n\n```python\ng.es["weight"] = [1 for _ in range(g.ecount())]\nmemb = se2.cluster(g)\n```\n\nBy default, SpeakEasy 2 will check if there is an edge attribute associated with the graph named `weight` and use those as weights. If you want to use a different edge attribute, pass the name of the attribute.\n\n```python\nmemb = se2.cluster(g, weights="tie_strength")\n```\n\nOr if a graph has a weight edge attribute but you don\'t want to use them, explicitly pass `None` to the `weights` keyword argument.\n\nSubclustering can be used to detect hierarchical community structure.\n\n```python\nmemb = se2.cluster(g, subcluster=2)\n```\n\nThe number determines how many levels to perform community detection at. The default 1 means only to perform community detection at the top level (i.e. no subclustering). When subclustering, membership will be a list of `igraph.VertexClustering` objects, the top level membership will be the object at index 0.\n\nA few other useful keywords arguments are `max_threads`, `verbose`, and `seed`. The `max_thread` keyword determines how many processors SpeakEasy 2 is allowed to use. By default the value returned by OpenMP is used. To prevent parallel processing, explicitly pass `max_threads = 1` to the method.\n\nThe `verbose` option will cause the algorithm to print out some information about the process.\n\nFor reproducible results, the `seed` option sets the seed of the random number generator. Note: this is a random number generator managed by the underlying C library and is independent of other random number generators that might have been set in python.\n\n## Installation\n\nspeakeasy2 is available from pypi so it can be installed with `pip` or other package managers.\n\n```bash\npip install --user speakeasy2\n```\n\n## Building from source\n\nCompilation depends on a C compiler, CMake, and (optionally) ninja.\n\nSince the `igraph` package is supplied by the vendored SE2 C library, after cloning the source directory, submodules most be recursively initialized.\n\n```bash\ngit clone "https://github.com/SpeakEasy-2/python-speakeasy2"\ncd python-speakeasy2\ngit submodule update --init --recursive\n```\n\nThe CMake calls are wrapped into the python build logic in the `build_script.py` (this is a `poetry` specific method for building C extensions).\nThis allows the package to be built using various python build backends.\nSince this package uses poetry, the suggested way to build the package is invoking `poetry build` and `poetry install`, which will install in development mode.\n\nFor convenience, the provided `Makefile` defines the `install` target to do this and `clean-dist` to clear all generated files (as well as other targets, see the file for more).\n\nIt should now be possible to run scripts through `poetry`:\n\n```bash\npoetry run ipython path/to/script.py\n```\n\nOr enter a python repository with the private environment activate in the same way.\n\n```bash\npoetry run ipython\n```\n\nIf you don\'t want to use `poetry`, it\'s possible to build with other method in their standard way.\nFor example `python -m build` or `pip install --editable .` should both work.\n',
    'author': 'David R Connell',
    'author_email': 'davidconnell12@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/SpeakEasy-2/python-speakeasy2',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.10',
}
from build_script import *
build(setup_kwargs)

setup(**setup_kwargs)
