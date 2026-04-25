"""
離線 mock 測試腳本：模擬翻譯流程，不需要 OpenAI 金鑰。
用法:
  python run_local_mock.py --dialog examples/dialogues.json --personas examples/personas.json --target-lang en
"""
import argparse
import json
import sys
from pathlib import Path

# 確保能 import src 套件（假定從 repo 根目錄執行）
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from src.persona import load_personas_from_json
from src.translator import PersonaAwareTranslator, load_dialogue_lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dialog", required=True)
    parser.add_argument("--personas", required=True)
    parser.add_argument("--target-lang", default="en")
    parser.add_argument("--tone", default="mock friendly")
    args = parser.parse_args()

    personas = load_personas_from_json(args.personas)
    lines = load_dialogue_lines(args.dialog)

    translator = PersonaAwareTranslator(provider="mock")
    results = translator.translate_lines(
        lines,
        personas,
        source_lang="auto",
        target_lang=args.target_lang,
        tone=args.tone,
        references=[],
        mode="translate",
    )
    out = [result.to_dict() for result in results]
    print(json.dumps(out, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
