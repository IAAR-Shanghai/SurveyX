---
**給維護者與 AI 代理的提示：**

此檔案 (`AGENTS.md`) 是指導原則的唯一權威來源。`GEMINI.md` 與 `CLAUDE.md` 均由此檔案透過 CI/CD 腳本自動同步生成。

**請只在此檔案進行修改**，對其他檔案的變更將會被自動覆蓋。
---

# AGENTS


## 專案準則（請嚴格遵守）
---

> 本檔同時供人類與開發代理（Codex、Cursor、Copilot、Gemini）閱讀。請嚴格遵守。  
> 所有指令預設在 conda 環境 `surveyx` 執行，如需切換其他環境必須先取得使用者同意。
> 請用中文回答，專有名詞請用原文。

---

- 除非使用者明確許可，嚴禁更改任何 source code。
- 未經使用者授權，嚴禁修改或覆寫 `outputs/` 目錄內的任何檔案（包含 `tmp/`、`latex/`、`metrics/` 等所有副產物）。
- 未經使用者同意，`resources/` 目錄內的檔案一律禁止改動。
- 操作前請確認當前 shell 已啟用 conda 環境 `surveyx`；若需切換或重建環境，務必先獲得使用者同意並記錄操作原因。
- 任何計畫寫入檔案或觸發長時間運算的流程（如模型微調、批次推論、生成報告）都需先向使用者確認輸出目錄與預期副作用。
- 回覆請保持中文敘述與簡潔條列，必要時可附英文專有名詞；若需引用長段程式碼或輸出，提供路徑與概要即可。
- 詳細受保護資產請參考 `docs/agent-protected-files.md`，如需更新列表務必先行報備。
- 回覆前必須先進行「事實檢查思考」，僅能依據使用者提供內容、模型內部已知資訊或經確認的資料回答。
- 若資訊不足須明確回覆「無法確定」或說明缺乏依據，禁止臆測、補完或擴大原意。
- 需要引用資料或推論時，請在回覆中標明依據；屬於推論或假設的內容須清楚標註。
- 不得替使用者重寫或改述成不同語意；如需重述，請標示「重述版本」並保持語義對等。
- 回覆時避免使用「應該是」「可能是」「我猜」等模糊語氣，除非使用者明確要求。
- 產出前請自檢三項：a. 回覆有明確資料依據 b. 未超出問題範圍 c. 無新增未被提及的人名／數字／事件。

## 0) 預設與工作範圍

- 預設工作目錄為倉庫根目錄 `SurveyX/`；若需在子目錄操作請於回報中說明目的與範圍。
- 所有指令預設在 conda 環境 `surveyx` 執行；每個新 shell session 先 `conda activate surveyx`，必要時依 `env/README.md` 重新建立環境。
- 變更環境（新增/升級套件、調整工具鏈）前務必提報動機與預期影響，完成後更新對應快照（如 `env/env-survey.yml`、`requirements.txt`）。
- 無法於本地驗證的流程需標註「未驗證」，並提供建議的補驗步驟或所需資源。

## 1) 專案結構（約定）

- `src/`：SurveyX 核心模組（含 `configs/`、`modules/`、`models/`、`schemas/`），屬關鍵 source code。
- `tasks/`：離線主流程與 `workflow` 分段腳本統一存放處，請勿另立入口。
- `scripts/`：PDF→Markdown、資料驗證等輔助腳本；`run.sh` 封裝常用任務。
- `docs/`：作業文件與協作紀錄，包含 `docs/qa-notes/` 與 `docs/temporary_issues/`。
- `env/`：環境快照與重建腳本；`models/`、`external/`、`examples/`、`assets/` 為模型／範例資源。
- `resources/`：使用者提供的離線參考資料；`outputs/` 收納每次 pipeline 執行結果，依 `task_id` 劃分。
- 新增檔案請遵循既有結構，勿將臨時資料放入 `outputs/`、`resources/`、`external/`。

## 2) 標準指令與流程

- 建立或重建環境：`conda env create -n surveyx -f env/env-survey.yml` → `conda activate surveyx`。
- 安裝 Python 依賴：`pip install -r requirements.txt`（僅在獲准後執行）。
- PDF→Markdown：`./run.sh convert <pdf_dir> <md_out_dir> [-- ...docling flags]`。
- Markdown 驗證：`./run.sh validate <md_dir>`。
- 離線主流程：`./run.sh offline "<title>" "<keywords_csv>" <md_dir> [-- ...flags]`。
- Workflow 後續階段：`./run.sh workflow <task_id>`（需確認 `outputs/<task_id>/tmp_config.json` 已生成）。
- 直接調用 Python 入口：`python tasks/offline_run.py --title ... --key_words ... --ref_path ...`。
- 測試建議：`python -m pytest -q`；若涉及遠端 API 請先取得允許。

## 3) 環境變數與密鑰管理

