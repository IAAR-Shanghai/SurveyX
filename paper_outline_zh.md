# **Speech Tokenizers and Speech Language Models: A Survey of Representations, Modeling, and Systems** —— 論文大綱（中文整理）

> 本大綱依據使用者提供之 `outlines.json` 彙整，除專有名詞外皆以中文呈現。

---

## 1. Introduction（導論）
- **為何此刻：從串接式 ASR→LLM→TTS 邁向統一的 SLM**  
  說明技術推力（模型擴展、neural audio codec、自監督編碼器、modality projector）與使用需求（互動代理、全雙工對話）使端到端 SLM 成為適時之選。
- **範圍、貢獻與分類法**  
  定義涵蓋主題（token 類型與速率；建模與生成；對齊與評估），並提出：token 分類、設計比較、與統一的訓練/評估實務。
- **表徵–延遲–比特率三難**  
  以語義忠實度、聲學細節與延遲/比特率之間的核心張力框定全文的取捨分析。
- **Survey 路線圖**  
  以 1–2 句預告各節：背景、tokenization、encoders、decoding、language modeling、training、systems、expressivity、streaming、datasets、metrics、efficiency、safety、tools、challenges、結語。
- **不在範圍內**  
  排除純文字 LLM、傳統 HMM/GMM 管線，以及非語音音訊領域（除非具啟發性）。

---

## 2. Background and Core Concepts（背景與核心概念）
- **從波形到語言模型再回來：管線與術語**  
  定義 speech tokenizer/quantizer、neural audio codec、VQ/RVQ、離散 vs 連續 tokens、semantic/acoustic/paralinguistic/mixed tokens、encoders、token-to-speech decoders、vocoders。
- **典型組件與代表模型**  
  概述 Encodec、SoundStream、HiFi-GAN、HuBERT、wav2vec、data2vec、Whisper、PAST 等在堆疊中的角色。
- **Token 介面與其速率**  
  釐清 semantic / acoustic / paralinguistic / mixed / continuous 介面、典型比特率與序列長度，及其對 LM 情境長度的影響。
- **資料集與評估家族概覽**  
  簡述核心語料（LibriSpeech、Common Voice、VoxPopuli、LibriTTS、CoVoST2、VoxCeleb、GigaSpeech、AISHELL、Fisher）與評估（ABX、sWUGGY/sBLIMP、sStoryCloze、SUPERB、VoxEval、MOS、WER、BLEU、BERTScore、FAD、RTF）。

---

## 3. Speech Tokenization and Neural Audio Codecs（語音標記化與神經音訊編解碼）
- **標記化目標與 LM 介面契約**  
  聚焦重建、語義保留、韻律維持等目標，以及 token 串流如何與 LM 在可預測性與條件設置上對接。
- **量化機制與 codec 家族**  
  說明 VQ/RVQ、殘差/乘積量化、RQ-Transformer、PQ-VAE、FSQ/BSQ；討論 index collapse 防治、codebook 使用與穩定性。
- **從連續特徵到離散單元：離散化與 codebook 設計**  
  涵蓋特徵來源（encoder 層）、粒度、codebook 大小/粗細與其對音素/詞彙/句級任務的效應。
- **速率與序列管理**  
  設定 frame-rate、比特率/序列長度取捨、acoustic BPE、壓縮，以及低比特率下的魯棒性。
- **解耦與混合 token 設計**  
  介紹多串流/混合 tokens 分離語義、聲學與韻律；以及風格/內容解耦機制。
- **連續與無 codec 介面**  
  檢視連續 token/特徵介面、無 codec 模式，相對於離散單元的魯棒與延遲特性。
- **代表方法與實證發現**  
  比較 Encodec、SoundStream、PAST、ALMTokenizer、RepCodec、HASRD、XY Tokenizer、LM-SPT、Universal token learning：整理比特率、重建、語義對齊等結果。
- **比較座標與未解議題**  
  彙整評比軸：重建、比特率、序列長度、語義忠實度、下游 SLM 表現、跨語言遷移；並點出開放挑戰。

---

## 4. Speech Encoders and Representations（語音編碼器與表徵）
- **編碼器家族與層級專化**  
  概述 HuBERT、wav2vec、data2vec、Whisper、PAST；說明各層在音系/語義上的專化與選擇策略。
- **表徵融合與選擇**  
  描述跨層/跨模型融合，以及挑選層作為標記化或直接條件化的啟發式。
- **魯棒性、串流與部署限制**  
  分析噪音/通道魯棒、裝置端限制、適合串流的 encoders，以及計算–延遲取捨。
- **表徵品質診斷**  
  使用 probes 與指標（ABX、音素分類、語義相似度）評估不變性與任務就緒度。
