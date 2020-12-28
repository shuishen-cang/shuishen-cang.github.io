---
title: "Lichee_02系统编译"
date: 2020-12-27T21:31:22+08:00
draft: false
tags: ["lichee"]
---

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


# 二、烧录uboot

sudo dd if=u-boot-sunxi-with-spl.bin of=/dev/sdb bs=1024 seek=8



