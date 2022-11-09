<div align="center">
  <a href="https://v2.nonebot.dev/store"><img src="https://raw.githubusercontent.com/tkgs0/nbpt/resources/nbp_logo.png" width="180" height="180" alt="NoneBotPluginLogo"></a>
  <br>
  <p><img src="https://raw.githubusercontent.com/tkgs0/nbpt/resources/NoneBotPlugin.svg" width="240" alt="NoneBotPluginText"></p>
</div>

<div align="center">

# nonebot-plugin-blacklist

_✨ NoneBot 黑名单插件 ✨_


<a href="./LICENSE">
    <img src="https://img.shields.io/github/license/tkgs0/nonebot-plugin-blacklist.svg" alt="license">
</a>
<a href="https://pypi.python.org/pypi/nonebot-plugin-blacklist">
    <img src="https://img.shields.io/pypi/v/nonebot-plugin-blacklist.svg" alt="pypi">
</a>
<a href="https://www.python.org">
    <img src="https://img.shields.io/badge/python-3.8+-blue.svg" alt="python">
</a>

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
  
**使用 pip 安装**  
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
拉黑用户 qq qq1 qq2
拉黑群 qq qq1 qq2
拉黑所有群
拉黑所有好友
```
  
解禁:  
```
解禁用户 qq qq1 qq2
解禁群 qq qq1 qq2
解禁所有群
解禁所有好友
```
  
查看黑名单:  
```
查看用户黑名单
查看群聊黑名单

重置黑名单
```
  
群内发送 **`/静默`**, **`/响应`** 可快捷拉黑/解禁当前群聊  
`拉黑/解禁所有` 只对已添加的群/好友生效  
  
