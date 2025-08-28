# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later


from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional
import contextlib
import hashlib
import json
import os
import shutil
import tempfile
import threading
import urllib.request
import urllib.error

import marisa_trie
import platformdirs
import zstandard as zstd

from textwizard.wizard_analyze_text.wizzard_correctness._utils import REMOTE_BASE, LANG_INFO
from textwizard.utils.errors.errors import (
    DictionaryUnsupportedError,
    DictionaryUnavailableError,
    DictionaryFileNotFoundError,
)

__all__ = ["load_trie", "load_trie_fast", "get_data_dir"]

_VERBOSE = os.getenv("TEXTWIZARD_VERBOSE", "").lower() in {"1", "true", "yes", "on"}

def _log(msg: str) -> None:
    if _VERBOSE:
        print(f"[textwizard] {msg}")

MAGIC_ZSTD = b"\x28\xB5\x2F\xFD"

def _is_zstd_file(p: Path) -> bool:
    try:
        with open(p, "rb") as f:
            return f.read(4) == MAGIC_ZSTD
    except OSError:
        return False

def _default_data_dir() -> Path:
    return Path(platformdirs.user_data_dir("textwizard"))

def get_data_dir(path_dict: Optional[Path] = None) -> Path:
    return _resolve_dir(path_dict)

def _resolve_dir(path_dict: Optional[Path]) -> Path:
    if path_dict:
        return Path(path_dict).expanduser().resolve()
    for var in ("TEXTWIZARD_DATA_DIR", "TEXTWIZARD_DICT_DIR", "TEXTWIZARD_HOME"):
        if val := os.getenv(var):
            return Path(val).expanduser().resolve()
    return _default_data_dir()

def _sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def _head_content_length(url: str) -> Optional[int]:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "textwizard/1.0"})
    with contextlib.closing(urllib.request.urlopen(req, timeout=20)) as r:  # nosec B310
        cl = r.headers.get("Content-Length")
        return int(cl) if cl and cl.isdigit() else None

def _prompt_download(lang_file: str, size_mb: float) -> bool:
    try:
        ans = input(f"[textwizard] Download {lang_file} (~{size_mb:.1f} MB)? [y/N] ")
    except (EOFError, KeyboardInterrupt):
        return False
    return ans.strip().lower() in {"y", "yes"}

_CHECKSUMS: dict[str, str]
try:
    with open(Path(__file__).with_suffix(".sha256.json"), "rt", encoding="utf8") as fh:
        _CHECKSUMS = json.load(fh)
except FileNotFoundError:
    _CHECKSUMS = {}

_TRIE_CACHE: dict[str, marisa_trie.Trie] = {}
_CACHE_LOCK = threading.Lock()

