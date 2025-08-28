# bdd-trace

一个方便 BDD 项目集成 OpenTelemetry 的 Python 库，提供简化的追踪初始化和配置功能。

## 功能特性

- 简化 OpenTelemetry 集成配置
- 支持开发和生产环境配置
- 提供统一的追踪初始化接口
- 支持 OTLP 导出器配置
- 自动处理追踪器设置

## 安装

推荐使用 uv 管理依赖：

```bash
uv add bdd-trace
uv sync

# 或者用 pip
pip install bdd-trace
```

然后安装 OpenTelemetry 的各种 Instrumentation：

```bash
# uv
uv run opentelemetry-bootstrap -a requirements | uv add -r -
uv sync

# pip
opentelemetry-bootstrap -a install
```

## 快速开始

### 基本使用

```python
# 在所有导入之前，先导入 bdd_trace 并调用 init_trace 初始化
from bdd_trace import Profile, init_trace

# 预置了 DEV, TEST 和 PROD 三个环境的配置
init_trace(service_name="my-service", profile=Profile.DEV)

# 支持自定义配置
init_trace(
    service_name="my-service",
    # 自定义 OTLP 端点
    exporter_otlp_endpoint="http://localhost:4317",
    # 其他设置可运行 opentelemetry-instrument --help 查看
    fastapi_exclude_urls="/healthCheck",
)

# 设置 profile=NO_TRACE 可以禁用自动追踪
init_trace(service_name="my-service", profile=Profile.NO_TRACE)
```
