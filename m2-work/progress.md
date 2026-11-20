# M2 本地进度

标题硬切代码已移除：批准的 V4 图覆盖整个 160×144 显示区，菜单独立覆盖；选择依据原版 RGB 箭头的两个实际位置，不写模拟器状态。正在验证两种光标截图和下方景物断言。森林目前仍是旧 94 tile atlas，尚未解决拼缝及精灵周围整块回退，不能视为 M2 已完成。

Reviewed fixes: title panel y324; forest animation structural metadata and seven scoped cells; guarded pinned read-only VRAM/OAM; existing four scene assets integrated with cliff/palace viewport sizing. Verification in progress.

Final: fresh Playwright general suite passed 16 tests; reviewed scene suite passed title/continue, forest animation five sampled times (zero unsupported BG and actor mismatch), cliff/palace/opening interior exact actor pixels; ROM and vendor hashes unchanged. Real screenshots visually inspected. Forest streamed rows limited fallback documented. README_zh and executable loopback start.sh updated. ZIP whitelist validated (integrity, executable flag, no secrets/cache/work dirs). No image generation or external publication.
