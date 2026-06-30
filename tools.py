"""
工具层 (Tools) —— agent 的"查询能力"
----------------------------------------------------------------------------
每个函数内部用 pandas 查聚合数据，返回的是"聚合后的小结果"，
真实明细永远不进 LLM。这层是 agent 真正的"手脚"。

也可独立 CLI 使用：
  python tools.py funnel --by country
  python tools.py supply --by category
  python tools.py mismatch
"""
import os
import math
import argparse
import pandas as pd
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

MIN_SAMPLE = 100          # 最小加购样本量门槛（低于此不下结论，避免追噪声）
Z_CRIT = -1.645           # 单侧 95% 显著性临界值（转化显著低于基准）

_cache = {}


def _semantic():
    if "semantic" not in _cache:
        with open(os.path.join(HERE, "semantic.yaml"), encoding="utf-8") as f:
            _cache["semantic"] = yaml.safe_load(f) or {}
    return _cache["semantic"]


def _opt(name):
    p = os.path.join(DATA, name)
    return pd.read_csv(p) if os.path.exists(p) else None


def _load():
    if "behavior" not in _cache:
        _cache["behavior"] = pd.read_csv(os.path.join(DATA, "behavior_funnel.csv"))
        _cache["supply"] = pd.read_csv(os.path.join(DATA, "supply_depth.csv"))
        _cache["acq"] = _opt("acquisition.csv")
        _cache["search"] = _opt("search_trend.csv")       # 外部域·搜索趋势
        _cache["events"] = _opt("event_calendar.csv")     # 外部域·大促日历
    return _cache


def _funnel_rates(df):
    """给一个已 sum 好各步 UV 的 DataFrame 追加分步转化率列。"""
    df = df.copy()
    df["首单转化率"] = (df["order_uv"] / df["exposure_uv"]).round(4)
    df["曝光→点击"] = (df["click_uv"] / df["exposure_uv"]).round(4)
    df["点击→搜索"] = (df["search_uv"] / df["click_uv"]).round(4)
    df["搜索→加购"] = (df["addcart_uv"] / df["search_uv"]).round(4)
    df["加购→下单"] = (df["order_uv"] / df["addcart_uv"]).round(4)
    return df


STEP_UV = ["exposure_uv", "click_uv", "search_uv", "addcart_uv", "order_uv"]


def query_behavior_funnel(by=None, filters=None):
    """按维度聚合站内行为漏斗，返回各步 UV + 分步转化率。"""
    b = _load()["behavior"]
    if filters:
        for k, v in filters.items():
            b = b[b[k] == v]
    if by:
        by = [by] if isinstance(by, str) else by
        g = b.groupby(by)[STEP_UV].sum().reset_index()
    else:
        g = b[STEP_UV].sum().to_frame().T
    return _funnel_rates(g)


def query_supply(by=None, filters=None):
    """按维度聚合供给深度（对率取均值、对 SKU 取均值）。"""
    s = _load()["supply"]
    if filters:
        for k, v in filters.items():
            s = s[s[k] == v]
    agg = {"sku_count": "mean", "in_stock_rate": "mean", "oos_rate": "mean",
           "price_competitiveness": "mean", "sell_through_rate": "mean"}
    if by:
        by = [by] if isinstance(by, str) else by
        g = s.groupby(by).agg(agg).reset_index()
    else:
        g = s.agg(agg).to_frame().T
    return g.round(4)


def overall_conversion():
    """全盘新客首单转化率 + 整体分步漏斗。"""
    f = query_behavior_funnel().iloc[0]
    return {
        "新客首单转化率": float(f["首单转化率"]),
        "曝光→点击": float(f["曝光→点击"]),
        "点击→搜索": float(f["点击→搜索"]),
        "搜索→加购": float(f["搜索→加购"]),
        "加购→下单": float(f["加购→下单"]),
        "exposure_uv": int(f["exposure_uv"]),
        "order_uv": int(f["order_uv"]),
    }


def _cac_by_country():
    acq = _load()["acq"]
    if acq is None:
        return {}
    return acq.groupby("country")["cac"].mean().to_dict()


def _zscore(p_hat, p0, n):
    """单比例 z 检验：观测转化 p_hat 是否显著偏离基准 p0（样本量 n）。"""
    if n <= 0 or not (0 < p0 < 1):
        return 0.0
    se = math.sqrt(p0 * (1 - p0) / n)
    return round((p_hat - p0) / se, 1) if se > 0 else 0.0


