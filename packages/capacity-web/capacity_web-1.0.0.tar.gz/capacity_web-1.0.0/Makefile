# Capacity Web Package - UV 极速工作流 ⚡
# 基于 uv 的现代化 Python 包开发

.PHONY: sync test build publish clean dev format lint check release

# 🚀 初始化项目 (仅需运行一次)
init:
	@echo "🎉 使用 uv 初始化项目..."
	uv sync
	@echo "✅ 项目初始化完成！"

# 📦 同步依赖 (超快速度)
sync:
	@echo "⚡ 同步依赖..."
	uv sync

# 🧪 运行测试 (UV 环境)
test:
	@echo "🧪 运行测试..."
	uv run python tests/test_search.py
	@echo "🧪 运行 pytest..."
	uv run pytest tests/ -v

# 🚀 开发模式测试
dev:
	@echo "🚀 开发模式测试..."
	uv run python -c "from capacity_web import search_with_nextchat; print('✅ 导入成功')"
	uv run python -c "from capacity_web import search_with_nextchat; result = search_with_nextchat('test', max_results=1); print(f'测试结果: {result[\"success\"]}')"

# 🔨 构建包 (UV 原生构建)
build:
	@echo "🔨 使用 uv 构建包..."
	uv build

# 🧪 发布到 TestPyPI (UV 原生)
test-publish:
	@echo "🧪 发布到 TestPyPI..."
	uv publish --repository testpypi

# 🚀 发布到 PyPI (UV 原生)
publish:
	@echo "🚀 发布到 PyPI..."
	uv publish

# 🏢 发布到私有仓库
publish-private:
	@echo "🏢 发布到私有仓库..."
	uv publish --repository-url http://your-private-pypi.com/simple/

# 🧹 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .uv_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# 📊 代码质量检查
lint:
	@echo "📊 代码质量检查..."
	uv run ruff check .
	uv run mypy capacity_web/

# 🎨 代码格式化
format:
	@echo "🎨 代码格式化..."
	uv run ruff format .

# ✅ 完整检查
check: lint test
	@echo "✅ 所有检查通过！"

# 🎉 完整发布流程 (极速版)
release: clean check build test-publish
	@echo "🎉 版本发布完成! 检查 TestPyPI 后运行 'make publish' 发布到正式 PyPI"

# ⚡ 添加依赖 (示例)
add-dep:
	@echo "示例: uv add requests"
	@echo "示例: uv add --dev pytest-cov"

# 🔄 更新所有依赖
update:
	@echo "🔄 更新所有依赖..."
	uv sync --upgrade

# 📋 显示依赖树
tree:
	@echo "📋 依赖树..."
	uv tree

# 🎯 快速开始 (新开发者)
quickstart: init test dev
	@echo "🎯 快速开始完成！可以开始开发了"
