import hanoi
from redis import Redis

redis = Redis()

rollout = hanoi.Rollout(redis)
rollout.add_func('cdc_on', lambda x: x.id)

print rollout.is_cdc_on()

print rollout.is_cdc_o()
