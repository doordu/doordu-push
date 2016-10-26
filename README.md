
## 依赖

* Python3
* pip

## 安装

    pip3 install -r requirements

## 配置

**config.ini**

    [apns]
    use_sandbox = yes                                   ; 生产环境配置为true
    cert_filename = doordu                              ; 通常不需要更改
    passphrase = doordu123456                           ; 证书密钥

    [huawei]
    client_id = 10201628                                ; 通常不需要更改
    client_secret = sv76t42d7qcashyjjz1s5hxzrubuuvvf    ; 通常不需要更改

    [xiaomi]
    package_name = com.doordu.mobile                    ; 通常不需要更改
    secret_key = xJB7WtOurXuwwP4zKGdDLQ==               ; 通常不需要更改
    
    [meizu]
    app_id = 110015                                     ; 通常不需要更改
    secret_key = 1e3412be25f44814827811fed0a1ff2c       ; 通常不需要更改
    

    [mqtt]
    host = localhost                                    ; mosquitto ip
    port = 1883                                         ; mosquitto 端口
    
    [redis]
    host = localhost                                    ; redis ip
    port = 6379                                         ; redis port
    auth = doordu                                       ; redis 连接密码
    

## 运行

    celery -A tasks worker --loglevel=info --concurrency=8 -P threads

    gunicorn main:app -w 8 -b 0.0.0.0:9700

**注意**: 0.0.0.0应该设置内网IP

启动脚本在init.d目录下

**参数解释**

* -w: 启动进程数
* -b: 监听端口和IP
