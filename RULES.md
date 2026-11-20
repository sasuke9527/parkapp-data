# 去哪玩数据：格式与填写说明（v2 · 2026-11-20）

> 这份说明写给四方看：**你**（了解格式）、**Sonnet**（照着收集数据）、**定时任务**（照着季度复查）、**Opus**（做 App 时读）。
> 「去哪玩」是公园 App 里新加的一栏，管公园以外带娃常去的地方：**游泳池**、**图书馆**（以及讲故事这类每周固定的亲子活动）、**学校假期活动**、**下水点**（海滩、海水池、港湾网池、河湖游泳点）和下水点的**实时水质**。
> **数据放在哪**：2026-11-20 起放在 GitHub 仓库 **sasuke9527/parkapp-data**，以它为准。这份说明在仓库里叫 RULES.md，在 claude.ai 项目「app」里是 claude/park-data/README-去哪玩数据格式与填写说明.md，两份一样，改的时候一起改。项目里 claude/park-data/ 下的 place_batches.csv、data/ 等是 11 月 20 日的旧副本，不再更新。
> **App 怎么拿到数据**：App 里带一份；另外每天读一次 GitHub Pages 上的 https://sasuke9527.github.io/parkapp-data/manifest.json，有新版本就下载，**不用等 App 发新版**。发布用 tools/publish.py（第十六节）。
> **谁在改**：新 council 的第一次收集由 Sonnet 对话做（第十一、十二节）；已经收过的，由定时任务「去哪玩数据季度复查」在每个学校假期前三四周复查一轮，顺便收这个假期的活动（第十五节）。
> 实时水质的代码写好了但关着（第九节），收集时不用管。公园数据的说明在 claude/park-data/README-数据格式与填写说明.md，这里的格式尽量和它一样。

## 一、收什么、不收什么

| 类别 | 收 | 不收 |
|---|---|---|
| 游泳池 | council 的游泳池、水上中心；council 委托运营方的官网（从 council 页面链接过去的）；州政府管的公共泳池 | 私人健身房、酒店、学校和大学的泳池；商业游泳学校自己的场地 |
| 图书馆 | council 的公共图书馆，**每个分馆一条** | 学校、大学图书馆 |
| 固定活动 | 图书馆每周固定的亲子活动：讲故事、儿歌律动、幼儿时间、双语讲故事、乐高、手工、科学 | 一次性的活动（放进假期活动）；要登录才能看的日程 |
| 假期活动 | council、council 图书馆、council 泳池、州政府机构（博物馆、植物园、公园机构等）**自己主办**的学校假期活动 | 商业营地、私人兴趣班；council 网站只是转登的商业活动；只在社交媒体上发的活动 |
| 下水点 | council 或州政府网站列出的海滩、海水池（ocean pool / rock pool / baths）、港湾网池（netted harbour pool）、政府标明可以游泳的河湖游泳点 | 没有官方说可以游的野泳点 |

和公园数据分开记：同一片海滩在公园数据里有（type 是 foreshore_beach），这里照样记一条下水点。

## 二、文件

| 文件（都在 GitHub 仓库 sasuke9527/parkapp-data 里） | 作用 | 谁改 |
|---|---|---|
| RULES.md | 本说明 | 你 / Opus |
| README.md | 仓库的简介 | Opus |
| place_codes.csv | **设施词表**：每个设施的代码、中文名、填法、怎么判断 | 你 / Opus（Sonnet、定时任务不改） |
| place_batches.csv | **批次清单**：第 0 条是学期日期，后面是 33 个 council，按 order 做，记录第一次收集的进度；最后三列 round、events_round、round_date 记季度复查做到哪一轮（第十五节） | Sonnet、定时任务 |
| runs.csv | 定时任务每次干了什么：日期、轮次、做了哪些 council、开了几个网页、改了几条、发布的版本 | 定时任务 |
| place_data_tool.py | 工具：自检、添加、校验、统计（只用 Python 自带的库） | 不改 |
| data/places/au-nsw-<slug>-<序号>.jsonl | 游泳池、图书馆、下水点，每行一个去处 | Sonnet、定时任务 |
| data/sessions/au-nsw-<slug>-<序号>.jsonl | 图书馆的固定活动，每行一个「每周几点」 | Sonnet、定时任务 |
| data/events/au-nsw-<slug>-<假期开始的年月>.jsonl | 学校假期活动，每行一个活动（例 au-nsw-hornsby-2026-12.jsonl） | Sonnet、定时任务 |
| data/school_terms.json | NSW 公立学校学期日期 | Sonnet（第 0 批）、定时任务（每年 11–12 月那一轮补下一年） |
| tools/build_places_data.py | 打包：校验全部数据，生成 App 读的 places.json | 不改 |
| tools/publish.py | 发布：打包 → 安全检查 → 写 docs/places.json 和 docs/manifest.json（第十六节） | 不改 |
| tools/round.py | 季度复查：现在是哪一轮、在不在窗口里、还有哪些 council 要做 | 不改 |
| docs/ | GitHub Pages 发布的内容，App 读这里；只由 publish.py 写 | publish.py |

