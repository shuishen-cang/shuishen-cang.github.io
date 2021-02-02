---

title: "ubuntu03-交叉编译器"
date: 2020-12-15T22:21:25+08:00
draft: false
tags: ["ubuntu"]
---

<div align="center" style= 'font-size: 48px;'>
    ubuntu-交叉编译器
</div>

# 一、安装交叉编译器

## 1. 安装		

在linux下面安装交叉编译器用来编译ARM的程序，其中M系统采用```arm-none-eabi-gcc```，其中linux程序采用```arm-linux-gnueabihf-gcc```，可以采用apt的方式安装。

```bash
sudo apt install gcc-arm-none-eabi
sudo apt install gcc-arm-linux-gnueabi

arm-linux-gnueabihf-gcc -v
arm-none-eabi-gcc -v
```

## 2. 配置

其中安装的交叉编译器并不能用来编译所有的芯片程序，大部分时候会受到库的影响和配置的影响。因此需要做出一定的修改，其关键参数如下：

```bash
--with-arch=armv7-a 
--with-fpu=vfpv3-d16 
--with-float=hard 
--with-mode=thumb 

--disable-sjlj-exceptions 
--disable-werror 
--enable-multilib 
--enable-checking=release 
--build=x86_64-linux-gnu 
--host=x86_64-linux-gnu 
--target=arm-linux-gnueabihf 
```

```bash
--disable-werror : 设置警告不报错
```

```bash
--enable-multilib : 可以支持多芯片
```

这些都是默认的配置，可以做一些芯片来适应不同的芯片，如下：

```bash
arm-linux-gnueabihf-gcc -v -mfpu=vfpv4 -mfloat-abi=soft -march=armv7 -mtune=cortex-a7 -mcpu=cortex-a7
```



# 二、测试代码

​	




<script src="../js/mermaid.min.js"></script>