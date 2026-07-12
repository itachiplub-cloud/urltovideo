import time
import os
from helpers.utils import format_size, format_duration


class ProgressTracker:
    def __init__(self):
        self.start_time = None
        self.last_update = 0
        self.update_interval = 3

    def start(self):
        self.start_time = time.time()
        self.last_update = 0

    def should_update(self) -> bool:
        now = time.time()
        if now - self.last_update >= self.update_interval:
            self.last_update = now
            return True
        return False

    def get_progress_text(self, current: int, total: int, status: str = "⬇️ Downloading") -> str:
        if not self.start_time:
            self.start()
        elapsed = time.time() - self.start_time
        if total > 0:
            percent = (current / total) * 100
            speed = current / elapsed if elapsed > 0 else 0
            eta = (total - current) / speed if speed > 0 else 0
            return (
                f"{status}...\n"
                f"━━━━━━━━━━━━━━━━━━━\n"
                f"📊 {percent:.1f}%\n"
                f"📦 {format_size(current)} / {format_size(total)}\n"
                f"⚡ {format_size(int(speed))}/s\n"
                f"⏱️ ETA: {format_duration(int(eta))}"
            )
        return f"{status}...\n📦 {format_size(current)} downloaded"


def progress_callback(tracker: ProgressTracker, message, total: int):
    last_update = [0]

    def callback(current, total_size):
        now = time.time()
        if now - last_update[0] >= 3:
            last_update[0] = now
            try:
                text = tracker.get_progress_text(current, total_size or total)
                # We don't await here since this is called from sync context
                # The actual update happens in the download wrapper
            except Exception:
                pass

    return callback
