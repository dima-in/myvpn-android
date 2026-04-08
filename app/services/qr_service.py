from pathlib import Path
import qrcode


def build_qr(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img = qrcode.make(value)
    img.save(path)