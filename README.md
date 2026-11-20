# parkapp-data

「公园有啥」App 里「去哪玩」一栏的数据：悉尼各 council 的游泳池、图书馆（讲故事这类每周固定的亲子活动）、下水点和学校假期活动。只记官网上写的事实和来源链接，以官网为准。

- **App 怎么拿到**：App 每天读一次 `https://sasuke9527.github.io/parkapp-data/manifest.json`，有新版本就下载同一目录下的 `places.json`（GitHub Pages 发布的是 `docs/` 文件夹）。
- **规则**：`RULES.md`。和 claude.ai 项目「app」里的 `claude/park-data/README-去哪玩数据格式与填写说明.md` 是同一份，改的时候两边一起改。
- **谁在改**：
  - 定时任务「去哪玩数据季度复查」：每个学校假期开始前三四周复查一轮，顺便收这个假期的活动（RULES.md 第十五节）。
  - 新 council 的第一次收集：在项目里开 Sonnet 对话，用 RULES.md 第十二节的提示词。
- **以这里为准**：从 2026-11-20 起，数据、词表、工具和批次表都以这个仓库为准；项目里的旧副本不再更新。

## 目录

| 路径 | 是什么 |
|---|---|
| `data/places/*.jsonl` | 游泳池、图书馆、下水点，每行一个去处 |
| `data/sessions/*.jsonl` | 图书馆每周固定的活动，每行一个「每周几点」 |
| `data/events/*.jsonl` | 学校假期活动，每行一个活动 |
| `data/school_terms.json` | NSW 公立学校学期日期（东部） |
| `place_codes.csv` | 设施词表 |
| `place_batches.csv` | 批次表：每个 council 收到哪了、复查到哪一轮 |
| `runs.csv` | 定时任务每次干了什么 |
| `place_data_tool.py` | 校验工具：`selftest`、`add`、`validate`、`stats` |
| `tools/build_places_data.py` | 打包成 App 读的 places.json |
| `tools/publish.py` | 校验 → 打包 → 安全检查 → 写 `docs/places.json`、`docs/manifest.json` |
| `docs/` | GitHub Pages 发布的内容（App 读这里） |

## 发布

```bash
python3 tools/publish.py      # 有错误或数量掉得太多就不写
git add -A && git commit -m "……" && git push
```

发错了：`git revert` 那次提交再 push，App 第二天会换回去（版本号以最新提交里的为准，所以 revert 之后要再跑一次 publish.py 生成新版本号）。
