import json
import os
import time
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional

from tqdm import tqdm

try:
    import openai
except ImportError:  # pragma: no cover - optional dependency when using mock provider
    openai = None


# Helper: exponential backoff for API calls

def retry_backoff(func, *args, retries: int = 3, backoff: float = 1.0, **kwargs):
    for attempt in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception:  # pragma: no cover - passthrough to caller
            if attempt == retries - 1:
                raise
            time.sleep(backoff * (2**attempt))


@dataclass
class Line:
    speaker: str
    text: str


@dataclass
class TranslationResult:
    speaker: str
    original: str
    translated: str
    notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class PersonaAwareTranslator:
    def __init__(
        self,
        model: str = "gpt-4-0613",
        provider: str = "openai",
        api_key: Optional[str] = None,
        temperature: float = 0.7,
    ):
        self.model = model
        self.provider = provider
        self.temperature = temperature

        if provider == "openai":
            if openai is None:
                raise RuntimeError("OpenAI SDK 未安裝。請安裝 openai 套件。")
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("未設定 OPENAI_API_KEY。")
            openai.api_key = api_key
        elif provider != "mock":
            raise NotImplementedError(f"不支援的 provider: {provider}")

    def build_system_prompt(
        self,
        personas: Dict[str, Any],
        target_lang: str,
        tone: str,
        references: List[str],
        mode: str,
    ) -> str:
        persona_blocks = []
        for name, persona in personas.items():
            description = getattr(persona, "description", None)
            if description is None and isinstance(persona, dict):
                description = persona.get("description", "")

            voice = getattr(persona, "voice", None)
            if voice is None and isinstance(persona, dict):
                voice = persona.get("voice", "")

            emotion = getattr(persona, "emotion", None)
            if emotion is None and isinstance(persona, dict):
                emotion = persona.get("emotion", "")

            samples = getattr(persona, "samples", None)
            if samples is None and isinstance(persona, dict):
                samples = persona.get("samples", [])
            samples_text = "\n".join(f"- {sample}" for sample in samples) if samples else ""
            persona_blocks.append(
                f"角色名稱: {name}\n描述: {description}\n語感: {voice}\n情緒基調: {emotion}\n範例: {samples_text}\n"
            )

        references_text = "\n".join(references) if references else "無"
        if mode == "translate":
            mode_text = "直接翻譯成目標語言，並確保本地化、語氣與情緒一致。"
        else:
            mode_text = "在原語上做校對，提供本地化改寫與更自然的表達建議。"

        system_prompt = f"""你是一個高品質語言翻譯與本地化專家。
目標語言: {target_lang}
任務模式: {mode_text}
整體語氣（通用指示）: {tone}
參考資料（可引用專有名詞或風格例句）: {references_text}

以下是各角色描述，翻譯或改寫時務必保持每個角色的個性與語氣差異，並根據情緒調整措辭與句型：
{''.join(persona_blocks)}

輸出要求:
- 對每一句話，輸出翻譯或校對結果，並附上必要時的簡短說明，解釋如何保留角色個性與語感。
- 保留原有特殊格式（如括號內舞台指示、表情、外語單字）。
- 若原句含模糊、含義不明或文化專有名詞，優先給出本地化翻譯，並在說明中標註替代選項。
"""
        return system_prompt

    def translate_lines(
        self,
        lines: List[Line],
        personas: Dict[str, Any],
        source_lang: str,
        target_lang: str,
        tone: str = "",
        references: Optional[List[str]] = None,
        mode: str = "translate",
    ) -> List[TranslationResult]:
        references = references or []
        system_prompt = self.build_system_prompt(personas, target_lang, tone, references, mode)

        results: List[TranslationResult] = []
        for line in tqdm(lines, desc="Translating lines"):
            user_prompt = f"""處理模式: {mode}
來源語言: {source_lang}
目標語言: {target_lang}
說話者: {line.speaker}
原文: {line.text}

請回傳 JSON，包含: translated(翻譯或改寫結果), notes(必要時的說明，若不需則空字串)"""
            translated, notes = self._call_chat_model(
                system_prompt,
                user_prompt,
                {
                    "speaker": line.speaker,
                    "persona": personas.get(line.speaker),
                    "mode": mode,
                    "target_lang": target_lang,
                    "text": line.text,
                },
            )
            results.append(
                TranslationResult(
                    speaker=line.speaker, original=line.text, translated=translated, notes=notes
                )
            )
        return results

    def _call_chat_model(
        self, system_prompt: str, user_prompt: str, provider_context: Optional[Dict[str, Any]] = None
    ) -> tuple[str, str]:
        if self.provider == "mock":
            return self._mock_response(provider_context or {})
        if self.provider != "openai":
            raise NotImplementedError("目前僅實作 openai 或 mock provider")

        def query():
            return openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=self.temperature,
                max_tokens=800,
            )

        resp = retry_backoff(query, retries=3, backoff=1)
        text = resp.choices[0].message.content.strip()
        try:
            obj = json.loads(text)
            translated = obj.get("translated", "")
            notes = obj.get("notes", "")
        except Exception:
            parts = text.split("\n\n", 1)
            translated = parts[0].strip()
            notes = parts[1].strip() if len(parts) > 1 else ""
        return translated, notes

    def _mock_response(self, context: Dict[str, Any]) -> tuple[str, str]:
        persona = context.get("persona")

        def _field(field: str, default: str = "") -> str:
            if hasattr(persona, field):
                value = getattr(persona, field)
                return value if value is not None else default
            if isinstance(persona, dict):
                return persona.get(field, default)
            return default

        voice = _field("voice", "neutral")
        emotion = _field("emotion", "")
        target_lang = context.get("target_lang", "")
        mode = context.get("mode", "translate").upper()
        text = context.get("text", "")
        speaker = context.get("speaker", "")

        translated = f"[{mode}->{target_lang}] {speaker}: {text}"
        notes = f"mock-response (voice={voice}; emotion={emotion})"
        return translated, notes


def load_dialogue_lines(path: str) -> List[Line]:
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [Line(speaker=item.get("speaker", "Unknown"), text=item.get("text", "")) for item in data]


def format_results_as_text(results: List[TranslationResult]) -> str:
    """Render translation results as human-readable text."""

    rendered = []
    for result in results:
        rendered.append(
            f"[{result.speaker}] {result.translated}\n  原文: {result.original}\n  備註: {result.notes or '（無）'}"
        )
    return "\n\n".join(rendered)