- **離散化 vs 連續條件化**  
  何時將 encoder 特徵離散化、何時以連續向量使用，以及對 LM 對齊的影響。
- **與文字 LLM 的對齊挑戰**  
  指出模態落差（聲調、韻律、時長）與橋接策略。

---

## 5. Token to Speech Decoding and Vocoders（Token→語音解碼與聲碼器）
- **解碼目標與路徑**  
  對比 codec 解碼器（Encodec/SoundStream）、unit vocoder、token→mel→neural vocoder 的管線。
- **目標家族與骨幹**  
  總結 GAN（HiFi-GAN）、flow/diffusion、AR/NAR 解碼器；涵蓋忠實度、韻律與說話人識別的損失設計。
- **連續–離散混合路線**  
  結合連續向量與語義 tokens，以保留音色並減少失真。
- **條件、可控性與風格維持**  
  涵蓋 prompt 條件、speaker embeddings、殘差向量，與情緒/韻律控制及延遲考量。

---

## 6. Language Modeling over Speech Tokens（語音 tokens 上的語言建模）
- **建模目標與架構**  
  對比 decoder-only AR、NAR、dual-token modeling、flow-matching；以及語音/文字交織序列。
- **模態遷移與 LLM 適配**  
  說明冷啟動 vs 持續預訓練、modality projectors、跨模態對齊損失。
- **交織與全雙工建模範例**  
  討論 DualSpeechLM、FlowSLM、VecTokSpeech、Ichigo；處理混合序列與雙工互動。
- **經驗規律與擴展趨勢**  
  整理隨規模與 token-rate 變化對 perplexity 與品質的影響，及對算力配置的啟示。

---

## 7. Training Paradigms and Modality Alignment（訓練範式與模態對齊）
- **多階段流程**  
  概述 pretraining、modality adaptation、supervised fine-tuning、instruction tuning、post-alignment（如 DPO）。
- **對齊機制與藍圖**  
  詳述 projectors、grounding、distillation、Stitch/KL alignment，以及 tokenizer→LM→decoder 之目標耦合。
- **大規模合成/程式監督**  
  介紹自動配對與可擴展指令資料（LLaSO、LLaMA Omni-KE、Omni VoiceTextBlender、Slamming）之利弊。
- **模態對齊、序列壓縮與介面一致**  
  在不破壞對齊的前提下進行壓縮，並維持穩定的 token 介面。
- **診斷、消融與報告**  
  建議量測對齊品質、遺忘與跨模態保留的作法，並強調透明報告。

---

## 8. System Architectures and Generation Strategies（系統架構與生成策略）
- **串接 vs 端到端 vs 交織**  
  以延遲、可控性、錯誤傳播對比各類架構；包含平行與交織變體。
- **生成機制與高效骨幹**  
  涵蓋 hierarchical RVQ、flow/diffusion backbones、Groupformer、RQ-Transformer、multi-token prediction 等長期序列方法。
- **排序與排程分類**  
  定義 interleaving、parallel、chunked generation；說明各自適用任務。
- **無文字 S2S 與雙分支設計**  
  討論語義+聲學聯合生成、textless S2ST、與雙分支的對齊/預測系統。

---

## 9. Expressivity, Paralinguistics, and Style Control（表現力、 副語言與風格控制）
- **韻律、說話人與情緒建模**  
  回顧 GOAT-SLM、ProsodyLM、SeamlessExpressiveLM 等捕捉韻律輪廓與說話人特徵的機制。
- **為表現力而設計的 tokenization**  
  介紹詞級韻律 tokens、多流聲學單元、與保留風格線索的統一 tokens。
- **控制介面與 prompts**  
  詳述 prompts、指令與 token 操作，用於風格轉換、角色扮演、可編輯性。
- **評估與浮水印**  
  描述 ALLM 評審與人工評審、可控性指標，以及針對編輯片段的 watermark（如 SSR Speech）。

---

## 10. Real-Time Streaming and Duplex Dialogue（即時串流與全雙工對話）
- **延遲感知設計**  
  說明分塊、緩衝、低比特率 tokenization、與以預算為導向的推論，以支援互動代理。
- **ASR/S2ST 串流政策**  
  涵蓋 wait-k、read–write、增量解碼，並說明與 tokenizers 與 SLM 的整合。
- **全雙工與輪替**  
  討論 barge-in、重疊處理、backchanneling、打斷偵測與對話政策學習。
- **串流與雙工架構**  
  描述 streaming encoders 與 interleaved decoders（如 SALM Duplex、NTPP、SyncSpeech、Ichigo、Stitch）與即時部署。

---

## 11. Datasets, Benchmarks, and Tasks（資料集、基準與任務）
- **核心語料與資料分類**  
  彙整 LibriSpeech、LibriTTS、Common Voice、VoxPopuli、CoVoST2、VoxCeleb、GigaSpeech、AISHELL、Fisher、TELEVAL、CVSS-C，依模態/領域/語言分類。
