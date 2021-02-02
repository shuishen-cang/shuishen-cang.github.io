---
title: "shuixia04-liteos-pwm"
date: 2021-02-01T16:06:09+08:00
draft: false
tags: ["shuixia"]

---



<div align = "center" style="font-size:48px">PWM设备驱动测试使用说明-liteos</div>

[TOC]

# 一、概述

​		脉冲宽度调制是一种模拟控制方式，根据相应载荷的变化来调制晶体管，来实现晶体管或MOS导通时间的改变，从而实现开关稳压电源输出的改变。这种方式能使电源的输出电压在工作条件变化时保持恒定，是利用微处理器的数字信号对模拟电路进行控制的一种非常有效的技术。PWM调制是利用数字输出来对模拟电路进行控制的一种非常有效的技术，广泛应用在从测量、通信到功率控制与变换的许多领域中。

​		HI3559A芯片的CPU子系统分为两部分，一个是以为A73+A53为主的SOC部分，另一个是为M7为主的Sensor Hub部分，其中SOC子系统与Sensor Hub子系统的外设均采用统一的外设接口，即寄存器组完全一样，并且可以通过地址转换实现跨子系统访问，但是SOC子系统与Sensor Hub子系统的中断系统完全肚子，并不能完全共享中断向量。

​		主 SOC 子系统提供 1 组 2 路独立的脉宽调制信号输出。
​		Sensor Hub 子系统提供 1 组 8 路独立的脉宽调制信号输出



# 二、 参考文件

GPIO复用功能描述文件《Hi3559A V100_PINOUT_EN.xlsx》

驱动操作使用指南《外围设备驱动 操作指南.pdf》

寄存器相关操作《Hi3559A╱C V100 ultra-HD Mobile Camera SoC 用户指南.pdf》



# 三、 驱动编译

​		海思官方没有提供PWM相关的驱动，因此需要自行操作寄存器进行PWM驱动编写，其编写流程如下：

<div class="mermaid">
graph TD
A(使能PWM时钟)-->B(配置GPIO复用功能)-->C(配置周期占空比)-->D(使能输出)
</div>

​		具体操作如下：

​		在hal_gpioaf.h中添加如下代码：

```c
......
#define AF_PWM_VAL              0x01
#define AF_PWM0_OUT             IOREG(73)
#define AF_PWM1_OUT             IOREG(74)
......
#define AF_PWM0_Config(){                   \
    writeor(AF_PWM0_OUT, AF_PWM_VAL);       \
}

#define AF_PWM1_Config(){                   \
    writeor(AF_PWM1_OUT, AF_PWM_VAL);       \
}    
```

​		新建hal_pwm.h

**hal_pwm.h**

```c
#ifndef __HAL_PWM_H__
#define __HAL_PWM_H__

#include "hal.h"

#define PWM0_BASE       0x12130000    
#define PWM1_BASE       0x12130020 
#define PERI_CRG101     0x12010194
#define EN_PWM          (1 << 19)
#define PWM_3M          (0 << 20)
#define PWM_24M         (2 << 20)
#define PWM_50M         (1 << 20)

#define PWM0_CFG0(n)    (n == 0 ? (PWM0_BASE + 0) : (PWM1_BASE + 0))
#define PWM0_CFG1(n)    (n == 0 ? (PWM0_BASE + 4) : (PWM1_BASE + 4))
#define PWM0_CFG2(n)    (n == 0 ? (PWM0_BASE + 8) : (PWM1_BASE + 8))
#define PWM0_CTRL(n)    (n == 0 ? (PWM0_BASE + 12) : (PWM1_BASE + 12))
#define PWM0_STATE0(n)  (n == 0 ? (PWM0_BASE + 16) : (PWM1_BASE + 16))
#define PWM0_STATE1(n)  (n == 0 ? (PWM0_BASE + 20) : (PWM1_BASE + 20))
#define PWM0_STATE2(n)  (n == 0 ? (PWM0_BASE + 24) : (PWM1_BASE + 24))

void hal_pwm_initial(void);
void hal_pwm_setoutput(uint8_t ch, float duty, float freq);

#endif
```

**hal_pwm.c**

```c
#include "hal_pwm.h"

#define PWM_FREQ    50000000

static void hal_pwm_set_clk(uint32_t clk){
    if(clk == 3000000){
        writeor(PERI_CRG101, PWM_3M);
    }
    else if(clk == 50000000){
        writeor(PERI_CRG101, PWM_50M);
    }
    else{
        writeor(PERI_CRG101, PWM_24M);   
    }
    writeor(PERI_CRG101, EN_PWM);
}

void hal_pwm_initial(void){
    hal_pwm_set_clk(PWM_FREQ);

    AF_PWM0_Config();
    AF_PWM1_Config();
}

void hal_pwm_setoutput(uint8_t ch, float duty, float freq){
    float period;
    
    period = (float)PWM_FREQ / freq;
    writel(PWM0_CFG0(ch), period);
    writel(PWM0_CFG1(ch), period * duty);
    writel(PWM0_CTRL(ch), 0x51);
}
```



# 四、 API描述

​		驱动提供的可操作的API如下：

```c
void hal_pwm_initial(void);
void hal_pwm_setoutput(uint8_t ch, float duty, float freq);
```



```c
/******************************************************************************
函数功能：对PWM设备进行初始化
输入参数：
​		void
输出参数：
​		void
******************************************************************************/
void hal_pwm_initial(void);
```



```c
/******************************************************************************
函数功能：设置PWM的占空比，频率，并且输出PWM。
输入参数：
​		ch： PWM通道，0或者1
​		duty： PWM占空比，0~1
​		freq： PWM频率
输出参数：
​		void
******************************************************************************/
void hal_pwm_setoutput(uint8_t ch, float duty, float freq);
```



# 五、 应用示例

**user_pwm.h**

```c
#ifndef __USER_PWM_H__
#define __USER_PWM_H__

#include "user.h"

void user_pwm_initial(void);

#endif
```

​		

**user_pwm.c**

```c
#include "user_pwm.h"

void user_pwm_initial(void){
    hal_pwm_initial();

    hal_pwm_setoutput(0, 0.5, 100000);  //pwm0输出频率100k，占空比50%的波形
    hal_pwm_setoutput(1, 0.75, 50000);  //pwm1输出频率50k，占空比75%的波形
}
```

![image-20210202155813358](../images/image-20210202155813358.png)

​		将上述代码拷贝到SDK目录下，其具体路径为：```osdrv/platform/liteos_a53/liteos/sample/sample_osdrv```，对程序进行编译，make之后便可以得到可执行文件，将该文件烧写到板卡上便可以执行，其测试步骤如上图所示：电脑通过网线连接HI3559A板卡，实现程序的烧写与调试，示波器通过探头连接到HI3559A的GPIO上，通过程序设置GPIO的输出电平，在示波器上观察IO波形的变化。



# 六、注意事项

* 使用PWM设备之前必须先配置IO复用功能。
* 使用PWM设备之前必须先配置时钟。
* 注意工程路径







<script src="../js/mermaid.min.js"></script>