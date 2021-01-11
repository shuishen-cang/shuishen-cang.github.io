---

title: "Ubuntu_02qt开发环境搭建"
date: 2020-12-15T22:21:25+08:00
draft: false
tags: ["ubuntu"]
---

# 一、安装qt

​		考虑到后期在docker中安装交叉编译器，并且在docker镜像中编译qt，docker镜像暂不考虑带图形界面，因此需要在主机安装qtcreator，但是qtcreator必须支持命令编译，这样便可以在主机中设置编译docker镜像上的程序。

## 安装QT

下载一个稳定版本的qt软件，其格式为.run，直接运行该程序即可。安装的时候带源码安装，以便后期的交叉编译。



# 二、新建项目

​		新建一个qt控制台项目，一切采用默认配置，其项目名称为qtest。修改其main.cpp。

```c
#include <QCoreApplication>
#include <QDebug>

int main(int argc, char *argv[])
{
    QCoreApplication a(argc, argv);

    qDebug() << "hello!";

    return a.exec();
}
```

编译，运行，在控制台上打印了hello。



# 三、命令编译

​		先clean工程，查看qmake的目录，我的qmake路径为：```/home/installed/Qt5.9.9/5.9.9/gcc_64/bin/qmake```

​		控制台进入qtest工程下面。

```bash
cd ~/Desktop/qtest/
/home/installed/Qt5.9.9/5.9.9/gcc_64/bin/qmake "OBJECTS_DIR=build" qtest.pro
make
ls
./qtest
```

​		程序已经能够正常运行，说明具备基本的docker镜像下开发条件。





