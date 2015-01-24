
# Introduction

Work in progress!! Alpha version.

Hanoi is a port of [rollout gem](https://github.com/FetLife/rollout) from [James Golick](https://github.com/jamesgolick) and [Eric Rafaloff](https://github.com/EricR).

The idea behind it is to ease a simple way to enable/disable functionalities to a subset of users in a production (or any other) environment. This is in general handy upon deploying a new version of your product, in order to test the new functionalities in a subset of users. It could be useful as well as ACL mechanism.

# Scenarios

* Enable/disable globally a functionality
* Enable a functionality to a specific user/subset of users
* Disable a functionality to a specific user/subset of users


# How to use


```python
# Setting the configuration
# -------------------------

# bootstrap.py

from redis import Redis
import hanoi

redis = Redis()

rollout = hanoi.Rollout(redis)

rollout.add_func(
    'cdc_on',        # Functionality name (CDC on)
    'id',            # Object identifier
    80               # Percentage for toggle ON
)

rollout.register('cdc_on', '447568110000')  # Register a specific user

import re

rollout.register('cdc_on', re.compile(r'01$')  # Register a subset of users

def get_rollout():
    return rollout


# Using Rollout
# -------------

# service.py

import bootstrap

roll = bootstrap.get_rollout()

# Define the current user (kind of ThreadLocal)
rollout.set_current_id(User('444401')

@roll.check('cdc_on')  # Check if the current user is registerd to `cdc_on`
def execute_cdc_logic():
    pass

execute_cdc_logic()

print rollout.is_enabled('cdc_on', '44488')  # Check if it's enabled `cdc_on` to the user `44488`


@rollout.check('cdc_on', 2)  # Check if it's enabled `cdc_on` to the second parameter
def execute_again_cdc_logic(parameter, user):
    return "I'm in"

print execute_again_cdc_logic('foo', '444401')

```

# TODO before BETA

- [X] Finish unit testing Rollout class
- [X] Finish unit testing Function class
- [X] Implement Redis BackEnd
- [X] Finish unit testing RedisBackEnd class
- [ ] Document the different use cases and when to use both backends
- [ ] Integrate travis.ci
- [ ] Upload a beta version to pypy
- [ ] Write a blog post
