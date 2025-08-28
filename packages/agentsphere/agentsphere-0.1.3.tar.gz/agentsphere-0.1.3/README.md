# agent-sphere-python-sdk

## 说明

**agent-sphere** 是一个云端安全隔离的沙箱基础设施，提供安全的环境来运行 AI 生成的代码。

**agent-sphere-python-sdk** 是用于连接和操作 agent-sphere 沙箱的 Python SDK，提供了启动沙箱、控制沙箱状态、执行代码、文件操作等功能。

## 开发

### 环境搭建

本项目使用 Poetry 进行依赖管理，虚拟环境将创建在项目目录内（`.venv` 文件夹）。

#### 前置要求

- Python 3.9+
- Poetry（如果未安装，请先安装 Poetry）（https://python-poetry.org/docs/）

#### 创建虚拟环境并安装依赖

```shell
# 1. 克隆项目后，进入项目根目录
cd agent-sphere-python-sdk

# 2. 创建虚拟环境并安装所有依赖（包括开发依赖）
poetry install

# 3. 配置 IDE 解释器
# 虚拟环境创建完成后，需要在 IDE 中选择正确的 Python 解释器
# 解释器路径指向到：项目根目录/.venv/bin/python 
```

## 分发

### 安装（用户安装SDK的方法）

```shell
  pip install agentsphere
```

## SDK维护和发布

### 本地测试

```shell
  # 在项目根目录（包含 pyproject.toml 的目录）执行：
  pip install -e .
```

### 测试发布

```shell
pip install ./dist/*
```

### 正式发布

```shell
# 1. 构建包（自动包含所有optional-dependencies）
python -m build

# 2. 检查包内容
unzip -l dist/agentsphere-1.0.0-py3-none-any.whl | grep METADATA
# 应显示所有可选依赖组（包括dev）

# 3. 上传到PyPI
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-api-token
twine upload dist/*
```

### 本地团队测试

```shell

# 启动本地 PyPI 服务器
python -m pip install pypiserver
mkdir ~/packages
pypi-server run -p 8080 ~/packages &

# 上传测试包
twine upload --repository-url http://localhost:8080 dist/*

# 从本地安装测试
pip install --index-url http://localhost:8080/simple/ agentsphere
```

# 版本号修改

> 每次上传需要使用新的版本号
>
> 版本号文件：pyproject.toml



