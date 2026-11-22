# 露营地数据：格式与填写说明（v3 · 2026-11-22）

> 「去哪玩」下一步要加的一类：悉尼周边开车两三小时内的露营地，**政府管的为主，私营和连锁的也收，但必须标明是非政府经营**（operator_type=private，并写 operator）。这份说明写给 **Sonnet**（照着收集）和 **Opus**（做 App 时读）。
> 通用的规矩（只记事实、页面没写不写、坐标不估、不记联系人、哪些网站不能用）和泳池、图书馆一样，在 RULES.md 第四节和第十节，**先读那两节**。这里只写露营地不一样的地方。
> **现在只收集、不发布**：露营地放在 `data/camps/`，打包和发布脚本（tools/）不读这个文件夹，所以已经上架的 App 1.0 不受影响。**收露营地时不要跑 tools/publish.py。** 等 App 1.1 能显示露营地了，再由 Opus 接上发布。

## 一、收什么、不收什么

| 收 | 不收 |
|---|---|
| NSW 国家公园（NPWS）网站上的 campground | 小屋、别墅、豪华帐篷（cabins、cottages、glamping、lodges） |
| NSW 州森林（Forestry Corporation）网站上的 camping area | 页面写明没有营位、只有小屋的公园（例 The Palms at Avoca） |
| council、联邦或州政府机构**自己经营**的 camping area / tourist park（第 6 批点了名的） | 以长住租户或站点持有人为主、几乎没有游客营位的公园（例 Leetsvale） |
| **非政府经营**的 holiday park / caravan park / 营地（第 7–10 批：NRMA、BIG4 站上挂牌的公园、G’day Group（Discovery Parks 和 G’day Parks）、Hampshire Holidays、Belgravia、独立公园）。**必须**写 operator_type=private 和 operator | Hipcamp、Youcamp 这类私人土地营地（只有平台页，没有自己的官网） |
| | 只能住房车、不让搭帐篷的 rest area |

**政府还是私营，按官网写的经营方判断**：议会拥有、但交给私人公司管的（例 NRMA 管的 Shellharbour Beachside、Belgravia 管的 Katoomba Falls）算私营，operator 写官网上的经营方名字。官网没写经营方的，operator 写公园自己的名字。同一个公园在两家运营商网站上都有，先收一条，status 写 needs_check，operator 把两家都写上。

**能用的来源**：管这个营地的机构自己的官网页面（nationalparks.nsw.gov.au、forestrycorporation.com.au、council 官网、harbourtrust.gov.au、waternsw.com.au 等）。**非政府营地**用运营商或这个公园自己的官网，来源 type 写 operator；BIG4 网站上挂牌、但不是 BIG4 品牌的公园（Ingenia、Eureka 和独立公园）写 other。**只用页面上的事实，客人评论一律不用**。
**不能用的来源**：WikiCamps、CamperMate、Anycamp、Hipcamp、Tripadvisor、Google 地图、Facebook、博客、旅游网站（visitnsw.com、sydney.com 也不用，它们是转述）。

**网站让不让抓**：
- nationalparks.nsw.gov.au 的 robots.txt（2026-11-22 看过）允许 /camping-and-accommodation/ 和 /sitemap.xml。**NPWS 的搜索页只显示前 10 条，但 sitemap 里列了全部 375 个 campground 页面**，所以按 sitemap 核对就能收全，不用翻页。
- 别的网站**第一次用时先看 robots.txt**（浏览器打开 `<站>/robots.txt`）。写了 Disallow: / 或点名禁止 ClaudeBot、anthropic-ai、Claude-Web（Cloudflare 的 Content-Signal 也算）的，这个站不让 Anthropic 的程序读：**不读它的页面**，这一块标 blocked 并向我汇报（2026-11-22 查到的：Patonga 的订位站 cchp.com.au）。robots.txt 打不开、或被带到登录页（WaterNSW）的，同样不读，除非 WebFetch 能直接读到那一页。
- 2026-11-22 看过、允许读取的：NPWS、Forestry Corporation、Holiday Haven、Kiama Coast、Wollongong、Booderee、Cockatoo Island、Hawkesbury、Central Coast 议会、Blue Mountains 议会、Lake Mac Holiday Parks、NRMA、BIG4、Discovery Parks、G’day Parks、Reflections、Hampshire Holidays、Katoomba Falls 和 Blackheath Glen（Belgravia）、Del Rio、Blue Lagoon、Walu。
- WebFetch 打不开、被拒或返回 403 的，就**不绕过**：这一批在 camp_batches.csv 里标 blocked，notes 写原因，向我汇报。
- robots.txt 只管「让不让程序读」，**版权和使用条款是另一回事**：每个新网站第一次用时，除了 robots.txt，还要看它的版权页或使用条款（页脚的 Copyright / Disclaimer / Terms），结论按下面「一·B」处理。

