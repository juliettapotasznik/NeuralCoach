from time import perf_counter
import sys

class PerformanceMetrics:
    def __init__(self):
        self.latency = 0
        self.fps = 0
        self.frame_count = 0
        self.total_latency = 0
        self.last_update_time = None

    def update(self, start_time, frame):
        if self.last_update_time is None:
            self.last_update_time = start_time
        
        self.frame_count += 1
        current_time = perf_counter()
        self.latency = current_time - start_time
        self.total_latency += self.latency
        
        if current_time - self.last_update_time > 1:
            self.fps = self.frame_count / (current_time - self.last_update_time)
            self.frame_count = 0
            self.last_update_time = current_time

    def log_total(self):
        print(f"\nProcessing finished", file=sys.stderr)
        print(f"Average latency: {self.total_latency / self.frame_count:.1f} ms", file=sys.stderr)
        print(f"Average FPS: {self.frame_count / self.total_latency:.1f}", file=sys.stderr) 