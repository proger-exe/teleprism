"""SQLite online backup support."""

import sqlite3
from pathlib import Path

from teleprism.app.core.time import utcnow


async def backup_database(source: Path, target_dir: Path, retention_days: int) -> Path:
    """Create an online SQLite backup and prune old backup files."""

    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / f"teleprism-{utcnow().strftime('%Y%m%d-%H%M%S')}.sqlite3"
    with sqlite3.connect(source) as src, sqlite3.connect(target) as dst:
        src.backup(dst)
    cutoff = utcnow().timestamp() - retention_days * 86_400
    for backup in target_dir.glob("teleprism-*.sqlite3"):
        if backup.stat().st_mtime < cutoff:
            backup.unlink()
    return target
