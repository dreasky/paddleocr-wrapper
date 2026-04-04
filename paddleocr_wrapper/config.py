"""Configuration loader for PaddleOCR wrapper."""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv


class ConfigLoader:

    def __init__(self, config_file: Path | None = None):
        load_dotenv()

        self.api_url = os.environ.get("PADDLEOCR_OCR_API_URL", "")
        self.access_token = os.environ.get("PADDLEOCR_ACCESS_TOKEN", "")
        if not self.api_url or not self.access_token:
            missing = [v for v in ("PADDLEOCR_OCR_API_URL", "PADDLEOCR_ACCESS_TOKEN")
                       if not os.environ.get(v)]
            for v in missing:
                print(f"Error: {v} not configured in environment", file=sys.stderr)
            sys.exit(1)

        self.payload = self._load_payload(
            config_file,
            Path(__file__).parent / "paddleocr_config.json",
        )

    @staticmethod
    def _load_payload(config_file: Path | None, builtin: Path) -> dict:
        # 优先级：传入参数 > cwd/paddleocr_config.json > 包内置默认配置
        cwd_file = config_file or Path.cwd() / "paddleocr_config.json"
        path = cwd_file if cwd_file.exists() else builtin
        if not path.exists():
            print(f"Error: paddleocr_config.json not found", file=sys.stderr)
            sys.exit(1)
        data = json.loads(path.read_text(encoding="utf-8"))
        payload = {}
        for k, v in data.items():
            if isinstance(v, dict) and "value" in v:
                if v["value"] is not None:
                    payload[k] = v["value"]
            else:
                payload[k] = v
        return payload
