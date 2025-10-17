
# GitHub 雲端沙箱 + 自動化測試（LLM Agent 模組與 PDF 格式錯誤偵測）—完整說明

> 目的：提供給「本地 AI agent」理解與複製的可執行意圖說明，彙整上面對話中的**所有細節**（不刪減）。

---

## 0) 你的核心需求（意圖）
- 需要一個**雲端、隔離**的測試環境，避免本地環境的權限與可見範圍風險。
- 你會**上傳有問題的 PDF 檔**（或整個資料夾），想測試一份「repo 清單」：
  - 自動逐一 **clone 各 GitHub repo**（只讀、最小權限）。
  - **為每個 repo 建置合適的環境**（優先走 devcontainer，否則 fallback）。
  - **對同一份 PDF 跑錯誤偵測**（glitches、?? 超連結、失效引用等）。
  - **生成各自的報告**，最後你在本地**打包下載**回來評測。
- 希望有一個「coding agent（類似 Copilot）」可以**從頭到尾自動跑測**。
- 額外要求：**避免 agent 讀取限制範圍外的 repo**。

---

## 1) 兩條原生 GitHub 路線（隔離執行）
### A. GitHub Actions（建議）
- **一次性 VM（ephemeral）**：每次工作都在全新 runner 上執行，跑完即重置，適合不可信/實驗性任務。
- **最小權限**：`GITHUB_TOKEN` 可設成 **Read-only**；要讀「被測」repo 時，改用**細粒度 PAT（Fine‑grained）**且**只讀、單一 repo**。
- **Artifacts**：每次執行後可上傳報告供下載。
- **網路控制**：配合工作流設計/白名單策略，可降低 egress 風險（相較 Codespaces 更容易控管）。

### B. GitHub Codespaces（互動式）
- **乾淨的雲端容器/VM**，預設只見建立它的那個 repo 的短期 token。
- **限制**：目前**無法完全封鎖對外網路**（不能做到真正的硬性 egress 阻擋）。若你需要嚴格外連控制，請選 Actions。
- 可在 Codespaces 內用只讀 PAT **手動** `git clone` 指定目標 repo；不會自動讀取其他私有 repo。

> **結論**：若求「隔離 + 最小權限 + 批次自動化」，**Actions 更適合**；若想互動式調整環境，Codespaces 也可用但請留意外連。

---

## 2) 「Copilot coding agent」路線（全自動）
- 你可以把 Issue **指派給 Copilot coding agent**，它會在**Actions 的一次性 VM** 中自動：
  - clone 指定 repo、建置環境、執行任務、以 **草稿 PR/註解附上 log/產物** 回報。
  - 可設定**可連線目的地白名單**（降低外連風險）。
- 方案註記：我們在對話中分別提到 **Copilot Enterprise / Pro+** 與 **Copilot Enterprise/Business**（命名有出入）。實際可用方案與名稱以 GitHub 當前產品為準，但結論是：**需要企業等級的 Copilot** 版本才能使用「coding agent」。

---

## 3) 上傳本地 PDF／資料夾的方式
- **放到 GitHub repo**：在目標 repo（建議新開 **sandbox/harness 私有 repo**）中，使用「Add file → Upload files」上傳 PDF 或整個資料夾。
- **VS Code/Codespaces**：直接把本地檔拖入工作區；或用 GitHub CLI（例如 `gh codespace cp`）在本地與雲端互傳。

> 建議在 sandbox/harness 裡建立 `inputs/` 目錄，將要測的 PDF 放入（例如 `inputs/problem.pdf`）。

---

## 4) 強烈建議：**拆成獨立私有 repo**（sandbox/harness）
### 為何要拆
- **可見範圍乾淨**：runner 只會 checkout sandbox repo，agent 看不到你原本大 repo 的其他內容。
- **最小權限**：`GITHUB_TOKEN` 只對 sandbox 有效；讀目標 repo 一律用**只讀、單一 repo 的 Fine‑grained PAT**。
- **審計/刪除容易**：測試腳本、adapters、報告全部集中在 sandbox；刪除或封存不影響主專案。
- **矩陣測試直觀**：一個 workflow 併行掃一串目標 repos，不與主專案的 CI/CD 相互干擾。
- **與 Copilot agent 搭配更單純**：只授權必要最小集合。

### 若暫時不拆（放在大 repo 的子資料夾）
- 仍可運作，但 runner 會把「整個大 repo」檔案帶進工作目錄，**agent 能讀到無關檔案**。
- 緩解（較繁瑣）：
  - 在 workflow 開始時，把 `sandbox/` 子樹 **同步到獨立 `work/` 目錄**，然後清掉其餘檔案再執行。
  - Repo 設 **Workflow permissions = Read-only**；所有對目標 repo 的讀取嚴格用**只讀細粒度 PAT**；禁止對主分支寫回。
