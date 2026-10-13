# 贡献指南

本项目保持小规模：一个 Python 服务、一个 HTML 页面和 SQLite，无前端构建步骤。修改应能在 Raspberry Pi 上运行。

## 启动开发环境

```bash
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements-dev.txt
python -m scripts.seed_demo data/demo.db
MISCALE_DB=data/demo.db MISCALE_SCANNER=off uvicorn app.main:app --reload --port 8800
curl -X POST 'localhost:8800/api/debug/simulate?weight=81.4&impedance=478'
```

这里使用独立演示数据库和模拟称重，不要指向真实数据。提交前运行受改动影响的测试与代码检查：

```bash
pytest tests/test_api.py tests/test_notify.py tests/test_analysis.py tests/test_demo.py
ruff check .
```

## 修改约定

- 修改 `scale.py`、`session.py` 或 `body.py` 时，用实际格式的数据包增加回归测试。`tests/packets.py` 提供构造方法。
- 用户界面文案加入 `app/static/index.html` 的 `STRINGS`，同时维护 `zh-CN`、`en` 和 `pt-BR`。保留占位符，不在页面写死提示文字。
- 通知语言在 `app/notify.py`，真实 AI 分析语言在 `app/analysis.py`，接口错误提示在 `app/errors.py`。
- 体重始终以千克保存，仅在显示时转换。
- 添加运行时依赖前说明理由并讨论。
- 新动画尊重 `prefers-reduced-motion`。
- 保持静态演示可用。`scripts/build_demo.py` 复用主页面，`demo/demo.js` 提供内存中的接口与模拟分析。页面接口变动时同步更新演示。
- API 协议字段、型号、单位、产品名和第三方专名保持原名。

## 支持其他体脂秤

在 `app/scale.py` 中为新型号增加解析器，将广播或 GATT 通知转为 `Reading`。贡献时附上：

- 型号、产品名与标签照片。
- 一次真实称重的原始数据包，可从 `/api/debug/packets` 或 `/api/debug/devices` 获取。
- 根据这些数据包编写的测试。

## 反馈问题

使用仓库的问题模板。读数异常请提供体脂秤型号、蓝牙适配器、操作系统，以及称重后立即获取的 `/api/debug/packets` 输出。分享前检查并移除个人数据与密钥。
