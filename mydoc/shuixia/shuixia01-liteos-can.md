---
title: "shuixia01-liteos-can"
date: 2021-02-01T16:06:09+08:00
draft: false
tags: ["shuixia"]

---



<div align = "center" style="font-size:48px">CAN设备驱动测试使用说明-liteos</div>

[TOC]

# 一、概述

​		控制器局域网络 CAN（Controller Area Network）最初是由德国 Bosch 公司设计并应用于汽车的监测和控制。由于其作为一种技术先进、可靠性高、功能完善、成本合理的远程网络通讯控制方式，因此 CAN 总线正逐步被广泛应用到各种控制领域,如中控车机等。
​		芯片共支持 3 个 CAN 总线控制器，主 SOC 子系统有 2 个，Sensor Hub 子系统有 1个。

​		芯片的3个CAN总线控制器的地址在经过地址转换后均可以访问，即SOC系统可以访问Sensor Hub 的CAN总线控制器，但是SOC上的CAN总线控制器其中断连接到GIC中断控制器上，Sensor Hub 上的CAN总线控制器其中断连接在M7的中断控制器上，因此SOC使用Sensor Hub 的CAN总线控制器只能使用查询模式，而不能使用中断模式。

​		CAN总线控制器模块特性如下：

* CAN 总线控制器的工作时钟为 50 MHz。

* 支持标准技术规范 CAN 2.0A 和 CAN 2.0B。

* 支持多设备时的总线仲裁，优先级高的 ID 可继续被发送。

* 支持传输速率可编程，最高可达 1Mbps。

* 最大支持 32 个报文对象，每个报文对象均可编程。

* 支持主动错误和被动错误的自我判定以及故障节点的隔离。

* 支持错误的自我修复。

* 支持自动重传模式。

* 支持报文屏蔽。

* 支持中断屏蔽。

* 支持连续报文接收。

* 支持 loop-back、silent、basic 三种测试模式，其中 loop-back 和 silent 可以组合使用。

* 不支持软件配置错误帧和过载帧。

  

# 二、 参考文件

GPIO复用功能描述文件《Hi3559A V100_PINOUT_EN.xlsx》

驱动操作使用指南《外围设备驱动 操作指南.pdf》

寄存器相关操作《Hi3559A╱C V100 ultra-HD Mobile Camera SoC 用户指南.pdf》



# 三、 驱动编译

​		CAN总线控制器在使用前需要先配置CAN设备的基本属性以及配置波特率相关、报文对象相关属性，其初始化以及收发相关过程如下：

<div class="mermaid">
graph TD
a0(配置GPIO)-->a(初始化报文对象)-->b(修改波特率相关寄存器)-->c(配置接收掩码)-->d(查询接收邮箱)-->f(读取数据)
c-->e(等待中断)-->f
</div>


**Makefile**

```makefile
LITEOSTOPDIR ?= ../..

SAMPLE_OUT = ./build

include $(LITEOSTOPDIR)/config.mk
RM = -rm -rf

include user/user.mk
include hal/hal.mk
SRCS += $(wildcard sample.c)
OBJS := $(SRCS:.c=.o)

#LITEOS_BASELIB += -lipcmsg_single_liteos
LITEOS_LIBDEPS := --start-group $(LITEOS_LIBDEP) --end-group
LITEOS_CFLAGS  += $(SINC)

all: chkbindir $(OBJS)
ifneq ($(LITEOS_CPU_TYPE), arm926)
ifneq ($(OUT)/lib/libipcm.a, $(wildcard $(OUT)/lib/libipcm.a))
	echo "$(OUT)"
	cp -rf $(LITEOS_CPU_TYPE)/*.a $(OUT)/lib
endif
endif
	@$(LD) $(LITEOS_LDFLAGS) --gc-sections -Map=$(SAMPLE_OUT)/sample.map -o $(SAMPLE_OUT)/sample $(addprefix $(SAMPLE_OUT)/,$(notdir $(OBJS)))  $(LITEOS_LIBDEPS) $(LITEOS_TABLES_LDFLAGS)
	@$(OBJCOPY) -O binary $(SAMPLE_OUT)/sample $(SAMPLE_OUT)/sample.bin
	cp $(SAMPLE_OUT)/sample.bin /workspace/05tftpboot/sample_a53

clean:
	@if test -d $(SAMPLE_OUT) ; \
	then \
	rm -rf $(SAMPLE_OUT) ; 		\
	fi
	@rm /workspace/05tftpboot/sample_a53

test: all
	@echo $(LITEOS_CXXOPTS)

debug: all
	python3 /workspace/04shell/download_python/makedebug_a53.py

flash:
	python3 /workspace/04shell/download_python/class_downlinux_emmc.py	

$(OBJS): %.o: %.c 
	@$(CC) $(LITEOS_CFLAGS) $(LITEOS_CXXFLAGS) -o $(SAMPLE_OUT)/$(notdir $@) -c $^

chkbindir:
	@if test ! -d $(SAMPLE_OUT) ; 	\
	then 							\
	mkdir $(SAMPLE_OUT) ; 			\
	fi

```