> 记录类型看文件放在哪个文件夹：places / sessions / events。工具和打包脚本都按文件夹认，放错了会报一堆错。

## 三、一个去处的格式（游泳池 / 图书馆 / 下水点）

文件里**每行一个去处**（一个 JSON）。下面为了好读排成了多行。**这是虚构的示例，别抄进数据**（工具会拦住带 example 的 id 和链接）：

```json
{
  "id": "au-nsw-hornsby-pool-example-aquatic-centre",
  "kind": "pool",
  "name": "Example Aquatic Centre",
  "council": "hornsby",
  "suburb": "Example Heights",
  "address": "1 Example Road",
  "lat": null,
  "lon": null,
  "operator": "Example Leisure",
  "sources": [
    {"type": "council", "url": "https://example.org/aquatic-centre"},
    {"type": "operator", "url": "https://example.org/operator/aquatic-centre"}
  ],
  "facts": [
    {"code": "pool_50m", "value": "yes", "ev": "50m outdoor pool"},
    {"code": "outdoor_pool", "value": "yes"},
    {"code": "heated", "value": "yes", "ev": "heated 25m indoor pool", "src": 1},
    {"code": "toddler_pool", "value": "yes"},
    {"code": "parking", "value": ["free_carpark"]},
    {"code": "entry_price", "value": "Adult $6.50; Child $5.00", "src": 1}
  ],
  "hours": [
    {"days": "mon-fri", "open": "05:30", "close": "20:00"},
    {"days": "sat,sun", "open": "07:00", "close": "18:00"},
    {"days": "public_holiday", "closed": true}
  ],
  "season": {"from": "09-01", "to": "04-30", "ev": "Outdoor pool open September to April"},
  "checked": "2026-11-20",
  "status": "ok",
  "note_zh": "室外 50 米池按季节开，室内池全年开"
}
```

下水点多两个字段：`"spot_type": "ocean_pool"`，以及可选的 `"beachwatch": "<Beachwatch 网站上这个点的名字>"`。

### 去处字段

| 字段 | 必填 | 怎么写 |
|---|---|---|
| id | ✓ | au-nsw-<council>-<kind>-<名字>：只用小写英文、数字、连字符。例 au-nsw-hornsby-pool-galston-aquatic-centre、au-nsw-hornsby-library-pennant-hills。撇号去掉，& 写成 and |
| kind | ✓ | pool（游泳池）/ library（图书馆）/ swim（下水点） |
| name | ✓ | 官网上的英文名 |
| council | ✓ | 所在 council 的 slug（place_batches.csv 里的）。州政府管的场馆也写所在的 council |
| suburb | ✓ | 所在 suburb |
| address |  | 街道地址，照来源写 |
| lat / lon |  | **页面上写了才填，不要估**；不知道就写 null |
| spot_type | 下水点必填 | beach（海滩）/ ocean_pool（海水池、rock pool、baths）/ harbour_pool（港湾网池）/ river_lake（河湖游泳点）。其他两类不写 |
| operator |  | 运营方的名字，官网写了才填（例如 council 委托的公司） |
| beachwatch |  | 只有下水点写：这个点在 Beachwatch 网站上的名字，照网站写，用来对实时水质；找不到就不写 |
| sources | ✓ | 来源列表，第一个放主要页面。type 可选 council / library / state_gov / federal_gov / open_data / operator / other |
| facts | ✓ | 设施事实列表（见第四、五节）；什么都没查到就写 [] |
| hours |  | 开放时间（见下） |
| season |  | 季节性开放（室外池）：{"from": "09-01", "to": "04-30"}，月-日，可以跨年，可以加 ev |
| checked | ✓ | 查的日期，YYYY-MM-DD（当天） |
| status | ✓ | ok / needs_check（来源互相矛盾）/ temporarily_closed / seasonal_closed / under_construction |
| note_zh |  | 一句中文备注，用自己的话写，最多 80 个字符 |
| aka |  | 别名列表 |

### 开放时间（hours）怎么写

- 每条写一段：{"days": "mon-fri", "open": "05:30", "close": "20:00"}。时间用 24 小时制 HH:MM。
- days 可以写：mon、tue、wed、thu、fri、sat、sun；范围 mon-fri；几天用逗号 sat,sun；还有 daily、weekdays、weekends、public_holiday。
- 中午休息、一天分两段的，写两条（同一个 days）。
- 某天不开：{"days": "tue", "closed": true}。公众假期单独写一条。
- 不收过夜的时间（close 必须晚于 open）。
- 夏季、冬季时间不同的，**只记现在这一季的**，在 note_zh 里写「冬季时间」之类。圣诞节等个别日子的临时安排不记。
- 页面没写开放时间就不写 hours——App 会显示「开放时间未知」，不会猜。

## 四、一条事实（fact）怎么写

和公园数据一样：

