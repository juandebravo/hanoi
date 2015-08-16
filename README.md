
# Hanoi

[![Version](https://pypip.in/v/hanoi/badge.png)](https://crate.io/packages/hanoi)
[![Downloads](https://pypip.in/d/hanoi/badge.png)](https://crate.io/packages/hanoi)
[![Build Status](https://travis-ci.org/juandebravo/hanoi.svg?branch=master)](https://travis-ci.org/juandebravo/hanoi)

Beta version.

Hanoi is a port of [rollout gem](https://github.com/FetLife/rollout) from [James Golick](https://github.com/jamesgolick) and [Eric Rafaloff](https://github.com/EricR).

The idea behind it is to ease a simple way to enable/disable functionalities to a subset of users in a production (or any other) environment. This is in general handy upon deploying a new version of your product, in order to test the new functionalities in a subset of users. It could be useful as well as ACL mechanism.

# Use cases

* Enable a functionality globally (every user).
* Enable a functionality to a percentage of users via Cyclic Redundancy Check(user identifier) % 100.
* Enable a functionality to a percentage of users via a predefined rule using a Reg Expr.
* Enable a functionality to specific users.
* Variants support (new in 0.0.4): inspired in [feature by Esty](https://github.com/etsy/feature) and [sixpack](https://github.com/seatgeek/sixpack), `hanoi` now supports variant for providing to users different
options for an experiment.

# Scenarios

* Check if the functionality A is enabled for user B.

```python
rollout.is_enabled('A', B)
```

* Pre-check while executing a function (functionality A) that user B (received as parameter in the function call) is granted permissions.

```python

@roll.check('A', 1)  # Check if user B (argument 1) is granted permissions to execute A
def execute_a_logic(user):
    pass  # Business logic here

execute_a_logic(B)
```

* Pre-check to ensure user B (attached to the process/thread) can execute functionality A (ACL mechanism). Be aware if your environment requires thread-safe behavior.

```python
rollout.set_current_id(B)

@roll.check('A')  # Check if the current user (B) is granted permissions to execute A
def execute_a_logic():
    pass  # Business logic here

execute_a_logic()
```

* Retrieving a valid variant for an experiment A for user B

```python
variant = rollout.variant('A', B)
```


# Examples of usage


```python
# Setting the configuration
# -------------------------

# bootstrap.py

import re

from redis import Redis
import hanoi

redis = Redis()

rollout = hanoi.Rollout(redis)

rollout.add_func(
    'cdc_on',               # Functionality name (CDC on)
    percentage=80,          # Percentage for toggle ON
    variants=('foo', 'bar') # Valid variants in case of toggle ON
)

rollout.register('cdc_on', '447568110000')  # Register a specific user

rollout.register('cdc_on', re.compile(r'01$')  # Register a subset of users

def get_rollout():
    return rollout


# Using Rollout
# -------------

# service.py

import bootstrap

roll = bootstrap.get_rollout()

# Define the current user (kind of ThreadLocal)
roll.set_current_id('444401')

@roll.check('cdc_on')  # Check if the current user is registerd to `cdc_on`
def execute_cdc_logic():
    pass

execute_cdc_logic()  # Based on the rules defined in bootstrap.py, the decorator will allow the function execution, as zlib.crc32('444401') % 100 = 89, and the predefined percentage is 80

# Check if it's enabled `cdc_on` to the user `44488`
# Based on the rules defined in bootstrap.py, it will return False
print roll.is_enabled('cdc_on', '44488')


@roll.check('cdc_on', 2)  # Check if it's enabled `cdc_on` to the second parameter
def execute_again_cdc_logic(parameter, user):
    return "I'm in"

print execute_again_cdc_logic('foo', '443301')  # Based on the rules defined in bootstrap.py, the decorator will allow the function execution, as 443301 matches the reg expr.

print roll.variant('cdc_on', '443301')  # Get a valid variant for user 443301.

```

# BackEnds

Currently there're three implemented BackEnds:

- [MemoryBackEnd](https://github.com/juandebravo/hanoi/blob/master/hanoi/backend.py#L65): useful for development or where you have predefined rules and don't need to share information between different processes.

- [RedisBackEnd](https://github.com/juandebravo/hanoi/blob/master/hanoi/backend.py#L125): useful for distributed environments, where you need to easily update functionalities, rules or users attached to a specific functionality.

- [RedisHighPerfBackEnd](https://github.com/juandebravo/hanoi/blob/master/hanoi/backend.py#L264): useful for distributed environments and high performance. It uses SET to store users and reduce significantly the time to verify an user. Check and execute `benchmark.py` file for details.

# TODO before BETA

- [X] Finish unit testing Rollout class
- [X] Finish unit testing Function class
- [X] Implement Redis BackEnd
- [X] Finish unit testing RedisBackEnd class
- [X] Document the different use cases and when to use both backends
- [X] Integrate travis.ci
- [X] Upload a beta version to pypi
- [X] Think about a cooler name :wink:. We'll stay with **hanoi**
- [X] [Write a blog post](http://www.juandebravo.com/2015/02/15/toggle-func-in-python/)

