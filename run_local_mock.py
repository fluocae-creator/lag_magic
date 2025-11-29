"""
離線 mock 測試腳本：模擬翻譯流程，不需要 OpenAI 金鑰。
用法:
  python tests/run_local_mock.py --dialog examples/dialogues.json --personas examples/personas.json --target-lang en
"""
import argparse
import json
import sys
from pathlib import Path

# 確保能 import src 套件（假定從 repo 根目錄執行）
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.persona import load_personas_from_json
from src.translator import load_dialogue_lines, Line, TranslationResult

def mock_translate_lines(lines, personas, target_lang):
    results = []
    for ln in lines:
        # 簡單模擬：在翻譯前綴加上標示，並以 persona voice 產生 notes
        persona = personas.get(ln.speaker, None)
        persona_hint = persona['voice'] if persona else "neutral"
        translated = f"[MOCK:{target_lang}] {ln.text} (speaker:{ln.speaker})"
        notes = f"mock-note: preserve voice={persona_hint}"
        results.append(TranslationResult(speaker=ln.speaker, original=ln.text, translated=translated, notes=notes))
    return results

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialog", required=True)
    parser.add_argument("--personas", required=True)
    parser.add_argument("--target-lang", default="en")
    args = parser.parse_args()

    personas = load_personas_from_json(args.personas)
    # load_dialogue_lines 會回傳 src.translator.Line list
    lines = load_dialogue_lines(args.dialog)

    results = mock_translate_lines(lines, {k:v.to_dict() for k,v in personas.items()}, args.target_lang)
    out = [r.__dict__ for r in results]
    print(json.dumps(out, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()