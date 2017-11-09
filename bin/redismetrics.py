#!/usr/bin/env python

import threading
import redis
import json
import time
from datetime import datetime
import requests
import os

class RedisMetrics(threading.Thread):
    status_map = {
        'green': 0,
        'yellow': 1,
        'red': 2
    }

    def __init__(self, falcon_url, endpoint, host, port, db = 0, password = '', tags = '', falcon_step = 60, daemon = False):
        self.falcon_url = falcon_url
        self.falcon_step = falcon_step
        self.host = host
        self.port = port
        self.endpoint = endpoint
        self.db = db
        self.password = password
        self.tags = tags

        self.keyword_metrics = ['uptime_in_days', 'connected_clients', 'blocked_clients', 'used_memory', 'maxmemory',
                              'used_memory_rss', 'used_memory_peak', 'used_memory_lua_human', 'mem_fragmentation_ratio',
                              'total_commands_processed',
                              'rejected_connections', 'expired_keys', 'evicted_keys', 'keyspace_hits',
                              'keyspace_misses']
        self.counter_keywords = ['total_commands_processed', 'rejected_connections',
            'expired_keys', 'evicted_keys',
            'keyspace_hits', 'keyspace_misses']
        super(RedisMetrics, self).__init__(None, name=endpoint)
        self.setDaemon(daemon)

    def run(self):
        try:
            self.redis = redis.Redis(host = self.host, port = self.port, db = self.db, password = self.password);
        except Exception as e:
            print datetime.now(), "ERROR: [%s]" % self.endpoint, e
            return
        falcon_metrics = []
        # Statistics
        try:
            timestamp = int(time.time())
            redis_info = self.redis.info()
            executable = os.path.basename(redis_info['executable'])
            # Original metrics
            for keyword in self.keyword_metrics:
                falcon_metric = {
                 'counterType': 'COUNTER' if keyword in self.counter_keywords else 'GAUGE',
                    'metric': "redis." + keyword,
                    'endpoint': self.endpoint,
                    'timestamp': timestamp,
                    'step': self.falcon_step,
                    'tags': self.tags,
                    'value': redis_info[keyword]
                }
                falcon_metrics.append(falcon_metric)
            # Self defined metrics
            falcon_metric = {
                'counterType': 'COUNTER',
                'metric': "redis.used_memory_ratio",
                'endpoint': self.endpoint,
                'timestamp': timestamp,
                'step': self.falcon_step,
                'tags': self.tags,
                'value': redis_info['used_memory']/redis_info['maxmemory']
            }
            falcon_metrics.append(falcon_metric)
            #print json.dumps(falcon_metrics)
            req = requests.post(self.falcon_url, data=json.dumps(falcon_metrics))
            print datetime.now(), "INFO: [%s]" % self.endpoint, "[%s]" % self.falcon_url, req.text
        except Exception, e:
            print datetime.now(), "ERROR: [%s]" % self.endpoint, e
            return

if __name__ == '__main__':
    RedisMetrics('', 'localhost', '127.0.0.1', 12700).run()