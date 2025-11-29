# Lag Magic — Translation & Proofreading with Persona-aware Localization

簡介
- 以角色（persona）為單位的翻譯與校對工具，強調本地化與情緒/語感保留。
- 預設使用 OpenAI Chat API，也支援離線 mock provider 方便驗證流程。

主要功能
- 選擇來源/目標語言與任務模式（翻譯 / 校對）。
- 為每位角色設定「個性 / 語感 / 情緒 / 範例句」，大量角色對話也能維持一致性。
- 可加入 tone（整體語氣）與 references（外部參考資料）作為提示。
- 批次處理整個對話腳本，輸出 JSON 或純文本摘要，附帶每句的備註說明。

快速開始
1. 建議建立虛擬環境並安裝套件：
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 設定 OpenAI 金鑰（若使用 OpenAI）：
   ```bash
   export OPENAI_API_KEY="sk-..."
   ```
3. 範例執行：
   ```bash
   # 真實翻譯（需要 API Key）
   python -m src.app --mode translate --source-lang zh --target-lang en \
     --dialog examples/dialogues.json --personas examples/personas.json --tone "localized and natural"

   # 離線 mock（不需要 API Key，可快速驗證流程與輸出格式）
   python -m src.app --provider mock --mode translate --source-lang zh --target-lang en \
     --dialog examples/dialogues.json --personas examples/personas.json --output-format text
   ```

在 GitHub Actions 上執行（Get started with GitHub Actions）
- 已內建 `.github/workflows/ci.yml`，會在 push / PR 時：
  1. 安裝 Python 3.11 與依賴套件
  2. 執行 `python -m compileall src`
  3. 執行 `python run_local_mock.py --dialog examples/dialogues.json --personas examples/personas.json --target-lang en`
- 若需使用真實的 OpenAI provider，可在 Actions secrets 設定 `OPENAI_API_KEY` 並自行於 workflow 追加對應步驟（預設 workflow 只跑 mock，不需要任何金鑰）。
- 可在 GitHub Repository 頁面 → Actions → 選擇「CI」workflow → Run workflow 即可手動觸發或等待 push/PR 自動觸發。

CLI 參數重點
- `--references`: 可提供 JSON 陣列或純文字（逐行）作為外部語料與語感參考。
- `--output-format`: `json`（預設）或 `text`，後者以人類可讀的摘要列出翻譯與備註。

檔案說明
- src/translator.py: 翻譯 / 校對 的核心 pipeline（含 mock provider 與文字輸出工具）。
- src/persona.py: Persona 結構與解析。
- src/app.py: CLI 入口，可切換 provider、模式、輸出格式。
- run_local_mock.py: 直接呼叫 mock provider 的便捷腳本。
- examples/dialogues.json: 範例對話（多角色）。
- examples/personas.json: 角色設定檔。
- requirements.txt: 相依套件。

設計要點與注意
- Prompt 設計將 persona（角色描述）、語氣（tone）、參考資料（references）組合成 system prompt，以確保翻譯能保留角色差異。
- 若要對大量對話保持一致性，建議將每個角色的「核心語句集」儲存在外部資料庫或向量資料庫，並在翻譯時檢索範例。
- 本範例以最簡單方式示範 pipeline；上線時請加強錯誤重試、超時與速率限制處理。

下一步
- 若你同意，我可以：
  - 幫你把程式推上 repo（需要你授權我推送或我幫你產生 PR 的內容）
  - 加入 Web UI（Flask / FastAPI + React）
  - 將 persona 儲存整合至向量 DB（Pinecone / Milvus / FAISS）以提升長篇一致性