#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish.py —— 「去哪玩」数据的发布：校验 → 打包 → 安全检查 → 写 docs/places.json 和 docs/manifest.json
（Opus 2026-11-20 写；只用 Python 标准库。GitHub Pages 发布的是 docs/ 这个文件夹，App 每天读 docs/manifest.json）

用法（在仓库根目录）：
  python3 tools/publish.py            正常发布：数据有错误、或者数量掉得太多，就不写
  python3 tools/publish.py --check    只检查、不写文件
  python3 tools/publish.py --force    数量掉得多也照样写（只有人看过、确认没问题才用）

退出码：0 写好了，或者内容和上一版一样（不写）；1 数据有错误；2 数量掉得太多，没写（安全检查）

安全检查（和 docs/places.json 里的上一版比）：
  - 去处总数少了 10% 以上（上一版至少 10 个）
  - 某个 council 的去处少了一半以上（上一版这个 council 至少 4 个）
  - 固定活动总数少了 30% 以上（上一版至少 10 条）
写好以后由调用的人 git commit、push；出了问题用 git revert 退回上一版。
"""
import argparse
import hashlib
import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
DOCS = ROOT / "docs"
DATA_FILE = "places.json"


def load_builder():
    spec = importlib.util.spec_from_file_location("build_places_data", HERE / "build_places_data.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def comparable(doc):
    """比较内容时不看版本号和日期"""
    return {k: v for k, v in doc.items() if k not in ("version", "generated")}


def safety_problems(prev, new):
    problems = []
    pp, np_ = len(prev.get("places", [])), len(new.get("places", []))
    if pp >= 10 and np_ < pp * 0.9:
        problems.append(f"去处从 {pp} 个变成 {np_} 个（少了 10% 以上）")
    before = Counter(p.get("council") for p in prev.get("places", []))
    after = Counter(p.get("council") for p in new.get("places", []))
    for council, n in sorted(before.items()):
        if n >= 4 and after.get(council, 0) < n * 0.5:
            problems.append(f"{council} 的去处从 {n} 个变成 {after.get(council, 0)} 个（少了一半以上）")
    ps, ns = len(prev.get("sessions", [])), len(new.get("sessions", []))
    if ps >= 10 and ns < ps * 0.7:
        problems.append(f"固定活动从 {ps} 条变成 {ns} 条（少了 30% 以上）")
    return problems


def changes(prev, new):
    """给人看的改动摘要"""
    lines = []
    for key, label in (("places", "去处"), ("sessions", "固定活动"), ("events", "假期活动")):
        a = {r["id"]: r for r in prev.get(key, [])}
        b = {r["id"]: r for r in new.get(key, [])}
        added = sorted(set(b) - set(a))
        removed = sorted(set(a) - set(b))
        changed = sorted(i for i in set(a) & set(b) if comparable(a[i]) != comparable(b[i]))
        if added or removed or changed:
            lines.append(f"{label}：新增 {len(added)}、删掉 {len(removed)}、改了 {len(changed)}")
            for tag, ids in (("新增", added), ("删掉", removed), ("改了", changed)):
                for i in ids[:15]:
                    lines.append(f"  {tag} {i}")
                if len(ids) > 15:
                    lines.append(f"  ……另外还有 {len(ids) - 15} 条")
    if prev.get("terms") != new.get("terms"):
        lines.append("学期日期有变化")
    return lines


def main(argv=None):
    p = argparse.ArgumentParser(description="发布「去哪玩」数据到 docs/")
    p.add_argument("--check", action="store_true", help="只检查、不写文件")
    p.add_argument("--force", action="store_true", help="数量掉得多也写（人看过才用）")
    args = p.parse_args(argv)

    builder = load_builder()
    new, errors, summary = builder.build(ROOT)
    if errors:
        print(f"数据有 {len(errors)} 个错误，没有发布：")
        for e in errors[:50]:
            print("  ", e)
        return 1

    prev_path = DOCS / DATA_FILE
    prev = {}
    if prev_path.exists():
        try:
            prev = json.loads(prev_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}
    if prev and comparable(prev) == comparable(new):
        print(f"内容和上一版（{prev.get('version', '?')}）一样，不用发布。{summary}")
        return 0

    for line in changes(prev, new) or ["（第一次发布）"]:
        print(line)
    problems = safety_problems(prev, new) if prev else []
    if problems and not args.force:
        print("安全检查没通过，没有发布：")
        for x in problems:
            print("  ", x)
        print("先找原因（官网改版？页面打不开？），确认没问题再用 --force。")
        return 2
    if args.check:
        print(f"检查通过（没写文件）：{summary}")
        return 0

    DOCS.mkdir(exist_ok=True)
    body = builder.dump(new).encode("utf-8")
    prev_path.write_bytes(body)
    manifest = {
        "format": new["format"],
        "version": new["version"],
        "generated": new["generated"],
        "file": DATA_FILE,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "places": len(new["places"]),
        "sessions": len(new["sessions"]),
        "events": len(new["events"]),
        "terms": len(new["terms"]),
    }
    (DOCS / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (DOCS / ".nojekyll").touch()
    print(f"发布好了 docs/{DATA_FILE}（版本 {new['version']}）：{summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