- 根目錄 `.env` 用於本地儲存 API key、token 等敏感資訊；嚴禁將實際值提交到版本庫。
- `src/configs/config.py` 導入時會讀取 `.env` 或 `SURVEYX_ENV_FILE` 指定檔案；請透過環境變數覆蓋預設值，而非直接硬編碼。
- 調整模型或端點設定前須與使用者確認影響範圍，並在回覆中說明變更理由。
- 更新環境或密鑰流程時，建議同步補充 `env/README.md` 或相關文件。

## 4) 產出與資料資源

- `outputs/` 僅供閱讀既有結果，新增輸出前需先告知寫入路徑與預期檔案體積，完成後於回覆中標註新增路徑。
- `resources/`、`external/`、`assets/` 為使用者整理的素材與依賴，未經授權不得新增、搬移或刪除其內容。
- `resources/` 內含：
  - `resources/offline_refs/`：使用者轉檔後的 Markdown 參考文獻與下載測試資料，請維持原有子資料夾結構（如 `example/`, `test_docling_md/`）與 JSON 清單檔案，新增內容前需先確認命名規則與儲存位置。
  - `resources/LLM/`：LLM 提示模板，依流程分類於子資料夾（如 `content_generator/`, `outline_generator/`）；如需調整 prompt，請提供差異與回滾方案。
  - `resources/latex/`：LaTeX 樣板與水印資產（如 `survey.ini.tex`, `figure_template/`），嚴禁擅改；若需替換樣式請先提出完整方案。
- 需分享暫存結果時，可建立經同意的子資料夾或於 `docs/temporary_issues/` 留存紀錄，避免混入正式輸出。

## 5) Git 工作流與提交政策

- 預設禁止直接推送 `main`／`master`；請建立 feature 分支並待審查後合併。
- Commit 應聚焦單一邏輯單元並撰寫清楚訊息；涉及 `src/`、`tasks/`、`scripts/` 的變更需同步更新對應文件或說明。
- 僅文件調整（如 `docs/`）可在回覆後由使用者決定是否提交；代理不得自行發布未經確認的程式碼。

## 6) 提交前自檢

- 視變更範圍執行 `python -m pytest -q` 或子集測試，若跳過需於回覆中註明原因。
- 確認 `outputs/`、`resources/`、`external/` 沒有未授權的新增或覆寫；必要時以 `git status` 佐證。
- 若本次作業新增受保護項或例外條件，請同步更新 `docs/agent-protected-files.md`。

## 7) Pipeline 操作 SOP

1. 準備資料：將 PDF 轉為 Markdown 後置於 `resources/offline_refs/<topic>/` 等資料夾。
2. 執行 `./run.sh validate` 檢查 Markdown 引用與格式，確保通過後再進入主流程。
3. 透過 `./run.sh offline ...` 啟動離線流程，輸出會建立新的 `outputs/<task_id>/` 與 `tmp_config.json`。
4. 需要進一步生成章節或 LaTeX 時，使用 `./run.sh workflow <task_id>` 或個別執行 `tasks/workflow/03-06` 腳本。
5. 每個階段完成後檢視 `outputs/<task_id>/logs/` 與產出檔案，並在回覆中摘要狀態與後續步驟。
6. 清除暫存或大型檔案前務必先徵得同意，避免遺失重要紀錄。

## 8) 常見誤用（請避免）

- ❌ 未經授權修改 `src/`、`tasks/`、`scripts/`、`run.sh` 或配置檔。
- ❌ 在未確認輸入資料品質時直接執行 `workflow` 腳本，導致覆蓋或污染既有輸出。
- ❌ 將 API key、token、cookie 寫入程式碼或納入版本庫。
- ❌ 將臨時測試資料放入 `outputs/`、`resources/`、`external/`，或刪除使用者整理的離線參考。
- ❌ 長時間運算前未與使用者確認資源使用、輸出路徑與可能的磁碟占用。

## 9) 測試與暫存資料

- 建議將臨時輸出集中於 `outputs/<task_id>/tmp/` 等經同意的資料夾，並在回覆中標註用途與清理計畫。
- 測試若生成大量檔案，可放置於 `test_artifacts/` 或 `tests/.tmp/`（如需）並於完成後清理或回報。
- 對流程或環境的疑慮，可於 `docs/temporary_issues/` 建立紀錄檔案並於回覆中引用。

## 10) Sandbox 測試環境

### LaTeX Citation Fix (`sandbox/latex_citation_fix/`)

- **目的**：測試 AI Agent 對 LaTeX 引用問題的診斷與修復能力。
- **入口**：`sandbox/latex_citation_fix/README.md` 為完整導覽文件。
- **結構**：
  - `broken/`：包含已植入問題的 LaTeX 原始檔（85 頁，602KB）
  - `fixed/`：所有問題已修復的標準答案（80 頁，634KB）
  - `reference_only/`：6 份完整修復文件與步驟說明（6 個 MD 檔案）
  - `tools/`：統一修復工具 `latex_fix_toolkit.py` 與輔助腳本
  - `agent_workspace/`：Agent 測試專用工作區（由 `reset.sh` 填充）
