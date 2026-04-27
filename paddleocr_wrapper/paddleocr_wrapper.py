"""PaddleOCR Wrapper — convert PDF/image to Markdown via PaddleOCR API."""

import base64
import re
import sys
from pathlib import Path
from typing import Any
from markdownify import markdownify

import requests

from .config import ConfigLoader


_SUPPORTED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".tiff", ".webp"}


def _get_file_type(file_path: Path) -> int:
    ext = file_path.suffix.lower()
    if ext == ".pdf":
        return 0  # FILE_TYPE_PDF
    return 1 if ext in _SUPPORTED_IMAGE_EXTS else 0  # FILE_TYPE_IMAGE


class PaddleocrWrapper:
    """Convert PDF/image to Markdown using PaddleOCR API."""

    DEFAULT_TIMEOUT = 300
    IMAGE_DOWNLOAD_TIMEOUT = 30

    def __init__(self, config_file: Path | None = None):
        config = ConfigLoader(config_file)
        self._api_url = config.api_url
        self._token = config.access_token
        self._payload_extra = config.payload
        self._session = requests.Session()

    def _send_request(self, file_data: str, file_type: int) -> dict[str, Any]:
        headers = {
            "Authorization": f"token {self._token}",
            "Content-Type": "application/json",
        }
        payload = {"file": file_data, "fileType": file_type, **self._payload_extra}
        try:
            resp = self._session.post(
                self._api_url,
                json=payload,
                headers=headers,
                timeout=self.DEFAULT_TIMEOUT,
            )
        except requests.exceptions.Timeout:
            raise RuntimeError(f"Request timed out after {self.DEFAULT_TIMEOUT}s")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Request failed: {e}")

        if resp.status_code != 200:
            raise RuntimeError(f"API returned {resp.status_code}: {resp.text}")

        try:
            return resp.json()["result"]
        except (KeyError, ValueError) as e:
            raise RuntimeError(f"Failed to parse API response: {e}")

    def _download_images(
        self, image_downloads: list[tuple[str, str]], output_dir: Path
    ) -> None:
        for img_path, img_url in image_downloads:
            dest = output_dir / img_path
            try:
                r = self._session.get(img_url, timeout=self.IMAGE_DOWNLOAD_TIMEOUT)
                if r.status_code == 200:
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(r.content)
                else:
                    print(
                        f"图片下载失败: {img_path} (status {r.status_code})",
                        file=sys.stderr,
                    )
            except Exception as e:
                print(f"图片下载失败: {img_path} - {e}", file=sys.stderr)

    def convert(self, input_file: Path, output_file: Path) -> None:
        """Convert a PDF or image file to Markdown and save to output_dir/<stem>.md."""
        if not input_file.exists():
            raise FileNotFoundError(f"Input file not found: {input_file}")

        file_type = _get_file_type(input_file)
        file_data = base64.b64encode(input_file.read_bytes()).decode("ascii")

        result = self._send_request(file_data, file_type)

        markdown_parts = []
        all_image_map: dict[str, str] = {}
        for res in result.get("layoutParsingResults", []):
            md = res.get("markdown", {})
            text = md.get("text", "")
            if text:
                markdown_parts.append(text)
            all_image_map.update(md.get("images", {}))

        result_text = "\n\n---\n\n".join(markdown_parts)
        result_md = markdownify(result_text)

        # Only download images actually referenced in the markdown text.
        # The API returns all images (including filtered regions like headers/footers),
        # but the markdown only links to a subset of them.
        _IMG_RE = re.compile(r"!\[.*?\]\(([^)]+)\)")
        referenced = _IMG_RE.findall(result_text) + _IMG_RE.findall(result_md)
        referenced_set = set(referenced)
        image_downloads = [
            (img_path, img_url)
            for img_path, img_url in all_image_map.items()
            if img_path in referenced_set
        ]

        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(result_md, encoding="utf-8")

        if image_downloads:
            self._download_images(image_downloads, output_file.parent)
