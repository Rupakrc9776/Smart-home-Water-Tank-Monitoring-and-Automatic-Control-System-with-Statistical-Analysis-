"""Validate repository structure and local Markdown references for CI."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_PATHS = (
    "README.md",
    "LICENSE",
    "CONTRIBUTING.md",
    "SECURITY.md",
    "requirements.txt",
    "Arduino_Code",
    "Circuit_Diagrams",
    "Documentation",
    "assets",
    "dashboard.py",
    "dashboard_assets.py",
    "water_logger.py",
)
MARKDOWN_LINK = re.compile(r"(?<!!)\[[^\]]+\]\(([^)\s]+)(?:\s+['\"][^)]*['\"])?\)")
HTML_IMAGE = re.compile(r"<img\b[^>]*\bsrc=[\"']([^\"']+)[\"'][^>]*>", re.IGNORECASE)
IMAGE_SUFFIXES = {".gif", ".jpeg", ".jpg", ".png", ".svg", ".webp"}


def local_target(source: Path, target: str) -> Path | None:
    parsed = urlsplit(unquote(target))
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None
    return (source.parent / parsed.path).resolve()


def main() -> int:
    errors: list[str] = []
    for relative in REQUIRED_PATHS:
        if not (ROOT / relative).exists():
            errors.append(f"missing required path: {relative}")

    markdown_files = sorted(ROOT.rglob("*.md"))
    markdown_files = [path for path in markdown_files if ".git" not in path.parts and ".venv" not in path.parts]
    for source in markdown_files:
        text = source.read_text(encoding="utf-8")
        if text.count("```") % 2:
            errors.append(f"unclosed fenced code block: {source.relative_to(ROOT)}")
        for target in [*MARKDOWN_LINK.findall(text), *HTML_IMAGE.findall(text)]:
            resolved = local_target(source, target)
            if resolved is None:
                continue
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(f"reference escapes repository: {source.relative_to(ROOT)} -> {target}")
                continue
            if not resolved.exists():
                errors.append(f"broken reference: {source.relative_to(ROOT)} -> {target}")
            elif target.lower().split("?", 1)[0].endswith(tuple(IMAGE_SUFFIXES)) and not resolved.is_file():
                errors.append(f"image reference is not a file: {source.relative_to(ROOT)} -> {target}")

    if errors:
        print("Documentation validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print(f"Documentation validation passed: {len(markdown_files)} Markdown files checked.")
    return 0


if __name__ == "__main__":
    sys.exit(main())