@contextlib.contextmanager
def _file_lock(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(lock_path, os.O_CREAT | os.O_RDWR)
    try:
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(fd, msvcrt.LK_LOCK, 1)
        else:
            import fcntl
            fcntl.flock(fd, fcntl.LOCK_EX)
        yield
    finally:
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
            else:
                import fcntl
                fcntl.flock(fd, fcntl.LOCK_UN)
        finally:
            os.close(fd)

def _zstd_decompress_bytes(src_bytes: bytes) -> bytes:
    try:
        return zstd.ZstdDecompressor().decompress(src_bytes)
    except zstd.ZstdError as e:
        raise RuntimeError("Zstd: invalid or corrupted input.") from e

def _zstd_decompress_to_file(src_zst: Path, dst_marisa: Path) -> None:
    d = zstd.ZstdDecompressor()
    with open(src_zst, "rb") as fin, open(dst_marisa, "wb") as fout:
        d.copy_stream(fin, fout)

def _resolve_lang_key(lang: str) -> tuple[str, str]:
    real = lang.casefold()
    if real in LANG_INFO:
        info = LANG_INFO[real]
        return real, info["dict_file"]
    base = real.split("_", 1)[0]
    if base in LANG_INFO:
        info = LANG_INFO[base]
        return base, info["dict_file"]
    raise DictionaryUnsupportedError(f"Unsupported language for spell-check: {lang!r}")

@lru_cache(maxsize=None)
def load_trie_fast(
    basename: str,
    src_dir: Path | None = None,
    use_mmap: bool = True,
) -> marisa_trie.Trie:
    return load_trie(
        basename,
        path_dict=src_dir,
        auto_download=False,
        ask_download=False,
        use_mmap=use_mmap,
    )

def load_trie(
    lang: str,
    *,
    path_dict: Optional[Path] = None,
    auto_download: bool = True,
    ask_download: bool = False,   
    use_mmap: bool = False,
) -> marisa_trie.Trie:
    # Risolvi chiave e filename reali
    lang_key, dict_file = _resolve_lang_key(lang)
    base_name = dict_file.replace(".marisa.zst", "")  # es. 'it' o 'gu_IN'

    with _CACHE_LOCK:
        if lang_key in _TRIE_CACHE:
            return _TRIE_CACHE[lang_key]

    cache_dir = _resolve_dir(path_dict)
    cache_dir.mkdir(parents=True, exist_ok=True)
    local_zst = cache_dir / dict_file
    raw_path  = cache_dir / f"{base_name}.marisa"
    lock_path = cache_dir / f".{base_name}.lock"

    _log(f"data dir: {cache_dir}")

    if raw_path.exists() and raw_path.stat().st_size > 0:
        trie = marisa_trie.Trie()
        if use_mmap:
            trie.mmap(str(raw_path))
            _log(f"mmap load: {raw_path.name}")
        else:
            trie.frombytes(raw_path.read_bytes())
            _log(f"in-memory load: {raw_path.name}")
        with _CACHE_LOCK:
            _TRIE_CACHE[lang_key] = trie
        return trie

    if not local_zst.exists():
        if not auto_download:
            raise DictionaryFileNotFoundError(str(local_zst))
        url = f"{REMOTE_BASE.rstrip('/')}/{dict_file}"
        size_b = None
        with contextlib.suppress(Exception):
            size_b = _head_content_length(url)
        human_mb = (size_b or 0) / (1024 * 1024)
        print(f"[textwizard] downloading {url} -> {local_zst} (~{human_mb:.1f} MB)")
        if ask_download and not _prompt_download(dict_file, human_mb):
            raise DictionaryFileNotFoundError(str(local_zst))
        with _file_lock(lock_path):
            if not local_zst.exists():
                _download_with_retries(url, local_zst)

    if not _is_zstd_file(local_zst):
        _log(f"{local_zst.name} invalid .zst; deleting")
        local_zst.unlink(missing_ok=True)
        # Non ritentiamo: segnaliamo indisponibilità dell'asset
        raise DictionaryUnavailableError(str(local_zst))

    expected_hash = _CHECKSUMS.get(dict_file)
    if expected_hash and _sha256(local_zst) != expected_hash:
        _log(f"checksum mismatch for {local_zst.name}; deleting")
        local_zst.unlink(missing_ok=True)
        raise DictionaryUnavailableError(f"Checksum mismatch for {dict_file}")

    if use_mmap:
        if not raw_path.exists() or raw_path.stat().st_size == 0:
            with _file_lock(lock_path):
                if not raw_path.exists() or raw_path.stat().st_size == 0:
                    _log(f"decompress -> {raw_path.name} (for mmap)")
                    _zstd_decompress_to_file(local_zst, raw_path)
        trie = marisa_trie.Trie()
        trie.mmap(str(raw_path))
        _log(f"mmap load: {raw_path.name}")
    else:
        _log(f"decompress {local_zst.name} into memory")
        raw = _zstd_decompress_bytes(local_zst.read_bytes())
        trie = marisa_trie.Trie()
        trie.frombytes(raw)
        _log("in-memory load complete")

    with _CACHE_LOCK:
        _TRIE_CACHE[lang_key] = trie
    return trie

def _download_with_retries(url: str, dst: Path, retries: int = 3) -> None:
    import sys, time
    last_exc: Exception | None = None
    BAR = 28
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "textwizard/1.0"})
            with contextlib.closing(urllib.request.urlopen(req, timeout=60)) as r:  # nosec B310
                total = r.headers.get("Content-Length")
                total = int(total) if total and total.isdigit() else None
                with tempfile.NamedTemporaryFile(delete=False) as tmp:
                    bytes_read = 0
                    start = time.time()
                    while True:
                        chunk = r.read(64 * 1024)
                        if not chunk:
                            break
                        tmp.write(chunk)
                        bytes_read += len(chunk)
                        # progress
                        if total:
                            frac = bytes_read / total
                            filled = int(BAR * frac)
                            bar = "█" * filled + "░" * (BAR - filled)
                            sys.stdout.write(
                                f"\r[textwizard] [{bar}] {frac*100:5.1f}% "
                                f"{bytes_read/1048576:.1f}/{total/1048576:.1f} MB"
                            )
                        else:
                            sys.stdout.write(
                                f"\r[textwizard] downloaded {bytes_read/1048576:.1f} MB"
                            )
                        sys.stdout.flush()
                    sys.stdout.write("\n"); sys.stdout.flush()
                    tmp.flush(); os.fsync(tmp.fileno())
                    tmp_path = Path(tmp.name)
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(tmp_path, dst)
            return
        except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError) as e:
            last_exc = e
            print(f"[textwizard] download error (attempt {attempt}/{retries}): {e}")
    raise DictionaryUnavailableError(url) from last_exc
