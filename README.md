# 新客增长 · 全链路跨域诊断 Agent

> 参赛作品 · AI 创新大赛（赛道一：AI Native / 扁平化协作）

> 📌 **评委请从这里开始 → [评委导览.md](评委导览.md)**（一页看懂：演示视频 / 象限图 / 头号结论 / 价值 / 复现）

## 一句话

锚定一个指标 **新客首单转化率**，让 agent 把 **站内行为 × 供给 × 价格 × 搜索趋势 × 大促日历……等多域信号**（框架可无限扩域）在
『品类 × 国家』上对齐，自动定位"高意图新客白白流失、且可通过补供给挽回"的
最大增长杠杆——这是任何单一团队、任何纯漏斗工具都看不到的"团队缝里的增长点"。
**域越多越有价值，人脑装不下的多维交叉正是 AI 不可替代之处。**

## 为什么巧

- **跨域**：增长卡点常掉在团队的缝里——获取看渠道、行为看漏斗、供给看库存，
  没人能同时看全。AI 把缝缝起来。
- **不是又一个漏斗工具**：纯漏斗只能看到"加购→下单转化低"，分不清是供给还是别的。
  本工具用跨域 join 把真凶定位到供给（内置"红鲱鱼"对照验证：转化低但供给健康的
  格子不会被误报）。
- **有数据对比**：直接量化"可挽回首单数"。

## 架构（3 层）

```
semantic.yaml   语义层/指标字典  ── agent 的地基(口径+维度+跨域方法)
      │            有了这层，口径稳定、结果可复现，agent 不臆造指标含义
      ▼
tools.py        工具层  ── pandas 查询函数，返回聚合小结果，明细永不进 LLM
      │
      ▼
analyze.py      诊断流程  ── 确定性算出所有数字(JSON)
      │
      ▼
SKILL.md        Claude Code Skill  ── LLM 在数字之上写诊断+动作打法(绝不编数字)
```

数据流：原始行为数据(海量 event)→ 离线预聚合成 3 张宽表 → agent 通过工具查询。
**原始数据留本地，只有聚合结果进 LLM**，天然合规。

## 跑起来

```bash
# 1. 装依赖
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

# 2. 造合成数据（演示用；真实使用见下）
.venv/bin/python gen_synthetic.py

# 3a. 直接看确定性诊断
.venv/bin/python analyze.py

# 3b. 单独看跨域错配排名
.venv/bin/python tools.py mismatch

# 3c. 生成供需错配象限图 → output/quadrant.png
.venv/bin/python chart.py

# 4. 作为 Claude Code Skill 演示（最炫）
#    在仓库根目录的 Claude Code 里直接调用 /growth-diagnose
```

## 换成真实数据

把你导出的 3 张 CSV 放进 `data/`，schema 与合成数据一致即可（**务必预聚合，不要导原始 event**）：

| 文件 | 粒度 | 关键列 |
|---|---|---|
| `behavior_funnel.csv` | date×channel×country×category×price_band | exposure_uv, click_uv, search_uv, addcart_uv, order_uv |
| `supply_depth.csv` | date×country×category | sku_count, in_stock_rate, oos_rate, price_competitiveness, sell_through_rate |
| `acquisition.csv`（可选） | date×channel×country | new_users, spend, cac |
| `search_trend.csv`（外部·可选） | date×country×category | search_index, wow_change |
| `event_calendar.csv`（外部·可选） | country | upcoming_event, days_to_event, is_peak_window |

各域 JOIN 键 = `category + country`。换数据后无需改代码，直接重跑。新增一个域 = 加一张宽表 + 一个查询函数。

## 文件

| 文件 | 作用 |
|---|---|
| `semantic.yaml` | 语义层：指标口径、维度、跨域归因方法 |
| `gen_synthetic.py` | 合成数据生成器（内埋一个真洞察 + 一个红鲱鱼） |
| `tools.py` | 工具层：行为/供给/外部查询 + 跨域 join（分品类基准·统计显著性·混杂守门·RICE·单位经济，含 CLI） |
| `analyze.py` | 诊断主流程，输出 JSON / 人类摘要 |
| `chart.py` | 可视化：供需错配象限图 → `output/quadrant.png` |
| `.claude/skills/growth-diagnose/` | Claude Code Skill 壳（位于仓库根目录） |

### 参赛提交材料
| 文件 | 作用 |
|---|---|
| `立项表.docx` / `立项表.md` | 方案文档（路演版立项书） |
| `提交内容.md` | 报名表 4 列（赛道/名称/简介/立项方案） |
| `落地数据与效果验证.md` | 实跑结果 + 效果对比（耗时/可挽回量化/红鲱鱼对照） |
| `复用说明.md` | 框架可平移性（加新域三步 + 5 个平移场景） |
| `演示脚本.md` | 演示视频录制脚本（分镜口播稿 + 操作命令） |
| `output/diagnosis.json` / `output/quadrant.png` | 落地数据产物（结构化诊断 + 象限图） |

## 可复用

框架 =「锁定一个业务对象 → 在它身上对齐多域信号 → 找跨团队断点」，
可直接套到：复购、大促冷启动、品类增长、商家经营参谋 skill 等场景。
