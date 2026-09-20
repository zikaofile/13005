# -*- coding: utf-8 -*-
"""生成《13005软件工程》Anki 知识库。

卡片设计（按用户要求）：
- 正面：D列知识点 + E列描述挖空版 + 以标签形式展示 A章节/B知识点要求/C章内小结
- 反面：E列完整描述（挖空处高亮）+ 挖空答案 + G列教材页码
- 真实 Anki 标签 = A章节 / B要求 / C小结（去空格），可按章节筛选复习
"""
import json
import re
import html as _html
import csv as _csv

import genanki

ROWS = json.load(open(r"F:\syncthing\考试\自考\13005软件工程\_build\rows.json", encoding="utf-8"))

# ---------------------------------------------------------------- 常量
OUT_APKG = r"F:\syncthing\考试\自考\13005软件工程\13005软件工程-大纲考点.apkg"
OUT_CSV = r"F:\syncthing\考试\自考\13005软件工程\13005软件工程-导入用.csv"
MAX_BLANKS = 3

# 软件工程术语词典（配合 D 列知识点名共同作为挖空候选）
TERMS = """
软件工程 软件危机 软件过程 过程模型 软件生命周期 生命周期 瀑布模型 原型模型 快速原型 螺旋模型 增量模型 迭代模型 演化模型
喷泉模型 统一过程 敏捷开发 敏捷 极限编程 结对编程 重构 测试驱动开发 持续集成 用户故事 冲刺 迭代
可行性 可行性分析 技术可行性 经济可行性 操作可行性 法律可行性 成本效益分析 风险分析
需求工程 软件需求 需求获取 需求分析 需求验证 需求管理 需求规格说明 需求规格说明书 需求文档
结构化 结构化分析 结构化设计 结构化方法 结构化语言 结构化英语
数据流图 数据字典 数据结构图 加工 数据流 数据存储 源点 终点 父图 子图 顶层图 分层 平衡 编号 细化
判定表 判定树 概要设计 详细设计 总体设计 体系结构设计 接口设计 数据设计 过程设计 模块化设计
模块 模块化 模块独立性 内聚 耦合 数据耦合 控制耦合 标记耦合 内容耦合 公共耦合 外部耦合 非直接耦合
功能内聚 顺序内聚 通信内聚 过程内聚 时间内聚 逻辑内聚 偶然内聚 信息内聚
扇入 扇出 深度 宽度 变换分析 变换型 事务分析 事务型 传入部分 传出部分 中心变换 主模块 控制模块
输入流 输出流 变换流 事务流 结构图 调用 矩形模块 菱形 环形 作用域 控制域
程序流程图 盒图 问题分析图 伪代码 基本控制结构 顺序结构 选择结构 循环结构
逐步求精 自顶向下 信息隐藏 抽象 局部化 高内聚低耦合
面向对象 对象 类 实例 封装 继承 多态 消息 方法 属性 操作 重载 覆盖 关联 聚合 组合 泛化 依赖 实现
参与者 用例 用例图 用例描述 基本流 备选流 扩展点 前置条件 后置条件
时序图 顺序图 协作图 状态图 活动图 类图 对象图 组件图 构件图 部署图 包图 统一建模语言 建模 模型
静态模型 动态模型 功能模型 对象模型 问题域 面向对象分析 面向对象设计 面向对象编程 面向对象测试
设计模式 体系结构 架构 分层架构 三层架构 构件 组件 子系统 边界类 控制类 实体类 分析类
可见性 公有 私有 受保护 多重性 状态 事件 触发 转换 泳道
移动应用 用户界面 用户体验 界面设计 手势 虚拟键盘 语音输入 传感器 响应式 自适应 适配 分辨率 屏幕尺寸
真机测试 模拟器 构件级设计 聚合 导航 人机交互 可用性 内容设计
软件测试 测试用例 测试方法 测试步骤 测试计划 单元测试 组装测试 集成测试 确认测试 系统测试 验收测试
回归测试 白盒测试 黑盒测试 穷举测试 选择测试 逻辑覆盖 语句覆盖 判定覆盖 分支覆盖 条件覆盖
条件组合覆盖 路径覆盖 判定/条件覆盖 基本路径测试 独立路径 环形复杂度 环路复杂度 圈复杂度 基路径
驱动模块 桩模块 驱动 桩 自底向上 增殖式 一次性组装 静态测试 动态测试 静态分析 人工测试
人工走查 人工审查 桌面检查 代码评审 代码走查 排错 调试 强行排错 回溯法 归纳法 演绎法 对分查找法
边界值分析 等价类划分 有效等价类 无效等价类 输入域 输出域 覆盖准则 冒烟测试
性能测试 压力测试 负载测试 安全性测试 兼容性测试 恢复测试 缺陷 故障 失效
软件维护 改正性维护 纠错性维护 适应性维护 完善性维护 预防性维护 可维护性 可理解性 可测试性
可修改性 可移植性 维护机构 维护申请 维护报告 维护过程 维护成本
软件项目管理 软件度量 度量 直接度量 间接度量 规模度量 代码行 功能点 面向规模 面向功能 面向人
生产率 质量度量 缺陷密度 风险评估 风险识别 风险估计 风险评价 风险驾驭 风险监控 项目风险 技术风险 商业风险
成本估算 估算 专家判断 算法模型 进度安排 甘特图 关键路径 里程碑 任务分解 并行性
软件团队 沟通 领导 激励 质量保证 质量审计 配置管理 变更控制 版本控制 基线 文档管理 软件工程标准
系统 用户 需求 功能 性能 设计 实现 错误 过程 数据 信息 开发 方法 工具 技术 阶段 任务 目标 原则 步骤
内容 特点 定义 结构 方式 标准 接口 资源 成本 时间 质量 项目 管理 控制 组织 计划 变更 配置 维护
""".split()

