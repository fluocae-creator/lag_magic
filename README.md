# Lag Magic — Translation & Proofreading with Persona-aware Localization

簡介
- 一個以角色（persona）為單位的翻譯與校對工具雛形，能針對大量角色對話做本地化、語氣與情緒保留。
- 預設使用 OpenAI Chat API，但設計為可替換後端。

主要功能
- 選擇來源/目標語言
- 為每位角色設定「個性 / 語感 / 情緒 / 範例句」
- 支援「翻譯」與「校對（在原語上給出本地化建議）」兩種模式
- 批次處理整個對話腳本，保留角色差異，輸出可選 JSON 或純文本

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
   python src/app.py --mode translate --source-lang zh --target-lang en --dialog examples/dialogues.json
   ```

檔案說明
- src/translator.py: 翻譯 / 校對 的核心 pipeline
- src/persona.py: Persona 結構與解析
- src/app.py: CLI 範例
- examples/dialogues.json: 範例對話（多角色）
- requirements.txt: 相依套件

設計要點與注意
- Prompt 設計將 persona（角色描述）、語氣（tone）、參考資料（references）組合成 system prompt，以確保翻譯能保留角色差異。
- 若要對大量對話保持一致性，建議將每個角色的「核心語句集」儲存在外部資料庫或向量資料庫，並在翻譯時檢索範例。
- 本範例以最簡單方式示範 pipeline；上線時請加強錯誤重試、超時與速率限制處理。

下一步
- 若你同意，我可以：
  - 幫你把程式推上 repo（需要你授權我推送或我幫你產生 PR 的內容）
  - 加入 Web UI（Flask / FastAPI + React）
  - 將 persona 儲存整合至向量 DB（Pinecone / Milvus / FAISS）以提升長篇一致性