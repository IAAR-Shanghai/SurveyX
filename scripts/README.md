````markdown
# Scripts Directory

這個資料夾包含專案的輔助腳本，分為以下類別：

## Unicode Glitch 工具 (新增)

用於偵測與修復 LaTeX 檔案中的 Unicode 數學符號問題，這些符號會導致 PDF 產生 spacing glitch。

### detect_unicode_glitches.py
偵測 LaTeX 檔案中的 Unicode 數學符號並生成報告。

**使用方式**:
```bash
# 生成報告到檔案
python scripts/detect_unicode_glitches.py outputs/xxx/latex/survey.tex -o report.txt

# 輸出到螢幕
python scripts/detect_unicode_glitches.py outputs/xxx/latex/survey.tex
```

### fix_unicode_glitches.py
自動修復 LaTeX 檔案中的 Unicode 數學符號,將其替換為對應的 LaTeX 巨集。

**使用方式**:
```bash
# 預覽變更 (不修改檔案)
python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex --preview

# 修復並建立備份
python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex

# 修復並儲存為新檔案
python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex -o survey_fixed.tex

# 修復且不建立備份
python scripts/fix_unicode_glitches.py outputs/xxx/latex/survey.tex --no-backup
```

### fix_and_recompile.py / fix_and_recompile.sh (一鍵修復)
自動偵測、修復 Unicode 符號並重新編譯 LaTeX,生成新的 PDF。

**使用方式**:
```bash
# Python 版本 (推薦,更可靠)
python scripts/fix_and_recompile.py 2025-10-09-1630_speec

# Bash 版本
bash scripts/fix_and_recompile.sh 2025-10-09-1630_speec
```

**執行步驟**:
1. 偵測 Unicode 符號並生成報告
2. 備份原始 .tex 檔案
3. 修復所有 Unicode 符號
4. 重新編譯 LaTeX 並生成 PDF (含浮水印版本)

**詳細說明**: 請參閱 `docs/temporary_issues/spacing_glitch_solution.md`

---

## Git Helper Scripts

這個資料夾包含 Git 輔助腳本，用於：
1) 建立並維護「舊版穩定線 + 最新開發線」的分支策略。
2) 一鍵建立功能分支、同步 main、收尾合併與清理。

## 1) init_branching.sh
- 目的：
  - 將目前提交點標記為舊版基線（包含 `docs/` 的狀態）。
  - 建立長期維護分支（例如 `legacy-stable`）。
  - 確保存在一條開發分支（例如 `main` 或 `develop`）。
  - 選配：推送分支與標籤到遠端。
- 需求：
  - 工作樹乾淨（無未提交/暫存變更）。
  - 在 repo 根目錄執行。
- 使用：
  - 預設（不推遠端）
    ```bash
    bash scripts/git/init_branching.sh
    ```
  - 預設並推送到 `origin`
    ```bash
    bash scripts/git/init_branching.sh --push
    ```
  - 自訂名稱與遠端
    ```bash
    bash scripts/git/init_branching.sh \
      --legacy-branch legacy-v1 \
      --legacy-tag v1.0.0-legacy \
      --dev-branch develop \
      --remote origin \
      --push
    ```
- 預設參數：
  - `--legacy-branch legacy-stable`
  - `--legacy-tag v0.1-legacy-with-docs`
  - `--dev-branch main`
  - `--remote origin`

## 2) new_feature_branch.sh
- 目的：
  - 從指定的開發分支（預設 `main`）切出新的功能分支，例如 `feat/refactor-io-layer`。
  - 選配：建立後直接推送至遠端。
- 需求：
  - 工作樹乾淨（無未提交/暫存變更）。
  - 在 repo 根目錄執行。
- 使用：
  - 從 `main` 切出 `feat/refactor-io-layer` 並推送：
    ```bash
    bash scripts/git/new_feature_branch.sh --name refactor-io-layer --push
    ```
  - 指定來源分支與前綴：
    ```bash
    bash scripts/git/new_feature_branch.sh \
      --name export-cli \
      --from develop \
      --prefix feat \
      --remote origin \
      --push
    ```
- 參數：
  - `--name <feature-name>`（必填）
  - `--from <dev-branch>`（預設：`main`）
  - `--prefix <prefix>`（預設：`feat`）
  - `--remote <remote>`（預設：`origin`）
  - `--push`（可選）

## 2.1) start_feature.sh（建議使用，簡化版）
- 目的：
  - 從最新的 `main` 一鍵切出 `feat/<name>`，可選「自動建立當日 QA 檔」與「直接推送」。
- 使用：
  - 一鍵開始並建立 QA：
    ```bash
    bash scripts/git/start_feature.sh --name pdf-ingestion --seed-qa --push
    ```
  - 參數：
    - `--name <feature-name>`（必填）
    - `--prefix <prefix>`（預設：`feat`）
    - `--remote <remote>`（預設：`origin`）
    - `--seed-qa`（可選：自動產生 `docs/qa-notes/<date>-<name>-qa.md` 並提交）
    - `--push`（可選）

## 2.2) sync_with_main.sh
- 目的：
  - 將功能分支與最新 `main` 同步，支援 `merge` 或 `rebase`。
