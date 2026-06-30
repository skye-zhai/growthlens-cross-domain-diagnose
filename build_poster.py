#!/usr/bin/env python3
"""生成自包含海报 submission/海报.html —— 浏览器打开后截图即可导出 PNG。
竖版 A 系比例(1240x1754, 约 A4@150dpi)，内嵌象限图。"""
import base64
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent
png_b64 = base64.b64encode((ROOT / "output" / "quadrant.png").read_bytes()).decode()

HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>GrowthLens 海报</title>
<style>
  :root{
    --ink:#0f1b2d; --sub:#5b6b82; --line:#e3e8f0;
    --brand:#1f5fff; --brand2:#7c4dff;
    --hot:#e8453c; --good:#16a34a; --bg:#f4f6fb;
  }
  *{box-sizing:border-box;margin:0;padding:0}
  body{background:var(--bg);font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;
       display:flex;justify-content:center;padding:32px;color:var(--ink)}
  .poster{
    width:1240px;height:1754px;background:#fff;position:relative;overflow:hidden;
    box-shadow:0 24px 80px rgba(15,27,45,.18);border-radius:20px;
    display:flex;flex-direction:column;
  }
  /* 顶部品牌条 */
  .head{
    background:linear-gradient(120deg,var(--brand) 0%,var(--brand2) 100%);
    color:#fff;padding:54px 64px 46px;position:relative;
  }
  .head .badge{display:inline-block;font-size:20px;letter-spacing:2px;font-weight:600;
    background:rgba(255,255,255,.18);padding:8px 18px;border-radius:999px;margin-bottom:22px}
  .head h1{font-size:74px;font-weight:800;letter-spacing:1px;line-height:1.05}
  .head h1 .en{font-size:42px;font-weight:600;opacity:.92;margin-left:6px}
  .head .tag{font-size:30px;font-weight:600;margin-top:18px;opacity:.97;line-height:1.45}
  .head .tag b{color:#ffe57a}
  /* 主体 */
  .body{flex:1;padding:36px 64px 0;display:flex;flex-direction:column;gap:24px}
  .lead{font-size:26px;line-height:1.6;color:var(--ink)}
  .lead b{color:var(--brand)}
  /* 多域输入带 */
  .domains{border:1px dashed #c7d2e8;border-radius:16px;padding:20px 22px;background:#fafbff}
  .domains .h{font-size:20px;font-weight:700;color:var(--brand);margin-bottom:14px;letter-spacing:.5px}
  .domains .h span{font-weight:500;color:var(--sub);font-size:18px}
  .chips{display:flex;flex-wrap:wrap;gap:10px}
  .chip{font-size:19px;padding:8px 16px;border-radius:999px;background:#eef2fb;color:#34507a;border:1px solid var(--line)}
  .chip.on{background:linear-gradient(120deg,var(--brand),var(--brand2));color:#fff;border:none;font-weight:600}
  .chip.ue{background:#eef9f1;color:var(--good);border:1px solid #bfe6cb;font-weight:600}
  .chip.more{background:#fff;color:var(--brand);border:1px dashed var(--brand);font-weight:600}
  .domains .why{font-size:19px;line-height:1.55;color:#36465c;margin-top:14px}
  .domains .why b{color:var(--hot)}
  /* 指标卡 */
  .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:18px}
  .kpi{background:var(--bg);border:1px solid var(--line);border-radius:16px;padding:22px 20px;text-align:center}
  .kpi .v{font-size:46px;font-weight:800;color:var(--brand);line-height:1}
  .kpi .v.hot{color:var(--hot)}
  .kpi .u{font-size:19px;color:var(--sub);margin-top:12px;line-height:1.35}
  /* 图 + 结论两栏 */
  .mid{display:grid;grid-template-columns:1.18fr 1fr;gap:30px;align-items:start}
  .chart{border:1px solid var(--line);border-radius:16px;overflow:hidden;background:#fff}
  .chart img{width:100%;display:block}
  .chart .cap{font-size:18px;color:var(--sub);padding:12px 16px;border-top:1px solid var(--line);line-height:1.4}
  .findings .f{padding:18px 20px;border-radius:14px;margin-bottom:16px;border:1px solid var(--line)}
  .findings .f.hot{background:#fdf0ef;border-color:#f6c9c5}
  .findings .f.good{background:#eef9f1;border-color:#bfe6cb}
  .findings .f .t{font-size:23px;font-weight:800;margin-bottom:8px}
  .findings .f.hot .t{color:var(--hot)}
  .findings .f.good .t{color:var(--good)}
  .findings .f p{font-size:19px;line-height:1.55;color:#36465c}
  .findings .f p b{color:var(--ink)}
  /* 三道防线 */
  .moat{background:#0f1b2d;border-radius:16px;padding:26px 30px;color:#dfe7f5}
  .moat h3{font-size:22px;color:#fff;margin-bottom:14px;letter-spacing:1px}
  .moat .row{display:grid;grid-template-columns:repeat(3,1fr);gap:22px}
  .moat .row div{font-size:19px;line-height:1.5}
  .moat .row b{color:#7fa8ff;display:block;font-size:20px;margin-bottom:6px}
  /* 底部 */
  .foot{padding:22px 64px 30px;display:flex;justify-content:space-between;align-items:center;
        border-top:1px solid var(--line);font-size:19px;color:var(--sub)}
  .foot .repro code{background:var(--bg);border:1px solid var(--line);border-radius:8px;
        padding:4px 10px;font-size:17px;color:#34507a}
  .foot .note{text-align:right;line-height:1.5}
  .foot .note b{color:var(--ink)}
</style>
</head>
<body>
<div class="poster">
  <div class="head">
    <span class="badge">AI Native ｜ 跨域归因引擎 + Claude Code Skill</span>
    <h1>增长透视镜<span class="en">GrowthLens</span></h1>
    <div class="tag">把"新客转化为什么掉了"——一个要五个团队吵一下午的问题，<br>变成 agent <b>90 秒</b>的诊断 + 一份能直接领走的行动清单。</div>
  </div>

  <div class="body">
    <div class="lead">
      锚定一个<b>没有单一团队 owns 的指标</b>(新客首单转化率)，让 agent 把
      <b>多域信号</b>在『品类 × 国家』上自动对齐，定位"高意图新客白白流失、
      且可补供给挽回"的最大增长杠杆。<b>域越多越有价值——人脑装不下的多维交叉，正是 AI 不可替代之处。</b>
    </div>

    <div class="domains">
      <div class="h">跨域输入 · 每个域 = 一张宽表 + 一个工具 <span>(蓝=已跑通跨域归因 4 域；绿=已跑通·供单位经济；灰=框架可扩展)</span></div>
      <div class="chips">
        <span class="chip on">站内行为漏斗</span>
        <span class="chip on">供给·库存·价格</span>
        <span class="chip on">搜索趋势</span>
        <span class="chip on">大促日历</span>
        <span class="chip ue">获取/CAC · 供单位经济</span>
        <span class="chip">物流时效</span>
        <span class="chip">渠道获取</span>
        <span class="chip">留存复购</span>
        <span class="chip">竞品动态</span>
        <span class="chip">客服/口碑</span>
        <span class="chip more">+ N 域可扩展</span>
      </div>
      <div class="why">一个『泰国×3C 缺货 47% × 搜索环比+121% × 距 618 仅 14 天 × 高意图加购崩盘』的结论，要<b>同时跨 4 个域、横扫几十个品类×国家格子</b>才能得出——这正是单一团队和人脑工作记忆做不到的判断。</div>
    </div>

    <div class="kpis">
      <div class="kpi"><div class="v">1.46%</div><div class="u">锚点指标<br>新客首单转化率</div></div>
      <div class="kpi"><div class="v hot">11.7%</div><div class="u">泰国×3C 加购→下单<br>(健康基准 38%)</div></div>
      <div class="kpi"><div class="v hot">47%</div><div class="u">缺货率<br>归因置信度 100%</div></div>
      <div class="kpi"><div class="v">$351K</div><div class="u">TOP3 可挽回 GMV<br>~2,928 单 / 止损 CAC $18K</div></div>
    </div>

    <div class="mid">
      <div class="chart">
        <img src="data:image/png;base64,__B64__" alt="供需错配象限图">
        <div class="cap">供需错配象限图：横轴=供给缺口，纵轴=需求意图，气泡大小=优先级。右上角红泡(东南亚 3C)一眼锁定卡点。</div>
      </div>
      <div class="findings">
        <div class="f hot">
          <div class="t">🔴 头号卡点 · 泰国×3C</div>
          <p>高意图加购 <b>4,340 人</b>，加购→下单仅 <b>11.7%</b>。主因=缺货 47% + 价格竞争力 0.56 → <b>供给问题，置信度 100%</b>。搜索环比 +119~125%、距 618 仅 14 天，正在丢大促红利。</p>
        </div>
        <div class="f good">
          <div class="t">🟢 红鲱鱼对照 · 巴西美妆</div>
          <p>转化同样低，但<b>供给健康</b>，引擎归因置信度只给 <b>0.36</b>、不报供给问题。<b>分得清"指标异常"和"异常是谁造成的"——这是看数工具做不到的一步。</b></p>
        </div>
      </div>
    </div>

    <div class="moat">
      <h3>凭什么可信 · 三道防线</h3>
      <div class="row">
        <div><b>数字防线</b>所有数字来自确定性 Python 计算，LLM 一个数都不编。</div>
        <div><b>统计防线</b>样本量门槛 n≥100 + 分品类基准 z 检验 + 价格带混杂修正。48 格仅 15 格过显著、11 格被降权。</div>
        <div><b>因果防线</b>每条结论带置信度与验证设计(A/B/增量)，交付排好序的强假设，不冒充因果真理。</div>
      </div>
    </div>
  </div>

  <div class="foot">
    <div class="repro">一键复现(固定种子 SEED=42)：<br><code>python analyze.py</code> &nbsp; <code>python chart.py</code> &nbsp; 或 Claude Code 内 <code>/growth-diagnose</code></div>
    <div class="note"><b>归因 0.5–2 天 → 分钟级</b><br>⚠️ 全部为演示用合成数据，不代表真实业务</div>
  </div>
</div>
</body>
</html>"""

out = ROOT / "submission" / "海报.html"
out.write_text(HTML.replace("__B64__", png_b64), encoding="utf-8")
print(f"wrote {out} ({out.stat().st_size//1024} KB)")
