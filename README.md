# redis-open-falcon

Redis Monitor Script for Open Falcon

### Step 1: Edit conf

Rename `redis-open-falcon.yml.default` to `redis-open-falcon.yml`, then edit the file, and add your redis servers.

```yml
falcon:
    push_url: http://127.0.0.1:6071/v1/push
    step: 60

# Redis clusters
redis-clusters:
    - {endpoint: "localhost", host: "127.0.0.1", port: 12700, password: "", tags: ""}

```

### Step 2: Add the monitor script to crontab

```
$ crontab -l
*/1 * * * * cd /path/to/redis-open-falcon && python -u ./bin/redis-falcon.py >> redis-open-falcon.log 2>&1
```

# redis-open-falcon

用于 Open Falcon 的 Redis 监控采集脚本

### 第一步：编辑配置文件

将 `redis-open-falcon.yml.default` 重命名为 `redis-open-falcon.yml`，然后编辑这个文件，添加你要监控的 Redis 服务器信息。

```yml
falcon:
    push_url: http://127.0.0.1:6071/v1/push
    step: 60

# Redis clusters
redis-clusters:
    - {endpoint: "localhost", host: "127.0.0.1", port: 12700, password: "", tags: ""}
```

### 第二步：将监控脚本添加到 crontab 中定时执行

```
$ crontab -l
*/1 * * * * cd /path/to/redis-open-falcon && python -u ./bin/redis-falcon.py >> redis-open-falcon.log 2>&1
```

## 好用就给个 Star 呗！