- 但**根本的可見性**仍遜於獨立 repo。

### 建議的 sandbox repo 結構
```
pdf-qa-sandbox/
├─ inputs/               # 你的 PDF
├─ harness/              # 共用測試腳本、adapters、runner
│  ├─ run_detector.py
│  └─ adapters.yaml      # (選) repo → 命令/介面映射
└─ .github/workflows/
   └─ pdf-qa-sandbox.yml # 見下方範本
```

---

## 5) Actions 版「最小可行」工作流程（workflow）
> 功能：讀取你給的「repo 清單」，以 **matrix 併行**逐一：只讀 clone → 優先 devcontainer 執行 → fallback（Python 範例）→ 產生報告 → 上傳 Artifacts。

```yaml
name: PDF QA Sandbox

on:
  workflow_dispatch:
    inputs:
      pdf_path:
        description: 'PDF path in this repo'
        required: true
        default: 'inputs/problem.pdf'
      repos:
        description: |-
          One per line: owner/name@ref (ref optional)
        required: true

permissions:
  contents: read   # 最小權限的 GITHUB_TOKEN
  actions: read

jobs:
  fanout:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.mk.outputs.matrix }}
    steps:
      - name: Build matrix from input
        id: mk
        run: |
          echo "${{ inputs.repos }}" | awk 'NF{print}' > list.txt
          sudo apt-get update && sudo apt-get install -y jq
          echo "matrix=$(jq -R -s '{target: (split("\n")|map(select(length>0)))}' list.txt)" >> "$GITHUB_OUTPUT"

  analyze:
    needs: fanout
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix: ${{ fromJson(needs.fanout.outputs.matrix) }}
    steps:
      - name: Checkout harness
        uses: actions/checkout@v4

      - name: Parse repo/ref
        id: parse
        run: |
          IFS='@' read REPO REF <<< "${{ matrix.target }}"
          echo "repo=$REPO" >> $GITHUB_OUTPUT
          echo "ref=${REF:-main}" >> $GITHUB_OUTPUT

      - name: Checkout TARGET repo (read-only PAT)
        uses: actions/checkout@v4
        with:
          repository: ${{ steps.parse.outputs.repo }}
          ref: ${{ steps.parse.outputs.ref }}
          token: ${{ secrets.TARGET_REPO_RO_PAT }}   # 細粒度 PAT：單一 repo + Contents:Read
          path: target
          fetch-depth: 1

      # 若目標 repo 有 .devcontainer/，就用它的環境執行 analyze.sh
      - name: Run in devcontainer if present
        if: ${{ hashFiles('target/.devcontainer/**') != '' }}
        uses: devcontainers/ci@v0.3
        with:
          runCmd: |
            bash -lc 'mkdir -p output && ./analyze.sh "${{ github.workspace }}/${{ github.event.inputs.pdf_path }}" "${{ github.workspace }}/output" || true'
          workspaces: |-
            .
            target

      # 簡易 fallback（Python 範例）
      - name: Fallback runner (Python)
        if: ${{ hashFiles('target/.devcontainer/**') == '' }}
        run: |
          python -m venv .venv && . .venv/bin/activate
          if [ -f target/requirements.txt ]; then pip install -r target/requirements.txt || true; fi
          python harness/run_detector.py \
            --pdf "${{ github.event.inputs.pdf_path }}" \
            --tool-dir target \
            --out "output/${{ steps.parse.outputs.repo//\//- }}.json"

      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: report-${{ steps.parse.outputs.repo }}
          path: output/**
```

### 關鍵設計說明
- **Matrix**：`fanout` job 以 `jq` 生成 JSON matrix，`analyze` 併行處理每個 `owner/name@ref`。
- **只讀 checkout**：對目標 repo 使用 **細粒度 PAT**（`TARGET_REPO_RO_PAT`），權限**鎖到單一 repo、只讀**。
- **devcontainer 優先**：若對方 repo 有 `.devcontainer/`，用 `devcontainers/ci@v0.3` 在它的容器定義裡執行 `analyze.sh`。
- **Fallback**：以 Python 虛擬環境展示最簡 fallback；你可擴充 Node/Java/… 分支或多語言偵測器。
- **Artifacts**：每個目標 repo 會有一個 `report-<owner/name>` 產物可下載。

---

