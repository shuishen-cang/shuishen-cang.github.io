---
title: "shuixia09-linux-makefile"
date: 2021-02-01T16:06:09+08:00
draft: false
tags: ["shuixia"]

---



<div align = "center" style="font-size:48px">Makefile修改使用说明-linux</div>

[TOC]

# 一、概述

​		Makefile是一种控制自动编译的工具，Makefile关系到整个工程的编译规则。它告诉系统哪些文件先编译，哪些文件后编译，哪些文件在什么时候清理掉等等。因为是用来告知系统如何进行操作的，所以Makefile的语言风格跟shell很像，Makefile中也可以执行操作系统的命令。

​		海思官方提供了liteos以及linux下面的makefile，用来编译程序，得到相应的库文件以及可执行文件，其中liteos部分提供了一个可用的makefile，顶层makefile通过调用底层makefile得到相应的编译结果，但是在sample中的makefile存在一些缺陷，其具体表现是只能编译单个文件，并不支持多文件的编译，但是在编写驱动以及应用程序的时候，往往需要多文件的编译以及多文件的支持，因此需要对makefile做一些修改，以下就makefile做一些讲解。



# 二、 参考文件

GPIO复用功能描述文件《Hi3559A V100_PINOUT_EN.xlsx》

驱动操作使用指南《外围设备驱动 操作指南.pdf》

寄存器相关操作《Hi3559A╱C V100 ultra-HD Mobile Camera SoC 用户指南.pdf》



# 三、驱动编译

​		linux的驱动分为内核驱动和模块驱动，内核驱动编译到内核里面，不方便后期的更改，一般后期添加的驱动都是以模块驱动的方式加载，驱动编译成.ko文件的模块，在用户程序空间以insmod的方式插入到内核。

​		linux的驱动根据类型分为字符驱动、块驱动和网络驱动，一般的外设都是以字符驱动的形式加载到内核空间，块驱动和网络驱动更多是作为字符驱动的上层驱动提供，因此本文只考虑字符驱动。

​		字符驱动的makefile如下：

**Makefile**

```makefile
obj-m+=hello.o
# KERNEL_PATH = /lib/modules/$(shell uname -r)/build/
CROSS_COMPILE := aarch64-himix100-linux-
ARCH_TYPE = arm64
KERNEL_PATH = /workspace/02sdk/Hi3559AV100R001C02SPC020/01.software/board/Hi3559AV100_SDK_V2.0.2.0/osdrv/opensource/kernel/linux-4.9.y_multi-core/
all:
	make -C ${KERNEL_PATH} M=${PWD} ARCH=${ARCH_TYPE} CROSS_COMPILE=${CROSS_COMPILE} modules
clean:
	make -C $(KERNEL_PATH) M=$(PWD) clean

.PHONE:install remove

install:all
	sudo insmod hello.ko
	sudo dmesg -c | grep hello

remove:
	sudo rmmod hello
```

**hello.c**

```c
#include "hello.h"

MODULE_LICENSE("GPL");              

//设置初始化入口函数
static int __init hello_world_init(void)
{
    printk(KERN_DEBUG "hello world!!!\n");
    return 0;
}

//设置出口函数
static void __exit hello_world_exit(void)
{
    printk(KERN_DEBUG "goodbye world!!!\n");
}

//将上述定义的init()和exit()函数定义为模块入口/出口函数
module_init(hello_world_init);
module_exit(hello_world_exit);
```

**hello.h**

```c
#ifndef __HELLO_H__
#define __HELLO_H__

#include <linux/init.h>             
#include <linux/module.h>          
#include <linux/kernel.h>   
#include <linux/fs.h>

#endif
```

​		编译该部分代码即可生成相对应的```hello.ko```文件，在用户程序空间```insmod hello.ko```即可插入该部分驱动。

# 四、 API描述

​	

# 五、 应用示例

​		linux的应用程序多以posix的接口访问底层硬件，程序编译以多以makefile的方式(也可以使用IDE工具搭建，但是makefile更方便)。

**Makefile**

```makefile
PROJECT = hello
BUILDDIR := ./build
CFLAGS += -O0 -g3 -pipe -lpthread -lm -Wall -Wextra -Wundef #-DRC_AUTOPILOT_EXT# -mfpu=vfpv3-fp16
CC = aarch64-himix100-linux-gcc

ALLINC += 	.	

ALLCSRC += 	main.c 

CSRC = $(ALLCSRC)
CINC += $(ALLINC)	
INCL	  		:= $(addprefix -I, $(CINC))
COBJS 			:= $(CSRC:.c=.o)
CPPOBJS 		:= $(CPPSRC:.cpp=.o)
ASMOBJS 		:= $(ASMSRC:.s=.o)
ASMXOBJS		:= $(ASMXSRC:.S=.o)
OBJS = $(ASMXOBJS) $(ASMOBJS) $(COBJS) $(CPPOBJS)

all: chkbindir $(OBJS)
	$(CC) $(CFLAGS) $(addprefix $(BUILDDIR)/,$(notdir $(OBJS))) -o $(BUILDDIR)/$(PROJECT)

.PHONE: chkbindir clean

clean:
	rm -rf $(BUILDDIR)

chkbindir:
	@if test ! -d $(BUILDDIR) ; \
	then \
	mkdir $(BUILDDIR) ; \
	fi

$(COBJS) : %.o : %.c
	$(CC) -c $(CFLAGS) $(INCL) $(IINCDIR) $< -o $(BUILDDIR)/$(notdir $@)	
```

**main.c**

```c
#include <stdio.h>
#include <fcntl.h>          /* File Control Definitions             */
#include <termios.h>        /* POSIX Terminal Control Definitions   */
#include <unistd.h>         /* UNIX Standard Definitions                */
#include <errno.h>          /* ERROR Number Definitions             */
#include <stdint.h>
#include "sys/statfs.h"
#include <stdlib.h> 
#include <sys/types.h> 
#include <sys/stat.h> 
#include <string.h>

int main(void){

    printf("hello-world!\n");

    return 0;
}
```

​		编译该部分代码即可在当前路径下创建一个build路径，在build路径下会生成相对应的可执行文件，该可执行文件可以在板卡上直接运行，使用NFS挂载该文件即可实现文件的挂载，在挂载目录直接运行即可。



# 六、注意事项

* linux的库多数以动态链接库的形式链接，因此程序放在任何路径下编译都是一样的
* 编译驱动需要linux的源文件，需要注意
<script src="../js/mermaid.min.js"></script>