| 字段 | 必填 | 说明 |
|---|---|---|
| code | ✓ | 设施代码，见第五节或 place_codes.csv |
| value | ✓ | 按类型写（见下表） |
| src |  | 来自 sources 里的第几个，从 0 数；不写就是 0 |
| ev |  | 证据：页面上的原话片段（英文，最多 120 个字符），方便以后核对 |
| conf |  | 把握程度 high / medium / low |

| 类型 | value 怎么写 | 例子 |
|---|---|---|
| 有/没有 | "yes" 或 "no" | {"code": "toilet", "value": "yes"} |
| 全/部分/没有 | "full" / "partial" / "none" | {"code": "shade", "value": "partial"} |
| 多选 | 列表，可以有多个 | {"code": "parking", "value": ["free_carpark", "street"]} |
| 文字 | 短文字，最多 120 个字符 | {"code": "patrolled", "value": "Sep–Apr 8am–6pm"} |

**页面没提到的设施，就不写这一条**——不写就等于「未知」。只有页面明确说没有，才写 "no" 或 "none"。

## 五、设施词表（A = 每个去处都要找；B = 看到了就记）

想在终端里看：python3 place_data_tool.py codes --kind pool（或 library、swim）。

| 代码 | 中文名 | 用在 | 填法 | 优先 | 怎么判断 |
|---|---|---|---|---|---|
| toilet | 厕所 | 都用 | 有/没有 | A | 在场馆里或紧挨着（同一个停车场）才算 |
| accessible_toilet | 无障碍厕所 | 都用 | 有/没有 | B |  |
| baby_change | 换尿布台 | 都用 | 有/没有 | A |  |
| parents_room | 母婴室 / 哺乳室 | 都用 | 有/没有 | B | 单独的房间，不只是厕所里的台子 |
| parking | 停车 | 都用 | 多选：free_carpark / paid_carpark / street / none | A | 自带免费停车场 free_carpark；收费 paid_carpark；只能路边停 street；可多选 |
| cafe_kiosk | 咖啡 / 小卖部 | 都用 | 有/没有 | B | 场馆里面或沙滩上的才算；附近的写在 note_zh |
| drinking_water | 饮水机 | 都用 | 有/没有 | B |  |
| near_station | 附近车站 | 都用 | 文字 | B | 来源写的车站名 |
| step_free | 不用走台阶（婴儿车、轮椅能进） | 都用 | 有/没有 | A | 来源写入口 step-free、level access、ramp access、wheelchair accessible entrance 才写 yes；写了只有楼梯（stairs only、steps to entrance）写 no；只说厕所、车位无障碍的不算；只写「有铺装小路」也不算 |
| pool_50m | 50 米池 | 游泳池 | 有/没有 | A |  |
| pool_25m | 25 米池 | 游泳池 | 有/没有 | A |  |
| indoor_pool | 室内池 | 游泳池 | 有/没有 | A |  |
| outdoor_pool | 室外池 | 游泳池 | 有/没有 | A |  |
| heated | 加热 / 恒温 | 游泳池 | 有/没有 | A | 来源写 heated 或 temperature controlled 才写 yes；只有某个池加热的在 ev 里写是哪个 |
| toddler_pool | 幼儿浅水池 | 游泳池 | 有/没有 | A | toddler pool、wading pool、baby pool、learners pool 都算 |
| leisure_pool | 戏水池 / 休闲池 | 游泳池 | 有/没有 | A | leisure pool、play pool；专门上课用的 program pool 不算 |
| splash_pad | 喷水乐园 | 游泳池 | 有/没有 | A | splash pad、water play area、aqua play、spray ground |
| waterslide | 水滑梯 | 游泳池 | 有/没有 | B |  |
| learn_to_swim | 游泳课 | 游泳池 | 有/没有 | A | 来源写 learn to swim 或 swim school；只写成人训练的不算 |
| pool_hoist | 下水升降椅 | 游泳池 | 有/没有 | B |  |
| pool_ramp | 下水坡道 | 游泳池 | 有/没有 | B |  |
| spa_sauna | 按摩池 / 桑拿 / 蒸汽房 | 游泳池 | 有/没有 | B |  |
| entry_price | 门票 | 游泳池 | 文字 | B | 照来源写，最多 120 个字符，例 Adult $6.50; Child $5.00；价格每年变，checked 一定要写当天 |
| kids_area | 儿童区 | 图书馆 | 有/没有 | A | 有专门给小孩的区域、书架或游戏角 |
| language_collection | 外语书 | 图书馆 | 多选：zh / ko / ja / hi / es / vi / ar / other | A | 来源写有哪种语言的馆藏：中文 zh、韩文 ko、日文 ja、印地文 hi、西班牙文 es、越南文 vi、阿拉伯文 ar，其他写 other；可多选 |
| toy_library | 玩具图书馆 | 图书馆 | 有/没有 | B | 能借玩具的 |
| patrolled | 救生员巡逻 | 下水点 | 文字 | A | 照来源写季节和时间，例 Sep–Apr 8am–6pm；来源没写就不填 |
| netted | 防鲨网 | 下水点 | 有/没有 | A | 港湾网池写 yes |
| ocean_pool_cleaning | 海水池清洁日 | 下水点 | 文字 | A | 照来源写，例 Closed Thursday mornings for cleaning |
| shower | 淋浴 | 下水点 | 有/没有 | A |  |
| change_rooms | 更衣室 | 下水点 | 有/没有 | B |  |
| shallow_area | 小孩浅水区 | 下水点 | 有/没有 | B | 海水池里单独的浅水池、或来源说适合小孩的浅水区 |
| beach_access_mat | 沙滩通道垫 / 沙滩轮椅 | 下水点 | 有/没有 | B |  |
| shade | 阴凉 | 下水点 | 全/部分/没有：full / partial / none | B | 大部分地方有阴凉写 full；一部分写 partial；来源明确说没阴凉写 none |
| dogs | 狗 | 下水点 | 多选：prohibited / on_leash / off_leash_area / off_leash_time_shared | B | 和公园的写法一样：禁止 prohibited；要拴绳 on_leash；有无绳区 off_leash_area；某些时段可以不拴 off_leash_time_shared |

