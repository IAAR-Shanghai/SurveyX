# Sandbox - AI Agent 練習環境

此目錄包含用於 AI Agent 練習與實驗的場景。

## 可用的練習場景

### 1. latex_citation_fix/

**問題類型**: LaTeX 編譯錯誤、引用系統問題  
**難度**: ⭐⭐⭐⭐ (中高)  
**學習目標**:
- 理解 LaTeX 套件選項衝突
- 掌握 LaTeX 轉義規則
- 練習批量檔案修改技巧
- 系統性調試流程

詳見: `latex_citation_fix/README.md`

---

## 使用指南

### 目錄結構

每個練習場景包含:
- `backup/` - 原始檔案備份 (唯讀)
- `broken/` - 有問題的版本 (參考用)
- `fixed/` - 正確版本 (參考答案,可選)
- `agent_workspace/` - Agent 工作區 (可任意修改)
- `tools/` - 驗證與重置工具

### 工作流程

1. **開始**: `cd <scenario>/tools && ./reset.sh`
2. **診斷**: 分析問題,查看錯誤
3. **修復**: 在 `agent_workspace/` 中修改
4. **驗證**: `python tools/verify.py agent_workspace/`
5. **重置**: 如需重新開始,執行 `./reset.sh`

---

## 添加新練習場景

1. 在 `sandbox/` 創建新目錄
2. 遵循標準結構: `backup/`, `broken/`, `fixed/`, `agent_workspace/`, `tools/`
3. 創建 README.md 說明問題與目標
4. 實作 `verify.py` 驗證腳本
5. 實作 `reset.sh` 重置工具
6. 更新本 README

---

**維護者**: GitHub Copilot (AI Agent)  
**最後更新**: 2025-10-16
