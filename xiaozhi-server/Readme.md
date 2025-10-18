# 3DOF-Robotic-Arm-xiaozhi-server

（开发中）基于[小智 AI](https://github.com/xinnan-tech/xiaozhi-esp32-server)的 RRR 构型三自由度机械臂的语音控制服务端

## Environment

 - Python version: Python 3.10

需要自行下载 `opus` 库，Windows 平台可能需要自行编译构建

然后添加环境变量到 Python 环境

```bash
export DYLD_LIBRARY_PATH="$(brew --prefix opus)/lib:$DYLD_LIBRARY_PATH"
```
## Quick Start
在 Web 端测试：

```bash
cd test
python -m http.server 8006
```

然后访问 `http://localhost:8006/test_page.html` 就好

目前通讯 Demo 基于本地虚拟串口，安装 `socat` 之后运行下面的命令启动虚拟串口

```bash
socat -d -d PTY,link=/tmp/ttyV0,raw,echo=0 PTY,link=/tmp/ttyV1,raw,echo=0
```