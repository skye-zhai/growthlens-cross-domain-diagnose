const fs = require("fs");
const path = require("path");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, AlignmentType, LevelFormat, HeadingLevel, BorderStyle,
  WidthType, ShadingType, PageNumber, Footer,
} = require("docx");

const HERE = __dirname;
const FONT = "Microsoft YaHei";
const CW = 9360; // US Letter, 1" margins

// 解析 **bold** 片段
function runs(t, base = {}) {
  return String(t).split("**").map((p, i) =>
    new TextRun({ text: p, bold: i % 2 === 1, ...base }));
}
const P = (t, opts = {}) => new Paragraph({
  children: runs(t), spacing: { after: 140, line: 330 }, ...opts,
});
const H1 = (t) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: runs(t) });
const BULLET = (t) => new Paragraph({
  numbering: { reference: "b", level: 0 }, children: runs(t),
  spacing: { after: 80, line: 330 },
});
const NUM = (t, ref) => new Paragraph({
  numbering: { reference: ref, level: 0 }, children: runs(t),
  spacing: { after: 80, line: 330 },
});
const SP = (h = 100) => new Paragraph({ children: [], spacing: { after: h } });
// 引导金句
const LEAD = (t) => new Paragraph({
  children: runs(t, { bold: true, size: 24 }),
  border: { left: { style: BorderStyle.SINGLE, size: 24, color: "C0392B", space: 12 } },
  indent: { left: 240 }, spacing: { before: 60, after: 200, line: 340 },
});

function cell(t, { w, head = false } = {}) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "BFBFBF" };
  return new TableCell({
    width: { size: w, type: WidthType.DXA },
    borders: { top: border, bottom: border, left: border, right: border },
    shading: head ? { fill: "EFEFEF", type: ShadingType.CLEAR } : undefined,
    margins: { top: 70, bottom: 70, left: 110, right: 110 },
    children: [new Paragraph({
      children: [new TextRun({ text: t, bold: head })], spacing: { after: 0, line: 300 },
    })],
  });
}
function table(headers, rows, widths) {
  const trs = [new TableRow({
    tableHeader: true,
    children: headers.map((h, i) => cell(h, { w: widths[i], head: true })),
  })];
  rows.forEach((r) => trs.push(new TableRow({ children: r.map((c, i) => cell(c, { w: widths[i] })) })));
  return new Table({ width: { size: CW, type: WidthType.DXA }, columnWidths: widths, rows: trs });
}

const img = fs.readFileSync(path.join(HERE, "output", "quadrant.png"));

const children = [];

children.push(new Paragraph({ heading: HeadingLevel.TITLE, children: runs("GrowthLens · 新客增长跨域诊断 Agent") }));
children.push(new Paragraph({
  children: runs("立项书（路演版）", { size: 26, color: "666666" }),
  spacing: { after: 200 },
}));
children.push(LEAD("一句话：把“新客转化为什么掉了”这个要五个团队吵一下午的问题，变成 agent 90 秒的诊断，和一份能直接领走的行动清单。"));
children.push(BULLET("赛道：AI Native"));
children.push(BULLET("形态：归因引擎（Python）+ Claude Code Skill"));
children.push(BULLET("团队：（待补）"));
children.push(SP());

children.push(H1("01｜每次大盘波动，都是一场罗生门"));
children.push(P("新客转化率掉了两个点。投放说渠道质量没变，产品说漏斗各步正常，品类说库存深度达标，物流说时效在 SLA 内——每个团队的数据都证明“不是我的问题”，但指标确实在掉。"));
children.push(P("会开了一下午，结论是“继续观察”。两周后复盘才发现：东南亚 3C 在大促前缺货，投放买来的高意图用户加购之后无货可买。等看清楚，窗口已经关了。"));
children.push(P("这不是某一次的故事。这是每次大盘波动的标准剧本。"));