**hal_can.h**

```c
#ifndef __HAL_CAN_H__
#define __HAL_CAN_H__

#include "hal.h"

#define PORT_CAN    0x02
#define PORT_UART   0x01
#define PORT_GPIO   0x00 
#define IOCFG_REG53 0x1F0000D4      //AA35,can0_rx
#define IOCFG_REG54 0x1F0000D8      //AB35,can0_tx
#define IOCFG_REG55 0x1F0000DC      //AD33,can1_rx
#define IOCFG_REG56 0x1F0000E0      //AD34,can1_tx
#define APB_CLK     50000000      
#define TSEG1       (4 - 1)         //prop + tseg1,这里后期需要调试
#define TSEG2       (5 - 1)
#define TSJW        (4 - 1)  


enum CAN_BASE{
    CAN0_REG_BASE = 0x12070000,
    CAN1_REG_BASE = 0x12071000
};

#define CAN_CONTROL(group_reg_base)  				((group_reg_base) + 0X0000)
#define CAN_STATUS(group_reg_base)            		((group_reg_base) + 0x0004)
#define CAN_ERRCOUNT(group_reg_base)            	((group_reg_base) + 0x0008)
#define CAN_BITTIMING(group_reg_base)            	((group_reg_base) + 0x000C)
#define CAN_INTERRUPT(group_reg_base)            	((group_reg_base) + 0x0010)
#define CAN_TEST(group_reg_base)            		((group_reg_base) + 0x0014)
#define CAN_BRPEXT(group_reg_base)            		((group_reg_base) + 0x0018)

#define CAN_IF1CMD_REQUE(group_reg_base)            ((group_reg_base) + 0x0020)
#define CAN_IF1CMD_MASK(group_reg_base)            	((group_reg_base) + 0x0024)
#define CAN_IF1_MASK1(group_reg_base)            	((group_reg_base) + 0x0028)
#define CAN_IF1_MASK2(group_reg_base)            	((group_reg_base) + 0x002C)
#define CAN_IF1_ARBIT1(group_reg_base)            	((group_reg_base) + 0x0030)
#define CAN_IF1_ARBIT2(group_reg_base)            	((group_reg_base) + 0x0034)
#define CAN_IF1_MSGCONT(group_reg_base)             ((group_reg_base) + 0x0038)
#define CAN_IF1_DATAA1(group_reg_base)            	((group_reg_base) + 0x003C)
#define CAN_IF1_DATAA2(group_reg_base)            	((group_reg_base) + 0x0040)
#define CAN_IF1_DATAB1(group_reg_base)            	((group_reg_base) + 0x0044)
#define CAN_IF1_DATAB2(group_reg_base)            	((group_reg_base) + 0x0048)

#define CAN_IF2CMD_REQUE(group_reg_base)            ((group_reg_base) + 0x0080)
#define CAN_IF2CMD_MASK(group_reg_base)            	((group_reg_base) + 0x0084)
#define CAN_IF2_MASK1(group_reg_base)            	((group_reg_base) + 0x0088)
#define CAN_IF2_MASK2(group_reg_base)            	((group_reg_base) + 0x008C)
#define CAN_IF2_ARBIT1(group_reg_base)            	((group_reg_base) + 0x0090)
#define CAN_IF2_ARBIT2(group_reg_base)            	((group_reg_base) + 0x0094)
#define CAN_IF2_MSGCONT(group_reg_base)             ((group_reg_base) + 0x0098)
#define CAN_IF2_DATAA1(group_reg_base)            	((group_reg_base) + 0x009C)
#define CAN_IF2_DATAA2(group_reg_base)            	((group_reg_base) + 0x00A0)
#define CAN_IF2_DATAB1(group_reg_base)            	((group_reg_base) + 0x00A4)
#define CAN_IF2_DATAB2(group_reg_base)            	((group_reg_base) + 0x00A8)

#define CAN_TRANS_REQUE1(group_reg_base)			((group_reg_base) + 0x0100)
#define CAN_TRANS_REQUE2(group_reg_base)			((group_reg_base) + 0x0104)
#define CAN_TRANS_NEWDATA1(group_reg_base)			((group_reg_base) + 0x0120)
#define CAN_TRANS_NEWDATA2(group_reg_base)			((group_reg_base) + 0x0124)
#define CAN_TRANS_INTERRUPT_PEND1(group_reg_base)	((group_reg_base) + 0x0140)
#define CAN_TRANS_INTERRUPT_PEND2(group_reg_base)	((group_reg_base) + 0x0144)
#define CAN_TRANS_MSG_VALID1(group_reg_base)		((group_reg_base) + 0x0160)
#define CAN_TRANS_MSG_VALID2(group_reg_base)		((group_reg_base) + 0x0164)
#define NUM_HAL_INTERRUPT_CAN0                      139
#define NUM_HAL_INTERRUPT_CAN1                      140

#define CANIR_EN    1
#define LOOPBACK    0

// #define can_event_signal(event, bit)                LOS_EventWrite(event, bit)
// #define can_event_wait(event, bit, timeout)         LOS_EventRead(event, bit,\
//                                                     LOS_WAITMODE_AND + LOS_WAITMODE_CLR, timeout)


void hal_can_initial(int canid, uint32_t bandrate);
void hal_can_recvmask(int canid,uint8_t msgNum, uint32_t mask, uint32_t id, uint8_t len);
void hal_can_transmit(int canid, uint32_t id, uint8_t *txbuff, uint8_t len);
uint16_t hal_can_receive(int canid);
uint8_t hal_can_readmsg(int canid, uint32_t *id, uint8_t *rxbuff, uint8_t msgNum);

#endif
```

