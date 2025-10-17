# 問題追蹤與歸檔流程 - 實施完成報告

**日期**: 2025-10-17  
**狀態**: ✅ 已完成  
**負責**: AI Agent (GitHub Copilot)

---

## 1. 實施背景

### 問題描述

用戶發現 `docs/temporary_issues/` 目錄存在兩個問題：

1. **堆積已解決問題**: 目錄內全是 LaTeX Citation Fix 相關的已解決問題文件
2. **未來擴展問題**: 未來其他主題的問題會與 LaTeX 問題混雜，難以管理

### 解決方案

實施 **Option A（主題分類歸檔機制）**：

- 建立 `docs/resolved_issues/` 目錄按主題歸檔已解決問題
- `docs/temporary_issues/` 僅存放進行中問題
- 相關工具與 sandbox 環境獨立維護，用 symlink 連結文檔

---

## 2. 執行步驟

### Step 1: 建立新目錄結構 ✅

```bash
mkdir -p docs/resolved_issues/latex_citation_fix/archive
```

### Step 2: 遷移 docs/temporary_issues 文件 ✅

**移動主文件** (5 個):
- `LaTeX_Fix_Complete_Guide.md` → `resolved_issues/latex_citation_fix/`
- `QUICKSTART.md` → `resolved_issues/latex_citation_fix/`
- `Documentation_Consolidation_and_OneClick_Fix_Report.md` → `resolved_issues/latex_citation_fix/`
- `Figure_Fix_Completion_Report.md` → `resolved_issues/latex_citation_fix/`
- `Figure_Placement_Issue.md` → `resolved_issues/latex_citation_fix/`

**移動歷史文件** (7 個):
- 整個 `archive/` 目錄 → `resolved_issues/latex_citation_fix/archive/`
  - `bibtex_compilation_issue.md`
  - `latex_citation_fix_plan.md`
  - `latex_sandbox_setup.md`
  - `sandbox_setup_completion.md`
  - `spacing_glitch.md`
  - `spacing_glitch_solution.md`
  - `QUICKSTART_fix_unicode.md`

**移動 README**:
- `README.md` → `resolved_issues/latex_citation_fix/README.md` (作為主題總覽)

**共計遷移**: 13 個檔案

### Step 3: 清理 sandbox 冗餘文件 ✅

**移動有價值報告**:
- `SANDBOX_COMPLETION_REPORT.md` → `resolved_issues/latex_citation_fix/`

**刪除冗餘文件** (6 個):
- `COMPILATION_VERIFICATION.md` (一次性驗證記錄)
- `README_old.md` (舊版 README)
- `SANDBOX_CHECKLIST.md` (與 README 重複)
- `Sandbox_Setup_Guide.md` (與 README 重複)
- `TEST_INSTRUCTIONS.md` (與 README 重複)
- `QUICKSTART.md` (與 docs 重複)

**保留檔案**:
- `README.md` - 測試環境主入口
- `COMPLETION_REPORT.md` - 本次整理記錄
- `reference_only/` - 6 個修復步驟參考文件
- `broken/`, `fixed/`, `agent_workspace/`, `tools/` - 測試核心

### Step 4: 建立 symlink ✅

在 sandbox 中連結文檔供參考：

```bash
cd sandbox/latex_citation_fix/
ln -s ../../docs/resolved_issues/latex_citation_fix/LaTeX_Fix_Complete_Guide.md docs_complete_guide.md
ln -s ../../docs/resolved_issues/latex_citation_fix/QUICKSTART.md docs_quickstart.md
```

### Step 5: 建立索引文件 ✅

**新建檔案**:
- `docs/resolved_issues/README.md` - 總索引（列出所有已解決問題）
- `docs/temporary_issues/README.md` - 重寫為空模板

### Step 6: 更新規範文件 ✅

**更新 3 個檔案**:
1. `docs/guides/temporary_issue_maintenance.md` - 新增歸檔流程說明
2. `AGENTS.md` - 新增 Section 12 "問題追蹤與歸檔流程"
3. `docs/agent-protected-files.md` - 更新文件紀錄保護項

---

## 3. 最終目錄結構

### docs/ 結構

```
docs/
├── temporary_issues/
│   └── README.md                        ← 空模板（0 個進行中問題）
│
├── resolved_issues/                     ← 新建
│   ├── README.md                        ← 總索引
│   └── latex_citation_fix/
│       ├── README.md                    ← 該主題總覽
│       ├── LaTeX_Fix_Complete_Guide.md  (12KB)
│       ├── QUICKSTART.md                (3.2KB)
│       ├── Documentation_Consolidation_and_OneClick_Fix_Report.md
│       ├── Figure_Fix_Completion_Report.md
│       ├── Figure_Placement_Issue.md
│       ├── SANDBOX_COMPLETION_REPORT.md
│       └── archive/
│           └── (7 個歷史文件)
│
├── guides/
│   └── temporary_issue_maintenance.md   ← 已更新
│
├── qa-notes/
└── agent-protected-files.md             ← 已更新
```

