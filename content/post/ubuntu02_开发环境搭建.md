---

title: "ubuntu02-开发环境搭建"
date: 2020-12-15T22:21:25+08:00
draft: false
tags: ["ubuntu"]
---

<div align="center" style= 'font-size: 48px;'>
    ubuntu开发环境搭建-安装软件
</div>







# 一、安装typora

```bash
wget -qO - https://typora.io/linux/public-key.asc | sudo apt-key add -
sudo add-apt-repository 'deb https://typora.io/linux ./'
sudo apt-get update
sudo apt-get install typora
```



# 二、安装vscode

​		先在官网下载vscode的安装包，然后使用下面命令安装。

```bash
sudo dpkg -i xxx.deb
```



# 三、安装sublime

```bash
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add -
sudo apt-add-repository "deb https://download.sublimetext.com/ apt/stable/"
sudo apt update
sudo apt install sublime-text
```



# 四、安装其他

```bash
sudo apt install python3-pip

# fsearch
sudo add-apt-repository ppa:christian-boxdoerfer/fsearch-daily
sudo apt update
sudo apt install fsearch-trunk



```



​		






<script src="../js/mermaid.min.js"></script>