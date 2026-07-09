import json
import os
from datetime import datetime
from typing import Optional


class ErrorLogger:
    """Logger for tracking download errors (404, 503, etc.)"""

    def __init__(self, base_path: str, service: str, creator_id: str, creator_name: str = "unknown"):
        """
        Initialize the error logger for a specific creator.

        Args:
            base_path: Base download directory path
            service: Service name (patreon, fanbox, etc.)
            creator_id: Creator ID
            creator_name: Creator name for readability
        """
        self.base_path = base_path
        self.service = service
        self.creator_id = creator_id
        self.creator_name = creator_name
        self.log_file_path = self._get_log_file_path()
        self.errors = self._load_existing_errors()

    def _get_log_file_path(self) -> str:
        """Get the path for the error log file in the creator's folder."""
        creator_folder = os.path.join(self.base_path, self.service, f"{self.creator_name} [{self.creator_id}]")
        os.makedirs(creator_folder, exist_ok=True)
        return os.path.join(creator_folder, "error_log.json")

    def _load_existing_errors(self) -> list:
        """Load existing errors from the log file if it exists."""
        if os.path.exists(self.log_file_path):
            try:
                with open(self.log_file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, OSError):
                return []
        return []

    def log_error(
        self,
        url: str,
        post_id: str,
        post_title: str,
        error_code: Optional[int] = None,
        error_message: str = "",
        attachment_info: Optional[dict] = None,
    ) -> None:
        """
        Log a download error.

        Args:
            url: URL that failed to download
            post_id: Post ID associated with the error
            post_title: Post title for reference
            error_code: HTTP error code (404, 503, etc.) or None for other errors
            error_message: Error message/details
            attachment_info: Additional info about the attachment
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "url": url,
            "post_id": post_id,
            "post_title": post_title,
            "error_code": error_code,
            "error_message": str(error_message),
            "attachment_info": attachment_info or {},
        }

        self.errors.append(error_entry)
        self._save_errors()

    def _save_errors(self) -> None:
        """Save current errors to the log file."""
        try:
            with open(self.log_file_path, "w", encoding="utf-8") as f:
                json.dump(self.errors, f, ensure_ascii=False, indent=2)
        except OSError as e:
            print(f"[Error] Failed to save error log to {self.log_file_path}: {e}")

    def get_error_count(self) -> int:
        """Get the total number of logged errors."""
        return len(self.errors)

    def get_errors_by_code(self, error_code: int) -> list:
        """Get errors filtered by error code."""
        return [e for e in self.errors if e.get("error_code") == error_code]
