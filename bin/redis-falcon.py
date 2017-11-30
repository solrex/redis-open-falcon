#!/usr/bin/env python

import yaml

import redismetrics

with open('conf/redis-open-falcon.yml', 'r') as ymlfile:
    config = yaml.load(ymlfile)

threads = []

for redis_cluster in config['redis-clusters']:
    metric_thread = redismetrics.RedisMetrics(config['falcon'], redis_cluster)
    metric_thread.start()
    threads.append(metric_thread)

for thread in threads:
    thread.join(5)