def _confounder_adjusted():
    """
    混杂守门（直接标准化）：把每个『品类×国家』的转化，按【全局价格带结构】
    重新加权，得到去混杂的 adj_conv。若 adj_conv 明显高于 raw_conv，说明那格的
    低转化部分是"价格带结构"造成的（混杂），而非纯供给——据此给供给归因降权。
    """
    b = _load()["behavior"]
    wpb = b.groupby("price_band")["addcart_uv"].sum()
    wpb = (wpb / wpb.sum()).to_dict()
    g = b.groupby(["category", "country", "price_band"])[
        ["addcart_uv", "order_uv"]].sum().reset_index()
    g["conv"] = g["order_uv"] / g["addcart_uv"].where(g["addcart_uv"] > 0)
    g["w"] = g["price_band"].map(wpb)
    g["wconv"] = g["w"] * g["conv"]
    agg = g.groupby(["category", "country"]).agg(
        wconv=("wconv", "sum"), wsum=("w", "sum")).reset_index()
    agg["adj_conv"] = agg["wconv"] / agg["wsum"]
    raw = b.groupby(["category", "country"]).agg(
        a=("addcart_uv", "sum"), o=("order_uv", "sum")).reset_index()
    raw["raw_conv"] = raw["o"] / raw["a"]
    out = raw.merge(agg[["category", "country", "adj_conv"]],
                    on=["category", "country"], how="left")
    out["mix_effect"] = (out["adj_conv"] - out["raw_conv"]).round(4)
    return out[["category", "country", "adj_conv", "mix_effect"]]


def _root_lever(r):
    """主因判断：先过统计/混杂关，再判缺货 / 价格 / 非供给。"""
    if r["样本量"] < MIN_SAMPLE or not r["统计显著"]:
        return "样本不足/不显著→暂不行动"
    if r["混杂解释比例"] >= 0.5:
        return "价格带结构混杂→非纯供给，需分价格带验证"
    flags = []
    if r["oos_rate"] >= 0.25:
        flags.append("补供给(缺货)")
    if r["price_competitiveness"] <= 0.70:
        flags.append("调价(价格竞争力低)")
    if not flags and r["加购→下单"] < r["基准"]:
        return "非供给主因→换假设验证(渠道/履约?)"
    return " + ".join(flags) if flags else "供给健康"


def supply_demand_mismatch(top=8):
    """
    跨域核心方法：在『品类 × 国家』上对齐"需求意图"与"供给健康"，定位高意图却
    供给不足、可挽回的最大错配格子。引擎含：分品类基准、样本量门槛、统计显著性、
    混杂因子守门、综合归因置信度、RICE 优先级、单位经济。
    """
    b = query_behavior_funnel(by=["category", "country"])
    s = query_supply(by=["category", "country"])
    m = b.merge(s, on=["category", "country"], how="inner")

    m["supply_health"] = (m["in_stock_rate"] * m["price_competitiveness"]).round(4)
    m["supply_gap"] = (1 - m["supply_health"]).round(4)
    m["demand_intent"] = m["addcart_uv"]
    m["demand_share"] = (m["demand_intent"] / m["demand_intent"].sum()).round(4)
    m["错配分"] = (m["demand_share"] * m["supply_gap"]).round(5)

    # —— ① 分品类健康基准（不同品类天然转化不同，全局基准会偏） ——
    healthy = m[m["supply_health"] >= 0.7]
    cat_bench = healthy.groupby("category")["加购→下单"].median()
    global_bench = float(healthy["加购→下单"].median())
    m["基准"] = m["category"].map(cat_bench).fillna(global_bench).round(4)
    m["可挽回首单"] = (m["addcart_uv"] * (m["基准"] - m["加购→下单"]).clip(lower=0)).round(0)

    # —— ② 样本量门槛 + 统计显著性（转化是否真的显著低于基准，避免追噪声） ——
    m["样本量"] = m["addcart_uv"].astype(int)
    m["z值"] = m.apply(lambda r: _zscore(r["加购→下单"], r["基准"], r["样本量"]), axis=1)
    m["统计显著"] = (m["样本量"] >= MIN_SAMPLE) & (m["z值"] <= Z_CRIT)

    # —— ③ 混杂因子守门（价格带结构标准化） ——
    conf = _confounder_adjusted()
    m = m.merge(conf, on=["category", "country"], how="left")
    gap = (m["基准"] - m["加购→下单"]).clip(lower=1e-6)
    m["混杂解释比例"] = (m["mix_effect"].clip(lower=0) / gap).clip(0, 1).round(2)

    # —— ④ 综合归因置信度 = 供给缺口 ×(1-混杂)× 统计显著 ——
    supply_conf = (m["supply_gap"] / 0.5).clip(0, 1)
    sig_factor = m["统计显著"].map({True: 1.0, False: 0.2})
    m["归因置信度"] = (supply_conf * (1 - m["混杂解释比例"]) * sig_factor).round(2)
    # RICE 式优先级（Effort 默认均一，待团队按补供给/调价难度填实际值）
    m["优先级分"] = (m["可挽回首单"] * m["归因置信度"]).round(0)

    # —— ⑤ 单位经济：可挽回 GMV / 白烧 CAC ——
    ue = _semantic().get("unit_economics", {})
    aov_map = ue.get("aov_by_category", {})
    default_aov = ue.get("default_aov", 40)
    m["AOV"] = m["category"].map(aov_map).fillna(default_aov)
    m["可挽回GMV"] = (m["可挽回首单"] * m["AOV"]).round(0)
    cac_map = _cac_by_country()
    m["CAC"] = m["country"].map(cac_map).fillna(0).round(2)
    m["白烧CAC"] = (m["可挽回首单"] * m["CAC"]).round(0)

    m["主因"] = m.apply(_root_lever, axis=1)

    m = m.sort_values("优先级分", ascending=False)
    cols = ["category", "country", "addcart_uv", "加购→下单", "基准",
            "oos_rate", "price_competitiveness", "supply_gap",
            "样本量", "z值", "统计显著", "混杂解释比例",
            "归因置信度", "可挽回首单", "可挽回GMV", "白烧CAC", "优先级分", "主因"]
    return m[cols].head(top).reset_index(drop=True), global_bench


