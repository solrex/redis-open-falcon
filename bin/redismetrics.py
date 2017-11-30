#!/usr/bin/env python

import threading
import redis
import json
import time
from datetime import datetime
import requests
import os


class RedisMetrics(threading.Thread):
    def __init__(self, falcon_conf, redis_conf):
        self.falcon_conf = falcon_conf
        self.redis_conf = redis_conf
        # Assign default conf
        if 'test_run' not in self.falcon_conf:
            self.falcon_conf['test_run'] = False
        if 'step' not in self.falcon_conf:
            self.falcon_conf['step'] = 60

        self.gauge_keywords  = ['uptime_in_days', 'connected_clients', 'blocked_clients',
                                'used_memory', 'maxmemory', 'used_memory_rss', 'used_memory_peak',
                                'used_memory_lua_human', 'mem_fragmentation_ratio']

        self.counter_keywords = ['total_commands_processed', 'rejected_connections',
                                 'expired_keys', 'evicted_keys',
                                 'keyspace_hits', 'keyspace_misses']

        self.db_keywords = ['keys', 'expires', 'avg_ttl']

        super(RedisMetrics, self).__init__(None, name=self.redis_conf['endpoint'])
        self.setDaemon(False)

    def new_metric(self, metric, value, type = 'GAUGE'):
        return {
            'counterType': type,
            'metric': metric,
            'endpoint': self.redis_conf['endpoint'],
            'timestamp': self.timestamp,
            'step': self.falcon_conf['step'],
            'tags': self.redis_conf['tags'],
            'value': value
        }

    def run(self):
        try:
            self.redis = redis.Redis(host = self.redis_conf['host'], port = self.redis_conf['port'],
                                     password = self.redis_conf['password'])
            falcon_metrics = []
            # Statistics
            self.timestamp = int(time.time())
            redis_info = self.redis.info()
            # Original keyword metrics
            for keyword in self.gauge_keywords:
                falcon_metric = self.new_metric("redis." + keyword, redis_info[keyword])
                falcon_metrics.append(falcon_metric)
            for keyword in self.counter_keywords:
                falcon_metric = self.new_metric("redis." + keyword, redis_info[keyword], type='COUNTER')
                falcon_metrics.append(falcon_metric)
            # DB metrics
            for key in redis_info:
                if key.startswith("db") and type(redis_info[key]) == dict:
                    for keyword in self.db_keywords:
                        falcon_metric = self.new_metric('redis.' + key + '.' + keyword, redis_info[key][keyword])
                        falcon_metrics.append(falcon_metric)
                    falcon_metric = self.new_metric('redis.' + key + '.persist_keys',
                                                    redis_info[key]['keys'] - redis_info[key]['expires'])
                    falcon_metrics.append(falcon_metric)
            # Self defined metrics
            falcon_metric = self.new_metric('redis.used_memory_ratio', float(redis_info['used_memory'])/redis_info['maxmemory'])
            falcon_metrics.append(falcon_metric)
            if self.falcon_conf['test_run']:
                print json.dumps(falcon_metrics)
            else:
                req = requests.post(self.falcon_conf['push_url'], data=json.dumps(falcon_metrics))
                print datetime.now(), "INFO: [%s]" % self.falcon_conf['endpoint'], "[%s]" % self.falcon_conf['push_url'], req.text
        except Exception as e:
            if self.falcon_conf['test_run']:
                raise
            else:
                print datetime.now(), "ERROR: [%s]" % self.redis_conf['endpoint'], e.message
