#!/usr/bin/env python

import yaml

import redismetrics

with open('conf/redis-open-falcon.yml', 'r') as ymlfile:
    config = yaml.load(ymlfile)

threads = []

for redis_cluster in config['redis-clusters']:
    redis_metric_thread = redismetrics.RedisMetrics(config['falcon']['push_url'],
                                                    redis_cluster['endpoint'],
                                                    redis_cluster['host'],
                                                    redis_cluster['port'],
                                                    redis_cluster['password'],
                                                    redis_cluster['tags'])
    redis_metric_thread.start()
    threads.append(redis_metric_thread)

for thread in threads:
    thread.join(10)

