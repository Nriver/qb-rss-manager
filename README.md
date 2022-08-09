# qb-rss-manager

qBittorrent rss订阅 下载规则管理

<a href="https://count.getloli.com"><img align="center" src="https://count.getloli.com/get/@Nriver_qb-rss-manager"></a><br>


<!--ts-->

* [qb-rss-manager](#qb-rss-manager)
* [windows环境下的qb使用](#windows环境下的qb使用)
* [docker等环境下的qb使用](#docker等环境下的qb使用)
* [导入/导出规则](#导入导出规则)
* [config.json部分配置参数说明](#configjson部分配置参数说明)
* [qb-rss-manager 懒人包](#qb-rss-manager-懒人包)
    * [警告](#警告)
    * [懒人包使用方法](#懒人包使用方法)
    * [提示](#提示)
* [声明](#声明)
* [关于图标](#关于图标)
* [最后](#最后)

<!--te-->

# windows环境下的qb使用

1. 从release下载最新exe程序
2. 首次运行会生成config.json, 修改`qb_executable`和`rules_path`为你的qb主程序
3. 运行exe进行编辑

已有的订阅规则可以通过右键导入. 编辑好之后记得先保存再生成规则

# docker等环境下的qb使用

docker等环境下, 程序可以通过api远程管理qbittorrent

打开`QBRssManager.exe`, 保存设置, 桌面右下角托盘里把它完全关掉
编辑`config.json`
修改以下内容

```
"use_qb_api": 1,
"qb_api_ip": "192.168.1.111",
"qb_api_port": 8080,
"qb_api_username": "admin",
"qb_api_password": "adminadmin"
```

参数说明
`use_qb_api` 启用api通信
`qb_api_ip` qb的ip地址
`qb_api_port` qb的端口
`qb_api_username` qb的用户名
`qb_api_password` qb的密码

之后打开`QBRssManager.exe`右键即可导入已有规则
(图片看不清可以点击看大图)

![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/docs/rss_read.gif)

点击生成规则可以写入到qb里

![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/docs/rss_write.gif)

# 导入/导出规则

在表格里右键就有导入和导出功能了，快把你的订阅规则和朋友分享吧！

# config.json部分配置参数说明

很多配置里的 1表示开启 0表示关闭, 以下不重复说明

`close_to_tray` 点击关闭最小化到托盘. 默认开启
`data_auto_zfill` 播出时间列输入的日期自动格式化. 比如 2022.8 2022-8 2022/8 转换成2022年8月, 默认开启

# qb-rss-manager 懒人包

填好想要自动下载的文件信息，就能让qb自动下载想要的番剧，自动追番必备，用过都说好！

## 警告

本工具没有任何售后, 在使用过程中发生的一切后果由使用者自己承担. 对于程序bug, 使用者因操作不当或其它原因导致的数据丢失,
硬件损坏等问题概不负责.

## 懒人包使用方法

[Release页面](https://github.com/Nriver/qb-rss-manager/releases) 找到懒人包下载下来解压.

0. 运行all in one初始化工具 aio_init.exe
1. 启动 qbittorrent.exe, 设置rss源, 更新数据.
2. 运行qb管理器 QBRssManager.exe
3. 修改 '保存路径' 列的存储路径, 注意目录命名会影响自动重命名是否执行
4. 点击 '保存', 点击 '生成RSS订阅下载规则', 会自动生成qb的rss下载规则并启动qb. (注意qb启动后,
   匹配到rss订阅规则就会开始下载.)
5. 仿照示例写自己的规则, 重复3-4

初始化  
![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/aio/0.gif)

加载RSS数据  
![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/aio/1.gif)

管理RSS订阅  
![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/aio/2.gif)

等待自动重命名  
![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/aio/3.gif)

## 提示

0. 程序路径可以有中文但是不要有空格
1. 输入关键字过滤时下方会显示过滤结果
2. 修改完记得点保存或者备份
3. 下载完成后 Season XX 目录下的文件会自动重命名, 默认下载完成后15秒自动改名. 有可能删除文件或者覆盖文件, 自己看着办吧.
4. 需要添加新的rss源请先在qb内添加, 确认qb能加载rss数据, 之后用管理器管理订阅就行了
5. 不要修改程序的文件名
6. 程序在右下角托盘里

# 声明

qb管理程序来自 https://github.com/Nriver/qb-rss-manager

重命名工具来自 https://github.com/Nriver/Episode-ReName

qb增强版主程序来自 https://github.com/c0re100/qBittorrent-Enhanced-Edition/

其它数据来自各rss网站和本工具无关

如果觉得对你有点用, 请给以上项目star, 再推荐给你的朋友吧！

# 关于图标

程序使用的图标为 [icon-icons.com](https://icon-icons.com/icon/qbittorrent/93768) 的免费图标

# 最后

感谢不愿留姓名的某位朋友的大力支持, 对整合版的诞生功不可没.

