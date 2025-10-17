# Agent-Protected Files

本清單列出 SurveyX 專案中需特別留意的檔案與目錄，協助代理在維護流程中避免誤觸敏感資產。除非使用者明確授權，請依下列原則操作，並以 `AGENTS.md` 為最終權威。

## 修改原則

- 任何會改動受保護資產的需求，應先向使用者說明動機、範圍與預期輸出，再依指示執行。
- 若需新增檔案，請優先放置於 `docs/` 或臨時工作目錄，待使用者確認後再移動到受保護區域。
- 無法判定是否屬於受保護範圍時，請先停止操作並向使用者確認。
- 受保護清單若有調整，請同步更新本檔與 `AGENTS.md` 內對應段落。

## 受保護清單

| 類型 | 路徑 / 範圍 | 保護理由 | 允許操作（預設） |
| --- | --- | --- | --- |
| 核心程式碼 | `src/`, `tasks/`, `scripts/`, `models/`, `eval/`, `examples/`, `tests/` | 實作 SurveyX pipeline 與範例流程，任何未授權改動皆可能影響系統行為。 | 僅可閱讀與分析；若需修改必須先取得書面指示。 |
| Workflow 腳本 | `tasks/offline_run.py`, `tasks/workflow/*.py`, `run.sh`, `test.sh` | 控管離線主流程與階段腳本，錯誤改動會破壞整體流程或覆寫輸出。 | 僅可在獲准後依指定調整；提交前需回報測試結果。 |
| 配置與環境 | `src/configs/config.py`, `src/configs/LLM.yaml`, `.env`, `env/env-survey.yml`, `env/requirements-freeze.txt`, `env/README.md`, `requirements.txt` | 定義 LLM 端點、密鑰載入與執行環境；錯誤設定會造成安全或部署風險。 | 僅可閱讀；調整需先提出方案並得到同意，完成後更新相關文件。 |
| 輸出資料 | `outputs/`（含 `tmp/`, `latex/`, `metrics/`, `logs/`, `figs/` 等子目錄） | 保存既有實驗結果與使用者資料；覆寫會造成紀錄遺失。 | 僅可閱讀；新增輸出前需說明寫入方式與路徑並獲得授權。 |
| 參考資源 | `resources/`、`external/`、`models/`、`assets/` | 使用者整理的資料、離線參考與模型快取；變更會影響重現性。`resources/` 內含 `offline_refs/`（Markdown 文獻）、`LLM/`（prompt 模板）、`latex/`（樣板與水印）。 | 僅可閱讀；新增或替換內容需先取得許可並記錄來源。 |
| 文件紀錄 | `docs/temporary_issues/`, `docs/resolved_issues/`, `docs/qa-notes/`, `docs/**`, `paper_outline_zh.md`, `paper內容.md`, `pipeline&modules.md` | 記錄協作歷史、流程說明與研究設定；錯誤修改會造成資訊斷層。`temporary_issues/` 僅存放進行中問題，已解決問題應歸檔至 `resolved_issues/<主題>/`。 | 可新增條目或補充內容，需遵循既有格式並於回報中說明調整。問題解決後務必歸檔。 |
| Sandbox 環境 | `sandbox/latex_citation_fix/reference_only/*.md`, `sandbox/latex_citation_fix/fixed/`, `sandbox/latex_citation_fix/broken/` | 測試環境參考資料與標準答案；Agent 測試時不得查看 `reference_only/` 或 `fixed/`。 | 測試時僅限操作 `agent_workspace/` 內檔案；開發者可閱讀所有資料。 |
| 同步檔案 | `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` | CI/CD 會依 `AGENTS.md` 自動覆寫其他代理版本。 | 僅能編輯 `AGENTS.md`；請勿直接修改衍生檔。 |

## 例外申請流程

1. 於回覆中清楚描述欲修改的受保護資產、理由與預期影響。
2. 等候使用者確認後再進行修改，並於作業完成後回報實際差異與檢驗結果。
3. 若修改涉及新增保護項，請同步更新本清單或明確告知使用者，以便維持一致性。

## 常見疑問

- **臨時草稿要放哪裡？** 建議使用 `docs/temporary_issues/` 或在工作流程中清楚標註尚未提交的檔案，避免誤放至受保護目錄。
- **可以重新產生模型或評估結果嗎？** 僅在使用者授權後進行，並確保新輸出使用獨立子目錄或新檔名，不覆蓋既有資料。
- **可以調整 `paper_outline_zh.md`、`pipeline&modules.md` 或其他根目錄文件嗎？** 這些屬於受保護文件，僅能在使用者指定內容與範圍後進行修改。
- **要不要把新參考資料放進 `resources/`？** 請先報備並提供來源、預期用途與目錄規劃，再依指示放入指定位置。
- **暫存問題紀錄怎麼維護？** 請遵循 `docs/guides/temporary_issue_maintenance.md` 的建立、更新與結案流程，並在回報中附上檔案路徑。問題解決後應立即歸檔至 `docs/resolved_issues/<主題>/`，避免堆積已完成事項。
- **已解決問題要放哪裡？** 按主題歸檔至 `docs/resolved_issues/<主題>/`，並更新該目錄的 README.md。相關工具或 sandbox 環境可獨立維護，用 symlink 連結文檔供參考。
- **發現清單有缺漏？** 請立即在回覆中註明並提出更新建議，經使用者確認後再補入本檔。 
