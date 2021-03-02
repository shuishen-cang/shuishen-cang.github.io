---
title: "shuixia10-linux-gpioaf"
date: 2021-02-01T16:06:09+08:00
draft: false
tags: ["shuixia"]
---



<div align = "center" style="font-size:48px">GPIO复用驱动测试使用说明-linux</div>

[TOC]

# 一、概述

​		HI3559A每个管脚可以配置为输入或者输出。这些管脚用于生成特定应用的输出信号或采集特定应用的输入信号。作为输入管脚时，GPIO 可作为中断源；作为输出管脚时，每个GPIO 都可以独立地清 0 或置 1。

​		该文档就GPIO的复用功能驱动部分做详细讲解。



# 二、 参考文件

GPIO复用功能描述文件《Hi3559A V100_PINOUT_EN.xlsx》

驱动操作使用指南《外围设备驱动 操作指南.pdf》

寄存器相关操作《Hi3559A╱C V100 ultra-HD Mobile Camera SoC 用户指南.pdf》



# 三、驱动编译

​		linux的的字符串驱动一般作为platform驱动编译，platform驱动具有良好的移植性，但是设计起来较为复杂，本文就单文件驱动进行设计，linux驱动的设计步骤如下：

* 实现基本的驱动功能函数
* 申请主次设备号
* 申请cdev设备，初始化cdev并且设置相关函数
* 创建一个class设备，并且在class下创建device

<div class="mermaid">
graph TD
d4-->d5(class_create)
d5-->d6(device_create) 
d5-->d7(device_create)
subgraph register_chrdev
	d1(alloc_chrdev)-->d2(cdev_alloc)-->d3(cdev_init)-->d4(cdev_add)
end
</div>

​		系统提供的驱动部分的函数如下:

| 函数          | 说明                                                         |
| ------------- | ------------------------------------------------------------ |
| alloc_chrdev  | 申请一组可用的主从设备号，当主设备号为零的时候表明是动态分配 |
| cdev_alloc    | 申请一个可用的dev对象，用于存储操作函数相关的结构体          |
| cdev_init     | 将操作函数结构体赋值                                         |
| cdev_add      | 将cdev与主从设备号关联起来                                   |
| class_create  | 在/sys/class/路径下面创建一个类用于存储驱动相关信息          |
| device_create | 在class_create创建的类下面创建一个device，分配唯一的主从设备号，并且uevent给udev在/dev下面创建软连接 |



​		字符驱动的文件如下：

**Makefile**

```makefile
obj-m+=gpioaf.o
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
	sudo insmod gpioaf.ko
	sudo dmesg -c | grep gpioaf

remove:
	sudo rmmod gpioaf

```

**gpioaf.c**

```c
#include "gpioaf.h"

static int tops_open(struct inode *inode,struct file *file){

	return 0;
}

static int tops_release(struct inode *inode,struct file *file){

	return 0;	
}

static ssize_t tops_read(struct file *file,char* buff,size_t count,loff_t *f_pos){

	return count;
}

static ssize_t tops_write(struct file *file,const char* buff,size_t count,loff_t *f_pos){

	return count;
}

// static void __iomem *gpioaf_int_base;
static long tops_ioctl(struct file *file, unsigned int cmd, unsigned long arg){
    struct hi_user_reg attr;
    uint32_t i;
    void __iomem *gpioaf_int_base;

	if (_IOC_TYPE(cmd) == 'U') {
		switch (_IOC_NR(cmd)) {
		case _IOC_NR(HI_USER_REG_WRITE):
            if(copy_from_user((void*)&attr, (void*)arg, sizeof(struct hi_user_reg))){
                printk("copy from user err");
                return -EFAULT;
            }
            // ioremap
            gpioaf_int_base = ioremap(attr.reg_start, attr.reg_num << 2);     
            for(i = 0;i < attr.reg_num; i++){
                SYS_WRITEL(gpioaf_int_base + (i << 2), attr.reg_value[i]);
            }
            //unioremap
            iounmap(gpioaf_int_base);

			break;
		case _IOC_NR(HI_USER_REG_READ):
            if(copy_from_user((void*)&attr, (void*)arg, sizeof(struct hi_user_reg))){
                printk("copy from user err");
                return -EFAULT;
            }

            // ioremap
            gpioaf_int_base = ioremap(attr.reg_start, attr.reg_num << 2);     
            for(i = 0;i < attr.reg_num; i++){
                attr.reg_value[i] = SYS_READ(gpioaf_int_base + (i << 2));
            }
            //unioremap
            iounmap(gpioaf_int_base);

            if(copy_to_user((void*)arg, (void*)&attr, sizeof(struct hi_user_reg))){
                printk("copy to user err");
                return -EFAULT;
            }
            break;
        }
    }

    return 0;
}

const struct file_operations gpioaf_fops = {
	.owner = THIS_MODULE,
	.read = tops_read,
	.write = tops_write,
	.open = tops_open,
	.release = tops_release,
    .unlocked_ioctl = tops_ioctl
};

static struct       class *dev_class;
static int 			major;
#define             GPIOAF  "gpioaf"

MODULE_LICENSE("GPL");              

//设置初始化入口函数
static int __init gpioaf_init(void)
{
    printk(KERN_DEBUG "gpioaf!!!\n");

    major = register_chrdev(0, GPIOAF, &gpioaf_fops);
	if (major < 0){
        printk(KERN_ALERT "can find valid majon\n");   
		return -EFAULT;
    }

	dev_class = class_create(THIS_MODULE, GPIOAF);
	device_create(dev_class, NULL, MKDEV(major, 0), NULL, "hello_udev");

    return 0;
}

//设置出口函数
static void __exit gpioaf_exit(void)
{
    class_destroy(dev_class);
	unregister_chrdev(major, GPIOAF);
    printk(KERN_DEBUG "goodbye gpioaf!!!\n");
}

//将上述定义的init()和exit()函数定义为模块入口/出口函数
module_init(gpioaf_init);
module_exit(gpioaf_exit);
```

