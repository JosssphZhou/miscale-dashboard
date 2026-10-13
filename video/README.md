# 上游宣传视频工程

这里保留上游约 41 秒的宣传视频源码。既有视频与录屏素材使用英语，属于上游展示素材；中文网页与连接流程请阅读根目录 [README](../README.md)。本次汉化不重新制作或发布宣传视频。

## 渲染视频

需要 Node.js 20 或更新版本。Remotion 提供所需的 ffmpeg。

```bash
cd video
npm ci
npm run render
```

命令先生成配乐，再输出两个视频：

- `out/miscale-dashboard.mp4`：1920×1080，30 帧/秒，H.264 + AAC。
- `out/miscale-dashboard-vertical.mp4`：1080×1920，用于竖屏平台。

场景通过 ANGLE 渲染 WebGL，配置位于 `remotion.config.ts`。`npm run docs` 更新根目录文档使用的预览图 `docs/video/poster.jpg`。

```bash
npm run studio
node scripts/stills.mjs --scale 0.5 96 204 600
node scripts/stills.mjs --vertical 1100
```

第一条命令打开预览，后两条在 `out/stills` 输出横屏或竖屏的指定帧。

## 场景结构

视频采用 150 BPM、30 帧/秒，每拍恰为 12 帧。`src/timeline.json` 定义场景与音效，视频和配乐共同读取这份时间表。

| 拍数 | 场景 | 源码 |
| --- | --- | --- |
| 0–24 | 轮廓人物走上玻璃体脂秤，体重稳定后显示身体成分 | `src/scenes/ScaleScene.tsx`、`src/three/` |
| 24–32 | 真实演示页面的称重录屏 | `src/scenes/ScreenScenes.tsx` |
| 32–40 | 90 天趋势图动画与页面录屏 | `src/components/Chart.tsx`、`src/scenes/ScreenScenes.tsx` |
| 40–48 | 称重后更新看板与指标 | `src/scenes/ScreenScenes.tsx` |
| 48–64 | 每周分析逐步显示 | `src/scenes/AiScene.tsx` |
| 64–80 | 通用手机和聊天界面的称重通知与分析 | `src/scenes/PhoneScene.tsx` |
| 80–88 | 免费与开源介绍 | `src/scenes/EndScenes.tsx` |
| 88–102 | 项目标识、仓库与演示链接 | `src/scenes/EndScenes.tsx` |

人物由胶囊形关节构成，腿部使用两段逆向运动学，模板缓冲区绘制外轮廓。实现位于 `src/three/Mannequin.tsx`。

## 录制演示素材

`public/footage/` 保留上游录屏，原始采集尺寸为 2560×1440。录制脚本为 `scripts/record_demo.py`：

```bash
uv run --with playwright python video/scripts/record_demo.py
uv run --with playwright python video/scripts/record_demo.py --cdp URL
```

脚本通过虚拟时钟推进计时器、日期、动画帧与 CSS 动画，逐帧截图，再合成 30 帧/秒视频。页面变动后如需重制视频，应重新录屏，并检查 `src/scenes/ScreenScenes.tsx` 中的片段时间。

## 素材与许可证

| 素材 | 来源与许可 |
| --- | --- |
| 配乐和音效 | `scripts/make_music.mjs` 用振荡器与固定随机噪声合成，无第三方采样，使用仓库 MIT 许可证 |
| 演示录屏 | 虚构数据与 AI 生成头像，使用仓库 MIT 许可证，见 [演示素材说明](../docs/demo/README.md) |
| 项目标识 | 基于 `scripts/make_icons.py` 绘制的 SVG，使用 MIT 许可证 |
| Anton、Inter 字体 | Google Fonts，SIL Open Font License 1.1 |
| 手机与聊天界面 | CSS 绘制的通用造型，使用 MIT 许可证 |
| Remotion | 使用 [Remotion 许可证](https://www.remotion.dev/license)，使用前核对适用条款 |
| three.js、React Three Fiber、React | MIT 许可证 |

消息中的表情符号由渲染机器的字体绘制。上游横屏视频见 [YouTube](https://youtu.be/ajvoJN0Qh_4)。