children.push(H1("02｜卡点不在任何一个团队手里，在团队之间"));
children.push(P("为什么五个团队都没看见？因为真正的卡点，要把两个团队的数据放进同一张表才会显形："));
children.push(BULLET("投放的数据说：这批用户意图很高，加购率高于大盘；"));
children.push(BULLET("供给的数据说：这个品类库存偏薄，但单看不算异常；"));
children.push(BULLET("两张表各自“正常”，join 起来才是事故。"));
children.push(P("人不是不会做这个 join，是做不过来：品类 × 国家 × 渠道 × 价格带，几百个格子，每个格子要同时看 4–8 个域，还要叠加搜索热度、大促节奏这些外部变量。这超出任何人的工作记忆——但对程序，只是一次 join。"));
children.push(P("BI 已经把“查得快”做到了头。没人解决的是“看得全”。这就是 agent 该站的位置。"));

children.push(H1("03｜方案：一个锚点指标，四层架构，域可无限加"));
children.push(P("锚定「新客首单转化率」。选它不是因为它好算，是因为解释它必然跨域——渠道质量、站内体验、供给深度、价格竞争力都会动它，任何单一团队都无法独立解释。它是天然的跨域入口。"));
children.push(table(["层", "职责", "产物"], [
  ["语义层", "指标口径、维度定义、归因方法的单一事实来源", "semantic.yaml"],
  ["数据层", "每个域一张预聚合宽表，原始明细不出本地", "行为 / 供给 / 投放 / 搜索趋势 / 大促日历"],
  ["归因引擎", "跨域 join、基准对照、显著性检验、优先级排序，全部确定性计算", "结构化诊断 + 象限图"],
  ["表达层", "在引擎数字之上组织诊断叙事与行动建议", "Claude Code Skill"],
], [1500, 4660, 3200]));
children.push(SP());
children.push(P("关键设计一句话：**新增一个域 = 一张聚合宽表 + 一个查询函数**。今天是行为 × 供给 × 搜索 × 大促 4 个域，明天加物流、投放、竞品，框架不动。域越多，人越看不过来，这套系统越值钱。"));

children.push(H1("04｜现场演示：90 秒，从“为什么掉”到“怎么办”"));
children.push(P("路演现场实跑（MVP 已可运行，以下输出为构造数据实测）。输入一条指令 /growth-diagnose，agent 给出四层："));
children.push(P("**第一层，整体体检**——“新客首单转化率 1.46%。聚合视角最弱的步骤是曝光→点击，但这是陷阱：基线最低 ≠ 机会最大，真正可挽回的钱不在这一步。”"));
children.push(P("**第二层，定位真凶**——“泰国 3C：高意图加购 4,340 人，加购→下单只有 11.7%（品类健康基准 38%），缺货率 47%、价格竞争力 0.56。主因：供给。置信度 1.0。”"));
children.push(P("**第三层，外部交叉**——“该品类搜索热度环比 +121%，距 618 还有 14 天。需求在涨、窗口在关、承接能力缺失，三件事同时成立——这是 TOP1 紧急项。”"));
children.push(P("**第四层，行动清单**——补供给、跟价、暂停该格子的高成本投放，按 RICE 排序，每条带预期影响（TOP3 格子合计可挽回约 2,900 单）。"));
children.push(P("然后是演示的关键一刻。评委一定会问：“AI 瞎说怎么办？”我们主动演示反例：巴西美妆，转化率同样显著偏低，但引擎不报供给问题，置信度只给 0.36——因为它的供给是健康的。**引擎分得清“指标异常”和“异常是谁造成的”，这是纯漏斗工具做不到的一步。**"));
children.push(SP());
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new ImageRun({
    type: "png", data: img,
    transformation: { width: 580, height: 396 },
    altText: { title: "供需错配象限图", description: "新客增长供需错配象限图", name: "quadrant" },
  })],
}));
children.push(new Paragraph({
  alignment: AlignmentType.CENTER,
  children: [new TextRun({ text: "配图：供需错配象限图（横轴供给缺口、纵轴需求意图、气泡大小为优先级，三个红色大泡一眼锁定卡点）", size: 18, color: "808080" })],
  spacing: { after: 200 },
}));