## 一·B、版权受限的来源：只收名称和地点（用户要求 2026-11-22 起）

**规矩**：来源网站的版权页或使用条款写了「要先取得许可才能：收费给别人用、放进销售的产品、复制或转载、商用」之类的，这个来源的营地**只收名称和地点，不收设施、价格、季节、预订等细节**。App 的 Pro 是收费的，所以按「放进销售产品」处理。

**怎么写（detail_policy=official_only）**：
- 留下：id、kind、name、area、park、suburb、address、lat、lon（地点）、operator / operator_type（私营的要标）、aka、sources（只放这个营地自己的页面）、checked、status。
- 加两个字段：`"detail_policy": "official_only"` 和 `"official_url"`（官网上这个营地的页面）。
- `facts` 写 `[]`；不写 booking、booking_url、season；`note_zh` 必须用固定提示语（工具会校验，App 直接显示它，旁边放「访问官网」按钮，链接是 official_url）：**该来源有版权要求，本 App 只收录名称和地点，详细信息请访问官网。**
- 名称和坐标、地址是事实，不是官网的表述，所以保留；页面上的介绍、设施清单、价格都不要。
- 之前收过的详细版本（提交 6509a0b）还在 git 历史里；将来取得许可，可以从那里恢复。

**2026-11-22 核对结果**（只看了条款页，不是法律意见）：

| 网站 | 条款页 | 怎么写的 | 处理 |
|---|---|---|---|
| nationalparks.nsw.gov.au（NPWS） | /copyright-disclaimer、/terms-of-use | 文字按 CC BY 4.0，但收费给别人用、放进销售产品、修改要先取得许可；使用条款写只限个人非商业使用 | official_only |
| forestrycorporation.com.au | /about/copyright | 收费（成本价除外）、放进销售产品、转载到别的网站要先取得许可 | official_only |
| lakemacholidayparks.com.au | /disclaimer/ | 不得商用或公开使用，其他用途要议会书面许可 | official_only |
| wollongongtouristparks.com.au | /website-terms/ | 没有书面授权不得复制、改编、转载 | official_only |
| bmcc.nsw.gov.au | /about-us/disclaimer | 不得转载、改编或用于任何商业目的 | official_only |
| hawkesbury.nsw.gov.au | /footer-links/disclaimer | 只限个人、内部或非商业使用，不得商业化 | official_only |
| discoveryholidayparks.com.au、gdayparks.com.au | /terms-and-conditions（第 7 条） | 禁止商用、复制转载，**也禁止用程序或自动方式读取页面** | official_only；这两家以后不再用程序读 |
| nrmaparksandresorts.com.au | /terms-conditions-and-policies/ | 列出的条款是预订、公园规则、隐私等，没找到网站使用或版权条款 | 暂保留详细信息，待确认 |
| big4.com.au | /terms-and-conditions | 页面动态加载，没找到网站使用条款 | 暂保留，待确认 |
| hampshireholidays.com.au | /terms-and-conditions | 条款里没有版权或转载的内容 | 暂保留，待确认 |
| holidayhaven.com.au、kiamacoast.com.au | — | 没找到条款页 | 暂保留，待确认 |
| centralcoast.nsw.gov.au、booderee.gov.au、cockatooisland.gov.au、waternsw.com.au | — | 没找到网站使用条款（Cockatoo Island 的是住宿预订条款；WaterNSW 的 robots 读不到） | 暂保留，待确认 |
| 其余独立公园（Belgravia 的两个、Del Rio、Blue Lagoon、Walu） | — | 没查 | 暂保留，待确认 |