**关于 step_free（不用走台阶）**：公园的「推婴儿车散步」原来只看「有没有硬化步道」，结果 Lisgar Gardens 这种入口有一段陡楼梯的花园也被筛了出来（2026-11-20 已改：公园词表也加了 step_free，App 里还能让去过的人回答「婴儿车能直接推进去吗」）。这里同样：页面明确写了 step-free、level access、ramp access、wheelchair accessible entrance 才写 yes；写了只有楼梯才写 no；**只写「有铺装小路」不算，只说厕所无障碍也不算**。

## 六、图书馆固定活动（sessions）的格式

每行一个「每周几点」：一周有两次的（周二、周四），拆成两条。

```json
{
  "id": "au-nsw-hornsby-library-example-branch-rhyme-time-tue",
  "place": "au-nsw-hornsby-library-example-branch",
  "title": "Rhyme Time",
  "type": "rhyme_time",
  "weekday": "tue",
  "start": "10:30",
  "end": "11:00",
  "age_min_months": 0,
  "age_max_months": 24,
  "language": "en",
  "term_only": true,
  "booking": "none",
  "cost": "free",
  "sources": [{"type": "library", "url": "https://example.org/library/whats-on"}],
  "checked": "2026-11-20"
}
```

| 字段 | 必填 | 怎么写 |
|---|---|---|
| id | ✓ | <图书馆的 id>-<活动简称>-<星期>，例 …-library-pennant-hills-storytime-wed |
| place | ✓ | 图书馆的 id（这个图书馆要先在 data/places 里登记） |
| title | ✓ | 官网上的活动名（英文，最多 100 个字符） |
| type | ✓ | storytime（讲故事）/ rhyme_time（儿歌律动）/ toddler_time（幼儿时间）/ bilingual_storytime（双语讲故事）/ lego_club / craft（手工）/ stem（科学）/ other |
| weekday | ✓ | mon / tue / wed / thu / fri / sat / sun |
| start / end | start ✓ | 24 小时制 HH:MM；页面没写结束时间就不写 end |
| age_min_months / age_max_months |  | 适合年龄，**按月写**（2 岁写 24，5 岁写 60）；页面写了才填 |
| language |  | en / zh / ko / ja / hi / es / vi / ar / other；双语写 en+zh |
| term_only |  | 页面说「只在学期内」（during school term、term time only）才写 true |
| booking |  | none（不用报名）/ required（要报名）/ recommended（建议报名） |
| cost |  | 免费写 "free"；收费照来源写价钱（最多 40 个字符） |
| valid_from / valid_to |  | 页面写了有效期（例如只到某个日期）才写，YYYY-MM-DD |
| sources / checked | ✓ | 同上 |
| note_zh |  | 一句中文备注 |

只收**写清楚每周哪天几点**的活动。只写「most Tuesdays」「check our calendar」这类说不清的，不收，在 place_batches.csv 的 notes 里记一句。

## 七、学校假期活动（events）的格式

```json
{
  "id": "au-nsw-hornsby-event-example-craft-2027-01-12",
  "title": "Example Holiday Craft",
  "council": "hornsby",
  "place": "au-nsw-hornsby-library-example-branch",
  "dates": [
    {"date": "2027-01-12", "start": "10:00", "end": "11:00"},
    {"date": "2027-01-14", "start": "10:00", "end": "11:00"}
  ],
  "age_min": 5,
  "age_max": 12,
  "cost": "free",
  "booking": "required",
  "booking_url": "https://example.org/booking/123",
  "sources": [{"type": "council", "url": "https://example.org/school-holidays"}],
  "checked": "2026-11-20"
}
```

