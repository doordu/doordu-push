
## 依赖

* Python3
* pip

## 安装和更新

安装和更新你都要执行：

    pip3 install -r requirements

## 配置

**config.yaml**

general:
  use_sandbox: true    #  正式环境一定是false
  
mqtt:
  host: 10.0.0.243
  port: 1883
  
redis:
  host: 127.0.0.1
  port: 6379
  auth: doordu


主要配置这些，其他都不用管
    

## 运行

    celery -A tasks worker --loglevel=info --concurrency=8 -P threads

    gunicorn main:app -w 8 -b 0.0.0.0:9700

**注意**: 0.0.0.0应该设置内网IP

启动脚本在init.d目录下

**参数解释**

* -w: 启动进程数
* -b: 监听端口和IP
