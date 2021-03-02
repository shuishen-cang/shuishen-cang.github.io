---
title: "Lichee_01开发环境"
date: 2020-12-27T21:31:22+08:00
draft: false
tags: ["lichee"]
---

<div align="center" style= 'font-size: 48px;'>
    Lichee_01开发环境
</div>

[toc]

# 一、开发环境搭建

## 1. 建立docker容器
​		手上有一块lichee板子很久了，lichee的资料相对较全，最近又在学习linux，因此拿这个平台验证一下也不错，要开发芯片，必须先搭建交叉编译环境，考虑到电脑上已经安装了一个树莓派的交叉编译环境了，那么就在docker里面安装交叉编译器吧。

​		先搭建一个最基本的docker开发环境吧，采用ubuntu18为基础。
```bash
docker pull ubuntu:18.04
docker images
```
​		可以看到已经存在ubuntu镜像了，然后在workspace下面建立一个目录用来作为lichee的开发目录，其目录为```~/workspace/02prj/01lichee_zero```下面，因此采用以下命令创建一个容器。
```bash
docker run -it --name=lichee -v ~/workspace/02prj/01lichee_zero:/workspace ubuntu:18.04 /bin/bash


# 进入docker容器后
apt update
apt install nano

nano /etc/apt/sources.list
# 修改为
deb http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-security main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-updates main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-proposed main restricted universe multiverse
deb-src http://mirrors.aliyun.com/ubuntu/ bionic-backports main restricted universe multiverse
#end

apt update
apt upgrade
apt install vim
apt install make
apt install gcc
exit
```

由此便完成了ubuntu的系统的基本搭建，将该镜像备份一下，以便于以后搭建别的开发环境。
```bash
docker commit lichee ubuntu:18.04
docker images
```

## 2. 安装交叉编译器
在百度网盘上可以下载到交叉编译器```gcc-linaro-6.3.1-2017.02-x86_64_arm-linux-gnueabihf.tar.xz```，在GUI下对该文件解压，将解压后的文件拷贝到docker容器下，并且设置环境变量。
```bash
cp -r gcc-linaro-6.3.1-2017.02-x86_64_arm-linux-gnueabihf/ ~/workspace/02prj/01lichee_zero/

docker start lichee 
docker attach lichee

# 进入docker容器中
mv /workspace/gcc-linaro-6.3.1-2017.02-x86_64_arm-linux-gnueabihf/ /opt/

vim ~/.bashrc
# 添加
export PATH=$PATH:/opt/gcc-linaro-6.3.1-2017.02-x86_64_arm-linux-gnueabihf/bin
```
至此交叉编译器搭建完毕。