| 字段 | 必填 | 怎么写 |
|---|---|---|
| id | ✓ | au-nsw-<council>-event-<活动简称>-<第一天的日期> |
| title | ✓ | 官网上的活动名（英文，最多 100 个字符） |
| council | ✓ | 主办方所在 council 的 slug；州政府机构办的写场馆所在的 council |
| place / venue | 至少一个 | 在已登记的泳池、图书馆办的写 place（去处的 id）；别的地方写 venue（地点名） |
| suburb |  | 地点所在 suburb |
| dates | ✓ | 一天一条：{"date": "YYYY-MM-DD", "start": "10:00", "end": "11:00"}；时间没写就只写 date |
| age_min / age_max |  | 适合年龄，**按岁写** |
| cost / booking |  | 同第六节 |
| booking_url |  | 报名链接。Eventbrite、Humanitix、TryBooking、Ticketek、Ticketmaster 这类报名平台**只能放在这里**，不能当来源 |
| holiday |  | 可选：哪个假期，写成 2026-summer、2027-autumn、2027-winter、2027-spring（只是方便整理） |
| sources / checked / note_zh |  | 同上（sources、checked 必填） |

- 只收**下一个**（或正在进行的）学校假期的活动，页面还没公布的不收。每个假期开始前 2–4 周收一轮。
- 结束 30 天以上的活动，打包时自动不放进 App；文件留着不用删。

## 八、学期日期（data/school_terms.json）

App 用它算「现在是不是学校假期」「下个假期什么时候开始」，以及讲故事这类「只在学期内」的活动在假期里要不要显示。没有这个文件也能用，只是这些地方会显示「不确定」。

```json
{
  "source": "https://education.nsw.gov.au/……（学期日期页面）",
  "terms": [
    {"year": 2027, "term": 1, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
    {"year": 2027, "term": 2, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"}
  ]
}
```

- 来源只能是 NSW 教育部的学期日期页面（education.nsw.gov.au），打包脚本会检查。
- 悉尼用**东部（Eastern division）**的日期。页面如果分开写老师返校日和学生上课日，用**学生**的。
- 写今年剩下的和明年全年的学期；学期不能重叠。两个学期之间就是假期，不用另外写。
- 写好后检查：`python3 place_data_tool.py validate data/school_terms.json`（打包脚本用同样的规则）。

## 九、实时水质（NSW Beachwatch）

- 下水点「今天能不能下水」用的是 NSW Beachwatch 的公开数据（NSW 政府发布，CC BY 4.0）：污染预报和最近一次水质检测。
- **不收进数据文件，也不放进 places.json**：App 直接去读最新的，读到的不存。Sonnet 收集时只需要在下水点记录里写 beachwatch（这个点在 Beachwatch 上的名字）。
- **现在关着**（代码里 SwimWatch.enabled = false）。开通要 Opus 做三件事：在 data.nsw 和 Beachwatch 官网上确认用哪个公开接口；用真实返回核对字段名；填上接口地址、打开开关、在手机上试。
- App 显示时一定做到：写明出处（NSW Beachwatch · NSW Department of Climate Change, Energy, the Environment and Water · CC BY 4.0）；写明这是预报、不保证准确；提醒下水前看现场的旗子、听救生员的；**永远不说「安全」**。

## 十、填写规则（最重要）

1. **只记事实和来源链接。** 有没有、是什么、几点开。不抄介绍原文，不保存、不转存任何照片。
2. **页面没写就不写。** 不要根据照片、常识或者「一般都有」去推测。
3. **坐标不估。** 页面上有才填，没有就写 null。
4. **不记联系人信息。** 电话、邮箱、工作人员的名字都不记（工具会拦电话和邮箱）。
5. **来源：** council 官网（包括 council 图书馆的网站）> council 委托运营方的官网（要从 council 页面能链接过去）> 州政府网站（包括 NSW 教育部、Beachwatch）。
6. **不能用的来源：** Google 地图和 Google 评论、Apple 地图、Facebook、Instagram、Reddit、小红书、TikTok、TripAdvisor、Yelp，以及任何要登录才能看的页面。工具会拦住这些链接。报名平台只能当 booking_url。
7. **会变的信息要有日期。** 开放时间、活动、门票价格都会变：checked 一定写当天；活动过期了自动不显示。
8. **step_free 要页面明说。** 见第五节。
9. **来源互相矛盾：** 两条都留（src 不同），status 写 needs_check。
10. **页面打不开或没有信息：** 去处照样登记（facts 写 []），在 note_zh 里说明。网站拦自动访问（403 之类）的不绕过，在 place_batches.csv 里记下来。
11. **App 只给链接。** 报名、买票都在主办方的网站上完成，App 不经手。
12. **只用 publish.py 发布。** docs/ 里的文件只由 tools/publish.py 写，不要手改；安全检查没过（退出码 2）就停下来汇报，不要自己加 --force。
13. **只动这个仓库。** 不改仓库以外的任何东西，不改 RULES.md、词表和 tools/ 里的脚本（要改先问我）。

## 十一、每次对话的流程（Sonnet 照做：新 council 的第一次收集）

**准备**

