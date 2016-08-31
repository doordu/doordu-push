
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

    [huawei]
    client_id = 10201628                                ; 通常不需要更改
    client_secret = sv76t42d7qcashyjjz1s5hxzrubuuvvf    ; 通常不需要更改

    [xiaomi]
    package_name = com.doordu.mobile                    ; 通常不需要更改
    secret_key = xJB7WtOurXuwwP4zKGdDLQ==               ; 通常不需要更改

    [mqtt]
    host = localhost                                    ; mosquitto ip
    port = 1883                                         ; mosquitto 端口
    
    [redis]
    host = localhost                                    ; redis ip
    port = 6379                                         ; redis port
    auth = doordu                                       ; redis 连接密码

## 运行

    gunicorn main:app -w 4 -b 0.0.0.0:8000

**参数解释**

* -w: 启动进程数
* -b: 监听端口和IP