# ---------------------------------------------------------------- 文本清洗
CJK = r"\u4e00-\u9fff"
CJK_RE = re.compile("([%s])\\s+(?=[%s])" % (CJK, CJK))
DIGIT_RE = re.compile(r"(\d)\s+(?=\d)")


def clean_text(s):
    """轻量去 OCR 噪音：多空格折叠、中文字符间空格删除、数字间空格删除（前瞻式，可处理连续链）。"""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+", " ", s)
    s = CJK_RE.sub(r"\1", s)
    s = DIGIT_RE.sub(r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def norm_term(s):
    """术语规范化：去空白与尾部标点。"""
    s = re.sub(r"\s+", "", s)
    return s.rstrip("。.，,；;：:、）)")


def build_term_pattern(term):
    """允许字符间有 0~1 个空格/制表符（兼容 OCR 噪音），不跨换行。"""
    return re.compile("".join(re.escape(c) + r"[ \t]*" for c in term))


# 合法术语字符（中文/字母，不含数字与符号），用于过滤 D 列进词典
TERM_OK = re.compile(r"^[\u4e00-\u9fffA-Za-z]{2,12}$")

# D 列全部知识点名 → 通用词典（每行挖空时排除该行自身的 D）
all_d = set()
for r in ROWS:
    t = norm_term(r["knowledge"])
    if TERM_OK.match(t):
        all_d.add(t)
COMMON_DICT = set(TERMS) | all_d
COMMON_DICT = {t for t in COMMON_DICT if TERM_OK.match(t)}

# 括号内英文别名
ALIAS_RE = re.compile(r"[（(]\s*([A-Za-z][A-Za-z ._-]{1,40}?)\s*[）)]")
# 引号短语
QUOTE_RE = re.compile(r"[“\"]([^”\"]{2,24})[”\"]")


def alias_ok(text):
    return (len(text) >= 2 and not re.search(r"\d|=|,|，|、|…|\.\.", text)
            and text.count(" ") <= 1)


def quote_ok(text):
    return ("\n" not in text and len(text.strip()) >= 2
            and re.search(r"[\u4e00-\u9fffA-Za-z]", text))


def collect_candidates(e, own_d):
    """返回候选 [(start, end, answer_text, kind)]，按优先级排序。"""
    cands = []
    for m in ALIAS_RE.finditer(e):
        alias = m.group(1).strip()
        if alias_ok(alias):
            cands.append((m.start(1), m.end(1), alias, "alias"))
    for m in QUOTE_RE.finditer(e):
        q = m.group(1).strip()
        if quote_ok(q):
            cands.append((m.start(1), m.end(1), q, "quote"))
    # 全部词典术语（含本行 D）首次出现位置：短术语若被更长术语覆盖则丢弃，
    # 避免把"数据"挖进"数据元素"、把"排序"挖进"堆排序"这类半词错误。
    allm = []
    for t in sorted(COMMON_DICT, key=len):
        if len(t) < 2:
            continue
        m = build_term_pattern(t).search(e)
        if m:
            allm.append((m.start(0), m.end(0), t, t == own_d))
    kept = []
    for i, (s, e2, t, is_own) in enumerate(allm):
        if any(s2 <= s and e2_ >= e2 and len(t2) > len(t)
               for j, (s2, e2_, t2, _) in enumerate(allm) if j != i):
            continue
        # 跨词骑跨：与其他术语部分重叠（互不包含）时，较长者保留；等长时更靠前者保留。
        # 防止"调用"挖进"强调用户体验"、"过程模型"挖进"统一过程模型"这类切错词。
        if any(
            s2 < e2 and e2_ > s and not (s2 <= s and e2_ >= e2) and not (s <= s2 and e2 >= e2_)
            and (len(t2) > len(t) or (len(t2) == len(t) and s2 < s))
            for j, (s2, e2_, t2, _) in enumerate(allm) if j != i
        ):
            continue
        kept.append((s, e2, t, is_own))
    for s, e2, t, is_own in kept:
        if is_own:
            continue
        if any(s <= b and e2 >= a for a, b, _, _ in cands):
            continue
        cands.append((s, e2, t, "term"))
    # 按 (span长度降序, 优先级) 稳定排序，避免同词重复
    cands.sort(key=lambda c: (-(c[1] - c[0]), {"alias": 0, "quote": 1, "term": 2}[c[3]]))
    return cands


def pick_blanks(cands, e):
    """挑出互不重叠的至多 MAX_BLANKS 个挖空点。"""
    chosen = []
    for a, b, ans, kind in cands:
        if len(chosen) >= MAX_BLANKS:
            break
        if any(not (b <= x or a >= y) for x, y, _, _ in chosen):
            continue
        chosen.append((a, b, ans, kind))
    return chosen


def build_html(e, chosen):
    """生成：正面填空版 + 反面完整版(挖空处高亮) + 挖空答案列表。

    e: 清洗后的描述文本；chosen: [(start,end,answer,kind)]
    返回 (front_html, back_html, answers_line, has_blank)
    """
    if not e:
        return "", "", "", False

    # --- 正面：挖空处替换为 ______（按出现位置排序，答案顺序与之对应） ---
    spans = sorted(chosen, key=lambda c: c[0])
    parts = []
    pos = 0
    for a, b, ans, kind in spans:
        parts.append(_html.escape(e[pos:a]))
        parts.append('<span class="blank">______</span>')
        pos = b
    parts.append(_html.escape(e[pos:]))
    front = "".join(parts)

    # --- 反面：先固定挖空位置（保证每个答案在反面可见），再补其余出现处高亮 ---
    hit_spans = []
    for a, b, ans, kind in chosen:
        pat = build_term_pattern(ans) if kind in ("term",) else re.compile(re.escape(ans))
        for m in pat.finditer(e):
            hit_spans.append((m.start(), m.end(), ans))
    kept = [(a, b, ans) for a, b, ans, _ in spans]
    seeded = {(a, b) for a, b, _ in kept}
    extra = [h for h in hit_spans if (h[0], h[1]) not in seeded]
    extra.sort(key=lambda s: (-(s[1] - s[0]), s[0]))
    for a, b, ans in extra:
        if any(not (b <= x or a >= y) for x, y, _ in kept):
            continue
        kept.append((a, b, ans))
    kept.sort()
    parts = []
    pos = 0
    for a, b, ans in kept:
        parts.append(_html.escape(e[pos:a]))
        parts.append('<span class="hit">%s</span>' % _html.escape(ans))
        pos = b
    parts.append(_html.escape(e[pos:]))
    back = "".join(parts)

    answers = "；".join(a for _, _, a, _ in spans)
    return front, back, answers, bool(chosen)


# ---------------------------------------------------------------- Anki 模型
MODEL_ID = 1300517000001
DECK_ID = 1300517000002

css = """
.card { font-family: "Microsoft YaHei","PingFang SC","Noto Sans SC",sans-serif;
  font-size:17px; line-height:1.75; color:#222; }
.top { margin-bottom:12px; }
.chip { display:inline-block; font-size:12px; padding:2px 12px; border-radius:12px; margin:2px 6px 2px 0; }
.c1 { background:#e3f2fd; color:#1565c0; }
.c2 { background:#e8f5e9; color:#2e7d32; }
.c3 { background:#fff3e0; color:#e65100; }
h1 { font-size:20px; color:#0d47a1; border-bottom:2px solid #e3e3e3; padding-bottom:6px; margin:6px 0 12px; }
.q { background:#f4f7fb; padding:12px 14px; border-radius:8px; border-left:4px solid #1565c0; }
.blank { color:#c62828; font-weight:bold; text-decoration:underline dotted #c62828; }
.a { background:#f4fbf5; padding:12px 14px; border-radius:8px; border-left:4px solid #2e7d32; }
.hit { color:#c62828; font-weight:bold; background:#ffecec; padding:0 3px; border-radius:3px; }
.ansbox { background:#fff8e1; padding:6px 12px; border-radius:6px; color:#795548;
  font-size:14px; margin-top:10px; border:1px dashed #e6c66b; }
.ansbox b { color:#c62828; }
.pg { margin-top:10px; font-size:13px; color:#8a8a8a; }
.note { color:#9e9e9e; font-size:14px; font-style:italic; }
"""

FRONT_TPL = """
<div class="top">
  {{#章节}}<span class="chip c1">章节：{{章节}}</span>{{/章节}}
  {{#要求}}<span class="chip c2">{{要求}}</span>{{/要求}}
  {{#小结}}<span class="chip c3">{{小结}}</span>{{/小结}}
</div>
{{#知识点}}<h1>{{知识点}}</h1>{{/知识点}}
{{#描述填空}}<div class="q">{{描述填空}}</div>{{/描述填空}}
"""

BACK_TPL = """
<div class="top">
  {{#章节}}<span class="chip c1">章节：{{章节}}</span>{{/章节}}
  {{#要求}}<span class="chip c2">{{要求}}</span>{{/要求}}
  {{#小结}}<span class="chip c3">{{小结}}</span>{{/小结}}
</div>
{{#知识点}}<h1>{{知识点}}</h1>{{/知识点}}
{{#描述答案}}<div class="a">{{描述答案}}</div>{{/描述答案}}
{{^描述答案}}<div class="note">{{#知识点}}（大纲未提供该知识点描述，请查阅教材对应页码）{{/知识点}}{{^知识点}}（大纲未提供该题答案，请对照教材核对）{{/知识点}}</div>{{/描述答案}}
{{#挖空答案}}<div class="ansbox">挖空答案：<b>{{挖空答案}}</b></div>{{/挖空答案}}
{{#页码}}<div class="pg">教材页码：P{{页码}}</div>{{/页码}}
"""

model = genanki.Model(
    MODEL_ID,
    "13005大纲考点卡",
    fields=[
        {"name": "章节"},
        {"name": "要求"},
        {"name": "小结"},
        {"name": "知识点"},
        {"name": "描述填空"},
        {"name": "描述答案"},
        {"name": "挖空答案"},
        {"name": "页码"},
    ],
    templates=[
        {
            "name": "大纲考点卡",
            "qfmt": FRONT_TPL,
            "afmt": BACK_TPL,
        }
    ],
    css=css,
)

deck = genanki.Deck(DECK_ID, "13005软件工程")


def sanitize_tag(s):
    return re.sub(r"\s+", "", s)


def fix_knowledge_title(d, e):
    """针对本文件 D 列的轻微噪音修正：
    1) 行首"构化"→"结构化"（漏字）；2) 残缺标题"难点是"→从 E 的"本章难点是：……"中取主题。"""
    d = re.sub(r"^构化", "结构化", d)
    if d in ("难点是", "重点是", "本章难点", "本章重点"):
        m = re.search(r"本章(?:重点|难点)[^：:]{0,8}[:：]\s*([^。\n]+)", e)
        if m:
            d = norm_term(m.group(1))
    return d


# ---------------------------------------------------------------- 生成卡片
notes = []
stats = {"total": 0, "with_desc": 0, "no_desc": 0, "with_blank": 0,
         "no_blank": 0, "skipped_no_knowledge": 0, "blank_count": {}}

for r in ROWS:
    d = norm_term(r["knowledge"])
    if not d:
        if r["desc"].strip():
            stats["skipped_no_knowledge"] += 1
        continue
    stats["total"] += 1

    chapter = clean_text(r["chapter"])
    req = clean_text(r["requirement"])
    summ = clean_text(r["summary"])
    e = clean_text(r["desc"])
    page = r["page"]

    d = fix_knowledge_title(d, e)

    front_desc, back_desc, answers, has_blank = "", "", "", False
    if e:
        stats["with_desc"] += 1
        cands = collect_candidates(e, d)
        chosen = pick_blanks(cands, e)
        if not chosen:
            # 保底挖空：该行自身 D 术语首次出现
            p = build_term_pattern(d)
            m = p.search(e)
            if m:
                chosen = [(m.start(0), m.end(0), d, "term")]
        front_desc, back_desc, answers, has_blank = build_html(e, chosen)
        if has_blank:
            stats["with_blank"] += 1
            stats["blank_count"][len(chosen)] = stats["blank_count"].get(len(chosen), 0) + 1
        else:
            stats["no_blank"] += 1
    else:
        stats["no_desc"] += 1
        # 无描述：若 D 是长题干，转为"题卡"：正面显示题干
        if len(d) > 24:
            front_desc = norm_term(d)
            d = ""

    tags = [sanitize_tag(chapter), sanitize_tag(req), sanitize_tag(summ), "13005软件工程"]
    tags = [t for t in tags if t]

    page_str = str(int(page)) if isinstance(page, (int, float)) and page is not None else (str(page).strip() if page else "")

    note = genanki.Note(
        model=model,
        fields=[chapter, req, summ, d, front_desc, back_desc, answers, page_str],
        tags=tags,
        guid=genanki.guid_for(str(r["excel_row"]), d, e[:40]),
    )
    notes.append(note)

# 同一行号不会重复；guid 唯一性校验
guids = [n.guid for n in notes]
assert len(guids) == len(set(guids)), "guid 冲突"

for n in notes:
    deck.add_note(n)
pkg = genanki.Package(deck)
pkg.write_to_file(OUT_APKG)


def csv_chips(ch, req, summ):
    parts = []
    if ch:
        parts.append('<span class="chip c1">章节：%s</span>' % _html.escape(ch))
    if req:
        parts.append('<span class="chip c2">%s</span>' % _html.escape(req))
    if summ:
        parts.append('<span class="chip c3">%s</span>' % _html.escape(summ))
    return '<div class="top">%s</div>' % "".join(parts) if parts else ""


# ---------------------------------------------------------------- CSV 备份
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = _csv.writer(f, delimiter="\t")
    w.writerow(["Front", "Back", "Tags"])
    for n in notes:
        ch, req, summ, d, front_desc, back_desc, answers, page = n.fields
        head = csv_chips(ch, req, summ) + (("<h1>%s</h1>" % _html.escape(d)) if d else "")
        front_html = head
        if front_desc:
            front_html += '<div class="q">%s</div>' % front_desc
        back_html = head
        if back_desc:
            back_html += '<div class="a">%s</div>' % back_desc
        else:
            note = "（大纲未提供该题答案，请对照教材核对）" if not d else "（大纲未提供该知识点描述，请查阅教材对应页码）"
            back_html += '<div class="note">%s</div>' % note
        if answers:
            back_html += '<div class="ansbox">挖空答案：<b>%s</b></div>' % _html.escape(answers)
        if page:
            back_html += '<div class="pg">教材页码：P%s</div>' % _html.escape(page)
        w.writerow([front_html, back_html, " ".join(n.tags)])

print("卡片总数:", stats["total"])
print("含描述:", stats["with_desc"], "| 无描述(只有知识点):", stats["no_desc"])
print("含挖空:", stats["with_blank"], "| 无挖空:", stats["no_blank"])
print("挖空数分布:", stats["blank_count"])
print("跳过(有E无D):", stats["skipped_no_knowledge"])
print("已写出:", OUT_APKG)
print("已写出:", OUT_CSV)
