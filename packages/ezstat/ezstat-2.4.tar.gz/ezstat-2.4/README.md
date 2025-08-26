# Ezstat: Easy statistics



OO For easy statistics, inspired by `Statistics` class of [deap](https://deap.readthedocs.io/en/master/index.html)

It is really easy and awesome! Believe me!

![](logo.jpg)

## Introduction

`ezstat` is built for easy statistics, esp. for the history of iterations.

### Statistics
The main class `Statistics` just extends `dict{str:function}` (called statistics dict), function here will act on the object of statistics. The values of dict have not to be a function, if it is a string, then the object of method with the same name is applied.

Frankly, It just borrows the idea from the `Statistics` class of [deap](https://deap.readthedocs.io/en/master/index.html). But unlike the author of deap, I just create it a subclass of dict, need not define strange methods.

See the following example and function `_call`, the underlying implementation.

### Examples

Example:

```python
>>> import numpy as np

>>> T = np.random.random((100,100)) # samples(one hundrand 100D samples)
>>> stat = Statistics({'mean': np.mean, 'max': 'max', 'shape':'shape'}) # create statistics
>>> print(stat(T))
>>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape': (100, 100)}

>>> print(stat(T, split=True)) # split the tuple if it needs
>>> {mean': 0.5009150557686407, 'max': 0.5748552862392957, 'shape[0]': 100, 'shape[1]': 100}
```

```python
# with sub-statistics
s = Statistics({'mean': np.mean,
'extreme': {'max':'max', 'min':np.min},  # as a sub-statistics
'shape':'shape'})
print(s(X))
# dict-valued statistics, equivalent to the above
s = Statistics({'mean': np.mean, 'extreme': lambda x:{'max': np.max(x), 'min': np.min(x)}, 'shape':'shape'})
print(s(X))

#Result: {'mean': 0.49786554518848564, 'extreme[max]': 0.9999761647791217, 'extreme[min]': 0.0001368184546896023, 'shape': (100, 100)}
```

### MappingStatistics
`MappingStatistics` is a subclass of `Statistics`. It only copes with iterable object, and maps the obect to an array by funcional attribute `key`.

Example:

```python
>>> stat = MappingStatistics(key='mean', {'mean':np.mean, 'max':np.max})
>>> print(stat(T))
>>> {'mean': 0.5009150557686407, 'max': 0.5748552862392957}
```

In the exmaple, 'mean', an attribute of T, maps T to a 1D array.

## Advanced Usage

`Statistics` acts on a list/tuple of objects iteratively, gets a series of results,
forming an object of `pandas.DataFrame`. In fact, it is insprited by `Statistics` class of third part lib [deap](https://deap.readthedocs.io/en/master/index.html). In some case, it collects a list of dicts of the statistics result for a series of objects. It is suggested to transform to DataFrame object.

```python
history = pd.DataFrame(columns=stat.keys())
for obj in objs:
    history = history.append(stat(obj), ignore_index=True)
```

## To Do

- [ ]  To define tuple of functions for the value of statistics dict.

