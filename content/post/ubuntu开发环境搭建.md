---
title: "Ubuntu开发环境搭建"
date: 2020-12-15T22:21:25+08:00
draft: true
---

# 一、换源



# 二、安装软件
```bash
sudo apt install vim
sudo apt install gcc
sudo apt install openocd
sudo apt install libusb
sudo apt install git
sudo apt install minicom

git config --global user.email "335403241@qq.com"
git config --global user.name "cang"
```

# 三、NFS
搭建NFS服务器环境，供ARM板挂载
### 安装 & 配置
```bash
sudo apt install nfs-kernel-server
sudo vim /etc/exports
# 添加：
/home/luocang/workspace *(rw,sync,no_subtree_check)

#重启nfs服务
sudo service nfs-kernel-server restart
```

### 测试

```bash
sudo mount -t nfs -o nolock 127.0.0.1:/home/luocang/workspace /mnt
```

### 脚本
```bash
#!/bin/sh

sudo apt install nfs-kernel-server
echo '/home/luocang/workspace *(rw,sync,no_subtree_check)' >> cang.txt
sudo service nfs-kernel-server restart

```

# 四、SSH

### 安装 & 配置
```bash
sudo apt install ssh
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub
```
### 添加远程公钥 (在目标远程机器中)
```bash
cd ~/.ssh
vim authorized_keys
#添加 讲主机的id_ras.pub的内容复制到该文件中


sudo service sshd restart
```
### SSH清楚know
当同样的ip地址，目标机的信息和保存的信息不同的时候，便会登录失败
```bash
ssh-keygen -R 192.168.xx.xx

```

# 五、tftpd
搭建TFTPD服务器环境，供ARM板下载
### 安装 & 配置
```bash
# 不需要安装tftpd，否则可能搭建失败
sudo apt install tftpd-hpa
sudo apt install tftp

sudo vim /etc//default/tftpd-hpa 
#修改为：
TFTP_USERNAME="tftp"
TFTP_DIRECTORY="/home/srv/tftp"
TFTP_ADDRESS=":69"
TFTP_OPTIONS="-l -c -s"
#TFTP_OPTIONS="--secure"

# 新建目录
cd /home/srv
mkdir tftp
chmod 777 tftp
cd tftp
touch lk.txt
echo 12 > lk.txt

sudo service tftpd-hpa restart
```

### 测试

```bash
tftp localhost
get lk.txt
cat lk.txt
```

# 六、docker
### 安装 & 配置
```bash
sudo apt-get update

sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common
sudo curl -fsSL https://mirrors.aliyun.com/docker-ce/linux/ubuntu/gpg | apt-key add -

sudo apt-key fingerprint 0EBFCD88
# 正常输出为：
# pub   rsa4096 2017-02-22 [SCEA]
#      9DC8 5822 9FC7 DD38 854A  E2D8 8D81 803C 0EBF CD88
# uid           [ unknown] Docker Release (CE deb) <docker@docker.com>
# sub   rsa4096 2017-02-22 [S]

sudo add-apt-repository "deb [arch=amd64] https://mirrors.aliyun.com/docker-ce/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install docker-ce

sudo groupadd docker                #添加docker用户组
sudo gpasswd -a $luocang docker     #检测当前用户是否已经在docker用户组中，其中XXX为用户名，例如我的，luocang
sudo gpasswd -a $USER docker        #将当前用户添加至docker用户组
newgrp docker                       #更新docker用户组
```
### docker开启镜像
```bash
# 挂载共享卷
docker run -it --name=hisys -v /home/luocang/workspace/04work:/work -v /home/srv/tftp:/tftp hiubuntu14 /bin/sh



```
