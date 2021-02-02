---
title: "Lichee_04驱动分析"
date: 2021-01-06T00:02:20+08:00
tags: ["lichee"]
draft: false
---

<div align="center" style= 'font-size: 48px;'>
    Lichee_04驱动分析
</div>

# 一、字符驱动

linux的驱动主要分为字符驱动、块驱动和网络驱动，字符驱动比较简单，容易上手。linux系统中一切皆是文件，驱动也不例外，用户程序在用户空间使用驱动主要是通过读写设备文件，并且对设备文件进行读写操作，因此实现驱动程序应该实现以下功能：

* 在文件系统中创建一个可以访问的文件
* 建立起读写打开等函数的实现
* 将读写打开等函数与创建的文件联系起来

<div class="mermaid">
graph TD
d4-->d5(class_create)
d5-->d6(device_create) 
d5-->d7(device_create)
subgraph register_chrdev
	d1(alloc_chrdev)-->d2(cdev_alloc)-->d3(cdev_init)-->d4(cdev_add)
end
</div>

如上图所示：驱动程序的注册的流程如上图所示：由上述一系列函数组成，其中函数说明如下：

| 函数          | 说明                                                         |
| ------------- | ------------------------------------------------------------ |
| alloc_chrdev  | 申请一组可用的主从设备号，当主设备号为零的时候表明是动态分配 |
| cdev_alloc    | 申请一个可用的dev对象，用于存储操作函数相关的结构体          |
| cdev_init     | 将操作函数结构体赋值                                         |
| cdev_add      | 将cdev与主从设备号关联起来                                   |
| class_create  | 在/sys/class/路径下面创建一个类用于存储驱动相关信息          |
| device_create | 在class_create创建的类下面创建一个device，分配唯一的主从设备号，并且uevent给udev在/dev下面创建软连接 |



tops.c

```c
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


uint8_t sizeof_tops = 0;
uint8_t tops_mem[64];
static int tops_open(struct inode *inode,struct file *file){

	return 0;
}

static int tops_release(struct inode *inode,struct file *file){


	return 0;	
}

static ssize_t tops_read(struct file *file,char* buff,size_t count,loff_t *f_pos){	
	if(count > 64)count = 64;
	if(count > sizeof_tops)count = sizeof_tops;
	if(copy_to_user(buff,tops_mem,count))
		return -EFAULT;

	sizeof_tops -= count;

	return count;
}

static ssize_t tops_write(struct file *file,const char* buff,size_t count,loff_t *f_pos){
	if(count > 64)count = 64;

	sizeof_tops = 0;
	if(copy_from_user(tops_mem,buff,count))
		return -EFAULT;

	sizeof_tops = count;

	return count;
}

static struct class *dev_class;
static int 			major;
static void tops_register(char* name,const struct file_operations* fops){
    major = register_chrdev(0, name, fops);
	if (major < 0){
        printk(KERN_ALERT "can find valid majon\n");   
		return;
    }

	dev_class = class_create(THIS_MODULE, name);
	device_create(dev_class, NULL, MKDEV(major, 0), NULL, "hello_udev");
}

static void tops_unregister(char* name){
	class_destroy(dev_class);
	unregister_chrdev(major, name);
}

const struct file_operations hello_fops = {
	.owner = THIS_MODULE,
	.read = tops_read,
	.write = tops_write,
	.open = tops_open,
	.release = tops_release
};

static int __init tops_init(void)
{
	printk(KERN_ALERT "tops World!\n");

    tops_register("tops",&hello_fops);
	return 0;
}
 
static void __exit tops_exit(void)
{
	printk(KERN_ALERT "tops exit!\n");

	tops_unregister("tops");
}
 

module_init(tops_init); 
module_exit(tops_exit);
 
MODULE_LICENSE("GPL");
```

Makefile

```makefile
obj-m+=tops.o
CLOSS = ARCH=arm CROSS_COMPILE=arm-linux-gnueabihf-
KDIR := /workspace/01system/linux

all:
	make $(CLOSS) -C $(KDIR) M=$(PWD) modules 
clean:
	make $(CLOSS) -C $(KDIR) M=$(PWD) clean
```

编译好的程序下载进去，便可以看到驱动已经加载到了系统，对数据进行写入写出，看看结果。

```bash
# ls /dev/hello_udev -la
crw-------    1 root     root      247,   0 Jan  1 00:42 /dev/hello_udev
# ls /sys/class/tops/
hello_udev
# echo "123" > /dev/hello_udev 
# cat /dev/hello_udev 
123
#
```

卸载驱动，发现/dev下面以及```/sys/class```下面已经没有了相对应的驱动信息，说明驱动卸载成功。

# 二、platform平台驱动

linux驱动为了实现硬件与驱动的分离，引入了总线的概念，其中采用vfs的方式实现总线的匹配，其中总线的目录位于```/sys/bus```下面，在bus下面新建一个自己的总线，实现匹配函数便可以实现device与driver的匹配，并初始化driver。

linux系统自带了platform总线驱动，在main函数中建立了platform总线，并且实现了其match函数。

