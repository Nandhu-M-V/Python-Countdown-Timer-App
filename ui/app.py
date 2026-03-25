import customtkinter as ctk
import threading
import os
from logic.timer import CountdownTimer


class CircularProgress(ctk.CTkCanvas):
    def __init__(self, parent, size=200):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        self.size = size
        self.progress = 0

    def set_progress(self, value):
        self.progress = value
        self.draw()

    def draw(self):
        self.delete("all")

        mode = ctk.get_appearance_mode()

        fg_color = self.master.cget("fg_color")

        if isinstance(fg_color, (list, tuple)):
            bg_color = fg_color[0] if mode == "Light" else fg_color[1]
        else:
            parts = fg_color.split()
            bg_color = parts[0] if mode == "Light" else parts[-1]

        self.configure(bg=bg_color)

        center = self.size // 2
        radius = self.size // 2 - 10

        self.create_oval(
            center - radius, center - radius,
            center + radius, center + radius,
            outline="#444", width=10
        )

        angle = self.progress * 360
        self.create_arc(
            center - radius, center - radius,
            center + radius, center + radius,
            start=90, extent=-angle,
            style="arc",
            outline="#00ffcc",
            width=10
        )


class TimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(" Timer")
        self.geometry("400x500")

        ctk.set_appearance_mode("dark")
        self.dark = True

        self.timer = CountdownTimer(10)
        self.animating = False

        self.progress = CircularProgress(self, 200)
        self.progress.pack(pady=20)
        self.progress.set_progress(0)
        self.paused = False
        self.loop_running = False

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10)

        self.min_entry = ctk.CTkEntry(self.input_frame, width=60, placeholder_text="MM")
        self.min_entry.pack(side="left", padx=5)

        self.sec_entry = ctk.CTkEntry(self.input_frame, width=60, placeholder_text="SS")
        self.sec_entry.pack(side="left", padx=5)

        self.min_entry.insert(0, "0")
        self.sec_entry.insert(0, "10")

        self.label = ctk.CTkLabel(self, text="00:10", font=("Arial", 40))
        self.label.pack(pady=15)

        self.start_btn = ctk.CTkButton(self, text="Start", command=self.toggle_timer)
        self.start_btn.pack(pady=5)

        self.theme_btn = ctk.CTkButton(self, text="Toggle Theme", command=self.toggle_theme)
        self.theme_btn.pack(pady=5)

    def toggle_timer(self):
        if not self.timer.running and not self.paused:
            try:
                minutes = int(self.min_entry.get() or 0)
                seconds = int(self.sec_entry.get() or 0)
            except ValueError:
                self.label.configure(text="Invalid")
                return

            total_seconds = minutes * 60 + seconds

            if total_seconds <= 0:
                self.label.configure(text="Enter time")
                return

            self.timer.set_time(total_seconds)
            self.timer.start()
            self.progress.set_progress(0)

            self.paused = False
            self.start_btn.configure(text="Pause")

            self.min_entry.configure(state="disabled")
            self.sec_entry.configure(state="disabled")

            self.update_timer()

        elif self.timer.running:
            self.timer.pause()
            self.paused = True
            self.start_btn.configure(text="Resume")

        elif self.paused:
            self.timer.resume()
            self.paused = False
            self.start_btn.configure(text="Pause")
            self.update_timer()

    def update_timer(self):
        if self.loop_running:
            return

        self.loop_running = True

        def loop():
            result = self.timer.tick()

            if result == "done":
                self.label.configure(text="Done!")
                self.play_sound()

                self.start_btn.configure(text="Start")
                self.paused = False
                self.loop_running = False

                self.min_entry.configure(state="normal")
                self.sec_entry.configure(state="normal")

                return

            if result is not None:
                mins = result // 60
                secs = result % 60
                self.label.configure(text=f"{mins:02}:{secs:02}")
                self.animate_label()
                self.animate_progress(self.timer.get_progress())

            self.after(1000, loop)

        loop()

    def animate_progress(self, target):
        if self.animating:
            return

        self.animating = True

        steps = 20
        start = self.progress.progress
        diff = target - start

        def animate(step=0):
            if step <= steps:
                value = start + (diff * step / steps)
                self.progress.set_progress(value)
                self.after(20, lambda: animate(step + 1))
            else:
                self.animating = False

        animate()

    def animate_label(self):
        current_size = 40
        bigger = 44

        def grow():
            self.label.configure(font=("Arial", bigger))
            self.after(100, shrink)

        def shrink():
            self.label.configure(font=("Arial", current_size))

        grow()

    def play_sound(self):
        def beep():
            if os.system("which paplay > /dev/null 2>&1") == 0:
                os.system("paplay /usr/share/sounds/freedesktop/stereo/complete.oga")
            else:
                print("\a")

        threading.Thread(target=beep, daemon=True).start()

    def toggle_theme(self):
        self.dark = not self.dark
        ctk.set_appearance_mode("dark" if self.dark else "light")
        self.progress.draw()