def query_search_trend(by=None):
    """外部域：搜索热度 + 环比。"""
    st = _load()["search"]
    if st is None:
        return None
    if by:
        by = [by] if isinstance(by, str) else by
        g = st.groupby(by).agg(search_index=("search_index", "mean"),
                               搜索环比=("wow_change", "mean")).reset_index()
    else:
        g = pd.DataFrame([{"search_index": st["search_index"].mean(),
                           "搜索环比": st["wow_change"].mean()}])
    return g.round(3)


def query_events():
    """外部域：临近大促/节日。"""
    return _load()["events"]


def external_context(cells):
    """
    给跨域错配格子叠加外部信号(搜索环比 + 临近大促)，判定机会类型：
      🔴紧急堵漏 / 🟢顺势加码 / 🟠堵漏 / 常规
    这是"人脑难同时判断"的多域交叉——内部供给短板 × 外部需求时机。
    """
    cells = cells.copy()
    st = query_search_trend(by=["category", "country"])
    if st is not None:
        cells = cells.merge(st[["category", "country", "搜索环比"]],
                            on=["category", "country"], how="left")
    ev = query_events()
    if ev is not None:
        evc = (ev.groupby("country")
               .agg(临近大促=("upcoming_event", "first"),
                    距大促天数=("days_to_event", "min")).reset_index())
        cells = cells.merge(evc, on="country", how="left")

    def opp(r):
        surge = r.get("搜索环比", 0) or 0
        gap = r.get("supply_gap", 0)
        if surge > 0.5 and gap >= 0.40:
            return "🔴紧急堵漏(需求飙升×供给不足)"
        if surge > 0.5 and gap < 0.30:
            return "🟢顺势加码(需求飙升×供给健康→加投放/备货)"
        if gap >= 0.40:
            return "🟠堵漏(供给不足)"
        return "常规"

    cells["机会类型"] = cells.apply(opp, axis=1)
    return cells


def _print_df(df):
    with pd.option_context("display.max_columns", None, "display.width", 200,
                           "display.unicode.east_asian_width", True):
        print(df.to_string(index=False))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["funnel", "supply", "mismatch", "overall"])
    ap.add_argument("--by", default=None)
    args = ap.parse_args()

    if args.cmd == "funnel":
        _print_df(query_behavior_funnel(by=args.by))
    elif args.cmd == "supply":
        _print_df(query_supply(by=args.by))
    elif args.cmd == "overall":
        print(overall_conversion())
    elif args.cmd == "mismatch":
        df, bench = supply_demand_mismatch()
        print(f"健康基准『加购→下单』中位数 = {bench:.3f}\n")
        _print_df(df)