**hal_can.c**

```c
#include "hal_can.h"

static void can_gpio_initial(int canid){
    if(0 == canid){
        writel((1 << 12) | PORT_CAN,IOCFG_REG53);       //
        writel(PORT_CAN,IOCFG_REG54);                   //

        writel(1 << 5,0x12151400);                      //GPIO17.5，sleeppin，must 0
        writel(0,(0x12151000 + (1 << ((6) + 2)))); 
    }
    else if(1 == canid){
        writel(0x1d00 | PORT_CAN,IOCFG_REG55);          //
        writel(0x400 | PORT_CAN,IOCFG_REG56);           //

        writel(1 << 6,0x12151400);                      //GPIO17.6 sleep引脚
        writel(0,(0x12151000 + (1 << ((6) + 2)))); 
    }
}

irqreturn_t can_isr(int a, void *arg){
    HWI_IRQ_PARAM_S *thirq = (HWI_IRQ_PARAM_S*)arg;
    uint8_t canid = thirq->swIrq == NUM_HAL_INTERRUPT_CAN0 ? 0 : 1;
    uint32_t can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    uint32_t reg = readl(CAN_STATUS(can_base));         //SR
    if(reg & 0x10){    
        writeand(~0x10, CAN_STATUS(can_base));
        writeor(0x07, CAN_STATUS(can_base));            //rxok
        // can_event_signal(&can_wait_event,canid == 0 ? 0x01 : 0x10);     
    }
    else if(reg & 0x08){                                //txok
        writeand(~0x08, CAN_STATUS(can_base));
        writeor(0x07, CAN_STATUS(can_base));
        // can_event_signal(&can_wait_event,(4 << canid));    
    }
    else if((reg & 0x07 != 0) && (reg & 0x07 != 7)){
        writeor(0x07, CAN_STATUS(can_base));
    }

    return IRQ_HANDLED;
}

/**************************************************
 * @func: 配置1~16号msg为发送，17~32为接收
 * ***********************************************/
static void hal_can_msg_config(int canid){
    uint8_t i;
    enum CAN_BASE can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    writel(0xB2 ,CAN_IF1CMD_MASK(can_base));                // 
    writel(0,CAN_IF1_ARBIT1(can_base));                     // id, 低16位
    writel(0xA000,CAN_IF1_ARBIT2(can_base));                // id, 高13位
    writel(0x0088, CAN_IF1_MSGCONT(can_base)); 

    for(i = 1;i <= 16;i ++){
        writel(i, CAN_IF1CMD_REQUE(can_base));              
    }
}


static void can_start(int canid, uint32_t bandrate){
    uint32_t reg = 1;
    uint16_t BRP;
    enum CAN_BASE can_base;
    int ret;
    
    can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;
    BRP = APB_CLK / bandrate / 10 - 1;
    writel(0x81 ,CAN_CONTROL(can_base));         //测试模式
    writel(0x1 << 4,CAN_TEST(can_base));         //环回模式
    writel(0xF3 ,CAN_IF1CMD_MASK(can_base));

    for(uint8_t i = 1;i <= 32; i++){
        writel(i ,CAN_IF1CMD_REQUE(can_base));   //清除msg
        do{
            reg = readl(CAN_IF1CMD_REQUE(can_base));
        }while(reg & 0x8000);                   //等待写完
    }
    writel(0x41 ,CAN_CONTROL(can_base));
    writel((TSEG2 << 12) | (TSEG1 << 8) | (TSJW << 6) | (BRP & 0x3F),CAN_BITTIMING(can_base)) ;  //波特率
    writel(((BRP >> 6) & 0x0F),CAN_BRPEXT(can_base)) ;

#if LOOPBACK
    reg |= 0x80; 
#endif
#if CANIR_EN
    reg |= (1 << 2) | (1 << 1);                 //错误中断，状态中断，总中断
    if(canid == 0)
        ret = request_irq(NUM_HAL_INTERRUPT_CAN0, can_isr, 0,"CAN0_IRQ",NULL);
    else
        ret = request_irq(NUM_HAL_INTERRUPT_CAN1, can_isr, 0,"CAN1_IRQ",NULL);

    // LOS_EventInit(&can_wait_event);             //中断唤醒
#endif

    writel(reg ,CAN_CONTROL(can_base));         //
    reg &= 0xFE;
    writel(reg ,CAN_CONTROL(can_base));         //初始化完毕
    hal_can_msg_config(canid);
}

void hal_can_recvmask(int canid,uint8_t msgNum, uint32_t mask, uint32_t id, uint8_t len){
    uint8_t i;
    enum CAN_BASE can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    writel(0xF8 ,CAN_IF2CMD_MASK(can_base));                            // mask, arb ctrl 清除IntPnd
    writel(mask & 0xFFFF ,CAN_IF2_MASK1(can_base));                     // mask, 低16位
    writel((mask >> 16) & 0xFFFF ,CAN_IF2_MASK2(can_base));             // mask, 高13位

    writel(id & 0xFFFF ,CAN_IF2_ARBIT1(can_base));                      // id, 低16位
    writel(((mask >> 16) & 0xFFFF ) | 0xC000,CAN_IF2_ARBIT2(can_base)); // id, 高13位

    for(i = 0;i < len;i ++){
        if(i == (len - 1))  writel(0x1088, CAN_IF2_MSGCONT(can_base)); 
        else                writel(0x1008, CAN_IF2_MSGCONT(can_base));   
        writel(msgNum ++, CAN_IF2CMD_REQUE(can_base));              
    }
}

void hal_can_initial(int canid, uint32_t bandrate){
    enum CAN_BASE can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    can_gpio_initial(canid);
    can_start(canid, bandrate);
    hal_can_recvmask(canid,17, 0, 0, 4);        //接收所有数据
}

void hal_can_transmit(int canid, uint32_t id, uint8_t *txbuff, uint8_t len){
    static uint8_t msgNum = 1;
    uint8_t i;
    enum CAN_BASE can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    if(len > 8)len = 8; 

    writel(0xB3 ,CAN_IF1CMD_MASK(can_base));                            // 
    writel(id & 0xFFFF,CAN_IF1_ARBIT1(can_base));                       // id, 低16位
    writel((id >> 16) & 0x1FFF | 0xE000,CAN_IF1_ARBIT2(can_base));      // id, 高13位
    writel(0x80 | len, CAN_IF1_MSGCONT(can_base)); 
    writel(msgNum, CAN_IF1CMD_REQUE(can_base));                         //

    writel(0x87 ,CAN_IF1CMD_MASK(can_base));                            // 
    writel(txbuff[0] | (txbuff[1] << 8) ,CAN_IF1_DATAA1(can_base));     // 
    writel(txbuff[2] | (txbuff[3] << 8) ,CAN_IF1_DATAA2(can_base));     // 
    writel(txbuff[4] | (txbuff[5] << 8) ,CAN_IF1_DATAB1(can_base));     // 
    writel(txbuff[6] | (txbuff[7] << 8) ,CAN_IF1_DATAB2(can_base));     // 
    writel(msgNum, CAN_IF1CMD_REQUE(can_base));                         //
    if(++ msgNum == 17)msgNum = 1;
    while(readl(CAN_IF1CMD_REQUE(can_base)) & 0x8000);
}

uint16_t hal_can_receive(int canid){
    uint16_t temp;
    enum CAN_BASE can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    if(readl(CAN_STATUS(can_base)) & 0x10){
        temp = readl(CAN_TRANS_NEWDATA2(can_base));
        writel(0,CAN_TRANS_NEWDATA2(can_base));

        return temp;
    }
    return 0;
}

uint8_t hal_can_readmsg(int canid, uint32_t *id, uint8_t *rxbuff, uint8_t msgNum){
    uint8_t ret = 0;
    enum CAN_BASE can_base = canid == 0 ? CAN0_REG_BASE : CAN1_REG_BASE;

    writel(0x3F ,CAN_IF1CMD_MASK(can_base));                            // 
    writel(msgNum, CAN_IF1CMD_REQUE(can_base));                         

    *id = readl(CAN_IF1_ARBIT1(can_base));                              // id, 低16位    
    *id |= (readl(CAN_IF1_ARBIT2(can_base)) & 0x1FFF) << 16;            // id, 高13位    
    ret = readl(CAN_IF1_MSGCONT(can_base)) & 0x0F;  

    rxbuff[0] = readl(CAN_IF1_DATAA1(can_base)) & 0xFF;
    rxbuff[1] = (readl(CAN_IF1_DATAA1(can_base)) >> 8) & 0xFF;
    rxbuff[2] = readl(CAN_IF1_DATAA2(can_base)) & 0xFF;
    rxbuff[3] = (readl(CAN_IF1_DATAA2(can_base)) >> 8) & 0xFF;
    rxbuff[4] = readl(CAN_IF1_DATAB1(can_base)) & 0xFF;
    rxbuff[5] = (readl(CAN_IF1_DATAB1(can_base)) >> 8) & 0xFF;
    rxbuff[6] = readl(CAN_IF1_DATAB2(can_base)) & 0xFF;
    rxbuff[7] = (readl(CAN_IF1_DATAB2(can_base)) >> 8) & 0xFF;

    return ret;
}
```



