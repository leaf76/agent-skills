# Shared Skill Routing Guide

Updated: 2026-07-19

## 目標
- 保持 `.system` 技能不變。
- 僅整理非 `.system` 技能的呼叫順序與責任邊界，降低重複選擇。
- 先以「文件化路由」降低歧義，不刪技能、不刪功能。

## 不變更項目
- provider / agent core mechanisms
- 任何 agent 核心機制（`default` / `explorer` / `worker`）

## 非 `.system` 技能總覽（26）

### 規劃與專案治理
- `create-plan`
- `project-planning`
- `plan-mode`

### 探索與盤點
- `explore`

### UI/UX
- `frontend-ui-ux-engineer`（Web / 一般前端）
- `frontend-mobile-uiux-designer`（iOS/Android）

### 文件與文件化
- `document-writer`
- `doc`

### 除錯與品質
- `fix-bug`
- `fix-lint`
- `review-changes`
- `security-threat-model`
- `debug-memory-leak`

### 驗證與觀測
- `playwright`
- `chrome-devtools-test`
- `screenshot`
- `computer-use`（原生桌面殼 / 明確要求；非 web 預設）
- `hermes-chrome`（daily Chrome cookies/SSO）
- `multimodal-looker`

### 領域專精工具
- `cloudflare-deploy`
- `figma`
- `openai-docs`
- `imagegen`
- `develop-web-game`
- `adb-android-app-ops`
- `yeet`
- `rust-programmer`
- `firmware-feature-writer`

## 優先路由（Primary → Secondary）

1. 規劃
   - `plan-mode`（先判斷是否需要計畫）
   - `create-plan`（主要）
   - `project-planning`（中長期計畫）

2. 探索
   - `explore`（主要）

3. UI/UX
  - Web / 一般前端
    - `frontend-ui-ux-engineer`
    - 10 秒視窗屬於 soft window（判定觀察窗），非硬性中止；若稍後有可用產出且流程成功完成，應判定為成功。
    - `429`/配額/授權/網路等依賴錯誤屬 dependency failure，不應誤標為 timeout。
  - Mobile
    - `frontend-mobile-uiux-designer`（iOS / Android）

4. 文件
   - `document-writer`（一般文件）
   - `doc`（DOCX 專用）

5. 測試 / UI 證據
   - Web：`hermes-chrome` → `playwright` / `chrome-devtools-test` / browser-e2e
   - `screenshot`（僅系統截圖、無控制）
   - `computer-use`（原生桌面殼或明確 computer use；非 web 預設）
   - `multimodal-looker`（圖片/視覺回饋解析）

## 重複職責回避規則
- `doc` 不再與 `document-writer` 重疊為預設入口，依據是否為 `.docx` 需求切換。
- `frontend-ui-ux-engineer` 與 `frontend-mobile-uiux-designer` 不重疊使用：前者先行 Web，一般行動端請直接用後者。
- UI/UX 路由以平台與交付型態為主，不再加入外部模型專屬的前置路由層。
- Web 證據不預設走 `computer-use`；`computer-use` 與 `screenshot` 分開：有 click/type 才用前者。

## 非 `.system` Skills 與 Agents
- Agents（現況）: `default`, `explorer`, `worker`
- Agents 流程不改，僅依技能路由分配任務。

## 後續建議
- 保持路由規則 1 週觀察實際使用誤召率。
- 觀察後再追加刪除候選（需你明確指令）。

---

## Version control

- Private remote: `https://github.com/leaf76/agent-skills` (canonical live path: `~/.agents/skills`)
- Snapshot habit: `agent-vc snapshot --only agent-skills` (from `agent-ssot`)
- Third-party `guizang-ppt-skill/` is gitignored — clone from `https://github.com/op7418/guizang-ppt-skill` if needed
- Never commit `.env`, API keys, or `auth.json`

