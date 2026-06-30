"""
诊断主流程 (Analysis Pipeline)
----------------------------------------------------------------------------
确定性地跑完整套分析，输出结构化结果(JSON) + 人类可读摘要。
所有数字都来自 tools.py 的 pandas 计算，LLM 只负责在这些数字之上写叙事/打法，
绝不自己编造数字。

  python analyze.py            # 人类可读摘要
  python analyze.py --json     # 结构化 JSON（给 Skill / agent 消费）
"""
import json
import argparse
import tools


AARRR_MAP = {"曝光→点击": "Acquisition", "点击→搜索": "Acquisition",
             "搜索→加购": "Activation", "加购→下单": "Revenue"}


def run():
    overall = tools.overall_conversion()
    mismatch_df, benchmark = tools.supply_demand_mismatch(top=8)

    # AARRR：聚合视角最弱步骤(可能是陷阱) vs 可挽回价值集中的步骤(真机会)
    steps = {k: overall[k] for k in ["曝光→点击", "点击→搜索", "搜索→加购", "加购→下单"]}
    visible_worst = min(steps, key=steps.get)
    recoverable_step = "加购→下单"   # 本场景可挽回价值集中处

    top = mismatch_df.iloc[0]
    top3 = mismatch_df.head(3)
    rec_orders = float(top3["可挽回首单"].sum())
    rec_gmv = float(top3["可挽回GMV"].sum())
    wasted_cac = float(top3["白烧CAC"].sum())

    # 外部放大：内部供给短板 × 外部需求时机（搜索环比 + 临近大促）
    full_df, _ = tools.supply_demand_mismatch(top=100)
    ext = tools.external_context(full_df)
    时效机会 = []
    if "搜索环比" in ext.columns:
        surging = ext[ext["搜索环比"] > 0.5].sort_values("优先级分", ascending=False)
        cols = [c for c in ["category", "country", "机会类型", "搜索环比",
                            "距大促天数", "加购→下单", "可挽回首单", "优先级分"]
                if c in surging.columns]
        时效机会 = surging[cols].head(6).to_dict(orient="records")

    result = {
        "锚点指标": "新客首单转化率",
        "全盘": {
            "新客首单转化率": overall["新客首单转化率"],
            "整体漏斗": steps,
            "AARRR最弱可见步骤": f"{visible_worst}（{AARRR_MAP[visible_worst]}阶段，基线最低≠最大机会，陷阱）",
            "可挽回价值集中步骤": f"{recoverable_step}（{AARRR_MAP[recoverable_step]}阶段，真机会）",
        },
        "健康基准_加购到下单": round(benchmark, 4),
        "跨域错配_TOP": mismatch_df.to_dict(orient="records"),
        "优先级行动清单": top3[["category", "country", "主因", "供给归因强度",
                          "可挽回首单", "可挽回GMV", "白烧CAC", "优先级分"]
                         ].to_dict(orient="records"),
        "头号错配": {
            "品类": top["category"], "国家": top["country"],
            "高意图加购量": int(top["addcart_uv"]),
            "加购到下单转化率": float(top["加购→下单"]),
            "缺货率": float(top["oos_rate"]),
            "价格竞争力": float(top["price_competitiveness"]),
            "供给归因强度": float(top["供给归因强度"]),
            "主因": top["主因"],
            "可挽回首单": float(top["可挽回首单"]),
        },
        "单位经济_TOP3": {
            "可挽回首单合计": round(rec_orders, 0),
            "可挽回GMV合计": round(rec_gmv, 0),
            "白烧CAC合计": round(wasted_cac, 0),
        },
        "外部放大_时效机会": 时效机会,
        "引擎质控": {
            "样本量门槛": tools.MIN_SAMPLE,
            "总格子数": int(len(full_df)),
            "转化缺口统计显著格子数": int(full_df["统计显著"].sum()),
            "因混杂降权格子数": int((full_df["混杂解释比例"] >= 0.5).sum()),
        },
    }
    return result


def human_summary(r):
    lines = []
    lines.append("=" * 70)
    lines.append("  新客增长 · 全链路跨域诊断")
    lines.append("=" * 70)
    g = r["全盘"]
    lines.append(f"锚点指标：新客首单转化率 = {g['新客首单转化率']:.2%}")
    lines.append("整体漏斗：" + "  ".join(f"{k} {v:.1%}" for k, v in g["整体漏斗"].items()))
    lines.append(f"[AARRR] 可见最弱步骤：{g['AARRR最弱可见步骤']}")
    lines.append(f"[AARRR] 真机会步骤：  {g['可挽回价值集中步骤']}")
    lines.append("")
    lines.append(f"健康基准（分品类中位数，全局≈{r['健康基准_加购到下单']:.1%}）")
    q = r.get("引擎质控", {})
    if q:
        lines.append(
            f"引擎质控：样本量门槛≥{q['样本量门槛']} · "
            f"{q['转化缺口统计显著格子数']}/{q['总格子数']} 格转化缺口统计显著 · "
            f"{q['因混杂降权格子数']} 格因价格带混杂被降权")
    lines.append("")
    lines.append("跨域错配定位（需求旺 × 供给差 → 可挽回，按 RICE 优先级排序）：")
    lines.append("-" * 70)
    lines.append(f"{'品类':<7}{'国家':<7}{'加购→下单':>10}{'缺货率':>8}{'显著':>5}"
                 f"{'置信':>7}{'可挽回单':>9}{'可挽回GMV':>11}{'优先级':>8}")
    for row in r["跨域错配_TOP"][:6]:
        sig = "✓" if row.get("统计显著") else "✗"
        lines.append(
            f"{row['category']:<7}{row['country']:<7}{row['加购→下单']:>9.1%}"
            f"{row['oos_rate']:>8.1%}{sig:>5}{row['供给归因强度']:>7.2f}"
            f"{int(row['可挽回首单']):>9}{int(row['可挽回GMV']):>11}"
            f"{int(row['优先级分']):>8}")
    lines.append("-" * 70)
    h = r["头号错配"]
    u = r["单位经济_TOP3"]
    lines.append("")
    lines.append("💡 头号增长杠杆（结论）：")
    lines.append(
        f"   「{h['国家']} × {h['品类']}」高意图新客加购 {h['高意图加购量']} 人，"
        f"加购→下单仅 {h['加购到下单转化率']:.1%}")
    lines.append(
        f"   主因：{h['主因']}（缺货率 {h['缺货率']:.0%}、价格竞争力 {h['价格竞争力']:.2f}，"
        f"供给归因强度 {h['供给归因强度']:.0%}）")
    lines.append(
        f"   单位经济（TOP3）：可挽回首单 ~{int(u['可挽回首单合计'])} 单 / "
        f"可挽回 GMV ~${int(u['可挽回GMV合计']):,} / 止损白烧 CAC ~${int(u['白烧CAC合计']):,}")

    ext = r.get("外部放大_时效机会") or []
    if ext:
        lines.append("")
        lines.append("🌐 外部放大（内部供给 × 外部需求时机，人脑难同时判断）：")
        for e in ext:
            tag = e.get("机会类型", "")
            d = e.get("距大促天数", "?")
            lines.append(
                f"   {e['category']}×{e['country']}：{tag}  "
                f"搜索环比 +{e.get('搜索环比', 0):.0%}  距大促 {d} 天  "
                f"可挽回 {int(e.get('可挽回首单', 0))} 单")
    lines.append("=" * 70)
    return "\n".join(lines)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    r = run()
    if args.json:
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        print(human_summary(r))
