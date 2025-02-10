cd $(dirname "$(realpath "$0")")/../

# 清理旧的构建文件
rm -rf dist/ build/ *.egg-info/

# 构建新的分发包
python -m build

# 上传到 PyPI
twine upload dist/*