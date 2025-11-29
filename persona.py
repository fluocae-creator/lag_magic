from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json

@dataclass
class Persona:
    name: str
    description: str  # 主描述：個性、身份、文化背景
    voice: str = ""   # 語感、語氣描述（例如：謹慎、俏皮、粗獷）
    emotion: str = "" # 常見情緒基調（例如：冷靜、易怒）
    samples: List[str] = None  # 範例句

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

def load_personas_from_json(path: str) -> Dict[str, Persona]:
    with open(path, 'r', encoding='utf-8') as f:
        raw = json.load(f)
    personas = {}
    for p in raw:
        personas[p["name"]] = Persona(
            name=p["name"],
            description=p.get("description", ""),
            voice=p.get("voice", ""),
            emotion=p.get("emotion", ""),
            samples=p.get("samples", [])
        )
    return personas

def persona_to_prompt_block(persona: Persona) -> str:
    """
    將 Persona 轉成可插入 system prompt 的文本塊。
    """
    samples_text = ""
    if persona.samples:
        samples_text = "\nSample lines:\n" + "\n".join(f"- {s}" for s in persona.samples)
    block = f"""角色: {persona.name}
描述: {persona.description}
語感/語氣: {persona.voice}
基調情緒: {persona.emotion}
{samples_text}
"""
    return block