"""
可视化：新客增长 · 供需错配象限图
----------------------------------------------------------------------------
x = 供给缺口（越右供给越差），y = 需求意图（新客加购量，越上需求越旺），
气泡大小 = 可挽回首单，颜色 = 机会类型。右上角=高需求×差供给=紧急堵漏区。
一张图让评委秒懂"钱卡在哪个象限"。

  python chart.py   →  output/quadrant.png
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
import pandas as pd
import tools

plt.rcParams["font.sans-serif"] = ["Arial Unicode MS", "PingFang HK",
                                   "STHeiti", "Heiti TC", "Songti SC"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.join(tools.HERE, "output")
os.makedirs(OUT, exist_ok=True)

LEGEND = [("紧急堵漏（高需求×差供给）", "#e23b3b"),
          ("顺势加码（高需求×好供给）", "#2ca02c"),
          ("堵漏（供给不足）", "#ff7f0e"),
          ("常规", "#b0b0b0")]


def _color(t):
    if "紧急堵漏" in t:
        return "#e23b3b"
    if "顺势加码" in t:
        return "#2ca02c"
    if "堵漏" in t:
        return "#ff7f0e"
    return "#b0b0b0"


def render():
    df, _ = tools.supply_demand_mismatch(top=100)
    df = tools.external_context(df)

    colors = [_color(t) for t in df["机会类型"]]
    # 气泡大小=优先级分(已计入供给归因强度)，让"真正该行动"的格子最大
    sizes = df["优先级分"].clip(lower=0) * 0.7 + 50

    fig, ax = plt.subplots(figsize=(11, 7.5))
    ax.scatter(df["supply_gap"], df["addcart_uv"], s=sizes, c=colors,
               alpha=0.65, edgecolors="white", linewidths=0.9, zorder=3)

    xm, ym = df["supply_gap"].median(), df["addcart_uv"].median()
    ax.axvline(xm, color="#cccccc", ls="--", lw=1, zorder=1)
    ax.axhline(ym, color="#cccccc", ls="--", lw=1, zorder=1)

    # 标注：优先级最高的几格 + 顺势加码代表格
    notable = df.sort_values("优先级分", ascending=False).head(4)
    green = df[df["机会类型"].str.contains("顺势加码")].head(1)
    for _, r in pd.concat([notable, green]).drop_duplicates(["category", "country"]).iterrows():
        ax.annotate(f"{r['category']}×{r['country']}",
                    (r["supply_gap"], r["addcart_uv"]),
                    fontsize=9, xytext=(6, 6), textcoords="offset points", zorder=4)

    ax.set_xlabel("供给缺口  →  越右供给越差", fontsize=11)
    ax.set_ylabel("需求意图：新客加购量  ↑  越上需求越旺", fontsize=11)
    ax.set_title("新客增长 · 供需错配象限图（气泡大小 = 优先级分）",
                 fontsize=14, fontweight="bold")
    ax.text(0.985, 0.97, "紧急堵漏区\n高需求 × 差供给", transform=ax.transAxes,
            ha="right", va="top", fontsize=10, color="#e23b3b",
            bbox=dict(boxstyle="round", fc="#fff0f0", ec="#e23b3b"))

    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=v,
                      markersize=11, label=k) for k, v in LEGEND]
    ax.legend(handles=handles, loc="upper left", fontsize=9, title="机会类型")

    fig.tight_layout()
    p = os.path.join(OUT, "quadrant.png")
    fig.savefig(p, dpi=140)
    print("已保存:", p)
    return p


if __name__ == "__main__":
    render()
