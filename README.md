
# nonebot-plugin-blacklist

*NoneBot 黑名单插件*


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tkgs0/nonebot-plugin-blacklist.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-blacklist">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-blacklist.svg" alt="pypi">
</a>
<img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">

</div>

  
## 📖 介绍
  
基于 [A-kirami](https://github.com/A-kirami) 大佬的 [黑白名单](https://github.com/A-kirami/nonebot-plugin-namelist) 插件 魔改(?)的仅黑名单插件  
  
超级用户不受黑名单影响  
  
## 💿 安装
  
**使用 nb-cli 安装**  
在 nonebot2 项目的根目录下打开命令行, 输入以下指令即可安装  
```bash
nb plugin install nonebot-plugin-blacklist
```
  
**使用pip安装**  
```bash
pip install nonebot-plugin-blacklist
```
  
打开 nonebot2 项目的 `bot.py` 文件, 在其中写入
```python
nonebot.load_plugin('nonebot_plugin_blacklist')
```
  
## 🎉 使用
  
拉黑:
```
拉黑/屏蔽用户 qq qq1 qq2
拉黑/屏蔽群 qq qq1 qq2
```
  
解禁:
```
解禁/解封用户 qq qq1 qq2
解禁/解封群 qq qq1 qq2
```
  
查看黑名单:
```
查看用户黑名单
查看群聊黑名单
```
  
群内发送 **`/静默`**, **`/响应`** 可快捷拉黑/解禁当前群聊  
  
  

