import re
import subprocess

from .base import BaseParser


class DOCParser(BaseParser):
    """Parser for legacy binary .doc files."""

    _MIN_ASCII_WORD_LEN = 3

    def parse(self, file_path):
        text = self._extract_with_antiword(file_path)
        if not text:
            with open(file_path, "rb") as f:
                raw = f.read()
            text = self._extract_text_heuristic(raw)

        return self.normalize(text, metadata={"format": "doc"})

    def _extract_with_antiword(self, file_path):
        """Try to parse .doc using antiword if available in runtime."""
        try:
            result = subprocess.run(
                ["antiword", file_path],
                check=False,
                capture_output=True,
            )
        except FileNotFoundError:
            return ""

        if result.returncode != 0:
            return ""

        text = result.stdout.decode("utf-8", errors="ignore").strip()
        if not text:
            return ""
        return self._cleanup_text(text)

    def _extract_text_heuristic(self, raw):
        """Best-effort fallback when antiword is unavailable."""
        utf16_text = raw.decode("utf-16le", errors="ignore")
        cp1251_text = raw.decode("cp1251", errors="ignore")
        latin1_text = raw.decode("latin1", errors="ignore")

        candidates = [utf16_text, cp1251_text, latin1_text]
        cleaned_candidates = [self._cleanup_text(candidate) for candidate in candidates]
        cleaned_candidates = [c for c in cleaned_candidates if c]

        if not cleaned_candidates:
            return ""

        # Prefer text with more word-like tokens and fewer control artifacts.
        def score(text):
            words = re.findall(r"[A-Za-zА-Яа-яЁё0-9]{2,}", text)
            return len(words)

        return max(cleaned_candidates, key=score)

    def _cleanup_text(self, text):
        text = text.replace("\x00", "")
        text = re.sub(r"[\x01-\x08\x0b\x0c\x0e-\x1f]", " ", text)
        text = re.sub(r"[ \t]+", " ", text)
        lines = [line.strip() for line in text.splitlines()]

        filtered_lines = []
        for line in lines:
            if not line:
                continue

            word_like = re.findall(r"[A-Za-zА-Яа-яЁё0-9]{%d,}" % self._MIN_ASCII_WORD_LEN, line)
            if not word_like:
                continue
            filtered_lines.append(line)

        return "\n".join(filtered_lines).strip()
