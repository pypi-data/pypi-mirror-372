# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['ezstat']
setup_kwargs = {
    'name': 'ezstat',
    'version': '2.4',
    'description': 'OOP For eazy statistics, inspired by `Statistics` class of the lib `deap` but more user-friendly',
    'long_description': "# Ezstat: Easy statistics\n\n\n\nOO For easy statistics, inspired by `Statistics` class of [deap](https://deap.readthedocs.io/en/master/index.html)\n\nIt is really easy and awesome! Believe me!\n\n![](logo.jpg)\n\n## Introduction\n\n`ezstat` is built for easy statistics, esp. for the history of iterations.\n\n### Statistics\nThe main class `Statistics` just extends `dict{str:function}` (called statistics dict), function here will act on the object of statistics. The values of dict have not to be a function, if it is a string, then the object of method with the same name is applied.\n\nFrankly, It just borrows the idea from the `Statistics` class of [deap](https://deap.readthedocs.io/en/master/index.html). But unlike the author of deap, I just create it a subclass of dict, need not define strange methods.\n\nSee the following example and function `_call`, the underlying implementation.\n\n### Examples\n\nExample:\n\n```python\n>>> import numpy as np\n\n>>> T = np.random.random((100,100)) # samples(one hundrand 100D samples)\n>>> stat = Statistics({'mean': np.mean, 'max': 'max', 'shape':'shape'}) # create statistics\n>>> print(stat(T))\n>>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}\n\n>>> print(stat(T, split=True)) # split the tuple if it needs\n>>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape[0]': 100, 'shape[1]': 100}\n```\n\n```python\n# with sub-statistics\ns = Statistics({'mean': np.mean,\n'extreme': {'max':'max', 'min':np.min},  # as a sub-statistics\n'shape':'shape'})\nprint(s(X))\n# dict-valued statistics, equivalent to the above\ns = Statistics({'mean': np.mean, 'extreme': lambda x:{'max': np.max(x), 'min': np.min(x)}, 'shape':'shape'})\nprint(s(X))\n\n#Result: {'mean': 0.49786554518848564, 'extreme[max]': 0.9999761647791217, 'extreme[min]': 0.0001368184546896023, 'shape': (100, 100)}\n```\n\n### MappingStatistics\n`MappingStatistics` is a subclass of `Statistics`. It only copes with iterable object, and maps the obect to an array by funcional attribute `key`.\n\nExample:\n\n```python\n>>> stat = MappingStatistics(key='mean', {'mean':np.mean, 'max':np.max})\n>>> print(stat(T))\n>>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957}\n```\n\nIn the exmaple, 'mean', an attribute of T, maps T to a 1D array.\n\n## Advanced Usage\n\n`Statistics` acts on a list/tuple of objects iteratively, gets a series of results,\nforming an object of `pandas.DataFrame`. In fact, it is insprited by `Statistics` class of third part lib [deap](https://deap.readthedocs.io/en/master/index.html). In some case, it collects a list of dicts of the statistics result for a series of objects. It is suggested to transform to DataFrame object.\n\n```python\nhistory = pd.DataFrame(columns=stat.keys())\nfor obj in objs:\n    history = history.append(stat(obj), ignore_index=True)\n```\n\n## To Do\n\n- [ ]  To define tuple of functions for the value of statistics dict.\n\n",
    'author': 'William Song',
    'author_email': '30965609+Freakwill@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Freakwill/ezstat',
    'py_modules': modules,
    'python_requires': '>=3.9,<4.0',
}


setup(**setup_kwargs)
