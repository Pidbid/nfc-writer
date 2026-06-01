# 代理指令

本文件定义 AI 代理在本项目中必须遵守的工作规范。所有指令均为强制性要求。

## 语言

- 所有代码注释、文档字符串、提交信息、交流对话一律使用中文。
- 代码标识符（变量名、函数名、类名）使用英文。

## 工具链

### Python

- 包管理器：uv，禁止使用 pip、pip-tools、poetry、pdm。
- 安装依赖：`uv add <包名>`，禁止直接编辑 `pyproject.toml` 中的依赖列表。
- 运行命令：`uv run <命令>`，禁止直接调用 `.venv` 中的二进制文件。
- 创建虚拟环境：由 uv 自动管理，禁止手动 `python -m venv`。
- Python 版本：3.12，由 `.python-version` 固定。

### Node.js

- 包管理器：pnpm，禁止使用 npm、yarn。
- 安装依赖：`pnpm add <包名>`（生产依赖）、`pnpm add -D <包名>`（开发依赖）。
- 运行脚本：`pnpm dev`、`pnpm build`、`pnpm preview`。
- 工作目录：`frontend/`。

## 开发流程

### 测试驱动开发（TDD）

所有功能开发必须遵循 TDD 循环：

1. **红灯**：先编写失败的测试用例，明确期望行为。
2. **绿灯**：编写最少的代码使测试通过。
3. **重构**：在测试保护下优化代码结构，确保测试始终通过。

禁止跳过测试直接编写实现代码。禁止删除或注释掉失败的测试来绕过问题。

### 测试规范

- 测试框架：pytest
- 运行测试：`uv run pytest`
- 测试文件位置：`tests/` 目录
- 测试文件命名：`test_<模块名>.py`
- 测试类命名：`Test<类名>`
- 测试方法命名：`test_<行为描述>`
- 测试文档字符串：使用中文描述测试意图
- 测试夹具：统一放在 `tests/conftest.py`

### 代码质量

- 代码检查：`uv run ruff check src/ tests/`
- 所有代码在提交前必须通过 ruff 检查，零警告零错误。
- 类型注解：所有函数签名必须包含完整的类型注解。

### 注释规范

每个 Python 文件必须包含头部注释：

```python
"""
文件名: <文件名>
创建日期: <YYYY-MM-DD>
功能描述: <一句话描述文件职责>
"""
```

每个函数和方法必须包含中文文档字符串，格式：

```python
def function_name(param: str) -> dict:
    """一句话描述函数功能。

    参数:
        param: 参数说明。

    返回:
        返回值说明。

    异常:
        ExceptionType: 异常触发条件。
    """
```

## 提交规范

### 禁止主动提交

除非用户明确要求提交代码，否则禁止执行 `git commit`。用户未提及提交时，完成任务后报告结果即可，不要自行提交。

### 提交信息格式

当用户要求提交时，必须遵循以下格式：

```
<类型>: <简要描述>
```

类型枚举：

| 类型 | 用途 |
|---|---|
| `feat` | 新功能 |
| `fix` | 修复问题 |
| `docs` | 文档变更 |
| `style` | 代码格式调整（不影响逻辑） |
| `refactor` | 重构（非新功能、非修复） |
| `test` | 测试相关 |
| `chore` | 构建、工具、依赖等杂项 |

示例：

```
feat: 添加 NFC 标签写入功能
fix: 修复未连接时读取标签导致的崩溃
test: 添加 NFCService 断开连接的测试用例
refactor: 将适配器导入改为延迟加载
docs: 更新 README 中的安装说明
chore: 通过 uv add 更新 pywebview 版本
```

禁止使用空泛描述如"更新代码"、"修复 bug"、"提交更改"。

## 项目结构

```
.
├── src/nfc_writer/          # Python 后端
│   ├── main.py              # 应用入口
│   ├── app.py               # pywebview 窗口管理
│   ├── bridge.py            # JS 桥接 API
│   └── nfc/                 # NFC 领域逻辑
│       ├── types.py         # 数据类型定义
│       ├── service.py       # 业务服务层
│       └── adapters/        # 硬件适配器
│           ├── base.py      # 适配器协议
│           ├── mock.py      # 模拟适配器
│           └── pyscard_adapter.py  # 真实硬件适配器
├── frontend/                # Vue 前端
│   ├── src/
│   │   ├── App.vue          # 主界面组件
│   │   ├── services/        # 桥接服务
│   │   └── types/           # TypeScript 类型
│   ├── package.json
│   └── vite.config.ts
├── tests/                   # Python 测试
├── pyproject.toml           # Python 项目配置（uv 管理）
├── uv.lock                  # Python 依赖锁文件
├── .python-version          # Python 版本锁定
├── LICENSE                  # GPLv3 协议
└── AGENTS.md                # 本文件
```

## 执行检查清单

在完成任何任务前，代理应自检：

- [ ] 是否使用了 uv 而非 pip？
- [ ] 是否使用了 pnpm 而非 npm？
- [ ] 是否先写了测试再写实现？
- [ ] 注释和文档字符串是否使用中文？
- [ ] 是否避免了主动 commit？
- [ ] ruff 检查是否通过？
- [ ] 测试是否全部通过？
