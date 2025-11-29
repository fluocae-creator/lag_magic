import argparse
import json
from src.persona import load_personas_from_json
from src.translator import PersonaAwareTranslator, load_dialogue_lines

def main():
    parser = argparse.ArgumentParser(description="Persona-aware translation/proofreading CLI")
    parser.add_argument("--dialog", required=True, help="對話 JSON 檔案路徑")
    parser.add_argument("--personas", required=True, help="角色設定 JSON 檔案路徑")
    parser.add_argument("--source-lang", default="auto", help="來源語言（例如 zh）")
    parser.add_argument("--target-lang", default="en", help="目標語言（例如 en）")
    parser.add_argument("--tone", default="natural and localized", help="整體指示語氣")
    parser.add_argument("--mode", choices=["translate", "proofread"], default="translate")
    parser.add_argument("--model", default="gpt-4-0613")
    args = parser.parse_args()

    personas = load_personas_from_json(args.personas)
    lines = load_dialogue_lines(args.dialog)

    translator = PersonaAwareTranslator(model=args.model)
    results = translator.translate_lines(lines, personas, args.source_lang, args.target_lang, args.tone, references=[], mode=args.mode)

    output = [r.__dict__ for r in results]
    print(json.dumps(output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()