- 使用：
  - 合併（預設）：
    ```bash
    bash scripts/git/sync_with_main.sh --branch feat/pdf-ingestion --mode merge
    ```
  - 重置為 rebase：
    ```bash
    bash scripts/git/sync_with_main.sh --branch feat/pdf-ingestion --mode rebase
    ```
  - 參數：
    - `--branch <name>`（不填則對當前分支操作）
    - `--mode merge|rebase`（預設：merge）
    - `--remote <remote>`（預設：origin）

## 3) rename_branch.sh
- 目的：
  - 將某分支改名（包含目前所在分支也可改名），可選擇同步遠端：刪除舊遠端分支、推送新分支並設定追蹤。
- 使用：
  - 改名本地目前分支為 `feat/pdf-ingestion` 並推送：
    ```bash
    bash scripts/git/rename_branch.sh --new feat/pdf-ingestion --push
    ```
  - 指定舊名與新名（不切換當前分支）：
    ```bash
    bash scripts/git/rename_branch.sh --old feat/newest_dev --new feat/pdf-ingestion --push
    ```

## 4) delete_branch.sh
- 目的：
  - 刪除本地與/或遠端分支（安全檢查：不可刪除目前所在分支、需工作樹乾淨）。
- 使用：
  - 同時刪除本地與遠端：
    ```bash
    bash scripts/git/delete_branch.sh --name feat/newest_dev --both
    ```
  - 僅刪本地：
    ```bash
    bash scripts/git/delete_branch.sh --name feat/newest_dev --local
    ```
  - 僅刪遠端（指定遠端）：
    ```bash
    bash scripts/git/delete_branch.sh --name feat/newest_dev --remote-delete --remote origin
    ```

## 5) finish_feature.sh（收尾）
- 目的：
  - 完成功能分支後，一鍵推送並提示開 PR；或直接在本機合併到 `main`、推送並刪除分支。
- 使用：
  - 推送並提示開 PR（預設）：
    ```bash
    bash scripts/git/finish_feature.sh --branch feat/pdf-ingestion
    ```
  - 在本機直接合併到 `main`，推送並刪除分支：
    ```bash
    bash scripts/git/finish_feature.sh --branch feat/pdf-ingestion --merge-local --delete
    ```
  - 參數：
    - `--branch <feature-branch>`（不填則用當前分支）
    - `--target <target-branch>`（預設：`main`）
    - `--remote <remote>`（預設：`origin`）
    - `--merge-local`（在本機直接合併 feature -> target 並推送）
    - `--delete`（與 `--merge-local` 搭配：刪除本地與遠端 feature 分支）

## 6) sync_legacy_with_main.sh（用 main 蓋回 legacy）
- 目的：
  - 讓 `legacy-stable` 與 `main` 同步，可選三種模式：
    - `fast-forward`：僅快轉（安全，若歷史已分歧會失敗）
    - `merge`：建立一個合併提交，保留雙方歷史
    - `hard-reset`：以 `main` 為準強制覆蓋 `legacy-stable`（會改寫歷史）
- 使用：
  - 快轉（若無分歧）：
    ```bash
    bash scripts/git/sync_legacy_with_main.sh --mode fast-forward --push
    ```
  - 合併：
    ```bash
    bash scripts/git/sync_legacy_with_main.sh --mode merge --push
    ```
  - 強制覆蓋（小心）：
    ```bash
    bash scripts/git/sync_legacy_with_main.sh --mode hard-reset --push
    ```
- 參數：
  - `--legacy-branch <name>`（預設：`legacy-stable`）
  - `--source-branch <name>`（預設：`main`）
  - `--mode fast-forward|merge|hard-reset`（預設：`fast-forward`）
  - `--remote <remote>`（預設：`origin`）
  - `--push`（可選）

## 7) sync_paths_to_branch.sh（只同步指定路徑）
- 目的：
  - 僅同步特定路徑（例如 `scripts/`、`docs/qa-notes/`）從某分支帶到目標分支，不影響其他檔案。
- 使用：
  - 從 `main` 同步 `scripts` 與 `docs/qa-notes` 到 `legacy-stable` 並推送：
    ```bash
    bash scripts/git/sync_paths_to_branch.sh \
      --from main \
      --to legacy-stable \
      --paths "scripts docs/qa-notes" \
      --push
    ```
- 參數：
  - `--from <source-branch>`（預設：`main`）
  - `--to <target-branch>`（預設：`legacy-stable`）
  - `--paths "<空白分隔的多個路徑>"`（必填）
  - `--remote <remote>`（預設：`origin`）
  - `--push`（可選）

## 建議工作流（針對你目前狀態：main 與 legacy-stable 已同步）
1) 開始新需求（切分支並建立 QA）
   ```bash
   bash scripts/git/start_feature.sh --name <feature-name> --seed-qa --push
   ```
2) 開發過程中定期同步 main
   ```bash
   bash scripts/git/sync_with_main.sh --mode merge   # merge 或 --mode rebase
   ```
3) 收尾：推送並開 PR（建議）
   ```bash
   bash scripts/git/finish_feature.sh   # 在 feature 分支執行，會 push 並提示 PR
   ```
   或者直接在本機合併（小型專案或你個人倉庫）：
   ```bash
   bash scripts/git/finish_feature.sh --merge-local --delete
   ```
4) 舊版維護（需要時）
   - `legacy-stable` 僅做必要 hotfix，依需要發 `v0.1.x` 標籤。

> 小提示：腳本不依賴可執行權限，可用 `bash scripts/...` 直接執行；若需改為直接執行可自行 `chmod +x`。
