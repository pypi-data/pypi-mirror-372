#!/usr/bin/env python3

"""Easy statistics

The main class `Statistics` just extends `dict{str:function}`,
where `function` will act on the object of statistics.
As the value of dict, `function` has not to be a function.
If it is a string, then the attribute of object will be called.

Please see the following example and the function `_call`, the underlying implementation.

Pseudo codes:
    ```
    if s: str
        f = getattr(obj, s)
        if f: function
            r = f()
        else
            r = f
    elif s: function
        r = s(obj)
    elif s is number:
        r = s
    ```

Example:

    >>> import numpy as np

    >>> T = np.random.random((100,100))
    >>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
    >>> print(s(T))
    >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

    >>> print(s(T, split=True)) # split the tuple if it needs
    >>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape[0]': 100, 'shape[1]': 100}

`MappingStatistics` subclasses Statistics. It only copes with iterable object,
and maps it to an array by a "key" function.

Example:

    >>> s = MappingStatistics('mean', {'mean':np.mean, 'max':np.max})
    >>> print(s(T))
    >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957}

In the exmaple, 'mean', an attribute of T, maps T to a 1D array.


Advanced Usage:
`Statistics` acts on a list/tuple of objects iteratively, gets a series of results,
forming an object of pandas.DataFrame.

    history = pd.DataFrame(columns=s.keys())
    for obj in objs:
        history = history.append(s(obj), ignore_index=True)

# A statistics with sub-statistics (a sub dict)
>>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'extreme': {'max':lambda x: np.max(np.mean(x, axis=1)), 'min':lambda x: np.min(np.mean(x, axis=1))}, 'shape':'shape'})
>>> print(s(T))
>>> {'mean': 0.4996204853996345, 'extreme[max]': 0.5725988408914174, 'extreme[min]': 0.44353206503438763, 'shape': (100, 100)}
"""

__version__ = '2.2'

from typing import Callable, Iterable, Dict, Union, TypeVar

import pandas as pd
import numpy as np

Constant = TypeVar('Constant', int, float, tuple)
Statistic = Union[str, Callable, Constant]
HStatistic = Dict[str, Statistic]
Result = Dict[str, Constant]


def _call(s, obj):
    """Core function of `ezstat`

    A functional extension for s(obj) or obj.s or obj.s()
    If s is an string, then it only returns obj.s or obj.s().

    s could be a tuple or dict, as a lifted form, though it is not recommended.
    
    Arguments:
        s {function | string} -- Statistics
        obj -- object of statistics
    
    Return:
        a number or a tuple of numbers, as the value of statistics
    """
    if isinstance(s, str):
        if not hasattr(obj, s):
            raise ValueError(f"the object '{obj}' of '{obj.__class__}' has no attribute `{s}`")
        f = getattr(obj, s)
        r = f() if callable(f) else f
    elif callable(s):
        r = s(obj)
    elif isinstance(s, (int, float)):
        print(Warning('Deprecated to use a constant number!'))
        r = s
    elif isinstance(s, tuple):
        return tuple(_call(si, obj) for si in s)
    elif isinstance(s, dict):
        return {i:_call(si, obj) for i, si in s.items()}
    else:
        raise TypeError(f"The type of `{s}` is not permissible!") 

    return r


def _check(d):
    for k, _ in d.items():
        if not isinstance(k, str):
            raise TypeError(f'The keys must be strings, but `{k}` is not a string.')


class Statistics(dict):
    """
    Statistics is a type of dict{str:function},
    where `function` will act on the object of statistics.

    As the value of dict, `function` has not to be a function.
    If it is a string, then the attribute of object will be called.
    """

    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls, *args, **kwargs)
        _check(obj)
        return obj

    def do(self, obj, split:bool=False) -> Result:
        """Execute a staistical task

        Arguments:
            obj {object} -- an object (population) of statistics
            split {bool} -- if True, it will split a tuple-type statistic result to numbers
        
        Returns:
            dict{str:value}

        Example:
        >>> import numpy as np

        >>> T = np.random.random((100,100))
        >>> s = Statistics({'mean': lambda x: np.mean(np.mean(x, axis=1)), 'max': lambda x: np.max(np.mean(x, axis=1)), 'shape':'shape'})
        >>> print(s(T))
        >>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

        >>> print(s(T, split=True)) # split the tuple if it needs
        >>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape[0]': 100, 'shape[1]': 100}
        """

        res = {}
        for k, s in self.items():
            if s is True:
                s = k.lower().replace(' ', '_').replace('-', '_')
            if isinstance(s, dict):
                r = do(s, obj, split=split)
                res.update({f"{k}[{i}]": ri for i, ri in r.items()})
            else:
                r = _call(s, obj)
                if split and isinstance(r, Iterable):
                    res.update({f"{k}[{i}]": ri for i, ri in enumerate(r)})
                elif isinstance(r, dict):
                    res.update({f"{k}[{i}]": ri for i, ri in r.items()})
                else:
                    res[k] = r
        return res

    def dox(self, objs:Iterable):
        # wrap the sequence of statistical resutls as a dataframe
        return pd.DataFrame(data=map(self, objs), columns=self.keys())

    def register(self, *args, **kwargs):
        d = {arg:arg for arg in args}
        _check(d)
        return self.update(d).update(kwargs)

    def __call__(self, *args, **kwargs):
        # alias of do
        return self.do(*args, **kwargs)


class MappingStatistics(Statistics):
    """Just a wrapper of `Statistics`

    Only recommanded to cope with iterable object of statistics.
    It will transfrom the object to array by `key` (functional attribute) before doing statistics.
    
    Extends:
        Statistics

    Example:
    >>> import numpy as np
    >>> T = np.random.random((100,100))
    >>> s = MappingStatistics('mean', {'mean':np.mean, 'min':np.min})
    >>> print(s(T))
    >>> {'mean': 0.4995186088546244, 'min': 0.39975807140966796}

    In the exmaple, 'mean', an attribute of np.ndarray, maps each row of T to a number.
    As a result, the object of statistics is a 1D array.
    """

    def __init__(self, key, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.key = key

    def do(self, obj:Iterable, split:bool=False)->Result:
        """
        `obj` is asserted to be iterable
        """
        a = np.array([_call(self.key, obj_) for obj_ in obj]) # an array of numbers
        return super().do(a, split=split)


def do(d, obj, *args, **kwargs):
    return Statistics(d)(obj, *args, **kwargs)
