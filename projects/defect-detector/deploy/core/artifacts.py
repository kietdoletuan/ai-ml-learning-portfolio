from __future__ import annotations

import hashlib
from pathlib import Path

from .contract import PartSpec

DEV_ROOT = Path(__file__).resolve().parents[2]
_CHUNK = 1 << 20


class ChecksumMismatch(RuntimeError):
    pass


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(_CHUNK):
            h.update(chunk)
    return h.hexdigest()


def verify_sha256(path: Path, expected: str) -> None:
    actual = sha256_file(path)
    if actual != expected:
        raise ChecksumMismatch(f"{Path(path).name}: expected sha256 {expected}, got {actual}")


def resolve_checkpoint(spec: PartSpec, *, prefer_local: bool = False) -> Path:
    use_local = spec.local_checkpoint is not None and (prefer_local or not spec.has_remote_source)
    if use_local:
        path = DEV_ROOT / spec.local_checkpoint
        if not path.is_file():
            raise FileNotFoundError(f"{spec.part_id}: local checkpoint not found at {path}")
    else:
        from huggingface_hub import hf_hub_download

        path = Path(hf_hub_download(
            repo_id=spec.model_repo_id,
            filename=spec.model_filename,
            revision=spec.model_revision,
        ))
    # the checkpoint is loaded with weights_only=False, so the bytes must match before anything reads them
    verify_sha256(path, spec.model_sha256)
    return path
