#!/usr/bin/env python

import threading
import redis
import json
import time
from datetime import datetime
import requests
import os

class RedisMetrics(threading.Thread):
    def __init__(self, falcon_url, endpoint, host, port, password = '', tags = '', falcon_step = 60, daemon = False):
        self.falcon_url = falcon_url
        self.falcon_step = falcon_step
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.password = password
        self.tags = tags

        self.gauge_keywords  = ['uptime_in_days', 'connected_clients', 'blocked_clients',
                                'used_memory', 'maxmemory', 'used_memory_rss', 'used_memory_peak',
                                'used_memory_lua_human', 'mem_fragmentation_ratio']

        self.counter_keywords = ['total_commands_processed', 'rejected_connections',
                                 'expired_keys', 'evicted_keys',
                                 'keyspace_hits', 'keyspace_misses']

        self.db_keywords = ['keys', 'expires', 'avg_ttl']

        super(RedisMetrics, self).__init__(None, name=endpoint)
        self.setDaemon(daemon)

    def new_metric(self, metric, value, type = 'GAUGE'):
        return {
            'counterType': type,
            'metric': metric,
            'endpoint': self.endpoint,
            'timestamp': self.timestamp,
            'step': self.falcon_step,
            'tags': self.tags,
            'value': value
        }

    def run(self):
        try:
            self.redis = redis.Redis(host = self.host, port = self.port, password = self.password);
        except Exception as e:
            print datetime.now(), "ERROR: [%s]" % self.endpoint, e
            return
        falcon_metrics = []
        # Statistics
        try:
            self.timestamp = int(time.time())
            redis_info = self.redis.info()
            #print json.dumps(redis_info)
            executable = os.path.basename(redis_info['executable'])
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
            print json.dumps(falcon_metrics)
            #req = requests.post(self.falcon_url, data=json.dumps(falcon_metrics))
            #print datetime.now(), "INFO: [%s]" % self.endpoint, "[%s]" % self.falcon_url, req.text
        except Exception, e:
            print datetime.now(), "ERROR: [%s]" % self.endpoint, e
            return

if __name__ == '__main__':
    RedisMetrics('', 'localhost', '127.0.0.1', 12700).run()
