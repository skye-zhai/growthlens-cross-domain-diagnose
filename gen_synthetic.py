"""
合成数据生成器
----------------------------------------------------------------------------
造一批"逼真的"拉新数据，并故意埋一个跨域洞察：
  【东南亚 3C数码 高意图新客旺，但供给不足(缺货+没价格优势)，导致加购后大量流失】
同时埋一个"红鲱鱼"：
  【巴西 美妆 加购到下单转化也低，但供给是健康的】—— 用来验证 agent 能否
  正确区分"供给问题"和"非供给问题"，证明跨域 join 比纯漏斗工具强。

真实使用时，把本文件换成你自己的导出脚本，产出同样 schema 的三张 CSV 即可。
"""
import os
import datetime as dt
import numpy as np
import pandas as pd

SEED = 42
rng = np.random.default_rng(SEED)
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
os.makedirs(DATA, exist_ok=True)

COUNTRIES = ["印尼", "越南", "泰国", "菲律宾", "马来西亚", "巴西", "墨西哥", "沙特"]
CATEGORIES = ["3C数码", "服饰", "美妆", "家居", "母婴", "食品"]
PRICE_BANDS = ["低", "中", "高"]
CHANNELS = ["信息流", "搜索广告", "联盟", "自然流量", "社媒"]
DATES = pd.date_range("2026-05-06", "2026-06-04", freq="D")  # 最近 30 天

# 埋点：供给不足的目标格子
BAD_SUPPLY = {("3C数码", c) for c in ["印尼", "越南", "泰国"]}
# 埋点：红鲱鱼——转化低但供给健康
RED_HERRING = {("美妆", "巴西")}
# 埋点：外部需求飙升的格子（含一个"供给健康"的，用于演示"顺势加码"正向机会）
SURGE = BAD_SUPPLY | {("服饰", "巴西")}

# 体量基准（各维度热度）
country_pop = {c: rng.uniform(0.6, 1.5) for c in COUNTRIES}
cat_pop = {c: rng.uniform(0.7, 1.3) for c in CATEGORIES}
channel_pop = {c: rng.uniform(0.6, 1.3) for c in CHANNELS}
price_pop = {"低": 1.2, "中": 1.0, "高": 0.6}

# 健康基准的分步转化率
BASE = dict(expo_click=0.25, click_search=0.50, search_addcart=0.35, addcart_order=0.45)


def gen_behavior():
    rows = []
    for d in DATES:
        for ch in CHANNELS:
            for co in COUNTRIES:
                for cat in CATEGORIES:
                    for pb in PRICE_BANDS:
                        lam = (180 * country_pop[co] * cat_pop[cat]
                               * channel_pop[ch] * price_pop[pb])
                        exposure = int(rng.poisson(lam))
                        if exposure < 5:
                            continue

                        r_ec = BASE["expo_click"] * rng.uniform(0.85, 1.15)
                        r_cs = BASE["click_search"] * rng.uniform(0.85, 1.15)
                        r_sa = BASE["search_addcart"] * rng.uniform(0.85, 1.15)
                        r_ao = BASE["addcart_order"] * rng.uniform(0.85, 1.15)

                        # —— 埋点1：东南亚 3C —— 高意图，但加购→下单被供给拖垮
                        if (cat, co) in BAD_SUPPLY:
                            r_ec *= 1.15            # 点击更积极
                            r_sa *= 1.30            # 搜了更愿意加购（高意图）
                            r_ao = rng.uniform(0.14, 0.20)   # 但下单崩了
                        # —— 埋点2：巴西美妆 —— 转化低但供给正常（红鲱鱼）
                        elif (cat, co) in RED_HERRING:
                            r_ao = rng.uniform(0.20, 0.26)

                        click = int(exposure * min(r_ec, 0.95))
                        search = int(click * min(r_cs, 0.95))
                        addcart = int(search * min(r_sa, 0.95))
                        order = int(addcart * min(r_ao, 0.95))

                        rows.append(dict(
                            date=d.date(), channel=ch, country=co,
                            category=cat, price_band=pb,
                            exposure_uv=exposure, click_uv=click,
                            search_uv=search, addcart_uv=addcart, order_uv=order))
    return pd.DataFrame(rows)


