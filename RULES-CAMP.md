# 露营地数据：格式与填写说明（v1 · 2026-11-22）

> 「去哪玩」下一步要加的一类：悉尼周边开车两三小时内、**政府管的露营地**。这份说明写给 **Sonnet**（照着收集）和 **Opus**（做 App 时读）。
> 通用的规矩（只记事实、页面没写不写、坐标不估、不记联系人、哪些网站不能用）和泳池、图书馆一样，在 RULES.md 第四节和第十节，**先读那两节**。这里只写露营地不一样的地方。
> **现在只收集、不发布**：露营地放在 `data/camps/`，打包和发布脚本（tools/）不读这个文件夹，所以已经上架的 App 1.0 不受影响。**收露营地时不要跑 tools/publish.py。** 等 App 1.1 能显示露营地了，再由 Opus 接上发布。

## 一、收什么、不收什么

| 收 | 不收 |
|---|---|
| NSW 国家公园（NPWS）网站上的 campground | 小屋、别墅、豪华帐篷（cabins、cottages、glamping、lodges） |
| NSW 州森林（Forestry Corporation）网站上的 camping area | 私人和连锁的 holiday park、caravan park（Big4、NRMA、Discovery、Ingenia、Reflections 等） |
| council、联邦或州政府机构**自己经营**的 camping area / tourist park（camp_batches.csv 第 6 批点了名的） | Hipcamp、Youcamp 这类私人营地 |
| | 只能住房车、不让搭帐篷的 rest area |

**能用的来源**：管这个营地的机构自己的官网页面（nationalparks.nsw.gov.au、forestrycorporation.com.au、council 官网、harbourtrust.gov.au、waternsw.com.au 等）。
**不能用的来源**：WikiCamps、CamperMate、Anycamp、Hipcamp、Tripadvisor、Google 地图、Facebook、博客、旅游网站（visitnsw.com、sydney.com 也不用，它们是转述）。

**网站让不让抓**：nationalparks.nsw.gov.au 的 robots.txt 在 2026-11-22 看过，营地页面没有被禁止。别的网站第一次用时，WebFetch 打不开、被拒或返回 403，就**不绕过**：这一批在 camp_batches.csv 里标 blocked，notes 写原因，向我汇报。

## 二、文件

| 文件 | 作用 | 谁改 |
|---|---|---|
| RULES-CAMP.md | 本说明 | Opus |
| camp_codes.csv | 露营地的设施词表 | Opus（Sonnet 不改） |
| camp_batches.csv | 批次清单：6 批，按 order 做 | Sonnet |
| data/camps/au-nsw-<slug>-<序号>.jsonl | 露营地，每行一个 | Sonnet |
| place_data_tool.py | 同一个工具：文件放在 data/camps/ 里就按露营地校验 | 不改 |

## 三、一个露营地的格式

每行一个 JSON。下面排成多行是为了好读。**这是虚构的示例，别抄进数据**：

```json
{
  "id": "au-nsw-npws-sydney-camp-example-creek-campground",
  "kind": "camp",
  "name": "Example Creek campground",
  "area": "npws-sydney",
  "park": "Example National Park",
  "suburb": "Example Heights",
  "lat": null,
  "lon": null,
  "booking": "required",
  "booking_url": "https://example.org/camping/example-creek/book",
  "sources": [
    {"type": "state_gov", "url": "https://example.org/camping/example-creek"}
  ],
  "facts": [
    {"code": "camp_types", "value": ["tent", "camper_trailer", "beside_vehicle"], "ev": "Tent, Camper trailer site, Camping beside my vehicle"},
    {"code": "access", "value": ["2wd"]},
    {"code": "toilet", "value": "yes"},
    {"code": "flush_toilet", "value": "no", "ev": "non-flush toilets"},
    {"code": "shower", "value": "no"},
    {"code": "drinking_water", "value": "no", "ev": "bring drinking and cooking water"},
    {"code": "campfire", "value": "yes", "ev": "fire rings (bring your own firewood)"},
    {"code": "firewood", "value": "no"},
    {"code": "dogs", "value": ["prohibited"]},
    {"code": "camp_fee", "value": "From $24.60 per night for 2 people"},
    {"code": "park_entry_fee", "value": "$8 per vehicle per day"}
  ],
  "checked": "2026-11-22",
  "status": "ok",
  "note_zh": "大门晚上锁，订好后会给门禁密码"
}
```

