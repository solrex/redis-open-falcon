# es-open-falcon
Redis Monitor Script for Open Falcon

```
$ crontab -l
*/1 * * * * cd /path/to/redis-open-falcon && python -u ./bin/redis-falcon.py >> /path/to/log/redis-open-falcon.log 2>&1
```
