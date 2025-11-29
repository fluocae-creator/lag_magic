import os
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from tqdm import tqdm

# 選擇 LLM 後端（此範例使用 OpenAI ChatCompletion）
try:
    import openai
except ImportError:
    openai = None

# Helper: exponential backoff for API calls
def retry_backoff(func, *args, retries=3, backoff=1, **kwargs):
    for i in range(retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if i == retries - 1:
                raise
            time.sleep(backoff * (2 ** i))

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

class PersonaAwareTranslator:
    def __init__(self, model: str = "gpt-4-0613", provider: str = "openai", api_key: Optional[str] = None):
        self.model = model
        self.provider = provider
        if provider == "openai":
            if openai is None:
                raise RuntimeError("OpenAI SDK 未安裝。請安裝 openai 套件。")
            api_key = api_key or os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise RuntimeError("未設定 OPENAI_API_KEY。")
            openai.api_key = api_key

    def build_system_prompt(self, personas: Dict[str, Any], target_lang: str, tone: str, references: List[str], mode: str):
        """
        mode: "translate" 或 "proofread"
        personas: dict of Persona objects or dicts keyed by speaker name
        """
        persona_blocks = []
        for name, p in personas.items():
            # p may be Persona instance or dict
            desc = p.description if hasattr(p, "description") else p.get("description", "")
            voice = p.voice if hasattr(p, "voice") else p.get("voice", "")
            emotion = p.emotion if hasattr(p, "emotion") else p.get("emotion", "")
            samples = getattr(p, "samples", None) or p.get("samples", [])
            sample_text = "\n".join(f"- {s}" for s in samples) if samples else ""
            block = f"角色名称: {name}\n描述: {desc}\n語感: {voice}\n情緒基調: {emotion}\n範例: {sample_text}\n"
            persona_blocks.append(block)

        references_text = "\n".join(references) if references else "無"
        mode_text = "直接翻譯成目標語言，並確保本地化、語氣與情緒一致。" if mode == "translate" else "在原語上做校對並提供本地化改寫建議（包含更自然的表達）"

        system_prompt = f"""你是一個高品質語言翻譯與本地化專家。
目標語言: {target_lang}
任務模式: {mode_text}
整體語氣（通用指示）: {tone}
參考資料: {references_text}

以下是各角色描述，翻譯或改寫時務必保持每個角色的個性與語氣差異，並根據情緒調整措辭與句型：
{''.join(persona_blocks)}

輸出要求:
- 對每一句話，輸出翻譯結果並附上簡短說明（若有必要），說明為何選該措辭以保留角色個性。
- 保留原有特殊格式（如括號內舞台指示、表情、外語單字）。
- 若原句含模糊、含義不明或文化專有名詞，優先給出一種本地化翻譯，並在說明中標註替代選項。
"""
        return system_prompt

    def translate_lines(self, lines: List[Line], personas: Dict[str, Any], source_lang: str, target_lang: str,
                        tone: str = "", references: List[str] = None, mode: str = "translate") -> List[TranslationResult]:
        references = references or []
        system_prompt = self.build_system_prompt(personas, target_lang, tone, references, mode)

        # build messages and call model per chunk (逐句或每段)
        results = []
        for ln in tqdm(lines, desc="Translating lines"):
            user_prompt = f"""請將下列文字處理為: {mode}
來源語言: {source_lang}
目標語言: {target_lang}
說話者: {ln.speaker}
原文: {ln.text}

請回傳 JSON 包含欄位: translated(翻譯文字), notes(必要時的說明，若不需則空字串)"""
            # call model
            translated, notes = self._call_chat_model(system_prompt, user_prompt)
            results.append(TranslationResult(speaker=ln.speaker, original=ln.text, translated=translated, notes=notes))
        return results

    def _call_chat_model(self, system_prompt: str, user_prompt: str):
        """
        內部呼叫 LLM 的簡化實作。返回 (translated_text, notes)
        """
        if self.provider != "openai":
            raise NotImplementedError("目前僅實作 openai provider 的呼叫介面")

        def query():
            resp = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=800,
            )
            return resp

        resp = retry_backoff(query, retries=3, backoff=1)
        # 解析回傳：嘗試解析成 JSON（如 LLM 按要求回傳 JSON）
        text = resp.choices[0].message.content.strip()
        # 嘗試安全解析 JSON
        try:
            obj = json.loads(text)
            translated = obj.get("translated", "")
            notes = obj.get("notes", "")
        except Exception:
            # 若非 JSON，則做簡單分割：首段為翻譯，接續為說明
            parts = text.split("\n\n", 1)
            translated = parts[0].strip()
            notes = parts[1].strip() if len(parts) > 1 else ""
        return translated, notes

# 小工具：解析對話 JSON 成 Line list
def load_dialogue_lines(path: str) -> List[Line]:
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    lines = []
    for item in data:
        lines.append(Line(speaker=item.get("speaker", "Unknown"), text=item.get("text", "")))
    return lines