「暂保留，待确认」的只是**没找到限制**，不等于没有；这些站在发布前要再核对一遍（或联系对方），一旦发现有限制，用同样的方法改成 official_only。新加的网站按上面的流程先查条款再收。

## 二、文件

| 文件 | 作用 | 谁改 |
|---|---|---|
| RULES-CAMP.md | 本说明 | Opus |
| camp_codes.csv | 露营地的设施词表 | Opus（Sonnet 不改） |
| camp_batches.csv | 批次清单：16 批（第 7–10 批是非政府经营的营地；第 11–16 批是远处的 NPWS 营地，只收名称和地点），按 order 做 | Sonnet |
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
| lat / lon |  | **页面上写了才填，不要估**，不知道写 null。页面自己的 Get directions 或地图链接里带的经纬度、页面里嵌的 latitude/longitude 数据（BIG4、Discovery、G’day 的页面有）、JSON-LD 的 geo 算页面写了的。**只给了 Google 地图链接的不用**，写 null |
| operator |  | 不是管理机构自己经营时，官网写的经营方名字。**operator_type 是 private 时必填** |
| operator_type |  | government（政府自己经营，默认）/ private（非政府经营：私营、连锁、council 外包给私人公司的）。**非政府的一定要写 private** |
| booking |  | required（要预订）/ recommended（建议预订）/ none（不用订，先到先得）；页面没说就不写 |
| booking_url |  | 官网上的预订页面链接 |
| season |  | 只在某几个月开：{"from": "09-01", "to": "04-30"}，可以加 ev |
| sources | ✓ | 第一个放这个营地自己的页面。type：NPWS、州森林、WaterNSW 写 state_gov；council 写 council；Harbour Trust 写 federal_gov；运营商或公园自己的官网写 operator；BIG4 网站上的非 BIG4 品牌公园写 other |
| facts | ✓ | 见第四节；什么都没查到写 [] |
| checked | ✓ | 查的当天，YYYY-MM-DD |
| status | ✓ | ok / needs_check（页面自相矛盾）/ temporarily_closed（页面写了现在关闭）/ seasonal_closed / under_construction |
| note_zh |  | 一句中文备注，自己的话，最多 80 个字符：大门几点锁、要走多远、现在为什么关 |
| aka |  | 别名列表（例 原来的名字：Camden Holiday Park 的 aka 写 ["Poplar Tourist Park"]） |
| detail_policy |  | 来源有版权要求时写 official_only（见「一·B」）：facts 写 []，不写 booking / booking_url / season，note_zh 用固定提示语 |
| official_url | detail_policy 时必填 | 官网上这个营地的页面，App 的「访问官网」按钮用它 |

版权受限的营地长这样（**虚构的示例，别抄进数据**）：

```json
{
  "id": "au-nsw-npws-north-coast-camp-example-beach-campground",
  "kind": "camp",
  "name": "Example Beach campground",
  "area": "npws-north-coast",
  "park": "Example National Park",
  "suburb": "Example Heads",
  "address": "1 Example Road, Example Heads, NSW 2000",
  "lat": -30.1,
  "lon": 153.0,
  "operator_type": "government",
  "detail_policy": "official_only",
  "official_url": "https://example.org/camping/example-beach",
  "sources": [{"type": "state_gov", "url": "https://example.org/camping/example-beach"}],
  "facts": [],
  "checked": "2026-11-22",
  "status": "ok",
  "note_zh": "该来源有版权要求，本 App 只收录名称和地点，详细信息请访问官网。"
}
```

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

5. **先列清单**：用网页搜索找到这一批的列表页（NPWS：Camping and accommodation 里按地区筛的 campground 列表；第 3、4、5 批按批次名字里点名的公园或森林，一个个找它的 camping 页面；第 7–10 批按运营商的公园列表或 sitemap，只收悉尼周边约 160km 内的），这样问 WebFetch：