| 字段 | 必填 | 怎么写 |
|---|---|---|
| id | ✓ | au-nsw-<area>-camp-<名字>：只用小写英文、数字、连字符。例 au-nsw-npws-sydney-camp-cattai-campground |
| kind | ✓ | 固定写 camp |
| name | ✓ | 官网上的英文名 |
| area | ✓ | 这一批在 camp_batches.csv 里的 slug（npws-sydney、forestry……） |
| park |  | 所在的国家公园、州森林或保护区的名字，照官网写（例 Cattai National Park） |
| suburb |  | 页面写了最近的地名或所在 suburb 才填 |
| address |  | 页面写了街道地址才填 |
| lat / lon |  | **页面上写了才填，不要估**，不知道写 null。页面自己的 Get directions 或地图链接里带的经纬度算页面写了的 |
| operator |  | 不是管理机构自己经营时，官网写的经营方名字 |
| booking |  | required（要预订）/ recommended（建议预订）/ none（不用订，先到先得）；页面没说就不写 |
| booking_url |  | 官网上的预订页面链接 |
| season |  | 只在某几个月开：{"from": "09-01", "to": "04-30"}，可以加 ev |
| sources | ✓ | 第一个放这个营地自己的页面。type：NPWS、州森林、WaterNSW 写 state_gov；council 写 council；Harbour Trust 写 federal_gov |
| facts | ✓ | 见第四节；什么都没查到写 [] |
| checked | ✓ | 查的当天，YYYY-MM-DD |
| status | ✓ | ok / needs_check（页面自相矛盾）/ temporarily_closed（页面写了现在关闭）/ seasonal_closed / under_construction |
| note_zh |  | 一句中文备注，自己的话，最多 80 个字符：大门几点锁、要走多远、现在为什么关 |
| aka |  | 别名列表 |

露营地**不写 hours**（工具会拦）。大门开关时间写在 note_zh。

## 四、设施词表（A = 每个营地都要找；B = 看到了就记）

在终端里看：`python3 place_data_tool.py codes --kind camp`。事实的写法（value、ev、src）见 RULES.md 第四节。

| 代码 | 中文名 | 填法 | 优先 | 怎么判断 |
|---|---|---|---|---|
| camp_types | 能怎么住 | 多选：tent / camper_trailer / caravan / campervan / beside_vehicle / walk_in / group | A | 照页面的 Suitable for 写。walk_in 是要背东西走进去的（remote、backpack、hike-in） |
| access | 怎么到 | 多选：2wd / 4wd / walk_in / boat | A | 普通轿车能到写 2wd；写了要四驱写 4wd；只能走进去 walk_in；只能坐船或渡轮 boat |
| toilet | 厕所 | 有/没有 | A | 不管哪种厕所，有就 yes |
| shower | 淋浴 | 有/没有 | A |  |
| drinking_water | 饮用水 | 有/没有 | A | 写 bring your own water、要自己烧开的，写 no |
| campfire | 能生火 | 有/没有 | A | fire rings、fire pits、wood barbecues 写 yes；no campfires、fuel stove only 写 no；夏天禁火这类条件摘到 ev |
| dogs | 狗 | 多选：prohibited / on_leash / allowed | A | 国家公园一般是 prohibited |
| camp_fee | 营地费 | 文字 | A | 照页面写每晚多少钱、按什么算；免费写 Free |
| flush_toilet | 冲水厕所 | 有/没有 | B | non-flush、pit、composting 写 no |
| hot_shower | 热水淋浴 | 有/没有 | B | cold showers only 写 no |
| bbq | 烧烤 | 多选：gas_electric / wood / none | B |  |
| park_entry_fee | 公园门票 | 文字 | B | 进公园另外收的车辆费 |
| site_count | 营位数 | 整数 | B |  |
| picnic_table | 野餐桌 | 有/没有 | B |  |
| powered_sites | 带电营位 | 有/没有 | B | unpowered only 写 no |
| camp_kitchen | 营地厨房 | 有/没有 | B |  |
| rubbish_bins | 垃圾桶 | 有/没有 | B | take your rubbish with you 写 no |
| firewood | 提供木柴 | 有/没有 | B | bring your own firewood 写 no |
| generator | 能用发电机 | 有/没有 | B |  |
| swimming | 旁边能游泳 | 有/没有 | B | 页面明说营地旁可以游泳才写 yes |
| playground | 儿童游乐场 | 有/没有 | B | 营地里或紧挨着的 |
| cafe_kiosk | 咖啡 / 小卖部 | 有/没有 | B | 营地里的 |
| accessible_toilet | 无障碍厕所 | 有/没有 | B |  |
| accessibility | 无障碍情况 | 文字 | B | 照页面 Accessibility 一栏摘一小句 |
| walk_in_distance | 从停车场走多远 | 文字 | B | 例 300m from carpark |

**页面没提到的就不写这一条。** 只有页面明确说没有，才写 no / none。WebFetch 回答「not stated」的，一律不写。

## 五、每次对话的流程（Sonnet 照做）

**准备**

1. 用 add_repo 接上 GitHub 仓库 sasuke9527/parkapp-data（access 选 push），clone 到 /home/claude/parkapp-data（已有就 `git pull --rebase`）。
2. 读 RULES.md 的第四节、第十节和这份 RULES-CAMP.md，运行 `python3 place_data_tool.py selftest`，「自检通过」和「露营地自检通过」都出现才继续。

**选批次**