# 四、 API描述

​		驱动提供的可操作的API如下：

```c
void hal_can_initial(int canid, uint32_t bandrate);
void hal_can_recvmask(int canid,uint8_t msgNum, uint32_t mask, uint32_t id, uint8_t len);
void hal_can_transmit(int canid, uint32_t id, uint8_t *txbuff, uint8_t len);
uint16_t hal_can_receive(int canid);
uint8_t hal_can_readmsg(int canid, uint32_t *id, uint8_t *rxbuff, uint8_t msgNum);
```



```c
/******************************************************************************
函数功能：对can设备进行初始化，并且初始化can设备的发送msg。
输入参数：
​		canid： 选择的can设备，0：can0(soc部分)  1：can1（soc部分）
​		bandrate：can波特率，最高测试到500kbps
输出参数：
​		void
******************************************************************************/
void hal_can_initial(int canid, uint32_t bandrate);
```



```c
/******************************************************************************
函数功能：给接收的msg设置mask，选择接收数据。
输入参数：
​		canid： 选择的can设备，0：can0(soc部分)  1：can1（soc部分）
​		msgNum： 接收的msg标号，其中17~32号msg用来接收
​		mask： can设备id掩码
​		id： can设备id
​		len：can设备的消息队列msg的长度，构成一个fifo
输出参数：
​		void
******************************************************************************/
void hal_can_recvmask(int canid,uint8_t msgNum, uint32_t mask, uint32_t id, uint8_t len);
```