- **測試模式（重要）**：
  - Agent 測試時**禁止查看** `reference_only/` 與 `fixed/` 目錄內容
  - 僅能操作 `agent_workspace/` 內檔案，並使用 `tools/` 中提供的工具
  - 開發者與維護者可閱讀所有資料進行學習與驗證
- **已植入問題**：
  1. `survey.tex` Line 578: `\ref{fig:tree_figure_Langu}` (將顯示 "??")
  2. `survey.tex` Line 701: `\ref{fig:tiny_tree_figure_5}` (將顯示 "??")
  3. `figs/structure_fig.tex` Line ~131: en-dash 字元問題
- **啟動測試**：

  ```bash
  cd sandbox/latex_citation_fix
  ./reset.sh        # 填充 agent_workspace/ 並清除舊輸出
  cd agent_workspace
  # Agent 開始診斷與修復...
  ```

- **預期結果**：修復後應從 85 頁減少至 80 頁，檔案大小從 602KB 增至 634KB。

## 11) 文件與協作紀錄

- 撰寫或補充文件時請維持既有格式；涉及流程變更者需同步更新 `docs/` 內對應說明（如 `docs/qa-notes/`、`pipeline&modules.md`、`paper_outline_zh.md`）。
- 若新增操作守則或保護項，請同步更新 `docs/agent-protected-files.md` 與本檔案相關段落。
- 暫存問題的詳細維護流程請遵循 `docs/guides/temporary_issue_maintenance.md`。
- 重要發現、疑難或待辦事項可記錄於 `docs/temporary_issues/` 與 `docs/qa-notes/`，並在回覆中標註檔名與重點。

## 12) 問題追蹤與歸檔流程

### temporary_issues/ - 進行中問題

- **用途**: 僅存放**尚未解決或需持續追蹤**的問題
- **檔名**: `YYYYMMDD_<主題>.md`（例：`20251017_pdf_conversion_error.md`）
- **維護**: 遵循 `docs/guides/temporary_issue_maintenance.md`
- **原則**: 
  - 保持目錄精簡（理想狀態：0-3 個進行中問題）
  - 定期檢視是否仍需追蹤
  - 清楚標註狀態（🔄 進行中 / ⏸️ 待觀察 / ⚠️ 阻塞中）

### resolved_issues/ - 已解決問題歸檔

- **用途**: 按主題歸檔已解決的問題與解決方案
- **結構**: `resolved_issues/<主題>/`
  - `README.md`: 該主題總覽與導覽
  - 相關文件（問題記錄、解決方案、指南等）
  - `archive/`: 該主題的詳細歷史文件
- **歸檔流程**:
  1. **結案確認**: 問題已完全解決且解決方案已驗證
  2. **建立主題目錄**（若不存在）: `mkdir -p docs/resolved_issues/<主題>/archive`
  3. **移動文件**: 從 `temporary_issues/` 移至對應主題目錄
  4. **建立或更新 README**: 在主題目錄建立總覽文件
  5. **更新索引**:
     - 在 `docs/resolved_issues/README.md` 新增該主題條目
     - 從 `docs/temporary_issues/README.md` 移除該問題
  6. **回報使用者**: 說明歸檔路徑、關鍵解決方案與結案理由

### 操作原則

- ❌ **禁止**在 `temporary_issues/` 堆積已解決問題
- ✅ 問題解決後**24 小時內**完成歸檔
- ✅ 按**主題分類**，避免混雜不同類型問題（例：latex_citation_fix、pdf_conversion、pipeline_optimization）
- ✅ 保留完整歷史記錄於 `archive/` 供追溯
- ✅ 相關工具與 sandbox 環境獨立維護，用 symlink 連結文檔供參考

### 範例：LaTeX Citation Fix

已歸檔至 `docs/resolved_issues/latex_citation_fix/`，包含：
- 完整指南、快速參考、修復報告
- 7 個歷史追蹤文件於 `archive/`
- Sandbox 測試環境位於 `sandbox/latex_citation_fix/`（獨立維護）
- 透過 symlink 從 sandbox 連結文檔供參考

## 13) 受保護檔案（請勿修改）

- 最新清單與允許操作詳見 `docs/agent-protected-files.md`。
- 需特別留意的核心檔案包含：`src/configs/config.py`、`tasks/offline_run.py`、`tasks/workflow/*.py`、`run.sh`、`requirements.txt`、`env/` 內快照、以及根目錄文件 `paper_outline_zh.md`、`paper內容.md`、`pipeline&modules.md`。
- `outputs/`、`resources/`、`external/`、`models/` 所有檔案視為使用者資產，除非獲得明確授權，禁止刪除、覆寫或重新命名。

## 暫存問題紀錄（已廢棄）

> ⚠️ **注意**: 本章節已過時，請參考 **Section 12) 問題追蹤與歸檔流程**。

- ~~已建立 `docs/temporary_issues/` 目錄，用於集中紀錄各階段暫時性問題與分析~~
- ~~最新紀錄為 `docs/temporary_issues/spacing_glitch.md`~~
- **新流程**: 已解決問題已歸檔至 `docs/resolved_issues/latex_citation_fix/`
