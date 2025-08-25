import time

class Timer:
    def __init__(self, label=">>Время выполнения"):
        self.label = label

    def __enter__(self):
        self.start = time.time()
        print(f"{self.label} — старт<<.")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = int(time.time() - self.start)
        hours, remainder = divmod(elapsed, 3600)
        minutes, seconds = divmod(remainder, 60)
        parts = []
        if hours > 0:
            parts.append(f"{hours} ч")
        if minutes > 0 or hours > 0:
            parts.append(f"{minutes} мин")
        parts.append(f"{seconds} сек")
        print(f"{self.label} — завершено за {' '.join(parts)}<<.")