def gen_supply():
    rows = []
    for d in DATES:
        for co in COUNTRIES:
            for cat in CATEGORIES:
                if (cat, co) in BAD_SUPPLY:
                    in_stock = rng.uniform(0.45, 0.62)
                    price_comp = rng.uniform(0.50, 0.65)
                    sku = int(rng.uniform(150, 400) * cat_pop[cat])
                    sell_through = rng.uniform(0.70, 0.92)   # 卖断货
                else:
                    in_stock = rng.uniform(0.90, 0.98)
                    price_comp = rng.uniform(0.80, 0.95)
                    sku = int(rng.uniform(800, 2000) * cat_pop[cat])
                    sell_through = rng.uniform(0.40, 0.60)
                rows.append(dict(
                    date=d.date(), country=co, category=cat,
                    sku_count=sku,
                    in_stock_rate=round(in_stock, 4),
                    oos_rate=round(1 - in_stock, 4),
                    price_competitiveness=round(price_comp, 4),
                    sell_through_rate=round(sell_through, 4)))
    return pd.DataFrame(rows)


def gen_acquisition(behavior):
    # 拉新成本：按 渠道×国家 汇总新客量并造 spend / CAC
    g = (behavior.groupby(["date", "channel", "country"])["exposure_uv"]
         .sum().reset_index().rename(columns={"exposure_uv": "new_users"}))
    base_cac = {ch: rng.uniform(3.0, 9.0) for ch in CHANNELS}
    cac = g["channel"].map(base_cac) * rng.uniform(0.85, 1.15, len(g))
    g["cac"] = cac.round(2)
    g["spend"] = (g["new_users"] * g["cac"]).round(2)
    return g[["date", "channel", "country", "new_users", "spend", "cac"]]


def gen_search_trend():
    """外部域①：搜索趋势（站内/外部搜索热度 + 环比）。"""
    rows = []
    for d in DATES:
        for co in COUNTRIES:
            for cat in CATEGORIES:
                if (cat, co) in SURGE:
                    idx = rng.uniform(120, 180)
                    wow = rng.uniform(0.80, 1.60)      # 环比飙升 +80%~+160%
                else:
                    idx = rng.uniform(80, 115)
                    wow = rng.uniform(-0.10, 0.25)
                rows.append(dict(date=d.date(), country=co, category=cat,
                                 search_index=round(idx, 1),
                                 wow_change=round(wow, 3)))
    return pd.DataFrame(rows)


def gen_events():
    """外部域②：大促/节日历。临近 618 大促（数据截止后第 14 天）。"""
    max_d = max(DATES).date()
    event_date = dt.date(2026, 6, 18)
    days = (event_date - max_d).days
    rows = [dict(country=co, upcoming_event="618大促",
                 event_date=event_date, days_to_event=days,
                 is_peak_window=days <= 21) for co in COUNTRIES]
    return pd.DataFrame(rows)


if __name__ == "__main__":
    behavior = gen_behavior()
    supply = gen_supply()
    acq = gen_acquisition(behavior)
    search = gen_search_trend()
    events = gen_events()

    behavior.to_csv(os.path.join(DATA, "behavior_funnel.csv"), index=False)
    supply.to_csv(os.path.join(DATA, "supply_depth.csv"), index=False)
    acq.to_csv(os.path.join(DATA, "acquisition.csv"), index=False)
    search.to_csv(os.path.join(DATA, "search_trend.csv"), index=False)
    events.to_csv(os.path.join(DATA, "event_calendar.csv"), index=False)

    print(f"behavior_funnel.csv : {len(behavior):>6} 行")
    print(f"supply_depth.csv    : {len(supply):>6} 行")
    print(f"acquisition.csv     : {len(acq):>6} 行")
    print(f"search_trend.csv    : {len(search):>6} 行  (外部域·搜索趋势)")
    print(f"event_calendar.csv  : {len(events):>6} 行  (外部域·大促日历)")
    print(f"已写入 {DATA}/")
