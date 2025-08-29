#
## Introduce
[![Python CI](https://github.com/XenosLu/xenoslib/actions/workflows/main.yml/badge.svg)](https://github.com/XenosLu/xenoslib/actions/workflows/main.yml)

This project provide some common utilities code.

## Requirements
- Python >= 3.6

## Installation
### Install from pypi

    pip3 install xenoslib

### Install directly from github

    pip3 install git+https://github.com/XenosLu/xenoslib.git

## Usage

### Base features

#### ArgMethodBase
```
# save as cli.py
from xenoslib import ArgMethodBase
class ArgMethod(ArgMethodBase):
    """cli utils"""

    @staticmethod
    def test(a, b, option='no'):
        """test"""
        print(a, b, option)

if __name__ == '__main__':
    ArgMethod()
```
```shell
root@bullseye:~# python cli.py
usage: cli.py [-h] {test} ...

cli utils

optional arguments:
  -h, --help  show this help message and exit

commands:
  {test}
    test      test
```
```shell
root@bullseye:~# python cli.py test -h
usage: cli.py test [-h] [--option OPTION] a b

positional arguments:
  a
  b

optional arguments:
  -h, --help       show this help message and exit
  --option OPTION
```
```shell
root@bullseye:~# python cli.py test aa bb --option yes
aa bb yes
OK
```
#### sleep
```
>>> from xenoslib import sleep
>>> sleep(5)
ETA 5/4  s
```
#### NestedData
```
import xenoslib
data = {'a': {'b': ['c', [0, {'d': 'e'}, {'a': 'b'}]]}}
nesteddata = xenoslib.NestedData(data)

result = nesteddata.find_key('d')
self.assertEqual(result, 'e')
result = nesteddata.path
self.assertEqual(result, "['a']['b'][1][1]['d']")

result = nesteddata.find_value('e')
self.assertEqual(result, {'d': 'e'})
result = nesteddata.path
self.assertEqual(result, "['a']['b'][1][1]['d']")

result = nesteddata.find_keyvalue('d', 'e')
self.assertEqual(result, {'d': 'e'})
result = nesteddata.path
self.assertEqual(result, "['a']['b'][1][1]['d']")
```
#### TestSingleton
```
class TestSingleton(xenoslib.Singleton):
    pass

obj_a = TestSingleton()
obj_b = TestSingleton()
self.assertEqual(id(obj_a), id(obj_b))
```
#### SingletonWithArgs
```
class TestSingletonWithArgs(xenoslib.SingletonWithArgs):
    pass

obj_a = TestSingletonWithArgs('a')
obj_b = TestSingletonWithArgs('b')
obj_c = TestSingletonWithArgs('a')
self.assertNotEqual(id(obj_a), id(obj_b))
self.assertEqual(id(obj_a), id(obj_c))
```
#### monkey_patch
```
self.assertNotEqual(xenoslib.__version__, 'injected version')
xenoslib.monkey_patch('xenoslib', '__version__', 'injected version')
self.assertEqual(xenoslib.version.__version__, 'injected version')
self.assertEqual(xenoslib.__version__, 'injected version')
```


### xenoslib.extend

```
from xenoslib.extend import YamlConfig
config = YamlConfig()
config2 = YamlConfig()
data = {'a': {'b': ['c', [0, {'d': 'e'}, {'a': 'b'}]]}}
config['data'] = data
self.assertEqual(config2.data, data)
self.assertEqual(id(config), id(config2))
```

### xenoslib.dev

- RestartWhenModified()

### to be continue

Finish the following docs...

NestedData
- pause() - press any key to continue, support both windows and linux
- timeout(seconds) - wait seconds or press any key to continue, support both windows and linux
- del_to_recyclebin(filepath, on_fail_delete=False) - delete file to recyclebin if possible


