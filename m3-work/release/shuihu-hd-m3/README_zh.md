# 水浒神兽高清场景版 M3（本地Windows包）

1. 右键压缩包 → 全部解压缩。
2. 如未安装Python3：从https://www.python.org/downloads/安装，勾选Add Python to PATH。
3. 在解压出的shuihu-hd-m3文件夹双击start.bat。别关闭黑色服务窗口。
4. 浏览器打开http://127.0.0.1:8765。如页面打开过早，等几秒刷新。请勿直接双击index.html。

本地离线运行，无需npm或联网。Mac/Linux：bash start.sh，然后打开上述地址。

方向键移动，X=A，Z=B，Enter=START，Shift=SELECT，空格暂停；也有触控按钮。点击开始/继续。高清/原版切换只影响显示。声音需要手动开启。

本版为开场场景重制，非全游戏100%高清。实测29160帧中26404帧背景全高清（90.55%）；背景像素覆盖99.32%。标题淡出、部分对话展开/扫描线切换、BG红色冲击和少量震动边缘仍有原版像素，详见reports/REPORT_zh.md。人物、头像、中文字保留原作，没有平滑放大兜底。

存档保存在此浏览器+主机名+端口的localStorage。请在原作游戏内存档，并导出电池存档备份；完整游戏内存档后重开继续未完整通关验证。

screenshots/m3_cutscenes_contact.png为最终实机总览；reports含逐帧统计、缺口和一致性测试。离线包在Linux无外网Chromium验证通过，但不是实际Windows运行测试。ROM和模拟器核心未修改。仅限本地私用。
