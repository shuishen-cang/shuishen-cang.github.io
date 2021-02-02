---
title: "shuixia01-liteos-makefile"
date: 2021-02-01T16:06:09+08:00
draft: false
tags: ["shuixia"]

---



<div align = "center" style="font-size:48px">Makefile修改使用说明-liteos</div>

[TOC]

# 一、概述

​		Makefile是一种控制自动编译的工具，Makefile关系到整个工程的编译规则。它告诉系统哪些文件先编译，哪些文件后编译，哪些文件在什么时候清理掉等等。因为是用来告知系统如何进行操作的，所以Makefile的语言风格跟shell很像，Makefile中也可以执行操作系统的命令。

​		海思官方提供了liteos以及linux下面的makefile，用来编译程序，得到相应的库文件以及可执行文件，其中liteos部分提供了一个可用的makefile，顶层makefile通过调用底层makefile得到相应的编译结果，但是在sample中的makefile存在一些缺陷，其具体表现是只能编译单个文件，并不支持多文件的编译，但是在编写驱动以及应用程序的时候，往往需要多文件的编译以及多文件的支持，因此需要对makefile做一些修改，以下就makefile做一些讲解。

# 二、 参考文件



# 三、 驱动编译

​		

# 四、 API描述

​	

# 五、 应用示例

## 1.官方makefile

```makefile
LITEOSTOPDIR ?= ../..

SAMPLE_OUT = .

include $(LITEOSTOPDIR)/config.mk
RM = -rm -rf

LITEOS_LIBDEPS := --start-group $(LITEOS_LIBDEP) --end-group

SRCS = $(wildcard sample.c)

OBJS = $(patsubst %.c,$(SAMPLE_OUT)/%.o,$(SRCS))

all: $(OBJS)

clean:
	@$(RM) *.o  sample *.bin *.map *.asm

$(OBJS): $(SAMPLE_OUT)/%.o : %.c
ifneq ($(LITEOS_CPU_TYPE), arm926)

ifneq ($(OUT)/lib/libipcm.a, $(wildcard $(OUT)/lib/libipcm.a))
	echo "$(OUT)"
	cp -rf $(LITEOS_CPU_TYPE)/*.a $(OUT)/lib
endif
endif
	$(CC) $(LITEOS_CFLAGS) $(LITEOS_CXXFLAGS) -c $< -o $@
	$(LD) $(LITEOS_LDFLAGS) --gc-sections -Map=$(SAMPLE_OUT)/sample.map -o $(SAMPLE_OUT)/sample ./$@ $(LITEOS_LIBDEPS) $(LITEOS_TABLES_LDFLAGS)
	$(OBJCOPY) -O binary $(SAMPLE_OUT)/sample $(SAMPLE_OUT)/sample.bin
	$(OBJDUMP) -d $(SAMPLE_OUT)/sample >$(SAMPLE_OUT)/sample.asm

```

​		如上述代码所示：整个编译从make all开始(在all之前没有指定其他，因此make默认为make all)，make all会调用```$(OBJS)```，而```$(OBJS)```下面的代码是：

```makefile
$(OBJS): $(SAMPLE_OUT)/%.o : %.c
ifneq ($(LITEOS_CPU_TYPE), arm926)

ifneq ($(OUT)/lib/libipcm.a, $(wildcard $(OUT)/lib/libipcm.a))
	echo "$(OUT)"
	cp -rf $(LITEOS_CPU_TYPE)/*.a $(OUT)/lib
endif
endif
	$(CC) $(LITEOS_CFLAGS) $(LITEOS_CXXFLAGS) -c $< -o $@
	$(LD) $(LITEOS_LDFLAGS) --gc-sections -Map=$(SAMPLE_OUT)/sample.map -o $(SAMPLE_OUT)/sample ./$@ $(LITEOS_LIBDEPS) $(LITEOS_TABLES_LDFLAGS)
	$(OBJCOPY) -O binary $(SAMPLE_OUT)/sample $(SAMPLE_OUT)/sample.bin
	$(OBJDUMP) -d $(SAMPLE_OUT)/sample >$(SAMPLE_OUT)/sample.asm
```

​		在该种方式下，当```$(OBJS)```只存在一个.c文件时，并不影响程序的编译，但是在多个c文件的系统中，该部分makefile会重复调用编译，最后得不到可用的可执行文件，会使得编译后的结果无法在A53上正确执行，因此必须修改```$(OBJS)```下的编译规则以支持多文件的编译。

## 2.修改makefile

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

​		如上述代码，将编译过程与连接过程分离开来，在链接过程中只执行链接过程，在编译过程中执行编译过程，这样便能使得编译与链接完全分离，并且在makefile中提供了make test；make debug；make flash等操作，以便于程序的测试，调试以及烧写等。



# 六、注意事项

* liteos的程序静态库链接位置均采用相对位置，因此不能随意修改sdk中程序的位置，否则会提示缺少库文件等。
* 使用make debug；make flash等操作必须先配置好tftp服务器以及设置好对应的脚本文件