1. 用 add_repo 接上 GitHub 仓库 sasuke9527/parkapp-data（access 选 push），按它返回的命令 clone 到 /home/claude/parkapp-data（那里已经有可用的 clone 就直接用，先 `git pull --rebase`）。下面的命令都在这个目录里跑。
2. 读仓库里的 RULES.md（就是这份说明），运行 `python3 place_data_tool.py selftest`，显示「自检通过」才继续。

**选批次**

3. 看 place_batches.csv：有 status=doing 的就接着做它；没有的话选 order 最小的 todo，把它改成 doing。第 0 条（学期日期）要先做。
4. 本次的文件名：data/places/au-nsw-<slug>-<序号>.jsonl 和 data/sessions/au-nsw-<slug>-<序号>.jsonl，序号 = 这一行的 files + 1，写两位数（01、02……）；假期活动放 data/events/au-nsw-<slug>-<假期开始的年月>.jsonl。notes 里写了上次做到哪，就从那里接着做。

**第 0 批：学期日期**（第一次先做它；以后每年年底再做一次）

- 用网页搜索找 NSW 教育部的学期日期页面（如「NSW public school term dates」，链接要在 education.nsw.gov.au 上），这样问 WebFetch：

> List the NSW public school term dates on this page for each year shown, for the Eastern division: the term number and the first and last day for students. If staff and student dates differ, give the student dates. Do not summarise.

- 按第八节写 data/school_terms.json（已有的学期留着，补上新一年的），运行 `python3 place_data_tool.py validate data/school_terms.json`，没有错误后把第 0 条改成 done（last_date 写今天，notes 写收了哪几年），按下面「收尾」的第 13–15 步发布、提交、推送。然后接着做下一个批次。

**收集（一个 council 按这个顺序）**

5. **游泳池**：用网页搜索找 council 官网的游泳池、水上中心页面（如「<council 名> aquatic centre」「<council 名> swimming pools」）。打开每个泳池的页面，这样问 WebFetch：

> List every facility at this pool or aquatic centre exactly as written on this page: each pool with its length (for example 50m or 25m), whether it is indoor or outdoor and whether it is heated; toddler, wading or leisure pools; splash pads or water play; waterslides; learn to swim; spa, sauna or steam room; accessibility (pool hoist, ramp, step-free or level entry, accessible toilets); baby change and parents rooms; parking; cafe or kiosk. Also give the opening hours (including public holiday and seasonal hours), the season dates if a pool is outdoor, entry prices, the operator, the street address and suburb, and any coordinates. Do not summarise or leave items out. Do not include phone numbers, email addresses or staff names.

6. **图书馆和固定活动**：找 council 图书馆的分馆列表，每个分馆一条去处；再找它的亲子活动日程（如「<council 名> library storytime」「rhyme time」），这样问 WebFetch：

> List the opening hours, street address and suburb of each library branch on this page, and every regular weekly children's activity (for example storytime, rhyme time, toddler time, bilingual storytime, Lego club, craft, STEM) with the branch, day of the week, start and end time, age range, language, whether it runs only during school term, whether booking is required, and the cost, exactly as written. Also list any facilities mentioned: children's area, baby change, parents room, toy library, collections in languages other than English, step-free or level access, parking. Do not summarise or leave items out. Do not include phone numbers, email addresses or staff names.

7. **下水点**（council 有海岸线、港湾或河边游泳点的才有）：找 council 的海滩、海水池、港湾网池页面，这样问 WebFetch：

> List every beach, ocean pool, rock pool, baths, netted harbour pool or river swimming spot on this page with its link and suburb. For each one, list exactly as written: lifeguard patrol season and hours, shark nets, toilets, showers, change rooms, shallow areas for children, beach wheelchairs or access mats, shade, dog rules, ocean pool cleaning days, parking, and any coordinates. Do not summarise or leave items out.

   然后在 Beachwatch 网站上查这个点的名字，填到 beachwatch（查不到就不写）。

8. **学校假期活动**（只在下一个假期的活动已经公布时做）：找 council、图书馆、泳池的假期活动页面，这样问 WebFetch：

> List every school holiday activity on this page with its title, organiser, venue, suburb, each date with start and end time, age range, cost, whether booking is required, and the booking link. Only include activities run by the council, its libraries, its pools or a NSW Government agency. Do not include phone numbers, email addresses or staff names.

9. 按第三、四、六、七节写成 JSON，用工具一条条添加。校验不过就不会加进去，按提示改完再加：

```bash
python3 place_data_tool.py add data/places/au-nsw-hornsby-01.jsonl <<'EOF'
{"id": "au-nsw-hornsby-pool-……", "kind": "pool", ……}
EOF
```

   固定活动要等它的图书馆加好以后再加（place 要对得上）。

10. 每做 10 个去处，跑一次 `python3 place_data_tool.py stats data/places/<本次文件>`，看 A 类覆盖。
11. **做满 30 个去处（固定活动、假期活动不算数），或者这个 council 做完，就停。** 连着 5 个页面都打不开，也停，在 notes 里写原因。