**gpioaf.h**

```c
#ifndef __GPIOAF_H__
#define __GPIOAF_H__

#include <linux/init.h>
#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/fs.h>
#include <linux/cdev.h>
#include <linux/slab.h>
#include <linux/uaccess.h>
#include <linux/semaphore.h>
#include <linux/miscdevice.h>
#include <linux/vmalloc.h>
#include <linux/wait.h>
#include <linux/poll.h>
#include <linux/sched.h>
#include <linux/proc_fs.h>
#include <linux/seq_file.h>
#include <linux/mutex.h>
#include <linux/spinlock.h>
#include <linux/timer.h>
#include <asm/io.h>
#include <linux/delay.h>
#include <linux/kthread.h>
#include <linux/irq.h>
#include <linux/interrupt.h>
#include <linux/err.h>
#include <linux/device.h>
#include <linux/gpio.h>

#define MAX_REGS    64
struct hi_user_reg {
    uint32_t    reg_start;
    uint32_t    reg_num;
    uint32_t    reg_value[64];
};

#define	HI_USER_DRV  'U'

#define HI_USER_REG_WRITE  \
	_IOW(HI_USER_DRV, 1, struct hi_user_reg)
#define HI_USER_REG_READ  \
	_IOW(HI_USER_DRV, 2, struct hi_user_reg)

#define SYS_WRITEL(Addr, Value) ((*(volatile unsigned int *)(Addr)) = (Value))
#define SYS_READ(Addr)          (*((volatile int *)(Addr)))

#endif
```

​		编译该部分代码即可生成相对应的```gpioaf.ko```文件，在用户程序空间```insmod gpioaf.ko```即可插入该部分驱动。



# 四、 API描述



​		如上述的驱动代码，其中仅实现了ioctl部分的代码，其余的oepn()、close()、read()、write()等函数都没有具体实现的定义，因此仅需要关注ioctl部分即可,ioctl实现了对硬件寄存器的读写，因此可以用来设置gpio的复用功能。

​		

可设置的参数如下：

| cmd宏定义           | 指令码 | 参数               | 说明                   |
| ------------------- | ------ | ------------------ | ---------------------- |
| HI_USER_REG_WRITE   | 1      | struct hi_user_reg | 往寄存器写一组数据     |
| HI_USER_REG_READ    | 2      | struct hi_user_reg | 往寄存器读取一组数据   |
| HI_USER_REG_WRITEOR | 3      | struct hi_user_reg | 往寄存器写一组数据，或 |



# 五、 应用示例

​		编译上述驱动便会在dev下生成一个udev设备，该设备的设备名为```/dev/gpioaf0```，访问该设备可以直接操作硬件寄存器，便可以在应用层实现GPIO的复用功能。

**Makefile**

