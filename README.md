# MonsterDeleterMac

[`531149627/MonsterDeleter`](https://github.com/531149627/MonsterDeleter) 的 macOS 移植版：从 Finder 选择文件后，用红色准星指定文件在屏幕上的位置，播放原版“大将怪兽”逐帧动画和音效，确认后把文件安全移入废纸篓。

本项目直接使用上游提交 `f2c43fd3c7efc6bb309d52d4f3884197fcaeaf40` 的原始角色、爆炸、选择界面和音频资源，并按原版顺序移植动画。素材使用授权由用户确认；来源、提交和完整性信息记录在 [THIRD_PARTY_ASSETS.md](THIRD_PARTY_ASSETS.md)。

## 原版动画流程

1. 原版选择界面淡入，鼠标变成红色狙击准星。
2. 点击文件所在位置后，大将怪兽以 8 FPS 从屏幕左侧行走 4.5 秒。
3. 播放原版指向帧 11–14 和怪兽语音，显示“喂，是这个吗？”。
4. 确认后播放原版踹击；第 6 帧同步播放爆炸、音效并移入废纸篓。
5. 播放原版“雷欧登场”和飞离动画，2 秒后退出。

## 安全设计

- 文件只会通过 `send2trash` 移入 macOS 废纸篓，不调用 `rm`。
- 真正移动前会再次校验目标。
- 只接受单个普通文件；拒绝目录、符号链接和关键系统路径。
- 必须在怪兽气泡处再次明确确认。
- `Esc`、`Ctrl+C`、演示模式和 dry-run 都不会移动文件。

## 环境要求

- macOS 13 或更高版本（已在 macOS 15.4.1 验证）。
- [`uv`](https://docs.astral.sh/uv/)；本机已经安装。

## 安装依赖

```bash
cd ~/Desktop/MonsterDeleterMac
uv sync --dev
```

## 运行原版安全演示

```bash
uv run monster-deleter-mac --demo
```

演示步骤：在原版选择画面中用红色准星点击一个位置，等待怪兽走到目标旁，再点击任意一个原版确认按钮。完整动画和音效都会播放，但不会处理任何文件。

程序会等待你的点击，不是启动卡住。按 `Esc`，或回到终端按 `Ctrl+C`，可以随时退出。

指定真实文件但保持 dry-run：

```bash
uv run monster-deleter-mac --dry-run ~/Desktop/example.txt
```

## 安装 Finder 快速操作

```bash
uv run python scripts/install_quick_action.py
```

安装后，在 Finder 或桌面中右键一个文件：

1. 选择“快速操作”。
2. 点击“召唤大将军（Mac）”。
3. 在原版选择界面中用准星点击该文件的位置。
4. 等待怪兽指向文件后再次确认。

如果菜单没有立即出现，请前往“系统设置 → 隐私与安全性 → 扩展 → Finder”启用快速操作。

卸载：

```bash
uv run python scripts/install_quick_action.py --uninstall
```

## 直接处理文件

```bash
uv run monster-deleter-mac ~/Desktop/example.txt
```

不提供路径且不是演示模式时会打开文件选择器：

```bash
uv run monster-deleter-mac
```

## 测试

```bash
uv run pytest
```

测试覆盖目标安全、废纸篓后端、Finder Quick Action、原版素材哈希、动画时序、Qt offscreen 启动和终端中断，不会删除真实文件。

## 后续

- 使用 PyInstaller 打包成签名 `.app`。
- 将 Automator 快速操作升级为原生 Finder Sync Extension。