### sandbox/ 結構

```
sandbox/latex_citation_fix/
├── README.md                            ← 測試環境主入口
├── COMPLETION_REPORT.md                 ← 整理完成報告
├── docs_complete_guide.md               ← symlink → ../../docs/resolved_issues/.../
├── docs_quickstart.md                   ← symlink → ../../docs/resolved_issues/.../
├── reset.sh
├── compile.sh
├── broken/                              (85 頁，602KB)
├── fixed/                               (80 頁，634KB)
├── agent_workspace/
├── tools/
│   └── latex_fix_toolkit.py
└── reference_only/                      (6 個 MD)
```

---

## 4. 文件統計

### 遷移統計

| 操作 | 數量 |
|------|------|
| 從 temporary_issues/ 移出 | 13 個檔案 |
| 從 sandbox/ 移出 | 1 個檔案 |
| 從 sandbox/ 刪除 | 6 個檔案 |
| 新建索引文件 | 2 個檔案 |
| 建立 symlink | 2 個連結 |
| 更新規範文件 | 3 個檔案 |

### 最終分布

| 目錄 | 檔案數 | 用途 |
|------|--------|------|
| `docs/resolved_issues/latex_citation_fix/` | 7 | 主文件與報告 |
| `docs/resolved_issues/latex_citation_fix/archive/` | 7 | 歷史追蹤文件 |
| `docs/temporary_issues/` | 1 | 空模板 README |
| `sandbox/latex_citation_fix/` (MD) | 4 | 2 核心 + 2 symlink |

---

## 5. 規範文件更新

### docs/guides/temporary_issue_maintenance.md

**Section 3 - 結案流程**:
- 新增「歸檔至 docs/resolved_issues/」為推薦方式
- 詳細說明建立主題目錄、移動文件、更新索引的步驟

**Section 4 - 常見注意事項**:
- 強調「問題解決後應立即歸檔」
- 新增「按主題歸檔」原則

**Section 5 - 聯動關係**:
- 新增 `docs/resolved_issues/README.md` 與 `docs/temporary_issues/README.md` 的聯動

### AGENTS.md

**新增 Section 12 - 問題追蹤與歸檔流程**:

包含三個子章節：
1. **temporary_issues/ - 進行中問題**
   - 用途、檔名規範、維護原則
   - 保持精簡（0-3 個問題）

2. **resolved_issues/ - 已解決問題歸檔**
   - 目錄結構說明
   - 完整歸檔流程（6 個步驟）

3. **操作原則**
   - 禁止堆積已解決問題
   - 24 小時內完成歸檔
   - 按主題分類
   - 保留完整歷史

**範例引用**: LaTeX Citation Fix 的歸檔案例

**更新舊章節**: 將 "暫存問題紀錄" 標註為已廢棄，引導至新流程

### docs/agent-protected-files.md

**更新「文件紀錄」條目**:
- 新增 `docs/resolved_issues/` 為受保護範圍
- 說明 `temporary_issues/` 僅存放進行中問題
- 強調已解決問題應歸檔至 `resolved_issues/<主題>/`

**新增常見疑問**:
- 「已解決問題要放哪裡？」
- 說明按主題歸檔至 resolved_issues，工具可獨立維護用 symlink 連結

---

## 6. 歸檔流程恆例

### 標準操作程序 (SOP)

#### 當問題解決時：

1. **結案確認**
   - ✅ 問題已完全解決
   - ✅ 解決方案已驗證
   - ✅ 相關文件已整理

2. **建立主題目錄**（如不存在）
   ```bash
   mkdir -p docs/resolved_issues/<主題>/archive
   ```

3. **移動文件**
   ```bash
   mv docs/temporary_issues/<相關檔案> docs/resolved_issues/<主題>/
   ```

4. **建立 README**
   - 在主題目錄建立或更新 `README.md`
   - 包含：問題描述、解決方案、相關資源、文件清單

5. **更新索引**
   - 在 `docs/resolved_issues/README.md` 新增條目
   - 從 `docs/temporary_issues/README.md` 移除該問題

6. **回報使用者**
   - 說明歸檔路徑
   - 附上關鍵解決方案
   - 確認結案理由

#### 時間要求：

