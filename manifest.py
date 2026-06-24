import hashlib
import json
from pathlib import Path
from typing import Any, Iterable

SEPARATOR = b"\x00"
PATH_SEPARATOR = "\x01"


def traverse(obj: dict[str, Any]) -> Iterable[tuple[str, str]]:
    for key, value in sorted(obj.items()):
        if isinstance(value, dict):
            for sub_path, sub_value in traverse(value):
                yield f"{key}\x01{sub_path}", sub_value
        else:
            yield key, value


def obj_hash(obj: dict[str, Any]) -> str:
    md5 = hashlib.md5()

    for key, value in traverse(obj):
        md5.update(key.encode("utf-8"))
        md5.update(SEPARATOR)
        md5.update(value.encode("utf-8"))
        md5.update(SEPARATOR)

    return md5.hexdigest()


def file_hash(path: Path) -> str:
    return obj_hash(json.loads(path.read_text(encoding="utf-8")))


class Manifest:
    CONTENT_TYPES = ("names","m_ability_details","m_chapter_quests","m_character_action_skills","m_character_profiles","m_dictionary_non_player_characters","m_enchantment_details","m_gacha_group_movies","m_missions","m_nether_code_category_skills","m_nether_codes","m_novel_character_skins","m_novel_characters","m_novel_events","m_novel_homes","m_novel_mains","m_novel_others","m_novel_prologues","m_part_voices","m_plans","m_preregist_taverns","m_tavern_character_cards")

    def __init__(self, translation_dir: str | Path, language: str = "zh_Hans"):
        self.base_dir = Path(translation_dir)
        self.language = language

    def _file(self, category: str) -> Path:
        return self.base_dir / category / f"{self.language}.json"

    def build(self):
        manifest: dict[str, Any] = {
            t: file_hash(f) for t in self.CONTENT_TYPES if (f := self._file(t)).exists()
        }

        manifest["novels"] = {
            f.parent.name: file_hash(f)
            for f in self.base_dir.glob(f"novels/*/{self.language}.json")
        }

        manifest["hash"] = obj_hash(manifest)
        return manifest

    def update(self):
        manifest = self.build()

        output = self.base_dir / "manifest" / f"{self.language}.json"
        output.parent.mkdir(parents=True, exist_ok=True)

        output.write_text(
            json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=4),
            encoding="utf-8",
        )


def main():
    for lang in ["zh_Hans", "zh_Hant"]:
        Manifest("translations", lang).update()


if __name__ == "__main__":
    main()
