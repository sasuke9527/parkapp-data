#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
place_data_tool.py —— 「去哪玩」数据工具：游泳池、图书馆、下水点、图书馆固定活动、学校假期活动
（Opus 2026-11-20 写；只用 Python 标准库。规则见 README-去哪玩数据格式与填写说明.md）

命令：
  selftest                         自检：确认工具和词表能用
  codes [--kind pool|library|swim] 列出设施代码
  add FILE                         从标准输入读一条记录（JSON），校验通过才追加到 FILE
  validate FILE [FILE ...]         校验数据文件（有错误时退出码为 1）；data/school_terms.json 也能校验
  stats FILE [FILE ...]            统计：每类几条、事实数、A 类覆盖

记录类型看文件放在哪：data/places/ 是去处，data/sessions/ 是固定活动，data/events/ 是假期活动；
也可以用 --type place|session|event 指定。
"""
import argparse
import csv
import json
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")
MMDD_RE = re.compile(r"^(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
URL_RE = re.compile(r"^https?://\S+$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE_RE = re.compile(r"(?:\+?61|\b0)[\s-]?\d(?:[\s-]?\d){7,}")

KINDS = ["pool", "library", "swim"]
SPOT_TYPES = ["beach", "ocean_pool", "harbour_pool", "river_lake"]
STATUSES = ["ok", "needs_check", "temporarily_closed", "seasonal_closed", "under_construction"]
SOURCE_TYPES = ["council", "library", "state_gov", "federal_gov", "open_data", "operator", "other"]
SESSION_TYPES = ["storytime", "rhyme_time", "toddler_time", "bilingual_storytime", "lego_club",
                 "craft", "stem", "other"]
LANGS = ["en", "zh", "ko", "ja", "hi", "es", "vi", "ar", "other"]
BOOKING = ["none", "required", "recommended"]
# 露营地的经营方：government（政府自己管）/ private（私人或连锁公司经营，用户要求 2026-11-22 起也收，但必须标出来）
OPERATOR_TYPES = ["government", "private"]
# 来源网站的版权/使用条款要求先获得许可（收费、放进销售产品、复制、商用……）的营地（用户要求 2026-11-22 起）：
# 只收名称和地点，不收设施等细节；facts 写 []，note_zh 用下面这句固定提示，App 里显示它并给「访问官网」按钮（official_url）。
DETAIL_POLICIES = ["official_only"]
NOTE_OFFICIAL_ONLY = "该来源有版权要求，本 App 只收录名称和地点，详细信息请访问官网。"
WEEKDAYS = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
DAY_WORDS = WEEKDAYS + ["daily", "weekdays", "weekends", "public_holiday"]
# 不能当来源的网站（和公园的一样）
BANNED_URL_PARTS = ["google.", "goo.gl", "g.page", "maps.apple.com", "facebook.com", "fb.com",
                    "instagram.com", "reddit.com", "xiaohongshu.com", "xhslink.com", "tiktok.com",
                    "tripadvisor.", "yelp."]
# 只能当报名链接、不能当事实来源的平台
BOOKING_ONLY_PARTS = ["eventbrite.", "humanitix.", "trybooking.", "ticketek.", "ticketmaster."]
GREATER_SYDNEY_BOX = (-34.45, -32.95, 149.95, 151.70)
# 露营地（Opus 2026-11-22）：放在 data/camps/，词表是 camp_codes.csv，批次是 camp_batches.csv，规则见 RULES-CAMP.md。
# 和泳池、图书馆分开放：打包、发布脚本不读 data/camps/，所以已经上架的 App 不受影响。
CAMP_BOX = (-37.60, -28.00, 140.90, 153.70)      # 新州范围（2026-11-22 起也收远处的 NPWS 营地），只用来提醒坐标写反

MAX_EV = 120
MAX_NOTE = 80
MAX_TEXT = 120
MAX_TITLE = 100

PLACE_REQUIRED = ["id", "kind", "name", "council", "suburb", "sources", "facts", "checked", "status"]
PLACE_OPTIONAL = ["address", "lat", "lon", "spot_type", "operator", "beachwatch", "hours", "season",
                  "note_zh", "aka"]
SESSION_REQUIRED = ["id", "place", "title", "type", "weekday", "start", "sources", "checked"]
SESSION_OPTIONAL = ["end", "age_min_months", "age_max_months", "language", "term_only", "booking",
                    "cost", "valid_from", "valid_to", "note_zh"]
CAMP_REQUIRED = ["id", "kind", "name", "area", "sources", "facts", "checked", "status"]
CAMP_OPTIONAL = ["park", "suburb", "address", "lat", "lon", "operator", "operator_type", "booking", "booking_url",
                 "season", "note_zh", "aka", "detail_policy", "official_url"]
EVENT_REQUIRED = ["id", "title", "council", "dates", "sources", "checked"]
EVENT_OPTIONAL = ["place", "venue", "suburb", "age_min", "age_max", "cost", "booking", "booking_url",
                  "holiday", "note_zh"]


CAMP_CODES = {}     # camp_codes.csv，main() 里读

# ---------------------------------------------------------------- 词表

def load_codes(path=None):
    path = Path(path) if path else HERE / "place_codes.csv"
    codes = {}
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            code = (row.get("code") or "").strip()
            if not code:
                continue
            t = row["type"].strip()
            allowed = [v for v in (row.get("allowed") or "").split("|") if v]
            codes[code] = {
                "kinds": [k for k in row["kinds"].split("|") if k],
                "type": t,
                "allowed": allowed,
                "priority": row["priority"].strip(),
                "name_zh": row["name_zh"].strip(),
                "name_en": row["name_en"].strip(),
                "judge_zh": (row.get("judge_zh") or "").strip(),
            }
    return codes


# ---------------------------------------------------------------- 校验

class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []

    def err(self, where, msg):
        self.errors.append(f"{where}：{msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}：{msg}")


def check_value(spec, v):
    t = spec["type"]
    opts = " / ".join(spec["allowed"])
    if isinstance(v, bool):
        return '不要用 true / false，按类型写（如 "yes" / "no"）'
    if t == "yes_no":
        return None if v in ("yes", "no") else '只能写 "yes" 或 "no"'
    if t == "level3":
        return None if v in spec["allowed"] else f"只能写 {opts}"
    if t == "count":
        if isinstance(v, int):
            return None if v >= 0 else "数量不能是负数"
        return None if v in ("yes", "no") else '写整数，或 "yes" / "no"'
    if t == "multi_enum":
        if not isinstance(v, list) or not v:
            return f"写成列表，可选 {opts}"
        bad = [x for x in v if x not in spec["allowed"]]
        return f"这些值不认识：{bad}，可选 {opts}" if bad else None
    if t == "text":
        if not isinstance(v, str) or not v.strip():
            return "写一段短文字"
        return None if len(v) <= MAX_TEXT else f"太长了（最多 {MAX_TEXT} 个字符）"
    return f"词表里的类型 {t} 不认识"


def private_info(text):
    """文字里有没有邮箱、电话（不记联系人信息）"""
    if not isinstance(text, str):
        return False
    return bool(EMAIL_RE.search(text) or PHONE_RE.search(text))


def check_url(rep, where, url, booking_ok=False):
    if not isinstance(url, str) or not URL_RE.match(url):
        rep.err(where, f"链接不对：{url!r}")
        return
    low = url.lower()
    if any(p in low for p in BANNED_URL_PARTS):
        rep.err(where, f"这个网站不能用：{url}")
    if not booking_ok and any(p in low for p in BOOKING_ONLY_PARTS):
        rep.err(where, f"报名平台只能当报名链接（booking_url），不能当来源：{url}")
    if "example" in low:
        rep.err(where, "示例链接不能放进数据")


def check_sources(rep, where, sources):
    if not isinstance(sources, list) or not sources:
        rep.err(where, "sources 至少要有一个")
        return
    for i, s in enumerate(sources):
        w = f"{where} 来源 {i}"
        if not isinstance(s, dict) or set(s) - {"type", "url"}:
            rep.err(w, '每个来源写成 {"type": ..., "url": ...}')
            continue
        if s.get("type") not in SOURCE_TYPES:
            rep.err(w, f"type 只能是 {' / '.join(SOURCE_TYPES)}")
        check_url(rep, w, s.get("url"))


def check_date(rep, where, value, field, today):
    if not isinstance(value, str) or not DATE_RE.match(value):
        rep.err(where, f"{field} 要写成 YYYY-MM-DD")
        return False
    try:
        d = date.fromisoformat(value)
    except ValueError:
        rep.err(where, f"{field} 不是真实的日期：{value}")
        return False
    if field == "checked" and d > today:
        rep.err(where, "checked 不能是以后的日期")
    return True


def check_common(rep, where, rec, required, optional, today):
    for k in required:
        if k not in rec:
            rep.err(where, f"缺字段 {k}")
    unknown = set(rec) - set(required) - set(optional)
    if unknown:
        rep.err(where, f"不认识的字段：{sorted(unknown)}")
    if "id" in rec and (not isinstance(rec["id"], str) or "example" in rec["id"]):
        rep.err(where, "id 要写，而且不能用示例 id")
    if "checked" in rec:
        check_date(rep, where, rec["checked"], "checked", today)
    note = rec.get("note_zh")
    if note is not None and (not isinstance(note, str) or len(note) > MAX_NOTE):
        rep.err(where, f"note_zh 最多 {MAX_NOTE} 个字符")
    for k, v in rec.items():
        if k in ("sources", "booking_url", "official_url"):
            continue
        texts = [v] if isinstance(v, str) else []
        if k == "facts" and isinstance(v, list):
            texts = [f.get("ev") for f in v if isinstance(f, dict)] + [f.get("value") for f in v if isinstance(f, dict)]
        if any(private_info(t) for t in texts):
            rep.err(where, f"{k} 里像是有邮箱或电话；不记联系人信息")
    if "sources" in rec:
        check_sources(rep, where, rec["sources"])


def day_spec_ok(spec):
    if not isinstance(spec, str) or not spec:
        return False
    for token in spec.split(","):
        token = token.strip()
        parts = token.split("-")
        if len(parts) == 2:
            if parts[0] not in WEEKDAYS or parts[1] not in WEEKDAYS:
                return False
        elif token not in DAY_WORDS:
            return False
    return True


def validate_place(rec, codes, rep, today, line, camp=False):
    """camp=True：露营地（data/camps/）。字段少一些：没有 hours，council 换成 area（camp_batches.csv 里的 slug）。"""
    where = f"第 {line} 行 {rec.get('id', '?')}"
    if camp:
        check_common(rep, where, rec, CAMP_REQUIRED, CAMP_OPTIONAL, today)
    else:
        check_common(rep, where, rec, PLACE_REQUIRED, PLACE_OPTIONAL, today)
    kind = rec.get("kind")
    if camp:
        if kind != "camp":
            rep.err(where, 'data/camps/ 里的 kind 只能是 "camp"')
            return
    elif kind not in KINDS:
        rep.err(where, f"kind 只能是 {' / '.join(KINDS)}" + ("（露营地放 data/camps/）" if kind == "camp" else ""))
        return
    council = rec.get("area" if camp else "council")
    if not isinstance(council, str) or not SLUG_RE.match(council):
        rep.err(where, "area 写 camp_batches.csv 里的 slug" if camp else "council 写 councils.csv 里的 slug")
    if camp:
        for k in ("park", "suburb", "address", "operator"):
            if k in rec and (not isinstance(rec[k], str) or not rec[k].strip()):
                rep.err(where, f"{k} 写文字；页面没写就不写这个字段")
        if "booking" in rec and rec["booking"] not in BOOKING:
            rep.err(where, f"booking 只能是 {' / '.join(BOOKING)}")
        if "operator_type" in rec and rec["operator_type"] not in OPERATOR_TYPES:
            rep.err(where, f"operator_type 只能是 {' / '.join(OPERATOR_TYPES)}")
        if rec.get("operator_type") == "private" and not rec.get("operator"):
            rep.err(where, "非政府经营（operator_type=private）要写 operator：官网上的经营方名字")
        if "booking_url" in rec:
            check_url(rep, where, rec["booking_url"], booking_ok=True)
        if "detail_policy" in rec:
            if rec["detail_policy"] not in DETAIL_POLICIES:
                rep.err(where, f"detail_policy 只能是 {' / '.join(DETAIL_POLICIES)}")
            else:
                if "official_url" not in rec:
                    rep.err(where, "detail_policy=official_only 要写 official_url：官网上这个营地的页面")
                if rec.get("facts"):
                    rep.err(where, "detail_policy=official_only 的营地只收名称和地点：facts 写 []")
                for k in ("booking", "booking_url", "season"):
                    if k in rec:
                        rep.err(where, f"detail_policy=official_only 不写 {k}（细节请访问官网）")
                if rec.get("note_zh") != NOTE_OFFICIAL_ONLY:
                    rep.err(where, f"detail_policy=official_only 的 note_zh 要用固定提示语：{NOTE_OFFICIAL_ONLY}")
        elif "official_url" in rec:
            rep.err(where, "official_url 只和 detail_policy 一起用")
        if "official_url" in rec:
            check_url(rep, where, rec["official_url"])
    rid = rec.get("id")
    if isinstance(rid, str) and isinstance(council, str):
        prefix = f"au-nsw-{council}-{kind}-"
        if not rid.startswith(prefix) or not SLUG_RE.match(rid[len(prefix):] or "x-"):
            rep.err(where, f"id 要写成 {prefix}<名字>（只用小写英文、数字、连字符）")
    if not isinstance(rec.get("name"), str) or not rec.get("name", "").strip():
        rep.err(where, "name 写官网上的英文名")
    if rec.get("status") not in STATUSES:
        rep.err(where, f"status 只能是 {' / '.join(STATUSES)}")
    lat, lon = rec.get("lat"), rec.get("lon")
    if (lat is None) != (lon is None):
        rep.err(where, "lat 和 lon 要么都写，要么都是 null")
    elif lat is not None:
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):
            rep.err(where, "lat / lon 写数字")
        else:
            a, b, c, d = CAMP_BOX if camp else GREATER_SYDNEY_BOX
            if not (a <= lat <= b and c <= lon <= d):
                rep.warn(where, "坐标不在悉尼周边范围里，看看是不是写反了" if camp else "坐标不在大悉尼范围里，看看是不是写反了")
    if camp:
        pass
    elif kind == "swim":
        if rec.get("spot_type") not in SPOT_TYPES:
            rep.err(where, f"下水点要写 spot_type：{' / '.join(SPOT_TYPES)}")
    else:
        for k in ("spot_type", "beachwatch"):
            if k in rec:
                rep.err(where, f"{k} 只有下水点（kind=swim）才写")
    if "beachwatch" in rec and (not isinstance(rec["beachwatch"], str) or not rec["beachwatch"].strip()):
        rep.err(where, "beachwatch 写 Beachwatch 上这个游泳点的名字")
    hours = rec.get("hours")
    if hours is not None:
        if not isinstance(hours, list) or not hours:
            rep.err(where, "hours 写成列表；不知道就不写")
        else:
            for i, h in enumerate(hours):
                w = f"{where} 开放时间 {i}"
                if not isinstance(h, dict) or set(h) - {"days", "open", "close", "closed"}:
                    rep.err(w, '写成 {"days": "mon-fri", "open": "05:30", "close": "20:00"}，或 {"days": ..., "closed": true}')
                    continue
                if not day_spec_ok(h.get("days")):
                    rep.err(w, "days 写 mon-fri、sat,sun、daily、weekdays、weekends 或 public_holiday")
                if h.get("closed") is True:
                    if "open" in h or "close" in h:
                        rep.err(w, "关门的那条不写 open / close")
                else:
                    o, c = h.get("open"), h.get("close")
                    if not (isinstance(o, str) and TIME_RE.match(o) and isinstance(c, str) and TIME_RE.match(c)):
                        rep.err(w, "open / close 写 24 小时制 HH:MM")
                    elif o >= c:
                        rep.err(w, "close 要晚于 open（不收过夜的时间）")
    season = rec.get("season")
    if season is not None:
        if not isinstance(season, dict) or set(season) - {"from", "to", "ev"} or not all(
                isinstance(season.get(k), str) and MMDD_RE.match(season.get(k)) for k in ("from", "to")):
            rep.err(where, 'season 写成 {"from": "09-01", "to": "04-30"}（月-日），可以加 ev')
    facts = rec.get("facts")
    if not isinstance(facts, list):
        rep.err(where, "facts 写成列表；什么都没查到写 []")
        return
    seen = set()
    for i, f in enumerate(facts):
        w = f"{where} 事实 {i}"
        if not isinstance(f, dict) or set(f) - {"code", "value", "ev", "src", "conf"}:
            rep.err(w, '写成 {"code": ..., "value": ...}，可以加 ev / src / conf')
            continue
        code = f.get("code")
        spec = codes.get(code)
        if not spec:
            rep.err(w, f"设施代码不认识：{code}")
            continue
        if kind not in spec["kinds"]:
            rep.err(w, f"{code} 不用在这一类（{kind}）上")
        if code in seen:
            rep.err(w, f"{code} 写了两次")
        seen.add(code)
        problem = check_value(spec, f.get("value"))
        if problem:
            rep.err(w, f"{code}：{problem}")
        ev = f.get("ev")
        if ev is not None and (not isinstance(ev, str) or len(ev) > MAX_EV):
            rep.err(w, f"ev 最多 {MAX_EV} 个字符，照页面原话摘一小段")
        if "src" in f and (not isinstance(f["src"], int) or not 0 <= f["src"] < len(rec.get("sources") or [])):
            rep.err(w, "src 是 sources 里的序号，从 0 数")
        if "conf" in f and f["conf"] not in ("high", "medium", "low"):
            rep.err(w, "conf 只能是 high / medium / low")


def validate_session(rec, rep, today, line):
    where = f"第 {line} 行 {rec.get('id', '?')}"
    check_common(rep, where, rec, SESSION_REQUIRED, SESSION_OPTIONAL, today)
    place = rec.get("place")
    if not isinstance(place, str) or "-library-" not in place:
        rep.err(where, "place 写图书馆的 id（au-nsw-<council>-library-<名字>）")
    elif isinstance(rec.get("id"), str) and not rec["id"].startswith(place + "-"):
        rep.err(where, "id 写成 <图书馆 id>-<活动简称>-<星期>，例 …-library-hornsby-rhyme-time-tue")
    title = rec.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > MAX_TITLE:
        rep.err(where, f"title 写官网上的活动名（最多 {MAX_TITLE} 个字符）")
    if rec.get("type") not in SESSION_TYPES:
        rep.err(where, f"type 只能是 {' / '.join(SESSION_TYPES)}")
    if rec.get("weekday") not in WEEKDAYS:
        rep.err(where, "weekday 写 mon / tue / wed / thu / fri / sat / sun；一周几次就拆成几条")
    for k in ("start", "end"):
        v = rec.get(k)
        if v is not None and (not isinstance(v, str) or not TIME_RE.match(v)):
            rep.err(where, f"{k} 写 24 小时制 HH:MM")
    if isinstance(rec.get("start"), str) and isinstance(rec.get("end"), str) and rec["end"] <= rec["start"]:
        rep.err(where, "end 要晚于 start")
    check_ages(rep, where, rec, "age_min_months", "age_max_months")
    lang = rec.get("language")
    if lang is not None:
        parts = lang.split("+") if isinstance(lang, str) else []
        if not parts or any(p not in LANGS for p in parts):
            rep.err(where, f"language 写 {' / '.join(LANGS)}，双语写 en+zh")
    if "term_only" in rec and not isinstance(rec["term_only"], bool):
        rep.err(where, "term_only 写 true / false（来源说「学期内」才写 true）")
    if "booking" in rec and rec["booking"] not in BOOKING:
        rep.err(where, f"booking 只能是 {' / '.join(BOOKING)}")
    check_cost(rep, where, rec.get("cost"))
    vf, vt = rec.get("valid_from"), rec.get("valid_to")
    ok_f = vf is None or check_date(rep, where, vf, "valid_from", today)
    ok_t = vt is None or check_date(rep, where, vt, "valid_to", today)
    if vf and vt and ok_f and ok_t and vf > vt:
        rep.err(where, "valid_from 不能晚于 valid_to")


def validate_event(rec, rep, today, line):
    where = f"第 {line} 行 {rec.get('id', '?')}"
    check_common(rep, where, rec, EVENT_REQUIRED, EVENT_OPTIONAL, today)
    rid, council = rec.get("id"), rec.get("council")
    if isinstance(rid, str) and isinstance(council, str) and not rid.startswith(f"au-nsw-{council}-event-"):
        rep.err(where, f"id 写成 au-nsw-{council}-event-<活动简称>-<第一天日期>")
    title = rec.get("title")
    if not isinstance(title, str) or not title.strip() or len(title) > MAX_TITLE:
        rep.err(where, f"title 写官网上的活动名（最多 {MAX_TITLE} 个字符）")
    if not rec.get("place") and not rec.get("venue"):
        rep.err(where, "place（去处的 id）和 venue（地点名）至少写一个")
    dates = rec.get("dates")
    if not isinstance(dates, list) or not dates:
        rep.err(where, '写 dates：[{"date": "YYYY-MM-DD", "start": "10:00", "end": "12:00"}]，一天一条')
    else:
        for i, d in enumerate(dates):
            w = f"{where} 日期 {i}"
            if not isinstance(d, dict) or set(d) - {"date", "start", "end"}:
                rep.err(w, '写成 {"date": ..., "start": ..., "end": ...}')
                continue
            check_date(rep, w, d.get("date"), "date", today)
            for k in ("start", "end"):
                v = d.get(k)
                if v is not None and (not isinstance(v, str) or not TIME_RE.match(v)):
                    rep.err(w, f"{k} 写 24 小时制 HH:MM")
    check_ages(rep, where, rec, "age_min", "age_max")
    if "booking" in rec and rec["booking"] not in BOOKING:
        rep.err(where, f"booking 只能是 {' / '.join(BOOKING)}")
    if "booking_url" in rec:
        check_url(rep, where, rec["booking_url"], booking_ok=True)
    check_cost(rep, where, rec.get("cost"))


def check_ages(rep, where, rec, lo_key, hi_key):
    lo, hi = rec.get(lo_key), rec.get(hi_key)
    for k, v in ((lo_key, lo), (hi_key, hi)):
        if v is not None and (not isinstance(v, int) or isinstance(v, bool) or v < 0):
            rep.err(where, f"{k} 写整数")
    if isinstance(lo, int) and isinstance(hi, int) and lo > hi:
        rep.err(where, f"{lo_key} 不能大于 {hi_key}")


def check_cost(rep, where, cost):
    if cost is None:
        return
    if not isinstance(cost, str) or not cost.strip() or len(cost) > 40:
        rep.err(where, 'cost 写 "free" 或照来源写的价钱（最多 40 个字符）')


def validate_terms(doc):
    """data/school_terms.json：返回 (按开始日期排好的学期, 错误列表)。打包脚本也用这个。"""
    if not isinstance(doc, dict):
        return [], ['要写成 {"source": ..., "terms": [...]}']
    errors = []
    unknown = set(doc) - {"source", "terms"}
    if unknown:
        errors.append(f"不认识的字段：{sorted(unknown)}")
    source = doc.get("source")
    if not isinstance(source, str) or not URL_RE.match(source) or "education.nsw.gov.au" not in source:
        errors.append("source 要写 NSW 教育部（education.nsw.gov.au）的学期日期页面")
    raw = doc.get("terms")
    if not isinstance(raw, list) or not raw:
        errors.append("terms 写成列表，至少一个学期")
        raw = []
    terms = []
    for i, t in enumerate(raw):
        ok = (isinstance(t, dict) and not set(t) - {"year", "term", "start", "end"}
              and isinstance(t.get("year"), int) and not isinstance(t.get("year"), bool)
              and t.get("term") in (1, 2, 3, 4) and not isinstance(t.get("term"), bool)
              and all(isinstance(t.get(k), str) and DATE_RE.match(t[k]) for k in ("start", "end")))
        if ok:
            try:
                date.fromisoformat(t["start"])
                date.fromisoformat(t["end"])
            except ValueError:
                ok = False
        if not ok or t["start"] > t["end"]:
            errors.append(f'第 {i} 个学期：写成 {{"year": 2027, "term": 1, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}}，start 不能晚于 end')
            continue
        if not t["start"].startswith(f'{t["year"]}-'):
            errors.append(f"第 {i} 个学期：start 的年份和 year 对不上")
        terms.append({"year": t["year"], "term": t["term"], "start": t["start"], "end": t["end"]})
    terms.sort(key=lambda x: x["start"])
    for a, b in zip(terms, terms[1:]):
        if b["start"] <= a["end"]:
            errors.append(f"{a['year']} 第 {a['term']} 学期和下一个学期日期重叠")
    return terms, errors


def record_type(path, override=None):
    if override:
        return override
    parts = Path(path).parts
    if "camps" in parts:
        return "camp"
    if "sessions" in parts:
        return "session"
    if "events" in parts:
        return "event"
    return "place"


def validate_records(records, rtype, codes, today=None):
    """records: [(行号, dict)]。返回 Report。"""
    today = today or date.today()
    rep = Report()
    ids = Counter(r.get("id") for _, r in records if isinstance(r, dict))
    for line, rec in records:
        if not isinstance(rec, dict):
            rep.err(f"第 {line} 行", "每行要是一个 JSON 对象")
            continue
        if rtype == "place":
            validate_place(rec, codes, rep, today, line)
        elif rtype == "camp":
            validate_place(rec, CAMP_CODES, rep, today, line, camp=True)
        elif rtype == "session":
            validate_session(rec, rep, today, line)
        else:
            validate_event(rec, rep, today, line)
    for rid, n in ids.items():
        if rid and n > 1:
            rep.err(f"id {rid}", f"出现了 {n} 次")
    return rep


def read_jsonl(path):
    records, rep = [], Report()
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                records.append((i, json.loads(line)))
            except json.JSONDecodeError as e:
                rep.err(f"第 {i} 行", f"不是合法的 JSON：{e}")
    return records, rep


# ---------------------------------------------------------------- 命令

def cmd_validate(args, codes):
    bad = 0
    for path in args.files:
        if Path(path).name == "school_terms.json":
            try:
                doc = json.loads(Path(path).read_text(encoding="utf-8"))
                terms, errors = validate_terms(doc)
            except json.JSONDecodeError as e:
                terms, errors = [], [f"不是合法的 JSON：{e}"]
            print(f"{path}：{len(terms)} 个学期，错误 {len(errors)}")
            for e in errors:
                print("  错误", e)
            bad += len(errors)
            continue
        records, rep0 = read_jsonl(path)
        rep = validate_records(records, record_type(path, args.type), codes)
        errors = rep0.errors + rep.errors
        print(f"{path}：{len(records)} 条，错误 {len(errors)}，警告 {len(rep.warnings)}")
        for e in errors:
            print("  错误", e)
        for w in rep.warnings:
            print("  警告", w)
        bad += len(errors)
    return 1 if bad else 0


def cmd_add(args, codes):
    text = sys.stdin.read().strip()
    try:
        rec = json.loads(text)
    except json.JSONDecodeError as e:
        print("不是合法的 JSON：", e)
        return 1
    existing = []
    if Path(args.file).exists():
        existing, _ = read_jsonl(args.file)
    rtype = record_type(args.file, args.type)
    rep = validate_records(existing + [(len(existing) + 1, rec)], rtype, codes)
    mine = [e for e in rep.errors if rec.get("id", "?") in e or f"第 {len(existing) + 1} 行" in e]
    if mine:
        print("没加进去，先改这些：")
        for e in mine:
            print("  ", e)
        return 1
    Path(args.file).parent.mkdir(parents=True, exist_ok=True)
    with open(args.file, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(f"加好了：{rec.get('id')}（{args.file} 现在 {len(existing) + 1} 条）")
    for w in rep.warnings:
        print("  警告", w)
    return 0


def cmd_stats(args, codes):
    kinds, facts, covered = Counter(), 0, Counter()
    if args.files and all(record_type(f, args.type) == "camp" for f in args.files):
        codes = CAMP_CODES
    a_codes = {c: s for c, s in codes.items() if s["priority"] == "A"}
    places = 0
    official_only = 0
    for path in args.files:
        records, _ = read_jsonl(path)
        rtype = record_type(path, args.type)
        for _, rec in records:
            if rtype not in ("place", "camp"):
                kinds[rtype] += 1
                continue
            if rec.get("detail_policy") == "official_only":
                official_only += 1          # 只收名称和地点，不算进事实统计
                continue
            places += 1
            kinds[rec.get("kind", "?")] += 1
            have = {f.get("code") for f in rec.get("facts", []) if isinstance(f, dict)}
            facts += len(have)
            for c, s in a_codes.items():
                if rec.get("kind") in s["kinds"] and c in have:
                    covered[c] += 1
    print("条数：", dict(kinds))
    if official_only:
        print(f"另有只收名称和地点（detail_policy=official_only）的 {official_only} 个，下面的统计不含它们")
    if places:
        print(f"去处 {places} 个，事实 {facts} 条，平均每个 {facts / places:.1f} 条")
        for c, s in sorted(a_codes.items()):
            n = sum(kinds[k] for k in s["kinds"])
            if n:
                print(f"  A 类 {c:22s} {covered[c]:4d} / {n}")
    return 0


def cmd_codes(args, codes):
    if args.kind == "camp":
        codes = CAMP_CODES
    for c, s in codes.items():
        if args.kind and args.kind not in s["kinds"]:
            continue
        allowed = f"（{' / '.join(s['allowed'])}）" if s["allowed"] else ""
        print(f"{c:22s} {s['priority']} {s['type']:10s} {s['name_zh']}{allowed}  {s['judge_zh']}")
    return 0


def cmd_selftest(args, codes):
    today = date(2026, 11, 20)
    good_place = {
        "id": "au-nsw-hornsby-pool-test-aquatic-centre", "kind": "pool", "name": "Test Aquatic Centre",
        "council": "hornsby", "suburb": "Hornsby", "lat": None, "lon": None,
        "sources": [{"type": "council", "url": "https://www.hornsby.nsw.gov.au/test"}],
        "facts": [{"code": "pool_50m", "value": "yes"}, {"code": "parking", "value": ["free_carpark"]}],
        "hours": [{"days": "mon-fri", "open": "05:30", "close": "20:00"}, {"days": "public_holiday", "closed": True}],
        "season": {"from": "09-01", "to": "04-30"}, "checked": "2026-11-20", "status": "ok",
    }
    bad_place = dict(good_place, id="au-nsw-hornsby-pool-test-2", facts=[{"code": "netted", "value": "yes"}],
                     sources=[{"type": "other", "url": "https://www.facebook.com/x"}], note_zh="电话 0412 345 678")
    good_session = {
        "id": "au-nsw-hornsby-library-test-rhyme-time-tue", "place": "au-nsw-hornsby-library-test",
        "title": "Rhyme Time", "type": "rhyme_time", "weekday": "tue", "start": "10:30", "end": "11:00",
        "age_min_months": 0, "age_max_months": 24, "language": "en", "term_only": True, "booking": "none",
        "cost": "free", "sources": [{"type": "library", "url": "https://www.hornsby.nsw.gov.au/library"}],
        "checked": "2026-11-20",
    }
    bad_session = dict(good_session, id="x", weekday="tuesday", start="10.30",
                       sources=[{"type": "other", "url": "https://www.eventbrite.com.au/e/1"}])
    good_event = {
        "id": "au-nsw-hornsby-event-test-craft-2027-01-12", "title": "Test Craft", "council": "hornsby",
        "venue": "Hornsby Library", "dates": [{"date": "2027-01-12", "start": "10:00", "end": "11:00"}],
        "age_min": 5, "age_max": 12, "cost": "free", "booking": "required",
        "booking_url": "https://www.eventbrite.com.au/e/123",
        "sources": [{"type": "council", "url": "https://www.hornsby.nsw.gov.au/holidays"}], "checked": "2026-11-20",
    }
    checks = [
        ("词表能读", len(codes) >= 30),
        ("好的去处没有错误", not validate_records([(1, good_place)], "place", codes, today).errors),
        ("坏的去处被拦住（错设施、Facebook、电话）",
         len(validate_records([(1, bad_place)], "place", codes, today).errors) >= 3),
        ("好的固定活动没有错误", not validate_records([(1, good_session)], "session", codes, today).errors),
        ("坏的固定活动被拦住（星期、时间、报名平台当来源）",
         len(validate_records([(1, bad_session)], "session", codes, today).errors) >= 3),
        ("好的假期活动没有错误（报名平台可以当报名链接）",
         not validate_records([(1, good_event)], "event", codes, today).errors),
        ("好的学期日期没有错误",
         not validate_terms({"source": "https://education.nsw.gov.au/test",
                             "terms": [{"year": 2027, "term": 1, "start": "2027-02-01", "end": "2027-04-09"},
                                       {"year": 2027, "term": 2, "start": "2027-04-27", "end": "2027-07-02"}]})[1]),
        ("坏的学期日期被拦住（来源不对、日期重叠）",
         len(validate_terms({"source": "https://www.example.com/terms",
                             "terms": [{"year": 2027, "term": 1, "start": "2027-02-01", "end": "2027-04-30"},
                                       {"year": 2027, "term": 2, "start": "2027-04-27", "end": "2027-07-02"}]})[1]) >= 2),
        ("下水点必须写 spot_type",
         any("spot_type" in e for e in validate_records(
             [(1, dict(good_place, id="au-nsw-hornsby-swim-test", kind="swim", facts=[]))], "place", codes, today).errors)),
    ]
    ok = all(passed for _, passed in checks)
    for name, passed in checks:
        print(("✓ " if passed else "✗ ") + name)
    print("自检通过" if ok else "自检没通过")
    if CAMP_CODES:
        good_camp = {"id": "au-nsw-npws-sydney-camp-test-campground", "kind": "camp", "name": "Test campground",
                     "area": "npws-sydney", "park": "Test National Park", "lat": -34.07, "lon": 151.1,
                     "booking": "required", "booking_url": "https://www.nationalparks.nsw.gov.au/test",
                     "sources": [{"type": "state_gov", "url": "https://www.nationalparks.nsw.gov.au/test"}],
                     "facts": [{"code": "camp_types", "value": ["tent", "walk_in"]}, {"code": "toilet", "value": "yes"},
                               {"code": "campfire", "value": "no", "ev": "no campfires"},
                               {"code": "camp_fee", "value": "From $24.60 per night for 2 people"}],
                     "checked": today.isoformat(), "status": "ok"}
        camp_checks = [
            ("露营地：好的记录能过", not validate_records([(1, good_camp)], "camp", codes, today).errors),
            ("露营地：不能放进 data/places", bool(validate_records([(1, good_camp)], "place", codes, today).errors)),
            ("露营地：不收 hours", bool(validate_records([(1, dict(good_camp, hours=[{"days": "daily", "open": "08:00", "close": "17:00"}]))], "camp", codes, today).errors)),
            ("露营地：泳池的代码不能用", bool(validate_records([(1, dict(good_camp, facts=[{"code": "pool_50m", "value": "yes"}]))], "camp", codes, today).errors)),
            ("露营地：泳池不能放进 data/camps", bool(validate_records([(1, dict(good_camp, kind="pool"))], "camp", codes, today).errors)),
            ("露营地：非政府经营必须写 operator", bool(validate_records([(1, dict(good_camp, operator_type="private"))], "camp", codes, today).errors)
                                      and not validate_records([(1, dict(good_camp, operator_type="private", operator="Test Holiday Park"))], "camp", codes, today).errors),
            ("露营地：operator_type 只能是 government / private", bool(validate_records([(1, dict(good_camp, operator_type="council"))], "camp", codes, today).errors)),
            ("露营地：版权受限的营地只收名称和地点",
             not validate_records([(1, dict({k: v for k, v in good_camp.items() if k not in ("facts", "booking", "booking_url")},
                                            facts=[], detail_policy="official_only", note_zh=NOTE_OFFICIAL_ONLY,
                                            official_url="https://www.nationalparks.nsw.gov.au/test"))], "camp", codes, today).errors),
            ("露营地：official_only 不能带设施事实", bool(validate_records([(1, dict(good_camp, detail_policy="official_only", note_zh=NOTE_OFFICIAL_ONLY,
                                            official_url="https://www.nationalparks.nsw.gov.au/test"))], "camp", codes, today).errors)),
            ("露营地：official_only 要写 official_url 和固定提示语", bool(validate_records([(1, dict({k: v for k, v in good_camp.items() if k not in ("facts", "booking", "booking_url")},
                                            facts=[], detail_policy="official_only"))], "camp", codes, today).errors)),
        ]
        for name, passed in camp_checks:
            print(("  ✓ " if passed else "  ✗ ") + name)
            ok = ok and passed
        print("露营地自检" + ("通过" if all(p for _, p in camp_checks) else "没过"))
    return 0 if ok else 1


def main(argv=None):
    p = argparse.ArgumentParser(description="「去哪玩」数据工具")
    p.add_argument("--codes", help="place_codes.csv 的位置（默认和脚本放一起）")
    p.add_argument("--type", choices=["place", "session", "event", "camp"], help="记录类型（默认看文件放在哪）")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    c = sub.add_parser("codes")
    c.add_argument("--kind", choices=KINDS + ["camp"])
    a = sub.add_parser("add")
    a.add_argument("file")
    v = sub.add_parser("validate")
    v.add_argument("files", nargs="+")
    s = sub.add_parser("stats")
    s.add_argument("files", nargs="+")
    args = p.parse_args(argv)
    codes = load_codes(args.codes)
    global CAMP_CODES
    camp_path = HERE / "camp_codes.csv"
    CAMP_CODES = load_codes(camp_path) if camp_path.exists() else {}
    return {"selftest": cmd_selftest, "codes": cmd_codes, "add": cmd_add,
            "validate": cmd_validate, "stats": cmd_stats}[args.cmd](args, codes)


if __name__ == "__main__":
    sys.exit(main())
