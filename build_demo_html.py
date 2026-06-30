"""
生成自包含演示网页 submission/演示视频.html
- 10 个分镜，按旁白朗读完自动翻页（浏览器内置中文 TTS）
- 象限图以 base64 内嵌，单文件可移植
- 控制：开始按钮 / 空格暂停 / 左右翻页 / R 重播 / M 静音
用 QuickTime（⌘⇧5）录屏即可出 3-5 分钟成片。
"""
import os, base64, json

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "output", "quadrant.png")
OUT = os.path.join(HERE, "submission", "演示视频.html")

with open(IMG, "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

SCENES = [
    {"kind": "title",
     "title": "增长透视镜 GrowthLens",
     "sub": "新客增长 · 全链路跨域诊断 Agent　｜　赛道：AI Native",
     "narration": "新客转化率掉了两个点。投放说渠道没变，产品说漏斗正常，品类说库存达标，物流说时效达标。每个团队都证明不是我的问题，但指标确实在掉。这是每次大盘波动的标准剧本。今天这个 agent，要把这场要五个团队吵一下午的罗生门，变成九十秒的诊断。"},
    {"kind": "points",
     "title": "卡点不在任何一个团队手里，在团队之间",
     "items": ["投放的表：这批用户意图很高，加购率高于大盘",
               "供给的表：这个品类库存偏薄，但单看不算异常",
               "两张表各自正常，<b>join 起来才是事故</b>",
               "品类 × 国家 × 渠道 × 价格带 = 几百个格子，每格 4–8 个域",
               "对人脑是过载，对程序只是一次 join"],
     "narration": "卡点不在任何一个团队手里，而在团队之间。投放的表说这批用户意图很高，供给的表说这个品类库存偏薄。两张表各自正常，合起来才是事故。人不是不会做这个关联，是做不过来——品类乘国家乘渠道乘价格带，几百个格子，每格要同时看四到八个域。对人脑是过载，对程序只是一次关联。"},
    {"kind": "arch",
     "title": "四层架构 · 域可无限扩展",
     "rows": [["语义层", "指标口径 / 维度 / 归因方法的单一事实来源", "semantic.yaml"],
              ["数据层", "每个域一张预聚合宽表，原始明细不出本地", "天然合规"],
              ["归因引擎", "跨域 join · 基准 · 显著性 · 混杂守门 · RICE", "确定性计算"],
              ["表达层", "LLM 在数字之上写诊断，一个数都不编", "SKILL.md"]],
     "foot": "新增一个域 = 一张宽表 + 一个查询函数",
     "narration": "架构分四层。语义层是指标口径的单一事实来源；数据层每个域一张预聚合宽表，原始明细不出本地，天然合规；归因引擎做跨域关联、基准对照、显著性检验，全部确定性计算；表达层才是大模型，只在数字之上写诊断，一个数都不编。关键设计一句话：新增一个域，等于一张宽表加一个查询函数，域可以无限扩展。"},
    {"kind": "metric",
     "title": "① 整体体检（AARRR）",
     "big": "1.46%", "biglabel": "新客首单转化率（锚点指标）",
     "funnel": [("曝光→点击", "24.9%"), ("点击→搜索", "49.0%"), ("搜索→加购", "33.4%"), ("加购→下单", "36.0%")],
     "note": "最弱步骤「曝光→点击」是<b>陷阱</b>：基线最低 ≠ 机会最大。真机会在「加购→下单」。",
     "narration": "第一层，整体体检。新客首单转化率百分之一点四六。注意，聚合视角下最弱的步骤是曝光到点击，但这是个陷阱——基线最低不等于机会最大。真正可挽回的钱，在加购到下单这一步。"},
    {"kind": "culprit",
     "title": "② 定位真凶 · 头号增长杠杆",
     "cell": "泰国 × 3C数码",
     "kv": [("高意图加购", "4,340 人"), ("加购→下单", "11.7%（基准 38%）"),
            ("缺货率", "46.9%"), ("价格竞争力", "0.56"),
            ("主因", "补供给 + 调价"), ("供给归因强度", "100%")],
     "narration": "第二层，定位真凶。泰国 3C 数码，高意图新客加购四千三百四十人，但加购到下单只有百分之十一点七，而品类健康基准是百分之三十八。缺货率百分之四十七，价格竞争力零点五六。主因：供给。供给归因强度百分之百。"},
    {"kind": "points",
     "title": "③ 外部交叉 · 🔴紧急堵漏",
     "items": ["搜索热度环比 <b>+119%</b>（需求在涨）",
               "距 618 大促仅 <b>14 天</b>（窗口在关）",
               "缺货率 <b>47%</b>（承接能力缺失）",
               "三件事同时成立 → TOP1 紧急项",
               "四个域同时交叉，<b>人脑难以同时装下</b>"],
     "narration": "第三层，外部交叉。这个品类搜索热度环比上涨百分之一百一十九，距离六一八大促只剩十四天。需求在涨、窗口在关、承接能力缺失，三件事同时成立——这是最紧急的堵漏项。这种四个域同时交叉的判断，人脑很难同时装下。"},
    {"kind": "money",
     "title": "④ 用钱说话 · 单位经济（TOP3 合计）",
     "cards": [("~2,928", "可挽回首单"), ("~$351K", "可挽回 GMV"), ("~$18K", "止损白烧 CAC")],
     "narration": "第四层，用钱说话。前三个格子合计可挽回大约两千九百单，三十五万美金的成交额，还止损了大约一万八千美金被白白烧掉的拉新预算。堵住这个供给漏点，既挽回成交，又止损了投放。"},
    {"kind": "redherring",
     "title": "杀手锏 · 主动演示反例（红鲱鱼）",
     "cell": "巴西 × 美妆",
     "kv": [("加购→下单", "16.6%（同样偏低）"), ("缺货率", "5.8%（供给健康）"),
            ("供给归因强度", "0.36（被正确降权）"), ("主因判定", "非供给 → 换假设验证")],
     "note": "引擎分得清「指标异常」与「异常归谁」——纯漏斗工具做不到，宁可少报，绝不误报。",
     "narration": "评委一定会问，AI 瞎说怎么办？我们主动演示反例。巴西美妆，转化率同样显著偏低，但引擎不报供给问题，置信度只给零点三六——因为它的供给是健康的，缺货率只有百分之六。引擎分得清指标异常，和异常到底是谁造成的。这是纯漏斗工具做不到的一步，宁可少报，绝不误报。"},
    {"kind": "image",
     "title": "供需错配象限图 · 一眼定位",
     "narration": "把它画成象限图。横轴是供给缺口，纵轴是需求意图，气泡大小是优先级。右上角三个红色大泡，就是东南亚 3C，一眼锁定卡点。左侧那个绿点是巴西服饰：需求飙升但供给健康，是正向的顺势加码机会，不是漏点。"},
    {"kind": "outro",
     "title": "不是又一个 BI",
     "lines": ["三道防线：数字确定性计算 · 48 格仅 15 格过显著性 · 每条结论带验证设计",
               "可平移：复购 / 大促冷启动 / 品类增长 / 商家经营参谋",
               "BI 回答「发生了什么」，这个 agent 回答「为什么、在哪、怎么办、值多少钱」"],
     "lead": "把五个团队的一下午，变成一个 agent 的 90 秒。",
     "narration": "三道防线撑起可信：数字全部来自确定性计算；统计上四十八个格子只有十五个通过显著性检验；每条结论都带验证设计。这套框架不绑定这一个指标，可以平移到复购、大促冷启动、品类增长、商家经营参谋。我们不是在做又一个 BI。BI 回答发生了什么，这个 agent 回答为什么、在哪、怎么办、值多少钱。把五个团队的一下午，变成一个 agent 的九十秒——这就是这个项目要证明的事。"},
]

HTML = """<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<title>GrowthLens 演示</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
html,body{height:100%;background:#0d1117;font-family:"PingFang SC","Microsoft YaHei",sans-serif;color:#e6edf3;overflow:hidden}
#deck{position:fixed;inset:0;display:flex;flex-direction:column}
#stage{flex:1;display:flex;flex-direction:column;justify-content:center;align-items:center;padding:6vh 9vw;text-align:center}
h1{font-size:5.2vw;font-weight:800;letter-spacing:1px;line-height:1.15}
.sub{margin-top:2.5vh;font-size:1.7vw;color:#8b949e}
.kicker{color:#f85149;font-size:1.5vw;font-weight:700;margin-bottom:2.5vh;letter-spacing:2px}
h2{font-size:3vw;font-weight:800;margin-bottom:4vh}
ul{list-style:none;text-align:left;font-size:1.9vw;line-height:2.3}
li{margin:0.6vh 0;padding-left:1.6em;position:relative}
li:before{content:"▸";color:#f85149;position:absolute;left:0}
b{color:#ffd33d;font-weight:700}
table{border-collapse:collapse;font-size:1.7vw}
td{padding:1.4vh 2vw;border:1px solid #30363d;text-align:left}
td.k{color:#58a6ff;font-weight:700;white-space:nowrap}
td.tag{color:#7ee787}
.big{font-size:9vw;font-weight:800;color:#f85149;line-height:1}
.biglabel{font-size:1.6vw;color:#8b949e;margin-top:1vh}
.funnel{display:flex;gap:1.5vw;margin-top:4vh}
.fstep{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:2vh 2vw}
.fstep .v{font-size:2.6vw;font-weight:800;color:#58a6ff}
.fstep .l{font-size:1.2vw;color:#8b949e;margin-top:0.6vh}
.note{margin-top:4vh;font-size:1.6vw;color:#c9d1d9;max-width:70vw;line-height:1.7}
.cellname{font-size:3.4vw;font-weight:800;color:#ffd33d;margin-bottom:3vh}
.cards{display:flex;gap:2.5vw}
.card{background:#161b22;border:1px solid #30363d;border-radius:14px;padding:4vh 3vw}
.card .v{font-size:5vw;font-weight:800;color:#7ee787}
.card .l{font-size:1.4vw;color:#8b949e;margin-top:1.2vh}
img{max-width:78vw;max-height:62vh;border-radius:10px;box-shadow:0 0 40px rgba(0,0,0,.6)}
.lead{font-size:2.6vw;font-weight:800;color:#f85149;border-left:6px solid #f85149;padding-left:1.5vw;margin-top:4vh;text-align:left}
.olines{font-size:1.7vw;line-height:2.4;color:#c9d1d9;text-align:left}
#bar{height:5px;background:#f85149;width:0;transition:width .3s}
#subtitle{position:fixed;bottom:0;left:0;right:0;background:rgba(0,0,0,.78);padding:2.4vh 10vw;font-size:1.55vw;line-height:1.7;min-height:9vh;display:flex;align-items:center;justify-content:center;text-align:center}
#hud{position:fixed;top:2vh;right:2.5vw;font-size:1vw;color:#586069}
#start{position:fixed;inset:0;background:#0d1117;display:flex;flex-direction:column;justify-content:center;align-items:center;z-index:10;cursor:pointer}
#start h1{font-size:4vw}#start p{margin-top:3vh;color:#8b949e;font-size:1.5vw}
.btn{margin-top:5vh;background:#238636;color:#fff;border:none;padding:2.2vh 5vw;font-size:1.8vw;border-radius:10px;cursor:pointer;font-weight:700}
.hint{margin-top:3vh;color:#586069;font-size:1.1vw}
</style></head>
<body>
<div id="start">
  <h1>增长透视镜 GrowthLens</h1>
  <p>自动播放演示 · 中文配音 · 约 4 分钟</p>
  <button class="btn" onclick="begin()">▶ 开始播放</button>
  <div class="hint">空格=暂停/继续　←/→=翻页　R=重播　M=静音　｜　建议用 QuickTime（⌘⇧5）全屏录制</div>
</div>
<div id="deck">
  <div id="stage"></div>
  <div id="bar"></div>
</div>
<div id="subtitle"></div>
<div id="hud"></div>
<script>
const SCENES = __SCENES__;
const IMG = "data:image/png;base64,__B64__";
let i = -1, token = 0, paused = false, muted = false, voice = null;
const stage = document.getElementById('stage'), sub = document.getElementById('subtitle'),
      bar = document.getElementById('bar'), hud = document.getElementById('hud');

function pickVoice(){
  const vs = speechSynthesis.getVoices();
  voice = vs.find(v=>/zh[-_]?CN/i.test(v.lang)) || vs.find(v=>/zh/i.test(v.lang))
       || vs.find(v=>/Ting|Mei|Yu|Han/i.test(v.name)) || null;
}
speechSynthesis.onvoiceschanged = pickVoice; pickVoice();

function render(s){
  let h = '';
  if(s.kind==='title') h = `<h1>${s.title}</h1><div class="sub">${s.sub}</div>`;
  else if(s.kind==='points') h = `<h2>${s.title}</h2><ul>${s.items.map(x=>`<li>${x}</li>`).join('')}</ul>`;
  else if(s.kind==='arch'){h=`<h2>${s.title}</h2><table>${s.rows.map(r=>`<tr><td class="k">${r[0]}</td><td>${r[1]}</td><td class="tag">${r[2]}</td></tr>`).join('')}</table><div class="note"><b>${s.foot}</b></div>`;}
  else if(s.kind==='metric'){h=`<h2>${s.title}</h2><div class="big">${s.big}</div><div class="biglabel">${s.biglabel}</div><div class="funnel">${s.funnel.map(f=>`<div class="fstep"><div class="v">${f[1]}</div><div class="l">${f[0]}</div></div>`).join('')}</div><div class="note">${s.note}</div>`;}
  else if(s.kind==='culprit'||s.kind==='redherring'){h=`<div class="kicker">${s.title}</div><div class="cellname">${s.cell}</div><table>${s.kv.map(r=>`<tr><td class="k">${r[0]}</td><td>${r[1]}</td></tr>`).join('')}</table>${s.note?`<div class="note">${s.note}</div>`:''}`;}
  else if(s.kind==='money'){h=`<h2>${s.title}</h2><div class="cards">${s.cards.map(c=>`<div class="card"><div class="v">${c[0]}</div><div class="l">${c[1]}</div></div>`).join('')}</div>`;}
  else if(s.kind==='image') h=`<h2>${s.title}</h2><img src="${IMG}">`;
  else if(s.kind==='outro'){h=`<h2>${s.title}</h2><div class="olines">${s.lines.map(l=>'· '+l).join('<br>')}</div><div class="lead">${s.lead}</div>`;}
  stage.innerHTML = h;
}

function speak(text, done){
  const my = token;
  const chars = text.length;
  if(muted || !('speechSynthesis' in window)){ setTimeout(()=>{ if(my===token) done(); }, Math.max(3500, chars*170)); return; }
  speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang='zh-CN'; if(voice) u.voice=voice; u.rate=1.0; u.pitch=1.0;
  let fired=false; const fin=()=>{ if(!fired&&my===token){fired=true;clearInterval(ka);done();} };
  u.onend=fin; u.onerror=fin;
  const safety=setTimeout(fin, chars*230+5000);
  const ka=setInterval(()=>{ if(my!==token){clearInterval(ka);return;} if(!paused){speechSynthesis.resume();} }, 5000); // Chrome 长句续命
  speechSynthesis.speak(u);
}

function play(n){
  token++; i=n; const s=SCENES[i];
  bar.style.width = ((i+1)/SCENES.length*100)+'%';
  hud.textContent = `${i+1} / ${SCENES.length}`;
  render(s); sub.textContent = s.narration;
  speak(s.narration, ()=>{ if(i<SCENES.length-1) setTimeout(()=>{ if(!paused) play(i+1); }, 650); });
}
function begin(){ document.getElementById('start').style.display='none'; play(0); }
function go(n){ if(n<0||n>=SCENES.length) return; paused=false; speechSynthesis.cancel(); play(n); }

document.addEventListener('keydown', e=>{
  if(e.code==='Space'){ e.preventDefault(); paused=!paused; if(paused) speechSynthesis.pause(); else speechSynthesis.resume(); }
  else if(e.code==='ArrowRight') go(i+1);
  else if(e.code==='ArrowLeft') go(i-1);
  else if(e.key==='r'||e.key==='R') go(0);
  else if(e.key==='m'||e.key==='M'){ muted=!muted; speechSynthesis.cancel(); hud.textContent+=muted?' 🔇':''; }
});
</script>
</body></html>
"""

html = HTML.replace("__SCENES__", json.dumps(SCENES, ensure_ascii=False)).replace("__B64__", b64)
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"已生成 {OUT}  ({len(html):,} bytes, {len(SCENES)} 个分镜)")
