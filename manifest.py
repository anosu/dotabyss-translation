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
                yield f"{key}{PATH_SEPARATOR}{sub_path}", sub_value
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


def binary_file_hash(path: Path) -> str:
    return hashlib.md5(path.read_bytes()).hexdigest()


class Manifest:
    STATIC_TYPE = "static"
    REPLACEMENTS_TYPE = "replacements"
    REPLACEMENT_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
    EXCLUDED_DIRS = {"manifest", "novels", STATIC_TYPE, REPLACEMENTS_TYPE}

    def __init__(self, translation_dir: str | Path, language: str = "zh_Hans"):
        self.base_dir = Path(translation_dir)
        self.language = language

    def _file(self, category: str) -> Path:
        return self.base_dir / category / f"{self.language}.json"

    def _static_file(self) -> Path:
        return self._file(self.STATIC_TYPE)

    def _replacement_hashes(self) -> dict[str, str]:
        root = self.base_dir / self.REPLACEMENTS_TYPE
        if not root.exists():
            return {}

        return {
            path.relative_to(root).as_posix(): binary_file_hash(path)
            for path in sorted(root.rglob("*"))
            if path.is_file()
            and (
                path == root / "manifest.json"
                or path.suffix.lower() in self.REPLACEMENT_IMAGE_EXTENSIONS
            )
        }

    def _category_hashes(self) -> dict[str, str]:
        return {
            path.parent.name: file_hash(path)
            for path in sorted(self.base_dir.glob(f"*/{self.language}.json"))
            if path.parent.name not in self.EXCLUDED_DIRS
        }

    def build(self):
        static_file = self._static_file()
        manifest: dict[str, Any] = self._category_hashes()

        if static_file.exists():
            manifest[self.STATIC_TYPE] = file_hash(static_file)

        replacements = self._replacement_hashes()
        if replacements:
            manifest[self.REPLACEMENTS_TYPE] = replacements

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
    for lang in ["zh_Hans"]:
        Manifest("translations", lang).update()


if __name__ == "__main__":
    main()