```c
/******************************************************************************
函数功能：发送一帧can数据
输入参数：
​		canid： 选择的can设备，0：can0(soc部分)  1：can1（soc部分）
​		id： 发送的消息的id号
​		txbuff： 发送的消息数据指针
​		len： 发送的数据长度，不大于8
输出参数：
​		void
******************************************************************************/
void hal_can_transmit(int canid, uint32_t id, uint8_t *txbuff, uint8_t len);
```



```c
/******************************************************************************
函数功能：查询接收buff里是否存在未读取的数据包
输入参数：
​		canid： 选择的can设备，0：can0(soc部分)  1：can1（soc部分）
输出参数：
​		返回当前接收buff里未读取的数据包 
|——————————————————————————————————————————————————————————————————
| bit |  0  |  1  |  2 | ... 15  
| msg |  17 |  18 | 19 | ... 32
******************************************************************************/
uint16_t hal_can_receive(int canid);
```



```c
/******************************************************************************
函数功能：发送一帧can数据
输入参数：
​		canid： 选择的can设备，0：can0(soc部分)  1：can1（soc部分）
​		id： 接收的消息的id号指针
​		rxbuff： 接收的消息数据指针
​		msgNum： 接收的消息编号17~32
输出参数：
​		读取的数据长度
******************************************************************************/
uint8_t hal_can_readmsg(int canid, uint32_t *id, uint8_t *rxbuff, uint8_t msgNum);
```



