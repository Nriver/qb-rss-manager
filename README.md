# qb-rss-manager

qBittorrent rss订阅 下载规则管理

[![Github all releases](https://img.shields.io/github/downloads/Nriver/qb-rss-manager/total.svg)](https://GitHub.com/Nriver/qb-rss-manager/releases/)
[![GitHub license](https://badgen.net/github/license/Nriver/qb-rss-manager)](https://github.com/Nriver/qb-rss-manager/blob/master/LICENSE)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://GitHub.com/Nriver/qb-rss-manager/graphs/commit-activity)
[![GitHub release](https://img.shields.io/github/v/release/Nriver/qb-rss-manager.svg)](https://github.com/Nriver/qb-rss-manager/releases/)

<a href="https://count.getloli.com"><img align="center" src="https://count.getloli.com/get/@Nriver_qb-rss-manager"></a><br>

<!--ts-->

* [qb-rss-manager](#qb-rss-manager)
* [qb-rss-manager 懒人包](#qb-rss-manager-懒人包)
    * [警告](#警告)
    * [懒人包使用方法](#懒人包使用方法)
    * [提示](#提示)
    * [懒人使用建议](#懒人使用建议)
* [qb订阅管理器 初始化配置](#qb订阅管理器-初始化配置)
    * [Windows/Linux桌面环境下的qb使用](#windowslinux桌面环境下的qb使用)
    * [通过api连接docker等环境下的qb使用](#通过api连接docker等环境下的qb使用)
* [导入/导出规则进行分享](#导入导出规则进行分享)
* [config.json部分配置参数说明](#configjson部分配置参数说明)
    * [自动填充](#自动填充)
        * [触发机制](#触发机制)
        * [默认关键字模板配置](#默认关键字模板配置)
        * [限制解析的 series_name 长度](#限制解析的-series_name-长度)
        * [默认订阅地址配置](#默认订阅地址配置)
* [快捷操作/快捷键说明](#快捷操作快捷键说明)
* [声明](#声明)
* [关于图标](#关于图标)
* [Stargazers 数据](#stargazers-数据)
* [捐赠](#捐赠)
* [感谢](#感谢)

<!--te-->

# qb-rss-manager 懒人包

填好想要自动下载的文件信息，就能让qb自动下载想要的番剧，自动追番必备，用过都说好！懒人包包含qb订阅管理工具, 自动重命名工具,
qb增强版, 都已经配置完毕, 可以开箱即用.

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

## 懒人使用建议

1. 先填写订阅地址. 如果是qb里没有订阅的地址, 先生成一次订阅规则, 就可以把订阅地址加入到qb里.
2. 填写保存路径, 使用类似 `Z:\Anime\各位打个赏吧我好饿呜呜呜呜呜\Season 1` 的格式, 程序可以自动解析相关内容.
3. 在使用api与qb通信的状态下, 编辑关键字可以实时过滤出匹配到的结果.

# qb订阅管理器 初始化配置

## Windows/Linux桌面环境下的qb使用

1. 从release下载最新对应平台的可执行文件
2. 首次运行会生成config.json, 请修改`qb_executable`和`rules_path`为你的qb主程序路径, 如果安装在默认路径可以不修改.
3. 运行程序进行编辑

已有的订阅规则可以通过右键导入. 编辑好之后记得先保存再生成规则

## 通过api连接docker等环境下的qb使用

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
`qb_api_ip` qb的ip地址,若填写域名，请附上“http://”
`qb_api_port` qb的端口
`qb_api_username` qb的用户名
`qb_api_password` qb的密码

之后打开`QBRssManager.exe`右键即可导入已有规则
(图片看不清可以点击看大图)

![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/docs/rss_read.gif)

点击生成规则可以写入到qb里

![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/docs/rss_write.gif)

# 导入/导出规则进行分享

在表格里右键就有导入和导出功能了，快把你的订阅规则和朋友分享吧！

![](https://raw.githubusercontent.com/Nriver/qb-rss-manager/main/docs/popup_menu.png)

# config.json部分配置参数说明

很多配置里的 1表示开启 0表示关闭, 以下不重复说明

`close_to_tray` 点击关闭最小化到托盘. 默认开启
`data_auto_zfill` 添加时间列输入的日期自动格式化. 比如 2022.8 2022-8 2022/8 转换成2022年08月, 默认开启

## 自动填充

### 触发机制

填写`关键字`时会触发自动填充机制, 程序会依据配置尝试自动填充订阅地址. 如果没有配置订阅地址的默认值, 则会自动复制表格上方最近的订阅地址.

填写`保存路径`时会触发自动填充机制, 程序会解析保存路径, 尽量解析出所有的数据.
推荐的保存路径格式为 `Z:\Anime\XXXXX\Season 1`. 程序可以解析出的数据 `XXXXX` 对应模板变量 `{series_name}`. 特殊格式 `Z:\Anime\XXXXX (2023)\Season 1`, 会忽略掉后面的年份.

### 默认关键字模板配置

全局配置中的 `keyword_default` 可以配置默认的订阅地址, 默认为 `{series_name}`,
参考配置值举例 `A组 {series_name} | B组 {series_name}`. 该配置可以被分组数据中的 `keyword_override` 配置给覆盖,
实现每个分组使用不同的自动填充模板来自动填写关键字.

### 限制解析的 series_name 长度

全局配置中 `keyword_trim_length` 可以限制解析到的 `{series_name}` 长度.
比如路径为 `Z:\Anime\各位打个赏吧我好饿呜呜呜呜呜 (2023)\Season 1` 的 `{series_name}`,
默认会被解析为 `各位打个赏吧我好饿呜呜呜呜呜`. 如果将 `keyword_trim_length` 设置为6, 会被解析为 `各位打个赏吧`.
对于名字超长的番剧可以通过设置这个值来限制关键字的长度, 因为一般只要前面几个字就足够过滤了.

### 默认订阅地址配置

全局配置中的 `rss_default` 可以配置默认的订阅地址. 多个订阅地址可以用 `空格`, ',' `|` 符号隔开.
该配置可以被分组数据中的 `rss_override` 配置给覆盖, 实现每个分组自动填充不同的.

# 快捷操作/快捷键说明

- 选中单元格后按 `回车键`, `F2`, `双击` 都能进入编辑模式.
- 在分组上`双击`可以修改分组名称, 修改名称后按 `回车键` 确认修改.
- `Ctrl+s` 保存.
- 用鼠标选中多个单元格, 按下 `Ctrl+c` 可以复制单元格数据, 复制的内容可以粘贴到其它单元格或其它标签里. 另注,
  复制的数据是标准的excel格式, 可以粘贴在excel软件里
- `Ctrl+v` 可以粘贴文本/单元格数据. 另注, 可以从excel里复制过来.
- `Ctrl+f` 可以打开查找/搜索框, 主界面下方文本框会显示共有多少个结果以及当前是第几个结果. 搜索状态下按 `F3` 可以跳到下一个结果.
  按`ESC`键退出搜索.
- `Ctrl+h` 可以打开替换/批量替换框. 基本操作和查找类似.
- `Delete` 可以删除数据, 用鼠标选中多个单元格可以删除多个数据
- `方向键` 上下左右可以切换选中的单元格
- `Alt+1`, `Alt+2` 等 `Alt+数字` 操作可以切换分组

# 声明

qb管理程序来自 https://github.com/Nriver/qb-rss-manager

重命名工具来自 https://github.com/Nriver/Episode-ReName

qb增强版主程序来自 https://github.com/c0re100/qBittorrent-Enhanced-Edition/

其它数据来自各rss网站和本工具无关

如果觉得对你有点用, 请给以上项目star, 再推荐给你的朋友吧！

# 关于图标

程序使用的图标为 [icon-icons.com](https://icon-icons.com/icon/qbittorrent/93768) 的免费图标


---

# Stargazers 数据

统计图使用 [caarlos0/starcharts](https://github.com/caarlos0/starcharts) 项目生成.

[![Stargazers over time](https://starchart.cc/Nriver/qb-rss-manager.svg)](https://starchart.cc/Nriver/qb-rss-manager)

---

# 捐赠

如果你觉得我做的程序对你有帮助, 欢迎捐赠, 这对我来说是莫大的鼓励!

支付宝:  
![Alipay](docs/alipay.png)

微信:  
![Wechat Pay](docs/wechat_pay.png)

---

# 感谢

感谢不愿留姓名的某位朋友的大力支持, 对本工具以及懒人包的诞生功不可没.

感谢 `J*s` 赞助的50元!

感谢 `**莲` 赞助的10元!

感谢 `**楷` 赞助的5元!

感谢Jetbrins公司提供的Pycharm编辑器!

[![Jetbrains](docs/jetbrains.svg)](https://jb.gg/OpenSource)