3. 看 camp_batches.csv：有 status=doing 的接着做；没有就选 order 最小的 todo，改成 doing。
4. 本次的文件：data/camps/au-nsw-<slug>-<序号>.jsonl，序号 = 这一行的 files + 1，写两位数。notes 里写了上次做到哪，就从那里接着做。

**收集**

5. **先列清单**：用网页搜索找到这一批的列表页（NPWS：Camping and accommodation 里按地区筛的 campground 列表；第 3、4、5 批按批次名字里点名的公园或森林，一个个找它的 camping 页面），这样问 WebFetch：

> List every campground or camping area linked on this page with its name, the park or forest it is in, and its full URL. Only include places where you can camp in a tent, camper trailer, caravan or campervan. Do not include cabins, cottages, lodges or glamping.

   列表有翻页或「Load more」拿不全时，改用网页搜索「<公园名> campground NSW National Parks」一个公园一个公园补，只开官网的结果。清单写进 notes，方便下次接着做。

6. **再一个个开营地页面**，这样问 WebFetch：

> List exactly as written on this page, for this campground: the park it is in and the region; the camping types it is suitable for (tent, camper trailer, caravan, campervan, camping beside vehicle, walk-in or remote camping, group); how you get there (2WD, 4WD, walk-in, boat) and the distance to walk from the carpark; the number of campsites; every facility (toilets and whether flush or non-flush, showers and whether hot, drinking water, barbecues and their type, picnic tables, camp kitchen, powered sites, rubbish bins, firewood, kiosk, playground); whether campfires, generators and pets are allowed; whether you can swim there; the Accessibility section; camping fees per night and how they are charged; park entry fees; whether booking is required and the booking link; any closure, seasonal closure or alert; the street address or nearest locality; and any latitude and longitude (including numbers inside a 'Get directions' or map link). Do not summarise or leave items out. Do not include phone numbers, email addresses or staff names.

   NPWS 的营地费常常不在这一页上（在预订页里）：页面没写就不填 camp_fee，不要另外去猜。

7. 按第三、四节写成 JSON，一条条添加（校验不过不会加进去）：

```bash
python3 place_data_tool.py add data/camps/au-nsw-npws-sydney-01.jsonl <<'EOF'
{"id": "au-nsw-npws-sydney-camp-……", "kind": "camp", ……}
EOF
```

8. 每做 10 个，跑一次 `python3 place_data_tool.py stats data/camps/<本次文件>`，看 A 类覆盖。
9. **做满 30 个营地，或者这一批做完，就停。** 连着 5 个页面打不开也停，在 notes 里写原因。

**收尾**

10. `python3 place_data_tool.py validate data/camps/<本次文件>`：错误改完，警告可以留。
11. 更新 camp_batches.csv 这一行：files 加 1，camps 写累计数，last_date 写今天，notes 写下次从哪继续；这一批全做完 status 改 done，做不了写 blocked。
12. **不要跑 tools/publish.py。** 直接提交并推送：`git add -A && git commit -m "露营地数据：<批次>（<N> 个营地）" && git -c push.negotiate=true push`。推送被拒就 `git pull --rebase` 再推，有冲突停下来汇报。
13. 用中文汇报：做的哪一批、几个营地、A 类平均覆盖、多少个有坐标、哪些页面打不开、还剩什么。

## 六、给 Sonnet 的开工提示词（每次新开对话时复制粘贴）

在「app」项目里新开对话，模型选 Sonnet：

```
请帮我收集悉尼周边政府管的露营地数据（国家公园、州森林、council 自营的营地）。数据和规则都在 GitHub 仓库 sasuke9527/parkapp-data：先用 add_repo 接上它（access 选 push）、clone 下来，读仓库里的 RULES-CAMP.md 和 RULES.md 的第四节、第十节，然后严格按 RULES-CAMP.md 第五节的流程做：准备、选批次、收集、收尾（提交、推送）。

铁律：只记事实和来源链接；页面没写的不写；不抄原文、不存照片；只用管理机构自己的官网，不用 WikiCamps、Hipcamp、Google 地图、Facebook、旅游网站这类来源；坐标页面上没有就写 null，不要估；不记电话、邮箱和工作人员的名字；网站不让访问就不绕过。不要跑 tools/publish.py。

这次做满 30 个营地或者这一批做完就停，更新 camp_batches.csv，提交并推送到 GitHub，然后用中文向我汇报。
```

## 七、收完以后（Opus 的活）

1. App 1.1：「去哪玩」加「露营」一栏（列表、详情、按怎么住和设施筛选）；详情和泳池、图书馆一样是 Pro。
2. 发布：露营地单独打包成 docs/camps.json，在 manifest.json 里另加一栏。**不要把 kind=camp 放进 places.json**：1.0 版 App 不认识这个 kind，会整份读不出来。
3. 没有坐标的营地：用公园数据里同一个国家公园的位置（来自 OpenStreetMap）定个大概，界面上写「大约」。
4. 营地费、开闭状态一年核一次，并进季度复查（建议每年春季那一轮）。

---

*最后更新：2026-11-22*