- **任務–資料–指標對映**  
  將 ASR、TTS、S2ST、spoken QA、dialogue、style control、duplex 等任務對映至資料集與標準流程。
- **Benchmark 套件與排行榜**  
  整理 SUPERB、VoxEval、ABX/sWUGGY/sBLIMP/sStoryCloze 等能力導向榜單。
- **多語、魯棒與串流**  
  強調低資源、噪音與串流評估資料集，以及領域遷移考量。
- **資料品質與可再現性**  
  討論切分、污染檢查、授權，以及確保公平可比的實務。

---

## 12. Evaluation Metrics and Methodology（評估指標與方法學）
- **指標分類與目標導向選擇**  
  說明 MOS、WER、BLEU/BERTScore、FAD、perplexity、codebook usage、bitrate、重建指標，與何時選用。
- **端到端流程**  
  制定語音生成、串流與雙工對話的評估設定（合適任務與控制變因）。
- **比特率與 token-rate 感知評估**  
  設計在 frame/token 速率、語義忠實 vs 聲學品質、壓縮穩定性上的消融。
- **延遲指標與方法**  
  定義 real-time factor、time-to-first-token、串流延滯、雙工重疊處理的標準化量測。
- **人因介入與統計嚴謹**  
  制定人/ALLM 評審協議、一致性與顯著性檢驗。

---

## 13. Efficiency, Compression, and Deployment（效率、壓縮與部署）
- **參數與訓練效率**  
  涵蓋 LoRA/PEFT、部分微調、避免災難性遺忘的策略。
- **模型與序列效率**  
  說明 acoustic BPE、token-rate 降低、knowledge distillation、TinyWave、緊湊交織模型、序列並行化。
- **快速解碼與串流**  
  提出 multi-token prediction、speculative decoding、KV-caching 等降低壁鐘延遲的技術。
- **頻寬與邊緣–伺服器取捨**  
  在比特率限制下評估計算/記憶/頻寬、量化與 MoE 專門化。
- **實作配方與基準**  
  提供可重現的效率基準與即時/雙工部署範式。

---

## 14. Safety, Robustness, and Ethics（安全、魯棒與倫理）
- **威脅模型與弱點**  
  包含 jailbreaks、對抗音訊（如 SPIRIT）、非語音擾動等。
- **多層防禦**  
  自資料、訓練、解碼到後處理的防護；guardrails 與 watermark（如 SSR Speech）。
- **來源、冒名與隱私**  
  涵蓋來源追蹤、反冒名、同意與隱私保護。
- **魯棒且不變的表徵**  
  討論增強不變性的離散 tokens 與跨語言/方言/說話人魯棒。
- **公平與評審偏誤**  
  處理族群差異、評審偏誤與資料衛生。
- **報告標準與紅隊測試**  
  建議安全報告、對齊文件與 red-teaming 流程。

---

## 15. Open Toolkits, Frameworks, and Reproducibility（開源工具鏈與可重現性）
- **5C：Code / Config / Compute / Corpora / Comparison**  
  以 5C 視角促進端到端可重現與公正比較。
- **Code：開放生態與技術棧**  
  強調 ESPnet、SpeechLM、LLaSO、OpenS2S、TinyWave、ComSL 等端到端 recipe。
- **Config：可複用積木**  
  倡議標準化設定、參考組件與透明管線。
- **Corpora：整理與授權**  
  關注資料整理、切分、授權與污染檢查。
- **Comparison：評估與測試**  
  推動開放評測套件、指標協議與統計檢驗。
- **Compute：資源與預算表**  
  報告訓練硬體/算力預算與統一資源表藍本。

---

## 16. Open Challenges and Future Directions（開放挑戰與未來方向）
- **統一 vs 多串流 tokens 與解耦**  
  辯論通用 tokens 與專門串流的取捨，以及語義–聲學解耦方法。
- **長情境與對話記憶**  
  指出真實雙工對話中穩定長情境推理與記憶的需求。
- **低資源與多語泛化**  
  規劃跨語言遷移、規模化資料創建與魯棒跨語言表現。
- **與文字知識對齊而不遺忘**  
  提議保留 text LLM 知識同時習得語音能力的訓練方案。
- **速率 vs 容量的理論化**  
  呼籲釐清 token rate 與 LM 容量、跨層抽象對齊、雙通道建模的原理。
- **取捨與限制**  
  總結設計指引與已知限制，指向未來研究。

---

## 17. Conclusion（結語）
- **重點與建議**  
  凝練在 token 介面、建模選擇、對齊、評估與部署上的實用建議。
- **社群資源與標準化**  
  連結開源工具、資料集，並呼籲標準化評測與公開基準。
