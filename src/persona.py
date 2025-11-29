from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import json


@dataclass
class Persona:
    """Represents a speaker's persona used to guide localization."""

    name: str
    description: str  # 個性、身份、文化背景
    voice: str = ""  # 語感、語氣描述（例如：謹慎、俏皮、粗獷）
    emotion: str = ""  # 常見情緒基調（例如：冷靜、易怒）
    samples: List[str] | None = None  # 範例句

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def load_personas_from_json(path: str) -> Dict[str, Persona]:
    """Load persona definitions from a JSON file."""

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    personas: Dict[str, Persona] = {}
    for persona in raw:
        personas[persona["name"]] = Persona(
            name=persona["name"],
            description=persona.get("description", ""),
            voice=persona.get("voice", ""),
            emotion=persona.get("emotion", ""),
            samples=persona.get("samples", []),
        )
    return personas


def persona_to_prompt_block(persona: Persona) -> str:
    """Convert a persona into a prompt-friendly text block."""

    samples_text = ""
    if persona.samples:
        samples_text = "\n範例句:\n" + "\n".join(f"- {sample}" for sample in persona.samples)

    block = f"""角色: {persona.name}
描述: {persona.description}
語感/語氣: {persona.voice}
基調情緒: {persona.emotion}
{samples_text}
"""
    return block
