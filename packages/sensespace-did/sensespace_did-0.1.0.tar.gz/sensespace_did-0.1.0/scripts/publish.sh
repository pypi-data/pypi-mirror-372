#!/bin/bash
set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 打印带颜色的消息
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查必要的工具
check_tools() {
    print_info "检查必要的工具..."
    
    if ! command -v python &> /dev/null; then
        print_error "Python 未安装"
        exit 1
    fi
    
    if ! python -c "import build" &> /dev/null; then
        print_warning "build 包未安装，正在安装..."
        pip install build
    fi
    
    if ! python -c "import twine" &> /dev/null; then
        print_warning "twine 包未安装，正在安装..."
        pip install twine
    fi
}

# 清理之前的构建
clean_build() {
    print_info "清理之前的构建文件..."
    rm -rf dist/ build/ *.egg-info/
}

# 构建项目
build_package() {
    print_info "构建项目..."
    python -m build
    
    if [ $? -eq 0 ]; then
        print_info "构建成功！"
        ls -la dist/
    else
        print_error "构建失败！"
        exit 1
    fi
}

# 检查构建的文件
check_build_files() {
    print_info "检查构建文件..."
    
    if [ ! -f "dist/sensespace_did-*.tar.gz" ]; then
        print_error "源码包未找到"
        exit 1
    fi
    
    if [ ! -f "dist/sensespace_did-*.whl" ]; then
        print_warning "Wheel包未找到，但源码包存在"
    fi
}

# 发布到TestPyPI
publish_to_testpypi() {
    print_info "发布到TestPyPI..."
    
    if [ -z "$TESTPYPI_TOKEN" ]; then
        print_warning "TESTPYPI_TOKEN 环境变量未设置，跳过TestPyPI发布"
        return 0
    fi
    
    export TWINE_USERNAME=__token__
    export TWINE_PASSWORD=$TESTPYPI_TOKEN
    
    twine upload --repository testpypi dist/*
    
    if [ $? -eq 0 ]; then
        print_info "TestPyPI发布成功！"
    else
        print_error "TestPyPI发布失败！"
        exit 1
    fi
}

# 测试从TestPyPI安装
test_testpypi_install() {
    print_info "测试从TestPyPI安装..."
    
    if [ -z "$TESTPYPI_TOKEN" ]; then
        print_warning "跳过TestPyPI安装测试"
        return 0
    fi
    
    # 获取版本号
    VERSION=$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")
    
    pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ sensespace-did==$VERSION
    
    if [ $? -eq 0 ]; then
        print_info "TestPyPI安装测试成功！"
        python -c "import sensespace_did; print(f'版本: {sensespace_did.__version__}')"
    else
        print_error "TestPyPI安装测试失败！"
        exit 1
    fi
}

# 发布到PyPI
publish_to_pypi() {
    print_info "发布到PyPI..."
    
    if [ -z "$PYPI_TOKEN" ]; then
        print_error "PYPI_TOKEN 环境变量未设置"
        print_info "请设置环境变量: export PYPI_TOKEN=your-token"
        exit 1
    fi
    
    export TWINE_USERNAME=__token__
    export TWINE_PASSWORD=$PYPI_TOKEN
    
    twine upload dist/*
    
    if [ $? -eq 0 ]; then
        print_info "PyPI发布成功！"
    else
        print_error "PyPI发布失败！"
        exit 1
    fi
}

# 测试从PyPI安装
test_pypi_install() {
    print_info "测试从PyPI安装..."
    
    # 等待PyPI更新
    print_info "等待PyPI更新（30秒）..."
    sleep 30
    
    # 获取版本号
    VERSION=$(python -c "import toml; print(toml.load('pyproject.toml')['project']['version'])")
    
    pip install sensespace-did==$VERSION
    
    if [ $? -eq 0 ]; then
        print_info "PyPI安装测试成功！"
        python -c "import sensespace_did; print(f'版本: {sensespace_did.__version__}')"
    else
        print_error "PyPI安装测试失败！"
        exit 1
    fi
}

# 主函数
main() {
    print_info "开始发布 sensespace-did 到 PyPI..."
    
    check_tools
    clean_build
    build_package
    check_build_files
    
    # 询问是否发布到TestPyPI
    read -p "是否发布到TestPyPI进行测试？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        publish_to_testpypi
        test_testpypi_install
    fi
    
    # 询问是否发布到正式PyPI
    read -p "是否发布到正式PyPI？(y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        publish_to_pypi
        test_pypi_install
    fi
    
    print_info "发布完成！"
}

# 运行主函数
main "$@"
