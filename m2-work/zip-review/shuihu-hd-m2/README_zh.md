# 水浒神兽 · Milestone 2

在现有本地版本上完成的显示层重制。ROM、vendored Binjgb 核心、游戏逻辑和输入时序保持原样；全部资源由本地服务器加载，无需 npm 构建。

## 启动与操作

运行 `./start.sh`，浏览器打开 http://127.0.0.1:8765 。不要直接打开 HTML。默认暂停，点击「开始 / 继续」运行。方向键移动，X=A、Z=B、Enter=START、Shift=SELECT、空格暂停；也支持页面触控按键。声音需主动开启。切换高清只改变显示。

电池 RAM 自动保存到当前来源的 localStorage，支持原始 `.sav` 导入/导出。游戏内仍需使用原作存档功能。测试验证了 RAM 持久化和导入导出字节一致；尚未验证完整的游戏内保存、重启、继续流程。不同主机名/端口属于不同存储来源。

## 已完成范围

- 标题使用已有、获批的全屏 V4 图；菜单面板从内在 y324 开始，覆盖烘焙红字。实时读取原作真实游标状态，键盘选择会同步显示；未重画角色。
- 初始森林、悬崖、宫殿及**开场室内**接入已有 `gpt-image-2` 图。文件名 `town` 是历史素材名，不表示去过城镇。宫殿生成响应质量为 low。
- 森林和室内按完整 256×256 参考几何使用。悬崖和宫殿的整张生成图缩放到 640×576，放在 1024×1024 世界纹理左上角，避免错误拉伸为整幅世界地图。
- 森林七个已审阅动画格按原坐标、tile15/attr4 验证。连续 180 个真实模拟帧又确认了其他动画变体，保存于 `assets/maps/forest_animation.json`，只允许对应坐标、tile、attribute 及实际采样 RGB hash 的组合。开场室内的 0/24 低色值差异仅在结构与规范化 RGB hash 同时匹配时接受。
- 只读观察器采用当前随包核心已独立验证的 VRAM/原始 OAM 布局；校验相对指针、内存边界，并在总线可读时比对。总线被 PPU 阻塞时仍能读取演员位置。非透明、可见原作精灵像素逐像素保留，没有用背景差分挖洞；窗口保留原作。

**覆盖限制：**森林素材只验证初始已加载视口。移动后新流入的行仍保留原始背景，匹配不足时整屏使用 Scale2x；不能声称完整森林探索覆盖。悬崖与宫殿仅验证固定视口。未知场景安全回退，WebGL 不可用时最近邻。生成美术存在解释差异，不承诺与原建筑轮廓逐像素一致，也没有全游戏或通关验证。

## 校验与测试

ROM `assets/game.gbc` SHA256（启动时强制检查）：

`ab42ec7ab339125dc685f4aa56eedfafaa2a8ecf46a4659e3c0f05eedd57ff95`

核心未修改，来源与许可证见 `vendor/README.txt`；本次打包的核心哈希及素材处理说明见 `assets/maps/provenance.json`。所有显示操作不回写核心，不为高清额外推进帧。`window.shuihu` 提供暂停、确定步进、同页完整 heap checkpoint、普通 state、原始 pixels 与只读 background；普通 state 恢复后需推进数帧恢复 framebuffer。

本次重新执行 Playwright：真实键盘标题选择、滚动到可见位置后的真实 CDP 触摸、电池 RAM 持久化/导入导出、同输入下原版与高清模拟状态字节一致、暂停/音频初始化、本地资源和错误检查。场景测试覆盖两种标题选项、四个场景、森林移动及多个动画时刻；演员输出像素必须与原作一致，已验证森林动画帧 unsupportedPixels=0。每个场景重新加载页面，验证冷启动观察器。实际结果与截图在包内 `screenshots/`，并非复用旧报告。

测试环境需要外部安装的 Playwright。当前工作区命令：

```bash
NODE_PATH=/home/box/opt/test-tools/node_modules PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers node tools/test_m2.cjs
NODE_PATH=/home/box/opt/test-tools/node_modules PLAYWRIGHT_BROWSERS_PATH=/home/box/opt/playwright-browsers node tools/test_reviewed.cjs
```

开发测试使用工作区已有的场景状态文件；发行包用于运行静态应用，未附开发工作/缓存目录。仅限本地私用，未发布或部署。
