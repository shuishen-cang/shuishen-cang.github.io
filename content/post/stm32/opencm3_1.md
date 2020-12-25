---
title: "opencm3使用教程(一)"
date: 2020-12-19T11:14:37+08:00
draft: false
---

# 一、下载opencm3
我的opencm3库的路径放在```/home/luocang/workspace/01library/02STM32/```路径下，在该目录下安装opencm3的库
```bash
cd /home/luocang/workspace/01library/02STM32/
git clone --recursive git@github.com:libopencm3/libopencm3-examples.git
mv libopencm3-examples/ 01libopencm3-examples/
cd 01libopencm3-examples/libopencm3/
git reset --hard v0.8.0
cd ../
make -j12
```
编译完毕后可以在路径下看到编译的链接库，在examples可以看到例程编译后的可执行文件。

# 二、设置路径



# 三、编写Makefile