children.push(H1("05｜凭什么可信：三道防线"));
children.push(NUM("**数字防线**：所有数字来自确定性 Python 计算，LLM 一个数都不编；", "na"));
children.push(NUM("**统计防线**：样本量门槛（n≥100）+ 分品类基准 z 检验 + 价格带混杂修正。48 个格子里只有 15 个过显著性关、11 个因混杂被降权——引擎宁可少报，不误报；", "na"));
children.push(NUM("**因果防线**：每条结论带置信度与验证设计（A/B 或增量测试）。我们交付的是“排好序的强假设”，不冒充因果真理。", "na"));

children.push(H1("06｜价值：三笔账"));
children.push(P("**效率账**：跨团队归因从 0.5–2 天降到分钟级。按每月 4–6 次归因，每月省 4–10 人天，且结论从“凭经验”变成“有统计把关、可复查”。"));
children.push(P("**机会账**：可挽回订单 = 高意图流量 ×（品类基准转化率 − 实际转化率），只统计置信度达标的格子。构造数据下 TOP3 约 2,900 单——此数字用于演示口径可行，业务收益以真实数据验证后的对比为准。"));
children.push(P("**资产账**：指标口径与归因方法论沉淀为结构化语义层（semantic.yaml），可审计、可复用。框架平移到复购、大促冷启动、品类增长，只需换一个锚点指标。"));

children.push(H1("07｜17 天计划"));
children.push(table(["时间", "目标", "验收标准"], [
  ["6/12–6/15", "第 1 个真实域数据接入", "真实数据上跑通完整诊断"],
  ["6/16–6/20", "第 2 个内部域接入，按真实数据调参", "诊断结论经业务方人工复核认可"],
  ["6/21–6/24", "外部域接真实源（搜索趋势 / 大促日历）", "输出至少一条“内外交叉”型结论"],
  ["6/25–6/28", "效果对比与交付", "归因耗时前后对比、演示视频、复用文档"],
], [1700, 4060, 3600]));
children.push(SP());
children.push(P("主要风险与应对：真实数据申请不齐（最大风险）→ 优先锁定最易获取的 2 个域，其余用构造数据演示扩展性并明确标注；归因可信度被挑战（必然被问）→ 统计防线 + 反例演示就是内置回答；内网模型限制 → 架构与模型解耦，明细不出本地，表达层可替换为内部模型。"));

children.push(H1("08｜收尾"));
children.push(P("我们不是在做“又一个 BI”。BI 回答“发生了什么”；这个 agent 回答“为什么、在哪、怎么办、值多少钱”。"));
children.push(LEAD("把五个团队的一下午，变成一个 agent 的 90 秒——这就是这个项目要证明的事。"));

const numLevel = (ref) => ({
  reference: ref,
  levels: [{
    level: 0, format: LevelFormat.DECIMAL, text: "%1.", alignment: AlignmentType.LEFT,
    style: { paragraph: { indent: { left: 600, hanging: 300 } } },
  }],
});

const doc = new Document({
  styles: {
    default: { document: { run: { font: FONT, size: 21 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 38, bold: true, font: FONT },
        paragraph: { spacing: { after: 80 } } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 27, bold: true, font: FONT },
        paragraph: { spacing: { before: 320, after: 150 }, outlineLevel: 0 } },
    ],
  },
  numbering: {
    config: [
      { reference: "b", levels: [{ level: 0, format: LevelFormat.BULLET, text: "•", alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 600, hanging: 300 } } } }] },
      numLevel("na"),
    ],
  },
  sections: [{
    properties: { page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } } },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [
            new TextRun({ text: "GrowthLens 立项书（路演版）· 第 ", size: 16, color: "999999" }),
            new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "999999" }),
            new TextRun({ text: " 页", size: 16, color: "999999" }),
          ],
        })],
      }),
    },
    children,
  }],
});

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(path.join(HERE, "立项表.docx"), buf);
  console.log("已生成 立项表.docx", buf.length, "bytes");
});
