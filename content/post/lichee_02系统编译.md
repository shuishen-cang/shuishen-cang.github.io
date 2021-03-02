---
title: "Lichee_02系统编译"
date: 2020-12-27T21:31:22+08:00
draft: false
tags: ["lichee"]
---

<div align="center" style= 'font-size: 48px;'>
    Lichee_02系统编译
</div>

# 一、编译uboot

## 1. 下载uboot
主机和容器之间存在共享文件夹，在主机里下载最新的uboot。
```bash
cd ~/workspace/02prj/01lichee_zero/01system/
git clone https://github.com/Lichee-Pi/u-boot.git -b v3s-current
```
等待下载完毕后，进入u-boot路径，由于买的板子没有spiflash，因此需要编译支持SD卡启动，修改uboot，

```bash
# 修改 include/configs/sun8i.h, 使u-boot可以直接从tf卡启动：
vim include/configs/sun8i.h

# 添加
#define CONFIG_BOOTCOMMAND "setenv bootm_boot_mode sec; load mmc 0:1 0x41000000 zImage; load mmc 0:1 0x41800000 sun8i-v3s-licheepi-zero-dock.dtb; bootz 0x41000000 - 0x41800000;"
#define CONFIG_BOOTARGS    "console=ttyS0,115200 panic=5 mtdparts=tf:1M(uboot),64k(dtb),4M(kernel),-(rootfs) rootwait root=/dev/mmcblk0p2 earlyprintk rw  vt.global_cursor_default=0"

```

## 2. 编译
先安装必须的依赖库。
```bash
apt-get install libncurses5-dev
apt-get install device-tree-compiler
apt-get install python
apt-get install bc

```

```bash
docker start lichee 
docker attach lichee

cd /workspace/01system/u-boot/

make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- LicheePi_Zero_800x480LCD_defconfig
make ARCH=arm menuconfig
time make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- 2>&1 | tee build.log
```

编译后的文件为u-boot-sunxi-with-spl.bin，将该文件拷贝到images目录下。
```bash
cd ../
mkdir -p images
cd u-boot/
cp u-boot-sunxi-with-spl.bin ../images/
cd 
```

# 二、编译linux内核
```bash
git clone https://github.com/Lichee-Pi/linux.git
cd linux
make ARCH=arm licheepi_zero_defconfig
make ARCH=arm menuconfig   #add bluethooth, etc.
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j16
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j16 INSTALL_MOD_PATH=out modules
make ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf- -j16 INSTALL_MOD_PATH=out modules_install
```
编译完成的zImage放置在/arch/arm/boot/路径下，将该文件拷贝到images路径下。

```bash
cp arch/arm/boot/dts/sun8i-v3s ../images/
cp arch/arm/boot/dts/sun8i-v3s-licheepi-zero-dock.dtb ../images/
```

# 三、编译rootfs
buildroot可以编译uboot，kernel以及rootfs，uboot上面已经编译成功，在这里进行rootfs编译。
先下载buildroot.

```bash
git clone git@github.com:buildroot/buildroot.git
cd buildroot
cp configs/licheepi_zero_defconfig .config
make menuconfig
```

默认使用的是国外的下载源，这里可以设置国内的镜像源。

![img](/home/luocang/.config/Typora/typora-user-images/image-20210202201215017.png)

在Target packages->etworking applications勾选openssh以及rpcbind。

在Bootloaders下面取消U-Boot。
在Kernel下面取消kernel。

## 1. 使用buildroot的交叉编译器make

buildroot内部默认配置了交叉编译器，可以直接用于make。

```bash
make
```

## 2.使用交叉编译器make

使用内部自带的交叉编译器，在后期更换交叉编译器可能会出现缺少库的情况，因此最好是用外部设置的交叉编译器，便于后期编写程序的方便。

```bash
make menuconfig
make
```

配置参数如下：

```bash
/ Toolchain  --->    
Toolchain type: 		External toolchain
Toolchain     :			Custom toolchain   
Toolchain origin :		Pre-installed toolchain
Toolchain path:   		/opt/gcc-linaro-6.3.1-2017.02-x86_64_arm-linux-gnueabihf
Toolchain prefix:		arm-linux-gnueabihf
External toolchain gcc version: 6.x					 # 和交叉编译器保持一致
External toolchain kernel headers series： 4.6.x		# 和交叉编译器保持一致
External toolchain C library：glibc/eglibc，			# 这里必须选glibc
Toolchain has SSP support： y						 # 必须选择，或者莫名其妙的错误
Toolchain has RPC support? y						 # 必须选择，或者莫名其妙的错误
```

## 3. 拷贝根文件系统

make后生成的根文件系统放置在output/images/路径下面。

```bash
cp output/images/rootfs.tar ../images/
```

# 四、烧录uboot

## 1. 分区

采用ubuntu自带的disks就可以对sd卡进行分区，分区分为两个区，根据上面的参数，uboot、内核、设备树都在第一个分区，文件系统为fat文件系统，命名为boot，根文件系统为第二个分区，文件系统为ext4文件系统，命名为rootfs。


## 2. 烧写
```bash
cd ../images
# 我的sd卡在电脑的盘符为sdb
sudo dd if=u-boot-sunxi-with-spl.bin of=/dev/sdb bs=1024 seek=8

cp zImage sun8i-v3s-licheepi-zero-dock.dtb /media/luocang/boot/
tar -xvf rootfs.tar -C /media/luocang/rootfs/
```

# 五、配置
将SD插入板卡，连接串口便可以开机进入系统了，为了后期的开发，必须配置好ssh，最好能够配置好nfs。

## 1. 开机配置
修改开机免登陆
```bash
vi /etc/inittab

# ttyS0::respawn:/sbin/getty -L  ttyS0 115200 vt100 # GENERIC_SERIAL
ttyS0::respawn:-/bin/sh 
```

修改IP地址
```bash
vi /etc/network/interfaces 

# 添加
auto usb0
iface usb0 inet static   
    address 192.168.4.200
    gateway 192.168.4.1
    netmask 255.255.255.0
```
重启，ping主机。
```bash
ping 192.168.4.1
```

## 2. ssh
使用ps指令查看ssh的相关状态，发现sshd并没有启动。
```bash
ps -ef | grep ssh
```

用于根文件系统的文件夹都不是rootfs的目录，因此需要修改文件夹的用户组。
```bash
cd /
chown -R root:root *
```

修改ssd相关配置。
```bash
ssh-keygen 
cd root/.ssh/
cp id_rsa.pub authorized_keys

vi /etc/ssh/sshd_config
#修改
#PermitRootLogin prohibit-password
PermitRootLogin yes
```
重启后，查看sshd已经启动了，在主机登录。
```bash
ssh root@192.168.4.200
```

## 3. nfs
为了后期开发时候的便捷，尝试一下nfs。
```bash
mount -t nfs -o nolock 192.168.4.1:/home/luocang/workspace /mnt
cd mnt
ls
```
发现nfs已经能够成功使用，说明nfs功能正常，至此环境搭建完毕，可以脱离串口进行开发了。建立脚本，以便后期nfs挂载。
```bash
mkdir -p /home/00shell
cd /home/00shell/

vi nfs.sh
# 添加
#!/bin/sh

mount -t nfs -o nolock 192.168.4.1:/home/luocang/workspace /mnt

chmod +x nfs.sh 
```



<script src="../js/mermaid.min.js"></script>