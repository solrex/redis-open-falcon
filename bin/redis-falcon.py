#!/usr/bin/env python

import yaml

import redismetrics

with open('conf/redis-open-falcon.yml', 'r') as ymlfile:
    config = yaml.load(ymlfile)

for redis_cluster in config['redis-clusters']:
    redis_metric_thread = redismetrics.RedisMetrics(config['falcon']['push_url'],
                                                    redis_cluster['endpoint'],
                                                    redis_cluster['host'],
                                                    redis_cluster['port'],
                                                    redis_cluster['db'],
                                                    redis_cluster['password'],
                                                    redis_cluster['tags'])
    redis_metric_thread.start()
