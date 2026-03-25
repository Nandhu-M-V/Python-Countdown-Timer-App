class CountdownTimer:
    def __init__(self, total_time: int):
        self.total_time = total_time
        self.remaining = total_time
        self.running = False

    def set_time(self, seconds: int):
        self.total_time = max(0, seconds)
        self.remaining = self.total_time

    def start(self):
        if self.total_time <= 0:
            return
        self.remaining = self.total_time
        self.running = True

    def pause(self):
        self.running = False

    def resume(self):
        if self.remaining > 0:
            self.running = True

    def tick(self):
        if not self.running:
            return None

        if self.remaining > 0:
            self.remaining -= 1
            return self.remaining
        else:
            self.running = False
            return "done"

    def get_progress(self):
        if self.total_time == 0:
            return 0
        return (self.total_time - self.remaining) / self.total_time