- ⏰ 問題解決後 **24 小時內**完成歸檔
- 📋 保持 `temporary_issues/` 精簡（0-3 個進行中問題）

#### 分類原則：

- 📁 按**主題**分類（如：latex_citation_fix、pdf_conversion、pipeline_optimization）
- 🔗 相關工具與 sandbox 獨立維護，用 symlink 連結文檔
- 📚 保留完整歷史於 `archive/` 供追溯

---

## 7. Sandbox 與文檔關係

### 獨立維護原則

**Sandbox 職能**:
- 提供測試環境（broken data + fixed data）
- 包含錯誤清單與修復流程參考
- 工具與腳本供測試使用

**保留在 Sandbox**:
- `reference_only/` - 修復步驟（測試標準答案）
- `broken/`, `fixed/` - 測試數據
- `tools/` - 修復工具
- `README.md` - 測試環境導覽

**不保留在 Sandbox**:
- 問題追蹤過程文件（移至 resolved_issues）
- 統整報告（移至 resolved_issues）
- 重複的指南（透過 symlink 連結）

### Symlink 策略

從 sandbox 連結至 resolved_issues 的文檔：

```bash
sandbox/<主題>/docs_complete_guide.md → ../../docs/resolved_issues/<主題>/Complete_Guide.md
sandbox/<主題>/docs_quickstart.md → ../../docs/resolved_issues/<主題>/QUICKSTART.md
```

**優點**:
- ✅ Sandbox 保持精簡
- ✅ 文檔有單一權威來源
- ✅ 測試時可參考完整文檔
- ✅ 避免重複與不同步

---

## 8. 預期效果

### 解決的問題

1. ✅ **避免堆積**: `temporary_issues/` 保持精簡，只有進行中問題
2. ✅ **主題分類**: 按主題歸檔，未來問題不會混雜
3. ✅ **結構清晰**: resolved_issues 按主題組織，易於查找
4. ✅ **完整歷史**: archive 保留詳細追蹤過程
5. ✅ **工具獨立**: sandbox 與文檔分離但保持連結

### 維護效益

- 📈 **可擴展**: 新問題主題可獨立建立目錄
- 🔍 **易查找**: 按主題組織，快速定位歷史方案
- 🤝 **易交接**: 清楚的目錄結構與索引文件
- 📚 **知識沉澱**: 解決方案系統性歸檔供重用

---

## 9. 後續維護

### 定期檢視

- 📅 每週檢視 `temporary_issues/`，確認狀態
- 🎯 解決後立即歸檔，避免堆積
- 📊 更新 `resolved_issues/README.md` 統計資訊

### 新問題主題

建立新主題時：

1. 在 `resolved_issues/` 建立主題目錄與 archive
2. 建立該主題的 README.md 總覽
3. 更新 `resolved_issues/README.md` 索引
4. 若有 sandbox，建立 symlink 連結文檔

### 文件同步

- `AGENTS.md` 為權威來源（會自動同步至 CLAUDE.md、GEMINI.md）
- 更新流程時同步修改 `temporary_issue_maintenance.md`
- 保持 `agent-protected-files.md` 與實際保護範圍一致

---

## 10. 驗證結果

### ✅ 目錄結構正確

```
docs/resolved_issues/
├── README.md
└── latex_citation_fix/
    ├── README.md
    ├── (7 個主文件)
    └── archive/
        └── (7 個歷史文件)

docs/temporary_issues/
└── README.md (空模板)

sandbox/latex_citation_fix/
├── README.md
├── COMPLETION_REPORT.md
├── docs_complete_guide.md (symlink)
├── docs_quickstart.md (symlink)
└── (測試核心檔案)
```

### ✅ 檔案完整性

- 13 個檔案已遷移至 resolved_issues
- 6 個冗餘檔案已清理
- 2 個 symlink 已建立
- 2 個索引文件已建立
- 3 個規範文件已更新

### ✅ 規範文件同步

- `AGENTS.md` 新增 Section 12
- `temporary_issue_maintenance.md` 更新結案流程
- `agent-protected-files.md` 更新保護範圍

---

## 11. 結論

✅ **已完成實施問題追蹤與歸檔流程恆例**

- 建立主題分類歸檔機制
- 清理並組織現有文件
- 更新所有相關規範文件
- 建立完整的操作 SOP

**此流程已成為 SurveyX 專案的標準作業程序**，所有 AI Agent 與維護者應遵循此規範管理問題追蹤與文檔歸檔。

---

**報告人**: AI Agent (GitHub Copilot)  
**執行時間**: 2025-10-17 15:30 - 15:50  
**審核**: 待使用者確認