<div class="mermaid">
graph TB
   A(/sys/bus) --> B(platform) 
   B --> C(device)
   B --> D(driver)
   E(match)
</div>

其初始化函数位于```platform.c```中的```platform_bus_init```函数，其匹配规则如下：

```c
static int platform_match(struct device *dev, struct device_driver *drv)
{
	struct platform_device *pdev = to_platform_device(dev);
	struct platform_driver *pdrv = to_platform_driver(drv);

	/* When driver_override is set, only bind to the matching driver */
	if (pdev->driver_override)									
		return !strcmp(pdev->driver_override, drv->name);	//匹配device->driver_override：driver->name

	/* Attempt an OF style match first */
	if (of_driver_match_device(dev, drv))					//匹配设备树
		return 1;

	/* Then try ACPI style match */
	if (acpi_driver_match_device(dev, drv))					//匹配acpi，少用
		return 1;

	/* Then try to match against the id table */
	if (pdrv->id_table)
		return platform_match_id(pdrv->id_table, pdev) != NULL;	//匹配driver->id_table:device

	/* fall-back to driver name match */
	return (strcmp(pdev->name, drv->name) == 0);				//匹配device_name与driver->name
}
```

其中用的比较多的是device_name:driver_name，以及id_table里面的名称。但是该部分匹配都是使用的device结构体以及driver结构体，平台驱动使用的是platform_device和platform_driver，其中platform_device中继承device，platform_driver继承driver。其中platform_device中的name属性会被其device结构体继承，因此保证

<div class="mermaid">
graph TB
	a2-->b2
	subgraph platform device
    a1(name)-.->a2(device)-.->a3(...)
    end
    subgraph platform driver
    b1(probe)-.->b2(driver.name)-.->b3(other)
    end
</div>

## 测试例程

* 新建platform设备
* 新建platform驱动
* 编译、运行

test_platform_device.c

```c
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
// #include "hello.h"
#include <linux/device.h>
#include <linux/gpio.h>
#include <linux/platform_device.h>

static struct resource hello_resource[] = {
	DEFINE_RES_MEM(0x1234, 0x18),
	DEFINE_RES_IRQ(12),
};

static struct platform_device hello_device = {
	.name		= "hello_platform",
	.id			= 1,
    .num_resources  = ARRAY_SIZE(hello_resource),
    .resource   = hello_resource
};

static int __init hello_world_init(void)
{
	platform_device_register(&hello_device);
	return 0;
}


static void __exit hello_world_exit(void)
{
    printk(KERN_DEBUG "goodbye world!!!\n");
}


module_init(hello_world_init);
module_exit(hello_world_exit);

MODULE_LICENSE("GPL");  
```

test_platform_driver.c

```c
/*
 * @Author: your name
 * @Date: 2021-01-12 22:58:29
 * @LastEditTime: 2021-01-12 23:33:10
 * @LastEditors: Please set LastEditors
 * @Description: In User Settings Edit
 * @FilePath: /03platform/test_platform_device.c
 */
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
#include <linux/platform_device.h>

static int hello_probe(struct platform_device *dev){
	struct resource *mem1, *irq1;
	
	printk(KERN_DEBUG "dev driver !!!\n");

	mem1 = platform_get_resource(dev, IORESOURCE_MEM, 0);
	irq1 = platform_get_resource(dev, IORESOURCE_IRQ, 1);

	printk(KERN_DEBUG "mem1 %lld !!!\n", mem1->start);
	printk(KERN_DEBUG "irq1 %lld !!!\n", irq1->start);

	return 0;	
}

static struct platform_driver hello_driver = {
	.driver.name = "hello_platform",
	.probe = hello_probe,
};

static int __init hello_world_init(void)
{
	platform_driver_register(&hello_driver);
	return 0;
}


static void __exit hello_world_exit(void)
{
    printk(KERN_DEBUG "goodbye world!!!\n");
}


module_init(hello_world_init);
module_exit(hello_world_exit);

MODULE_LICENSE("GPL");  
```

Makefile

```makefile

```

编译后，插入device后，在系统的```/sys/bus/platform/devices```查看如下信息：

```bash
cd /sys/bus/platform/devices/
luocang@luocang-SC:/sys/bus/platform/devices$
luocang@luocang-SC:/sys/bus/platform/devices$ ls
 ACPI0003:00         INT0800:00         pcspkr       PNP0C14:01
 ACPI000C:00         INT345D:00         PNP0103:00   PNP0C14:02
 alarmtimer.0.auto   intel_pmc_core.0   PNP0C04:00   reg-dummy
 coretemp.0          intel_rapl_msr.0   PNP0C09:00   regulatory.0
 eisa.0              iTCO_wdt           PNP0C0A:00   serial8250
'Fixed MDIO bus.0'   kgdboc             PNP0C0C:00   vesa-framebuffer.0
 hello_platform.1    microcode          PNP0C0D:00   VPC2004:00
 i8042               MSFT0101:00        PNP0C14:00


```

![image-20210202201445504](../images/image-20210202201445504.png)



![image-20210202201641525](../images/image-20210202201641525.png)
























































<script src="../js/mermaid.min.js"></script>