**收尾**

12. 运行 `python3 place_data_tool.py validate <本次的每个文件>`：错误要改完，警告可以留。
13. 更新 place_batches.csv 里这一行：files 加 1，places、sessions、events 写累计数，last_date 写今天，notes 写**下次从哪继续**（如「泳池、图书馆做完，下水点还没做」）。这个 council 全部做完就把 status 改成 done；网站打不开、做不了的写 blocked。再看 `python3 tools/round.py`：今天在复查窗口里，这一行的 round 写它说的轮次、round_date 写今天（刚收的就算这一轮复查过了）；这次也收了这个假期的活动，events_round 也写这个轮次。
14. 运行 `python3 tools/publish.py`：退出码 0 才继续；1 是数据有错，改完再跑；2 是安全检查没过，停下来向我汇报，不要加 --force。
15. 提交并推送：`git add -A && git commit -m "去哪玩数据：<council> 第一次收集（<N> 个去处）" && git -c push.negotiate=true push`。推送被拒（别人先推了）就 `git pull --rebase` 再推；pull 时有冲突，停下来向我汇报。
16. 用中文向我汇报：做的是哪个批次、这次几个去处（泳池、图书馆、下水点各几个）、几条固定活动、几条假期活动、A 类平均覆盖、发布的版本号、还剩什么、遇到什么问题。

## 十二、给 Sonnet 的开工提示词（每次新开对话时复制粘贴）

在「app」项目里新开一个对话，模型选 Sonnet，发下面这段。每次做一个 council，做完再开新对话继续。什么时候收、收几个，你自己定（用的是你账号的额度）。

```
请帮我收集悉尼「去哪玩」的数据：游泳池、图书馆和讲故事这类每周固定的亲子活动、下水点（海滩、海水池、港湾网池）、学校假期活动。数据和规则都在 GitHub 仓库 sasuke9527/parkapp-data：先用 add_repo 接上它（access 选 push）、clone 下来，读仓库里的 RULES.md，然后严格按第十一节的流程做：准备、选批次、收集、收尾（发布、提交、推送）。

铁律：只记事实和来源链接；页面没写的不写；不抄原文、不存照片；不用 Google 地图、Google 评论、Facebook、Reddit、小红书这类来源；坐标页面上没有就写 null，不要估；不记电话、邮箱和工作人员的名字。

这次做满 30 个去处或者这个 council 做完就停，用 tools/publish.py 发布，更新 place_batches.csv，提交并推送到 GitHub，然后用中文向我汇报。
```

## 十三、什么时候还要找 Opus

数据的发布不用找 Opus：Sonnet 和定时任务跑完 publish.py、推送到 GitHub，App 第二天（或者下拉刷新时）就换上新数据。下面这些才要在「app」项目里开 Opus 对话：

1. **App 要发新版本时**：把 docs/places.json 复制成 App 里带的 app/ParkApp/Resources/places.json（新装 App 的人第一次打开、还没联网时用它）。
2. **规则、词表、工具要改时**：改 RULES.md（同时改项目里那一份）、place_codes.csv、tools/ 里的脚本，以及 App 里对应的代码。
3. **安全检查没过、推送冲突、定时任务报错时**：看原因，确认没问题再发布。
4. 你说要开实时水质的时候，按第九节开通。

## 十四、工作量的预期

- 33 个 council。一般每个 council 有几个泳池、几个图书馆分馆，每个分馆有几条每周活动；有海岸线或港湾的 council 再加上下水点。大多数 council 一次对话能做完，大的分两三次。
- 建议和公园一样，从 Hornsby 和周边开始。
- 季度复查每年 4 轮（每个学校假期前一轮），每轮把收过的 council 都核一遍：一次大约做 3–4 个 council，33 个都收完以后，一轮大约要跑 10 次左右；还没收完的时候少得多。没活的时候定时任务查一下就结束，只用一点点额度。
- 学期日期每年收一次（11–12 月那一轮补下一年的）。

## 十五、季度复查（定时任务「去哪玩数据季度复查」照做）

**什么时候**

- 一轮 = 一个学校假期。假期开始前 28 天到假期前一天是这一轮的复查窗口；`python3 tools/round.py` 会算出今天是哪一轮、在不在窗口里、还有哪些 council 要做。轮次的名字是「假期开始的年份-季节」，例 2026-summer、2027-autumn。
- 定时任务每年 3、6、9、11、12 月隔一天跑一次（悉尼时间晚上）。不在窗口里、或者这一轮已经做完，就马上结束。
- 每次最多开 40 个网页（WebFetch 次数）、最多做 4 个 council；做不完的留给下一次。

**每次的步骤**

1. **准备**：用 add_repo 接上 sasuke9527/parkapp-data（access 选 push），clone 到 /home/claude/parkapp-data；运行 `python3 place_data_tool.py selftest` 和 `python3 tools/round.py`。
   - 它说「不在复查窗口」或「这一轮已经做完了」：什么都不改、不提交，汇报一句就结束。
   - 它说「学期日期用完了」或「还要先收下一年的学期日期」：先做第十一节的第 0 批，补上下一年的学期，再跑一次 round.py。
