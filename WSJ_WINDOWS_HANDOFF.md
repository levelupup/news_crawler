# WSJ body-fetcher — Windows 端實作規格（交給 Windows 的 Claude Code）

## 背景

WSJ（Dow Jones）的登入頁與文章頁都由 **DataDome** 防護，會對任何自動化瀏覽器丟出硬互動式
captcha（`captcha-delivery.com` 拼圖）。DGX（.105，Linux/arm64）上 headless、headful+xvfb、
stealth、匯入 cookie 全部試過都被擋——指紋對不上真實瀏覽器。

**唯一可行解：在這台 Windows、用一個「專用 Chrome profile」抓 WSJ 文章正文**，因為真實
Chrome 的指紋能過 DataDome（第一次可能要你手動解一次 captcha，之後靠 clearance cookie 撐）。
抓到的內文透過 **SMB 共用資料夾**送回 .105。你（Windows 的 Claude Code）只負責「抓 + 寫回
共用資料夾」，其餘（待抓清單、合併入庫、餵 corpus）都由 .105 那端處理。

## 硬性需求（來自使用者）

- **不可影響日常瀏覽**：務必用「**專用 Chrome profile + 獨立 user-data-dir**」，開起來是另一個
  獨立 Chrome 視窗，跟平常那個完全隔離。**不要**用 `channel="chrome"` 去附掛使用者日常 profile
  （那會要求關掉他正在用的 Chrome）。用 Playwright 的 `launch_persistent_context(user_data_dir=...)`
  指向一個**新建的專用資料夾**。
- **不是 headless**：`headless=False`。DataDome 對 headless 零容忍。第一次跑要讓使用者看得到視窗、
  能手動登入 WSJ + 解 captcha。

## 交換協定（SMB 共用資料夾）

共用資料夾 = `\\gx10-4336\shared`（.105 的 `~/projects/shared`）。子資料夾 `wsj_transfer\`：

| 檔案 | 方向 | 內容 |
|------|------|------|
| `wsj_pending.txt` | .105 → Windows | 待抓 WSJ 文章 URL，一行一個（.105 每小時 :25 更新） |
| `wsj_content.json` | Windows → .105 | `{url: 內文文字}`，**累積式**（你每批 append 進去） |

- 先把 `\\gx10-4336\shared` 掛成網路磁碟機（或用 Tailscale 路徑 `\\100.107.198.121\shared`；
  帳號 `jingyueh`）。若掛載不便，退而用 `scp` 也行——但共用資料夾是使用者選定的管道。
- **累積式合併**：讀既有 `wsj_content.json`（若存在），抓完的新內文 merge 進去，原子寫回
  （寫 `.tmp` 再 rename）。.105 端的匯入是冪等的，所以你只要保證這個檔案是有效 JSON 即可。
- 跳過已抓：讀 `wsj_pending.txt` 後，扣掉你自己 `wsj_content.json` 裡已有的 url，只抓剩下的。

## 抓取行為（反封鎖——這是使用者最在意的）

- **專用 persistent context**，`headless=False`，viewport ~1366×900。
- **首次啟動流程**：開 `https://www.wsj.com/`，若被導到登入或看到 captcha，**暫停並提示使用者
  手動登入 + 解 captcha**（persistent context 會把 clearance/登入 cookie 存進 user-data-dir，
  之後重跑免登）。偵測方式：頁面 HTML 很小（~1–2KB）或含 `captcha-delivery` / `geo.captcha`
  → 尚未通關。
- **節流（比照 .105 對付費站的規格）**：每篇之間隨機 **10–25 秒**；**每次執行上限 ~40 篇**
  （`--max` 參數，預設 40）；一天別跑太多輪。目標是「像重度訂閱讀者」，不是掃檔案庫。
- 若連續多篇都撞 captcha（clearance 過期）→ 停止該輪、提示使用者重解一次，不要硬撞。
- UA 用該 Chrome profile 的真實 UA（persistent context 自帶即可，不要硬塞假 UA）。

## 抽正文

- 用 `trafilatura.extract(html)`（規則式，零 LLM）。抽出 < 200 字視為失敗，不寫入該 url
  （留給下次；不要寫空字串或 sentinel——sentinel 由 .105 端管理）。
- WSJ 文章正文在 `page.content()` 拿到的 rendered HTML 裡；`goto(url, wait_until="domcontentloaded")`
  後再 `wait_for_timeout(3000~4000)` 讓內文 hydrate，再抽。

## 輸出契約（務必嚴格遵守，.105 靠這個入庫）

- 只寫 `wsj_transfer\wsj_content.json`，格式嚴格 `{ "https://www.wsj.com/...": "正文…", ... }`。
- UTF-8、`ensure_ascii=False`。原子寫入。**不要**動 `wsj_pending.txt`（那是 .105 產的）。
- **絕不**把內文寫到任何會被 push 的地方——這是付費內容，只進 .105 的本地 corpus。

## 建議 CLI

```
wsj_fetch.py            # 讀 pending、抓、寫回；預設 --max 40
wsj_fetch.py --max 20   # 這輪只抓 20 篇
wsj_fetch.py --login    # 只開視窗讓使用者手動登入/解 captcha，不抓（初始化 profile 用）
```

## 完成後 .105 端會自動做的事（你不用管）

- 每小時 :25，.105 的 `wsj_bridge.py sync` 會把你寫回的 `wsj_content.json` 合併進
  `data/content/wsj_content.json`，並刷新 `wsj_pending.txt`（已入庫的 url 自動從清單消失）。
- 那些內文接著餵 web_search / deep_research 的本地 corpus，永不外流、不進 git。

## backlog 規模

首次匯出約 **960 篇**。以每輪 40 篇、一天跑一兩輪計，約一兩週抓完；之後每天新增的 WSJ 文章
（來自 .105 的 RSS 爬蟲）會持續進 `wsj_pending.txt`，維持增量即可。
