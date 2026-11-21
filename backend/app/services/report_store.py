from pathlib import Path
from uuid import UUID

from app.core.config import Settings


def delete_report_files(scan_id: UUID | str, settings: Settings) -> None:
    identifier = str(scan_id)
    data_dir = Path(settings.database_path).resolve().parent
    roots = (data_dir, data_dir / "reports")
    patterns = (
        f"{identifier}.pdf",
        f"{identifier}.md",
        f"neurospider-audit-{identifier}.pdf",
        f"neurospider-{identifier}.md",
        f"*{identifier}*.pdf",
        f"*{identifier}*.md",
    )

    for root in roots:
        if not root.is_dir():
            continue
        for pattern in patterns:
            for path in root.glob(pattern):
                if path.is_file():
                    path.unlink(missing_ok=True)