## 6) 你的測試腳本（範例介面）
### `harness/run_detector.py`（自訂）
- 負責「吃 PDF → 呼叫被測工具 → 產出統一格式的報告（JSON/Markdown 皆可）」。
- 範例 CLI（上面 workflow 已呼叫）：
  ```bash
  python harness/run_detector.py \
    --pdf inputs/problem.pdf \
    --tool-dir target \
    --out output/owner-repo.json
  ```
- 你可以在 `adapters.yaml` 規範不同 repo 的呼叫方式（例如 CLI 名稱、環境需求、輸出位置）。

### `target/analyze.sh`（建議規範）
- 若被測 repo 願意配合，要求它們提供一個通用的 `analyze.sh`：
  ```bash
  ./analyze.sh <PDF_ABS_PATH> <OUTPUT_DIR_ABS_PATH>
  ```
- 這能讓 devcontainer 路線完全自包含。

---

## 7) 安全與隔離重點（不遺漏）
- **一次性 runner**：GitHub-hosted runners 每次都是全新 VM，**跑完即銷毀**。
- **Workflow permissions 設為 Read-only**；需要時在 job/step 上再**個別開必要 scope**。
- **細粒度 PAT（Fine‑grained）**：嚴格限縮到「**單一目標 repo、Contents: Read**」，避免廣域個人 token。
- **禁止寫回主分支/異動目標 repo**：不必要就別開寫權；必要時走 fork / PR、受 branch protection 管控。
- **Codespaces 外連限制**：目前**不能完全封鎖**；若風險模型要求強控管，選 Actions 或在 agent 端做白名單約束。
- **Copilot coding agent**：可設定網路白名單；仍受你原本的 branch protection / 必要審核規則管控。
- **檔案可見性**：獨立 sandbox repo > 大 repo 子資料夾；後者即使清理，仍有誤讀/洩露風險。

---

## 8) 用 VS Code 還是 GitHub 網頁？（兩者都行）
### 在 VS Code 內完成（推薦）
- 安裝官方延伸模組：
  - **GitHub Actions**：看 logs、觸發/重跑 workflow。
  - **GitHub Pull Requests and Issues**：管理 Issue（若走 Copilot agent）。
- 設定 secrets（不開網頁也可）：
  ```bash
  gh auth login
  gh secret set TARGET_REPO_RO_PAT
  ```
- 觸發 workflow（帶 inputs）：
  ```bash
  gh workflow run pdf-qa-sandbox.yml \
    -F pdf_path=inputs/problem.pdf \
    -F repos="$(printf '%s\n' owner1/repo1@main owner2/repo2@v1.2)"
  ```
- 下載報告（Artifacts）：
  ```bash
  gh run download             # 下載最新一次（或指定 --name / --run-id）
  ```

### 全程 GitHub 網頁也可以
- 上傳檔案、建立/編輯 workflow、設定 Secrets、手動執行 `workflow_dispatch`、下載 Artifacts 都能在網頁完成。

---

## 9) 執行清單（Checklist）
- [ ] 建立**獨立私有 repo**：`pdf-qa-sandbox`（或你要的名稱）。
- [ ] 建目錄：`inputs/`、`harness/`、`.github/workflows/`。
- [ ] 放入 PDF → `inputs/problem.pdf`（或多份）。
- [ ] 寫好 `harness/run_detector.py`（與 `adapters.yaml` / `analyze.sh` 規範）。
- [ ] 新增 `pdf-qa-sandbox.yml`（上面範本）。
- [ ] 建立 **細粒度 PAT**（針對每個「被測」repo，或共用一把但每次限定單一 repo），設為 repo secret：`TARGET_REPO_RO_PAT`。
- [ ] 在 VS Code 或網頁**手動觸發 workflow**，貼上：
  - `pdf_path`: 你的 PDF 路徑。
  - `repos`: 每行 `owner/name@ref`。
- [ ] 在 **Artifacts** 下載 `report-*` 檔案；或用 `gh run download`。

---

## 10) 若要從大 repo 抽離 sandbox
- 可用 `git subtree split` 或 `git filter-repo`（較新、彈性更好）把 `sandbox/` 目錄抽出成獨立歷史的新 repo。
- 抽離後照本說明配置 workflow / secrets 即可。

---

### TL;DR（一句話總結）
> **把 sandbox 拆成獨立私有 repo**，上傳你的 PDF；用提供的 **Actions 工作流** 以 **matrix** 併行、只讀 PAT + devcontainer/fallback 跑測各目標 repo，最後在 **Artifacts** 中下載報告。要全自動，可用 **Copilot coding agent** 在一次性 VM 中跑並 PR 回報。