> List every campground or camping area linked on this page with its name, the park or forest it is in, and its full URL. Only include places where you can camp in a tent, camper trailer, caravan or campervan. Do not include cabins, cottages, lodges or glamping.

   列表有翻页或「Load more」拿不全时：NPWS 用 https://www.nationalparks.nsw.gov.au/sitemap.xml 核对全部 campground 页面（robots 允许）；别的站用它自己的 sitemap.xml；都没有再改用网页搜索「<公园名> campground NSW National Parks」一个公园一个公园补，只开官网的结果。清单写进 notes，方便下次接着做。

6. （先看「一·B」：这个来源的条款要求许可的，只收名称和地点，不用读设施。）**再一个个开营地页面**。WebFetch 打不开或字段读不全时，用 Claude 内置浏览器：先 request_access，打开 `<站>/robots.txt` 确认允许，再在页面里用 JavaScript fetch 同站页面并解析（每次请求间隔 0.4–0.6 秒，不要并发；单次脚本别超过约 45 秒；只打印需要的一小段）。BIG4、Discovery、G’day 的页面里有 JSON-LD（名字、地址、petsAllowed、设施清单）和 latitude/longitude；Discovery 和 G’day 的正文用 `document.body.textContent`（`main` 里是空占位）；页面里的客人评论不用。WebFetch 可以这样问：

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
请帮我收集悉尼周边的露营地数据（政府管的：国家公园、州森林、council 自营的营地；也收非政府经营的私营和连锁营地，但要标明是非政府经营）。数据和规则都在 GitHub 仓库 sasuke9527/parkapp-data：先用 add_repo 接上它（access 选 push）、clone 下来，读仓库里的 RULES-CAMP.md 和 RULES.md 的第四节、第十节，然后严格按 RULES-CAMP.md 第五节的流程做：准备、选批次、收集、收尾（提交、推送）。

铁律：只记事实和来源链接；页面没写的不写；不抄原文、不存照片；只用管理机构或运营商自己的官网，不用 WikiCamps、Hipcamp、Google 地图、Google 评论、Facebook、旅游网站、客人评论这类来源；坐标页面上没有就写 null，不要估；不记电话、邮箱和工作人员的名字；网站不让访问就不绕过（robots.txt 禁止 Claude 的程序读的，不读，标 blocked 并汇报）。新网站先看它的版权页或使用条款：要求先取得许可的，只收名称和地点（RULES-CAMP.md 第一·B 节，detail_policy=official_only）。非政府经营的营地要写 operator_type=private 和 operator。不要跑 tools/publish.py。

这次做满 30 个营地或者这一批做完就停，更新 camp_batches.csv，提交并推送到 GitHub，然后用中文向我汇报。
```

## 七、收完以后（Opus 的活）

1. App 1.1：「去哪玩」加「露营」一栏（列表、详情、按怎么住和设施筛选）；详情和泳池、图书馆一样是 Pro。
2. 发布：露营地单独打包成 docs/camps.json，在 manifest.json 里另加一栏。**不要把 kind=camp 放进 places.json**：1.0 版 App 不认识这个 kind，会整份读不出来。
3. 没有坐标的营地：用公园数据里同一个国家公园的位置（来自 OpenStreetMap）定个大概，界面上写「大约」。
4. 营地费、开闭状态一年核一次，并进季度复查（建议每年春季那一轮）。
5. App 显示：detail_policy=official_only 的营地只显示名称、公园、地点、地图位置，加固定提示语（note_zh）和「访问官网」按钮（official_url）；这类营地不参加按设施的筛选。
6. 「暂保留，待确认」的来源（NRMA、BIG4、Hampshire、Holiday Haven 等）发布前再核对一次条款，必要时联系对方。NPWS 如果书面同意收费使用，可以从 git 提交 6509a0b 恢复详细版本。

---

*最后更新：2026-11-22（v3：版权受限来源只收名称和地点、条款核对结果、远处 NPWS 营地）*
