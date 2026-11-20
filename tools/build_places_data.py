#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_places_data.py —— 把「去哪玩」的数据打包成 App 读的 places.json（Opus 2026-11-20 写；只用 Python 标准库）

读（都相对 --root，默认是这个脚本的上一级目录）：
  data/places/*.jsonl      游泳池、图书馆、下水点（每行一个去处）
  data/sessions/*.jsonl    图书馆的固定活动（讲故事等，每行一个「每周几点」）
  data/events/*.jsonl      学校假期活动（每行一个活动）
  data/school_terms.json   NSW 公立学校学期日期（可以没有）
  place_codes.csv          设施词表（校验用）
  place_batches.csv        council 的名字和官网（App 里「链接打不开？去 council 官网」用；可以没有）
写：
  --out 指定的文件；不写就是 app/ParkApp/Resources/places.json（在 pm-park 里用）。
  GitHub 仓库 sasuke9527/parkapp-data 里不直接用它，用 tools/publish.py（它调这里的 build()，写 docs/）。

先用 place_data_tool.py 的规则校验，有错误就不写。同一个 id 出现多次，留 checked 较新的那条。
结束 30 天以上的假期活动不打包。没有任何数据时也会写一个空的 places.json（App 显示「资料还在整理」）。

用法：python3 tools/build_places_data.py [--root 目录] [--out 文件]
规则见 RULES.md（和项目文档 README-去哪玩数据格式与填写说明.md 是同一份）
"""
import argparse
import csv
import importlib.util
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
DEFAULT_ROOT = HERE.parent
EXPIRED_EVENT_DAYS = 30
FORMAT = 1          # places.json 的格式版本；App 只认它会读的版本（PlacesFeed.formatSupported）


def load_tool(root):
    """读 root 下的 place_data_tool.py（校验规则都在那里）"""
    spec = importlib.util.spec_from_file_location("place_data_tool", Path(root) / "place_data_tool.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    return tool


def sydney_today():
    """悉尼的今天（找不到时区数据就用 UTC+10 近似）"""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Australia/Sydney")).date()
    except Exception:
        return (datetime.now(timezone.utc) + timedelta(hours=10)).date()


def new_version():
    """版本号：UTC 的 YYYYMMDDHHMM，越新越大。App 靠它判断要不要下载"""
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M")


def collect(root, folder, rtype, tool, codes, today):
    """读一个文件夹里的 jsonl，校验，按 id 去重（留 checked 新的）。返回 (记录列表, 错误列表)"""
    errors, best = [], {}
    for path in sorted((Path(root) / "data" / folder).glob("*.jsonl")):
        records, rep0 = tool.read_jsonl(path)
        rep = tool.validate_records(records, rtype, codes, today)
        errors += [f"{path.name} {e}" for e in rep0.errors + rep.errors]
        for _, rec in records:
            rid = rec.get("id")
            if not rid:
                continue
            if rid not in best or rec.get("checked", "") > best[rid].get("checked", ""):
                best[rid] = rec
    return [best[k] for k in sorted(best)], errors


def load_terms(root, tool):
    path = Path(root) / "data" / "school_terms.json"
    if not path.exists():
        return [], "", []
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [], "", [f"school_terms.json 不是合法的 JSON：{e}"]
    terms, errors = tool.validate_terms(doc)
    source = doc.get("source", "") if isinstance(doc, dict) else ""
    return terms, source, [f"school_terms.json：{e}" for e in errors]


def load_councils(root, used):
    """place_batches.csv 里用到的 council：slug → {name, website}"""
    path = Path(root) / "place_batches.csv"
    out = {}
    if not path.exists():
        return out
    with open(path, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            slug = (row.get("slug") or "").strip()
            site = (row.get("website") or "").strip()
            if slug in used and site.startswith("https://"):
                out[slug] = {"name": (row.get("name") or slug).strip(), "website": site}
    return out


def build(root=DEFAULT_ROOT, today=None, version=None):
    """校验并打包。返回 (places.json 的内容, 错误列表, 一行摘要)；有错误时内容是 None"""
    root = Path(root)
    tool = load_tool(root)
    today = today or sydney_today()
    codes = tool.load_codes(root / "place_codes.csv")
    places, e1 = collect(root, "places", "place", tool, codes, today)
    sessions, e2 = collect(root, "sessions", "session", tool, codes, today)
    events, e3 = collect(root, "events", "event", tool, codes, today)
    terms, terms_source, e4 = load_terms(root, tool)
    errors = e1 + e2 + e3 + e4

    # 跨文件的检查：固定活动要挂在已有的图书馆上；假期活动写了 place 的，那个去处要存在
    ids = {p["id"]: p for p in places}
    for s in sessions:
        p = ids.get(s["place"])
        if not p or p.get("kind") != "library":
            errors.append(f"固定活动 {s['id']}：place {s['place']} 不是已有的图书馆")
    for ev in events:
        if ev.get("place") and ev["place"] not in ids:
            errors.append(f"假期活动 {ev['id']}：place {ev['place']} 不存在")
    if errors:
        return None, errors, ""

    cutoff = (today - timedelta(days=EXPIRED_EVENT_DAYS)).isoformat()
    kept = [ev for ev in events if max(d["date"] for d in ev["dates"]) >= cutoff]
    used = {p["council"] for p in places} | {ev["council"] for ev in kept}
    out = {
        "format": FORMAT,
        "version": version or new_version(),
        "generated": today.isoformat(),
        "places": places,
        "sessions": sessions,
        "events": kept,
        "terms": terms,
        "terms_source": terms_source,
        "councils": load_councils(root, used),
    }
    kinds = {}
    for p in places:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    summary = (f"游泳池 {kinds.get('pool', 0)}、图书馆 {kinds.get('library', 0)}、下水点 {kinds.get('swim', 0)}；"
               f"固定活动 {len(sessions)}；假期活动 {len(kept)}（过期没打包 {len(events) - len(kept)}）；学期 {len(terms)}")
    return out, [], summary


def dump(out):
    return json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n"


def main(argv=None):
    p = argparse.ArgumentParser(description="把「去哪玩」的数据打包成 places.json")
    p.add_argument("--root", default=str(DEFAULT_ROOT), help="数据所在的目录（默认是脚本的上一级）")
    p.add_argument("--out", help="写到哪里（默认 app/ParkApp/Resources/places.json）")
    args = p.parse_args(argv)
    root = Path(args.root).resolve()
    out_path = Path(args.out) if args.out else root / "app" / "ParkApp" / "Resources" / "places.json"
    out, errors, summary = build(root)
    if errors:
        print(f"有 {len(errors)} 个错误，没有写 places.json：")
        for e in errors[:50]:
            print("  ", e)
        return 1
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(dump(out), encoding="utf-8")
    print(f"写好了 {out_path}：{summary}；版本 {out['version']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
