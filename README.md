
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
# bootstrap.py

from redis import Redis

from hanoi import Rollout

redis = Redis()

rollout = Rollout(redis)

rollout.add_func(
    'cdc_on',        # Functionality name (CDC on)
    lambda x: x.id   # How to get the identifier
)

def get_rollout():
    return rollout

# Using Rollout
# service.py

import bootstrap

roll = bootstrap.get_rollout()

user = User(id="foo")

@roll.check('cdc_on')
def execute_cdc_logic(user):
    pass


execute_cdc_logic(user)
```

# TODO before BETA

- [X] Finish unit testing Rollout class
- [X] Finish unit testing Function class
- [ ] Finish unit testing MemoryBackEnd class
- [X] Implement Redis BackEnd
- [ ] Document the different use cases and when to use both backends
- [ ] Integrate travis.ci
- [ ] Upload a beta version to pypy
- [ ] Write a blog post