# 五、 应用示例

**user_can.h**

```c
#ifndef __USER_CAN_H__
#define __USER_CAN_H__

#include "hal_can.h"

void user_can_initial(void);

#endif
```

​		

**user_can.c**

```c
#include "user_can.h"


uint8_t tx_buff[8],rx_buff[8];
void user_can_initial(void){
    uint16_t recv_flag,i,len;
    uint32_t recv_id;
    hal_can_initial(1,500000);

    while(1){
        LOS_Msleep(20);

        recv_flag = hal_can_receive(1);
        for(i = 0; i < 16;i ++){
            if(recv_flag & 0x01){
                len = hal_can_readmsg(1, &recv_id, rx_buff, i + 17);
                hal_can_transmit(1,recv_id, rx_buff, len);
            }
            recv_flag >>= 1;
        }
    }
}
```

![image-20210201151929006](/home/luocang/.config/Typora/typora-user-images/image-20210201151929006.png)

​		将上述代码拷贝到SDK目录下，其具体路径为：```osdrv/platform/liteos_a53/liteos/sample/sample_osdrv```，对程序进行编译，make之后便可以得到可执行文件，将该文件烧写到板卡上便可以执行，其测试步骤如上图所示：电脑连接一个USB转CAN的设备，使用上位机给HI3559A发送CAN数据帧，HI3559A接收到CAN数据帧后便可以反馈其数据包，形成闭环。



# 六、注意事项

* 使用CAN设备之前必须先配置IO复用功能。
* CAN0与uart0复用功能，需要谨慎使用。
* 官方的板卡上存在sleep引脚，需要配置该引脚。
* 官方的板卡上有拨码开关，需要配置对应的拨码开关选择GPIO功能。

<script src="../js/mermaid.min.js"></script>




