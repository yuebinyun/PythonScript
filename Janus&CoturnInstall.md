
# Janus 和 Coturn 服务器的部署说明

## 0x00 基础环境准备

下述软件为通用软件，主要用于调试使用，查看网络流量，查看日志信息等。

### 添加源
如果系统为 Centos， 则先添加 EPEL 源
```
// for Centos 64 Bit
wget http://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
rpm -ivh epel-release-latest-7.noarch.rpm
yum repolist
```

### 常用软件
vim net-tools(ifconfig) iftop wget mlocate


### 升级软件
```
// 升级， 防止 git clone 失败
yum update -y nss curl libcurl 
```

### 防火墙
测试过程中先关闭防火墙，实际部署中，请按需配置
```
// Centos 关闭防火墙
systemctl disable firewalld && systemctl stop firewalld
```

## 注意。
部署服务器的时候，请部署一台服务器，测试一台服务器。请确保部署的服务器没有问题后部署下一台，千万不要，所有的服务器都部署成功了，在一起测试，那样很危险。

## 0x02 Janus 部署

### Janus 安装

[Janus 的 github 主页](https://github.com/meetecho/janus-gateway)

```
// 0. 新建个人目录
// 建个目录，防止文件凌乱
mkdir /home/xx && cd /home/xx


// 1. 安装依赖环境
yum install libmicrohttpd-devel jansson-devel libnice-devel \
   openssl-devel libsrtp-devel sofia-sip-devel glib-devel \
   opus-devel libogg-devel libcurl-devel lua-devel \
   pkgconfig gengetopt libtool autoconf automake cmake


// 2. 升级 openssl
wget https://github.com/cisco/libsrtp/archive/v2.0.0.tar.gz
tar xfv v2.0.0.tar.gz
cd libsrtp-2.0.0
./configure --prefix=/usr --enable-openssl
make shared_library && sudo make install

// 3. 安装 websockets
git clone git://git.libwebsockets.org/libwebsockets
cd libwebsockets
# If you want the stable version of libwebsockets, uncomment the next line
# git checkout v2.4-stable
# 这里需要要使用 v2.4.0 的版本，否则 websockets 通信会异常。
git checkout fcf5b2c
mkdir build
cd build
# See https://github.com/meetecho/janus-gateway/issues/732 re: LWS_MAX_SMP
cmake -DLWS_MAX_SMP=1 -DCMAKE_INSTALL_PREFIX:PATH=/usr -DCMAKE_C_FLAGS="-fpic" ..
make && sudo make install

// 4. 安装 Janus
git clone https://github.com/meetecho/janus-gateway.git
cd janus-gateway
sh autogen.sh
./configure --prefix=/opt/janus --disable-data-channels --disable-rabbitmq --disable-mqtt
make
make install

// 5. 生成 Janus 默认配置文件
make configs
```

`注意：` 编译 Janus 源码的使用，如果 `make` 失败，请不要紧张，这很正常，一次编过只是偶然。遇到的情况有：
  1. openssl 升级了，没有正确指向。
  2. libsoup 版本过低，需要升级，这个情况定位了很久。
  3. 最新版本代码编译失败，git 切换到旧的稳定版本分支。


### Janus 配置


需要关注的配置文件如下：
  * /opt/janus/etc/janus/janus.cfg
  * /opt/janus/etc/janus/janus.plugin.videoroom.cfg
  * /opt/janus/etc/janus/janus.transport.websockets.cfg
上述文件是 `make configs` 后自动生成的，而非自己创建。
如果只是测试使用，无需修改配置文件。


### Janus 启动
 
```
cd /opt/janus/bin/
./janus
```

请留意输出日志，如果出现 `error` 信息，可能是出现了问题。


### 信令交互接口测试
目前信令交互使用 `WebSockets` 协议，子协议是 `janus-protocol`，默认端口是 8188.

使用 python 脚本做连通性测试。
```
// 1. 安装 WebSockets python 库
pip install websocket-client

// 2. 使用 websocket-client 自带测试脚本
pwsdump.py <ws://ip:8188> -s "janus-protocol"

// 3. 输出日志如下，表示连通性 ok
//  wsdump.py ws://103.229.215.202:8188 -s "janus-protocol"
//  Press Ctrl+C to quit
//  > test
//  < {
//     "janus": "error",
//     "error": {
//        "code": 456,
//        "reason": "Missing mandatory element (transaction)"
//     }
//  }
```


### Janus Web 客户端

Janus 源码中自带提供测试的 web app。
路径：/opt/janus/bin/html
使用方法，只需起个 http 服务，路径指向即可。
```
// 起 http 服务的一种简单方法
cd /opt/janus/bin/html
// python -m SimpleHTTPServer 80
python -m SimpleHTTPServer // 默认使用 8000 端口
```
页面访问，即可测试您部署的 Janus 服务器。


## 0x03 Coturn 部署

`Coturn` 安装容易，配置可以简单也可以很复杂，需要对 `stun` 和 `turn` 协议有所了解。

Coturn 是 Turn 服务器的一种，目前使用最多。
Coturn 提供的功能：
  * 打洞
  * 流媒体中继

在我们的方案中，Coturn 服务器是作为边缘节点使用。

### Coturn 安装
[Coturn 的 github 主页](https://github.com/coturn/coturn)

`安装 Coturn 前，请先确保基本软件已经安装完毕，否则回头阅读 0x00 部分。`


```
// 0. 新建个人目录
// 建个目录，防止文件凌乱
mkdir /home/xx && cd /home/xx


// 1. 安装依赖环境
yum install openssl-devel sqlite libevent-devel sqlite-devel 

// 2. 安装 Coturn
git clone https://github.com/coturn/coturn 
cd coturn 
./configure 
make 
make install

// 生成证书
openssl req -x509 -newkey rsa:2048 -keyout /etc/turn_server_pkey.pem -out /etc/turn_server_cert.pem -days 99999 -nodes


// 编辑配置文件
配置文件默认路径： /etc/turnserver.conf
这个配置文件，在您安装完 coturn 后可能自动生成，也可能没有自动生成。两种情况都遇到过。
如果没有，新建该文件。

// pidfile="/var/run/turnserver/turnserver.pid"
// listening-ip= <监听IP,公网IP>
// listening-port=3478
// tls-listening-port=5349
// relay-ip=<该服务器上的内网 IP，没有就不配>
// user=user:user
// verbose
// userdb=/usr/local/var/db/turndb
// lt-cred-mech
```

### Coturn 的启动
Coturn 安装完毕后，自动添加系统路径。

```
turnserver -L <公网可访问 IP> -o -a -b -f -r demo -v
```

请仔细阅读启动日志，谢谢。

### 连通性测试

``` 
// 1. 安装 python app pystun
pip install pystun

// 2. 使用，如果运行出错，则表明 python 版本太高
// 作者已停更....
pythun -d -H <ip> -P <port>

// 3. 输出，如果输出如下，表明连通性 ok
// .....
// DEBUG:pystun:recvfrom:('<ip>', <port>)
// .....
// ......
// ........
```

## 0x04 End
`Thanks!!`