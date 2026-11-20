#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
round.py —— 季度复查：现在是哪一轮、今天在不在复查窗口里、还有哪些 council 要做（RULES.md 第十五节）
（Opus 2026-11-20 写；只用 Python 标准库）

一轮 = 一个学校假期。假期开始前 28 天到假期前一天是这一轮的复查窗口：
复查每个已经收过的 council，顺便收这个假期的活动。轮次的名字是「假期开始的年份-季节」，例 2026-summer。

用法（在仓库根目录）：
  python3 tools/round.py                    看今天
  python3 tools/round.py --today 2027-03-20 看某一天
  python3 tools/round.py --json             给脚本用
"""
import argparse
import csv
import importlib.util
import json
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
WINDOW_DAYS = 28
SKIP_SLUGS = {"nsw-school-terms"}


def sydney_today():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Australia/Sydney")).date()
    except Exception:
        return (datetime.now(timezone.utc) + timedelta(hours=10)).date()


def load_terms():
    spec = importlib.util.spec_from_file_location("place_data_tool", ROOT / "place_data_tool.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    path = ROOT / "data" / "school_terms.json"
    if not path.exists():
        return [], ["没有 data/school_terms.json"]
    terms, errors = tool.validate_terms(json.loads(path.read_text(encoding="utf-8")))
    return terms, errors


def season(d):
    return {12: "summer", 1: "summer", 3: "autumn", 4: "autumn", 6: "winter", 7: "winter",
            9: "spring", 10: "spring"}.get(d.month, f"m{d.month:02d}")


def next_holiday(terms, today):
    """今天之后最近的一个假期：(开始日, 结束日或 None, 假期后面的学期有没有数据)"""
    for i, t in enumerate(terms):
        start = date.fromisoformat(t["end"]) + timedelta(days=1)
        if start <= today:
            continue
        if i + 1 < len(terms):
            end = date.fromisoformat(terms[i + 1]["start"]) - timedelta(days=1)
            return start, end, True
        return start, None, False
    return None, None, False


def councils(current_round):
    path = ROOT / "place_batches.csv"
    recheck, events = [], []
    if not path.exists():
        return recheck, events
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    rows.sort(key=lambda r: ((r.get("round_date") or ""), int(r.get("order") or 0)))
    for r in rows:
        slug = r.get("slug", "")
        if slug in SKIP_SLUGS or r.get("status") not in ("done", "doing"):
            continue
        if (r.get("round") or "") != current_round:
            recheck.append(slug)
        if (r.get("events_round") or "") != current_round:
            events.append(slug)
    return recheck, events


def main(argv=None):
    p = argparse.ArgumentParser(description="季度复查：现在是哪一轮")
    p.add_argument("--today", help="YYYY-MM-DD（默认悉尼的今天）")
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    today = date.fromisoformat(args.today) if args.today else sydney_today()
    terms, errors = load_terms()
    out = {"today": today.isoformat(), "errors": errors}
    start, end, known_after = next_holiday(terms, today) if not errors else (None, None, False)
    if start is None:
        out.update({"round": None, "in_window": False, "need_terms": True,
                    "message": "学期日期用完了：先按第 0 批收新一年的学期日期"})
    else:
        rnd = f"{start.year}-{season(start)}"
        wstart = start - timedelta(days=WINDOW_DAYS)
        wend = start - timedelta(days=1)
        in_window = wstart <= today <= wend
        recheck, events = councils(rnd)
        out.update({
            "round": rnd,
            "holiday_start": start.isoformat(),
            "holiday_end": end.isoformat() if end else None,
            "window_start": wstart.isoformat(),
            "window_end": wend.isoformat(),
            "in_window": in_window,
            "days_to_holiday": (start - today).days,
            "need_terms": not known_after,
            "recheck": recheck,
            "events": events,
        })
        if not in_window:
            out["message"] = f"不在复查窗口（{rnd} 的窗口是 {wstart} 到 {wend}），这次不用做"
        elif not recheck and not events and known_after:
            out["message"] = f"{rnd} 这一轮已经做完了"
        else:
            out["message"] = (f"{rnd} 这一轮：要复查 {len(recheck)} 个 council，要收假期活动 {len(events)} 个"
                              + ("；还要先收下一年的学期日期" if not known_after else ""))
    if args.json:
        print(json.dumps(out, ensure_ascii=False, indent=2))
    else:
        print(out["message"])
        for k in ("round", "holiday_start", "window_start", "window_end", "days_to_holiday", "recheck", "events", "errors"):
            if out.get(k):
                print(f"  {k}: {out[k]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
