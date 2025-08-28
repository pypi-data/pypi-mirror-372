# SOC Executor

SOC工具执行器 - 执行本地Python文件并通过HTTP API提交到SOC平台

## 功能特性

- 读取本地Python脚本文件
- 通过HTTP API提交代码到SOC平台执行
- 支持环境变量配置
- 命令行工具，使用简单
- 支持传递JSON格式参数

## 安装

```bash
pip install soc-executor
```

## 使用方法

### 基本用法

```bash
# 执行Python文件
soc-executor script.py

# 使用 --file 参数
soc-executor --file /path/to/script.py

# 传递参数
soc-executor script.py --params '{"key": "value"}'
```

### 环境变量配置

```bash
export HTTP_BASE_URL="http://your-soc-server:port"
export HTTP_TOKEN="your-api-token"
```

## 示例

创建一个测试脚本 `test_script.py`:

```python
def test_function():
    print("Hello from SOC executor!")
    return {"status": "success", "message": "Test completed"}

if __name__ == "__main__":
    result = test_function()
    print(result)
```

执行脚本:

```bash
soc-executor test_script.py
```

## 开发

使用 uv 进行开发环境管理:

```bash
# 安装开发依赖
uv sync --dev

# 运行测试
uv run pytest

# 构建包
uv run python -m build
```

## 许可证

MIT License