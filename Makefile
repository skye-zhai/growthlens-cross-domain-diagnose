# ============================================================================
# Makefile —— 常用入口 / convenience targets
#   make          等价于 make all（建环境→造数→分析→自检）
#   make setup    只建虚拟环境并装依赖
#   make verify   只跑声明自检（假设环境已就绪）
#   make chart    生成象限图（额外需要 matplotlib）
#   make clean    清理生成物（venv / 数据 / 缓存）
# ============================================================================
VENV := .venv
VPY  := $(VENV)/bin/python

.PHONY: all setup data analyze verify chart clean

all:
	bash run.sh

setup:
	python3 -m venv $(VENV)
	$(VPY) -m pip install -q --upgrade pip
	$(VPY) -m pip install -q -r requirements.txt

data: setup
	$(VPY) gen_synthetic.py

analyze: data
	$(VPY) analyze.py

verify:
	$(VPY) verify.py

chart:
	$(VPY) -m pip install -q matplotlib
	$(VPY) chart.py

clean:
	rm -rf $(VENV) __pycache__ data/*.csv