2. **先收假期活动**（round.py 列出的 events，按顺序）：照第十一节第 8 步，收这个假期由 council、图书馆、泳池、州政府机构主办的活动，写进 data/events/au-nsw-<slug>-<假期开始的年月>.jsonl（例 2026 年暑假：au-nsw-hornsby-2026-12.jsonl），然后把 place_batches.csv 这一行的 events_round 写成这一轮。
   - 官网还没公布这个假期的活动：离假期还有 7 天以上，events_round 先不写（下次再看），notes 里记一句；不到 7 天了，events_round 照写，notes 记「这个假期官网没公布活动」。
3. **再复查**（round.py 列出的 recheck，round_date 最早的先做）：
   - 每个去处打开 sources 里的第一个页面（主页面），泳池还要打开门票页；每条固定活动的来源页各打开一次（几条共用一页的只开一次）。11–12 月那一轮（名字以 -summer 结尾）把每条记录的所有来源页都打开一次，设施也核一遍。
   - 问 WebFetch 用第十一节第 5、6、7 步的问法。不要把我们记的内容告诉它，让它照页面原样列，我们自己比。
   - 只改页面上明确写了的：开放时间、季节、门票、status（关门维修、季节性关闭等）、每周活动（新增、删掉、改时间、改年龄）。设施只在页面明确写了变化时才改。拿不准的不改，status 写 needs_check，note_zh 里记一句。
   - 页面打不开（404、跳回首页、内容没了）：不删记录，status 改成 needs_check，note_zh 写「官网页面打不开（日期）」。网站拦自动访问（403 之类）不绕过，在 notes 里记下来。
   - 页面打开、核对过的记录，不管有没有变化，checked 都写今天。
   - 改记录用 Python 小脚本读 jsonl、改字段、写回原文件（一行一个 JSON，ensure_ascii=False），不要手打整行；新增的固定活动用 `place_data_tool.py add`；官网上已经没有的每周活动，从文件里删掉那一行。改完跑 `python3 place_data_tool.py validate <改过的文件>`。
   - 做完一个 council：place_batches.csv 这一行 round 写这一轮、round_date 写今天，notes 写这一轮改了什么（一句话）。
4. **收尾**：
   - 运行 `python3 tools/publish.py`。退出码 0 继续；1 是数据有错，改完再跑，改不好就把这个 council 的改动撤掉（`git checkout -- <文件>`），在汇报里说；2 是安全检查没过，不发布，照下面推到 hold 分支。
   - 在 runs.csv 末尾加一行：日期,轮次,做了什么（例「复查 hornsby ku-ring-gai；活动 hornsby」）,开了几个网页,改了几条记录,发布的版本号（没发布写 none，被安全检查拦住写 held）,备注。
   - 提交：`git add -A && git commit -m "季度复查 <轮次>：<做了哪些 council>（改了 <N> 条）"`。
   - 推送：正常就 `git -c push.negotiate=true push`。安全检查没过时推到新分支 `git push origin HEAD:hold-<今天的日期>`，不推 main，App 就不会拿到。推送被拒就 `git pull --rebase` 再推，有冲突就停下来汇报。
5. **汇报**（中文，几行就好）：这是哪一轮、这次做了哪些 council、改了什么（讲故事时间、开放时间、门票的变化写清楚）、哪些页面打不开、发布的版本号、这一轮还剩哪些 council。没活就一句话。

**不做的**

- 不做还没收过的 council（status 是 todo 的），那是第十一节 Sonnet 对话的活。
- 不用 --force，不改 RULES.md、词表和 tools/，不动仓库以外的任何东西。

## 十六、发布和退回

- `python3 tools/publish.py`：校验全部数据 → 打包 → 和上一版（docs/places.json）比 → 写 docs/places.json 和 docs/manifest.json。内容和上一版一样就不写。
- 安全检查（退出码 2，不写）：去处总数少了 10% 以上（上一版至少 10 个）；某个 council 的去处少了一半以上（上一版这个 council 至少 4 个）；固定活动总数少了 30% 以上（上一版至少 10 条）。
- 版本号是 UTC 的 YYYYMMDDHHMM。App 只换比手上新的版本，还会核对格式和条数，对不上就继续用手上的。
- `--check`：只检查、不写。`--force`：安全检查没过也写，只有人看过、确认没问题（比如 council 真的关了几个图书馆）才用。
- 发错了要退回：`git revert <那次提交>`，再跑一次 `python3 tools/publish.py`（生成一个更新的版本号，App 才会换），提交、推送。
- 以后格式改到旧版 App 读不懂时：build_places_data.py 的 FORMAT 加 1，App 里的 PlacesFeed.formatSupported 跟着改；旧版 App 会提示「有新数据，要先更新 App」，继续用手上的数据。

---

*最后更新：2026-11-20*
