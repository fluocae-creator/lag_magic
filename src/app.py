import argparse
import json
from pathlib import Path
from typing import List, Optional

from src.persona import load_personas_from_json
from src.translator import (
    PersonaAwareTranslator,
    format_results_as_text,
    load_dialogue_lines,
)


def load_references(path: Optional[str]) -> List[str]:
    """Load reference sentences or notes for prompting.

    Accepts either JSON array or newline-separated text.
    """

    if not path:
        return []

    reference_path = Path(path)
    text = reference_path.read_text(encoding="utf-8")
    try:
        data = json.loads(text)
        if isinstance(data, list):
            return [str(item) for item in data]
    except json.JSONDecodeError:
        pass
    return [line.strip() for line in text.splitlines() if line.strip()]


def main():
    parser = argparse.ArgumentParser(description="Persona-aware translation/proofreading CLI")
    parser.add_argument("--dialog", required=True, help="對話 JSON 檔案路徑")
    parser.add_argument("--personas", required=True, help="角色設定 JSON 檔案路徑")
    parser.add_argument("--source-lang", default="auto", help="來源語言（例如 zh）")
    parser.add_argument("--target-lang", default="en", help="目標語言（例如 en）")
    parser.add_argument("--tone", default="natural and localized", help="整體指示語氣")
    parser.add_argument("--mode", choices=["translate", "proofread"], default="translate")
    parser.add_argument("--model", default="gpt-4-0613")
    parser.add_argument(
        "--provider",
        choices=["openai", "mock"],
        default="openai",
        help="選擇 LLM provider；使用 mock 可離線快速測試",
    )
    parser.add_argument("--api-key", default=None, help="API key（可選，預設讀取 OPENAI_API_KEY）")
    parser.add_argument("--references", help="參考資料檔案（JSON 陣列或純文字換行）", default=None)
    parser.add_argument(
        "--output-format", choices=["json", "text"], default="json", help="輸出格式：JSON 或純文本"
    )
    args = parser.parse_args()

    personas = load_personas_from_json(args.personas)
    lines = load_dialogue_lines(args.dialog)
    references = load_references(args.references)

    translator = PersonaAwareTranslator(model=args.model, provider=args.provider, api_key=args.api_key)
    results = translator.translate_lines(
        lines,
        personas,
        args.source_lang,
        args.target_lang,
        args.tone,
        references=references,
        mode=args.mode,
    )

    if args.output_format == "json":
        print(json.dumps([result.to_dict() for result in results], ensure_ascii=False, indent=2))
    else:
        print(format_results_as_text(results))


if __name__ == "__main__":
    main()
