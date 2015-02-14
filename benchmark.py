import hanoi
import redis
import time

_redis = redis.Redis('localhost', 6379)

rollout = hanoi.Rollout(hanoi.RedisBackEnd(_redis))

rolloutHP = hanoi.Rollout(hanoi.RedisHighPerfBackEnd(_redis))

FN = 'FOO'

USER = "USER-{0}"

LOOP = 10000

for client in (rollout, rolloutHP):

    t0 = time.time()

    client.add_func(FN)

    for i in xrange(0, LOOP):
        client.register(FN, USER.format(str(i)))

    for i in xrange(0, LOOP):
        client.is_enabled(FN, USER.format(str(i)))
        client.is_enabled(FN, USER.format('a'))

    t1 = time.time()

    print "%.2f" % round(t1-t0, 2)

    _redis.flushdb()