```makefile
PROJECT = test
BUILDDIR := ./build
CFLAGS += -O0 -g3 -pipe -lpthread -lm -Wall -Wextra -Wundef #-DRC_AUTOPILOT_EXT# -mfpu=vfpv3-fp16
CC = aarch64-himix100-linux-gcc

ALLINC += 	.	

ALLCSRC += 	main.c 	\
			hal_gpioaf.c

CSRC = $(ALLCSRC)
CINC += $(ALLINC)	
INCL	  		:= $(addprefix -I, $(CINC))
COBJS 			:= $(CSRC:.c=.o)
CPPOBJS 		:= $(CPPSRC:.cpp=.o)
ASMOBJS 		:= $(HIPWMASMSRC:.s=.o)
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
#include "hal_gpioaf.h"

const char  tx_buff[8] = "helle";
char        rx_buff[8] = ""; 
int main(void){
    AF_UARTO_Config();

    return 0;
}
```

**hal_gpioaf.c**

```c
#include "hal_gpioaf.h"

#define GPIOAF      "/dev/gpioaf0"      

void AF_UARTO_Config(void){
    int fd;
    struct hi_user_reg wreg;

    fd = open(GPIOAF, O_RDWR);
    if(fd < 0){
        printf("can't open port!\n");
        return;       
    }

    wreg.reg_num = 2;
    wreg.reg_value[0] = AF_UART0_VAL;
    wreg.reg_value[1] = AF_UART0_VAL;
    wreg.reg_start = AF_UART0_TX;
    ioctl(fd, HI_USER_REG_WRITEOR, &wreg);

    ioctl(fd, HI_USER_REG_READ, &wreg);
    printf("reg1:%x\n",wreg.reg_value[0]);
    printf("reg2:%x\n",wreg.reg_value[1]);

    close(fd);
}
```

**hal_gpio.h**

```c
#ifndef __HAL_GPIOAF_H__
#define __HAL_GPIOAF_H__

#include <stdio.h>
#include <fcntl.h>          /* File Control Definitions             */
#include <termios.h>        /* POSIX Terminal Control Definitions   */
#include <unistd.h>         /* UNIX Standard Definitions 	        */
#include <errno.h>          /* ERROR Number Definitions             */
#include <stdint.h>
#include "sys/statfs.h"
#include <stdlib.h> 
#include <sys/types.h> 
#include <sys/stat.h> 
#include <string.h>
#include <sys/ioctl.h>

#define IOREGL(N)              (0x1F000000 + N * 4)
#define IOREGM(N)              (0x1F001000 + (N - 76) * 4)
#define IOREGH(N)              (0x1F002000 + (N - 138) * 4)
#define IOREG(N)                (N <= 75 ?  IOREGL(N): IOREGM(N))

#define AF_UART0_VAL            0x01
#define AF_UART0_TX             IOREG(53)
#define AF_UART0_RX             IOREG(54)
#define AF_UART1_VAL            0x01
#define AF_UART1_TX             IOREG(55)
#define AF_UART1_RX             IOREG(56)
#define AF_UART2_VAL            0x01
#define AF_UART2_TX             IOREG(57)
#define AF_UART2_RX             IOREG(58)
#define AF_UART3_VAL            0x01
#define AF_UART3_TX             IOREG(59)
#define AF_UART3_RX             IOREG(60)
#define AF_UART4_VAL            0x01
#define AF_UART4_TX             IOREG(61)
#define AF_UART4_RX             IOREG(62)

#define MAX_REGS    64
struct hi_user_reg {
    uint32_t    reg_start;
    uint32_t    reg_num;
    uint32_t    reg_value[64];
};

#define	HI_USER_DRV  'U'

#define HI_USER_REG_WRITE  \
	_IOW(HI_USER_DRV, 1, struct hi_user_reg)
#define HI_USER_REG_READ  \
	_IOW(HI_USER_DRV, 2, struct hi_user_reg)
#define HI_USER_REG_WRITEOR \
    _IOW(HI_USER_DRV, 3, struct hi_user_reg)

#define SYS_WRITEL(Addr, Value) ((*(volatile unsigned int *)(Addr)) = (Value))
#define SYS_READ(Addr)          (*((volatile int *)(Addr)))

void AF_UARTO_Config(void);

#endif
```



# 六、注意事项

* 使用应用程序之前，必须先insmod驱动
<script src="../js/mermaid.min.js"></script>