# Resolved Issues（已解決問題歸檔）

本目錄用於歸檔已解決的問題及其解決方案，按主題分類存放。

---

## 📁 目錄結構

```
resolved_issues/
├── README.md                    # 本檔案（總索引）
└── <主題名稱>/                  # 各主題獨立目錄
    ├── README.md               # 該主題總覽
    ├── <相關文件>.md           # 問題記錄、解決方案、指南等
    └── archive/                # 該主題的歷史文件
```

---

## 📚 已歸檔的問題

### 1. LaTeX Citation Fix（LaTeX 引用問題修復）

**路徑**: `latex_citation_fix/`  
**解決日期**: 2025-10-16  
**狀態**: ✅ 已完全解決

**問題摘要**:
- natbib 與 xcolor 套件衝突
- 缺失顏色定義（c12-c16）
- 重複的 bibliography 指令
- 245 處 double-escaped citations (`\\cite{}`)
- Page 58 spacing glitch
- Figure placement 問題

**解決方案**:
- 一鍵修復腳本: `scripts/fix_latex_issues.py`
- 完整指南: `latex_citation_fix/LaTeX_Fix_Complete_Guide.md`
- 快速參考: `latex_citation_fix/QUICKSTART.md`

**相關資源**:
- Sandbox 測試環境: `sandbox/latex_citation_fix/`
- 修復工具: `sandbox/latex_citation_fix/tools/latex_fix_toolkit.py`

**文件清單** (7 個主文件 + 7 個歷史文件):
- `LaTeX_Fix_Complete_Guide.md` - 完整指南（12KB）
- `QUICKSTART.md` - 快速參考（3.2KB）
- `Documentation_Consolidation_and_OneClick_Fix_Report.md` - 統整報告
- `Figure_Fix_Completion_Report.md` - Figure 修復報告
- `Figure_Placement_Issue.md` - Figure placement 問題追蹤
- `SANDBOX_COMPLETION_REPORT.md` - Sandbox 完成報告
- `README.md` - 該主題總覽與導覽
- `archive/` - 7 個歷史追蹤文件

---

## 🔍 如何使用本目錄

### 查找已解決的問題

1. 查看本 README 的「已歸檔的問題」列表
2. 進入對應主題目錄查看詳細文件
3. 閱讀該主題的 README.md 了解問題概況

### 參考解決方案

每個主題目錄包含：
- **完整指南**: 詳細的問題分析與解決步驟
- **快速參考**: 常用指令與操作
- **相關工具**: 自動化腳本或修復工具
- **歷史記錄**: archive/ 中的詳細追蹤過程

### 提取可重用資源

- 修復腳本通常位於 `scripts/` 或主題目錄的 `tools/`
- Sandbox 測試環境位於 `sandbox/<主題>/`
- 可將成功的解決方案模式應用於類似問題

---

## 📋 歸檔原則

### 何時歸檔

問題符合以下條件時應移至本目錄：
- ✅ 問題已完全解決或不再需要追蹤
- ✅ 解決方案已驗證且可重現
- ✅ 相關文件已整理完善

### 歸檔流程

1. **建立主題目錄**: `mkdir -p resolved_issues/<主題>/archive`
2. **移動文件**: 從 `temporary_issues/` 移動相關文件
3. **建立 README**: 在主題目錄建立總覽文件
4. **更新索引**: 在本檔案新增條目
5. **清理來源**: 從 `temporary_issues/` 移除已歸檔問題

### 文件組織

- **主目錄**: 存放核心文件（指南、報告、快速參考）
- **archive/**: 存放詳細追蹤過程、歷史版本、一次性記錄
- **保持精簡**: 避免重複內容，優先整合為單一權威文件

---

## 🔗 相關文件

- **進行中問題**: `docs/temporary_issues/`（應保持為空或極少檔案）
- **維護指南**: `docs/guides/temporary_issue_maintenance.md`
- **Agent 規範**: `AGENTS.md` Section "問題追蹤與歸檔流程"
- **受保護檔案**: `docs/agent-protected-files.md`

---

## 📊 統計資訊

| 統計項目 | 數量 |
|---------|------|
| 已歸檔主題 | 1 |
| 總文件數 | 14 |
| 涵蓋問題數 | 8+ |

---

**維護者**: GitHub Copilot (AI Agent)  
**最後更新**: 2025-10-17  
**遵循規範**: `docs/guides/temporary_issue_maintenance.md`
