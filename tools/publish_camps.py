#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
publish_camps.py —— 露营地数据的发布：校验 → 打包 → 安全检查 → 写 docs/camps.json，并在 docs/manifest.json 里加（或更新）「camps」一栏
（Fable 2026-11-22 写；只用 Python 标准库。和 publish.py 分开：这个脚本不碰 docs/places.json，也不改 manifest 里别的字段。）

为什么单独一个文件：已经上架的 App 1.0 只认识 pool / library / swim 三种去处，places.json 里出现 kind=camp 会整份读不出来。
所以露营地放在 docs/camps.json，manifest.json 多一栏 camps；1.0 不认识这一栏，会直接忽略；1.1 起的 App 才读。

用法（在仓库根目录）：
  python3 tools/publish_camps.py            正常发布：数据有错误、或者数量掉得太多，就不写
  python3 tools/publish_camps.py --check    只检查、不写文件
  python3 tools/publish_camps.py --force    数量掉得多也照样写（人看过、确认没问题才用）

打包时做的事：
  - 每条事实只留 code 和 value（ev 是官网原文的摘录、src 是出处序号，只给整理的人核对用，不进 App）；
  - 去掉 kind（全是 camp）；按 id 排序；
  - detail_policy=official_only 的（来源有版权要求）只有名称和地点，facts 是空的——校验工具已经保证。
退出码：0 写好了，或者内容和上一版一样（不写）；1 数据有错误；2 数量掉得太多，没写
"""
import argparse
import datetime
import glob
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
DATA_FILE = "camps.json"
FORMAT = 1


def read_camps():
    camps, errors, seen = [], [], set()
    for path in sorted(glob.glob(str(ROOT / "data" / "camps" / "*.jsonl"))):
        for n, line in enumerate(open(path, encoding="utf-8"), 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
            except json.JSONDecodeError as e:
                errors.append(f"{path}:{n} 不是合法的 JSON（{e}）")
                continue
            if r.get("id") in seen:
                errors.append(f"{path}:{n} id 重复：{r.get('id')}")
                continue
            seen.add(r.get("id"))
            if r.get("detail_policy") == "official_only" and r.get("facts"):
                errors.append(f"{path}:{n} official_only 不能带设施事实：{r.get('id')}")
            out = {k: v for k, v in r.items() if k != "kind"}
            out["facts"] = [{"code": f["code"], "value": f["value"]} for f in r.get("facts", [])]
            if isinstance(out.get("season"), dict):
                out["season"] = {k: v for k, v in out["season"].items() if k in ("from", "to")}
            camps.append(out)
    camps.sort(key=lambda r: r["id"])
    return camps, errors


def main(argv=None):
    p = argparse.ArgumentParser(description="发布露营地数据到 docs/camps.json")
    p.add_argument("--check", action="store_true", help="只检查、不写文件")
    p.add_argument("--force", action="store_true", help="数量掉得多也写（人看过才用）")
    args = p.parse_args(argv)

    files = sorted(glob.glob(str(ROOT / "data" / "camps" / "*.jsonl")))
    run = subprocess.run([sys.executable, str(ROOT / "place_data_tool.py"), "--type", "camp", "validate"] + files,
                         capture_output=True, text=True)
    if run.returncode != 0:
        print("校验没通过，没有发布：")
        print(run.stdout[-3000:] or run.stderr[-3000:])
        return 1
    camps, errors = read_camps()
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
    if prev and prev.get("camps") == camps:
        print(f"内容和上一版（{prev.get('version', '?')}）一样，不用发布。共 {len(camps)} 个营地")
        return 0
    before = len(prev.get("camps", []))
    if before >= 10 and len(camps) < before * 0.9 and not args.force:
        print(f"安全检查没通过，没有发布：营地从 {before} 个变成 {len(camps)} 个（少了 10% 以上）。确认没问题再用 --force。")
        return 2
    full = sum(1 for c in camps if c.get("detail_policy") != "official_only")
    summary = f"营地 {len(camps)} 个（有详细信息 {full}，只有名称和地点 {len(camps) - full}）"
    if args.check:
        print(f"检查通过（没写文件）：{summary}")
        return 0

    now = datetime.datetime.now(datetime.timezone.utc)
    doc = {"format": FORMAT, "version": now.strftime("%Y%m%d%H%M"), "generated": now.strftime("%Y-%m-%d"), "camps": camps}
    body = (json.dumps(doc, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    DOCS.mkdir(exist_ok=True)
    prev_path.write_bytes(body)
    manifest_path = DOCS / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    manifest["camps"] = {
        "format": FORMAT,
        "version": doc["version"],
        "generated": doc["generated"],
        "file": DATA_FILE,
        "bytes": len(body),
        "sha256": hashlib.sha256(body).hexdigest(),
        "count": len(camps),
    }
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"发布好了 docs/{DATA_FILE}（版本 {doc['version']}）：{summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
