# 发布到PyPI指南

## 准备工作

### 1. 安装必要的工具

```bash
# 安装构建工具
pip install build twine

# 或者使用uv
uv add --dev build twine
```

### 2. 检查项目配置

确保以下文件已正确配置：
- `pyproject.toml` - 项目元数据和依赖
- `README.md` - 项目文档
- `LICENSE` - 许可证文件
- `sensespace_did/__init__.py` - 包含版本信息

### 3. 测试构建

```bash
# 清理之前的构建
rm -rf dist/ build/ *.egg-info/

# 构建项目
python -m build

# 检查构建的文件
ls -la dist/
```

## 发布到PyPI

### 1. 注册PyPI账户

如果还没有PyPI账户，请访问 https://pypi.org/account/register/ 注册。

### 2. 配置API Token

1. 登录PyPI
2. 进入账户设置
3. 创建API Token
4. 配置到本地环境

```bash
# 方法1: 使用环境变量
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-your-token-here

# 方法2: 创建配置文件
mkdir ~/.pypirc
```

创建 `~/.pypirc` 文件：
```ini
[pypi]
username = __token__
password = pypi-your-token-here
```

### 3. 发布到PyPI

```bash
# 上传到PyPI
twine upload dist/*

# 或者只上传源码包
twine upload dist/*.tar.gz

# 或者只上传wheel包
twine upload dist/*.whl
```

### 4. 验证发布

```bash
# 检查包是否可以安装
pip install --index-url https://pypi.org/simple/ sensespace-did

# 测试导入
python -c "import sensespace_did; print(sensespace_did.__version__)"
```

## 发布到TestPyPI（推荐）

在发布到正式PyPI之前，建议先发布到TestPyPI进行测试：

### 1. 注册TestPyPI账户

访问 https://test.pypi.org/account/register/ 注册TestPyPI账户。

### 2. 配置TestPyPI Token

类似PyPI，创建TestPyPI的API Token。

### 3. 发布到TestPyPI

```bash
# 上传到TestPyPI
twine upload --repository testpypi dist/*

# 从TestPyPI安装测试
pip install --index-url https://test.pypi.org/simple/ sensespace-did
```

## 自动化发布脚本

创建 `scripts/publish.sh` 脚本：

```bash
#!/bin/bash
set -e

echo "Building package..."
python -m build

echo "Uploading to TestPyPI..."
twine upload --repository testpypi dist/*

echo "Testing installation from TestPyPI..."
pip install --index-url https://test.pypi.org/simple/ sensespace-did

echo "Uploading to PyPI..."
twine upload dist/*

echo "Done!"
```

## 版本管理

### 更新版本号

1. 更新 `pyproject.toml` 中的版本号
2. 更新 `sensespace_did/__init__.py` 中的 `__version__`

### 版本号规范

使用语义化版本号：
- MAJOR.MINOR.PATCH
- 例如：0.1.0, 0.1.1, 1.0.0

## 常见问题

### 1. 包名冲突
如果包名已被占用，需要修改 `pyproject.toml` 中的 `name` 字段。

### 2. 依赖问题
确保所有依赖都在 `dependencies` 列表中正确声明。

### 3. 文件包含问题
确保所有必要的Python文件都在 `sensespace_did/` 目录中。

### 4. 许可证问题
确保LICENSE文件存在且格式正确。

## 发布检查清单

- [ ] 更新版本号
- [ ] 更新README.md
- [ ] 测试本地构建
- [ ] 测试TestPyPI发布
- [ ] 验证安装和导入
- [ ] 发布到正式PyPI
- [ ] 验证正式PyPI安装
