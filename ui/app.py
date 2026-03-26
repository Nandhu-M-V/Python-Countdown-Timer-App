import customtkinter as ctk
import threading
import os
from logic.timer import CountdownTimer


class CircularProgress(ctk.CTkCanvas):
    def __init__(self, parent, size=200):
        super().__init__(parent, width=size, height=size, highlightthickness=0)
        self.size = size
        self.progress = -1

    def set_progress(self, value):
        if abs(self.progress - value) < 0.01:
            return
        self.progress = value
        self.draw()

    def draw(self):
        self.delete("all")

        mode = ctk.get_appearance_mode()
        fg_color = self.master.cget("fg_color")

        if isinstance(fg_color, (list, tuple)):
            bg_color = fg_color[0] if mode == "Light" else fg_color[1]
        else:
            bg_color = fg_color

        self.configure(bg=bg_color)

        center = self.size // 2
        radius = self.size // 2 - 10

        self.create_oval(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            outline="#444",
            width=10,
        )

        angle = self.progress * 360
        self.create_arc(
            center - radius,
            center - radius,
            center + radius,
            center + radius,
            start=90,
            extent=-angle,
            style="arc",
            outline="#9dff00",
            width=10,
        )


class TimerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Timer")
        self.geometry("400x500")

        ctk.set_appearance_mode("dark")
        self.dark = True

        self.timer = CountdownTimer(10)
        self.done_played = False

        # --- UI ---
        self.progress = CircularProgress(self, 200)
        self.progress.pack(pady=20)

        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.pack(pady=10)

        self.min_entry = ctk.CTkEntry(self.input_frame, width=60)
        self.min_entry.pack(side="left", padx=5)

        self.sec_entry = ctk.CTkEntry(self.input_frame, width=60)
        self.sec_entry.pack(side="left", padx=5)

        self.min_entry.insert(0, "0")
        self.sec_entry.insert(0, "10")

        self.label = ctk.CTkLabel(self, text="00:10", font=("Arial", 40))
        self.label.pack(pady=15)

        self.start_btn = ctk.CTkButton(self, text="Start", command=self.toggle_timer)
        self.start_btn.pack(pady=5)

        self.stop_btn = ctk.CTkButton(self, text="Stop", command=self.stop_timer)
        self.stop_btn.pack(pady=5)

        self.theme_btn = ctk.CTkButton(
            self, text="Toggle Theme", command=self.toggle_theme
        )
        self.theme_btn.pack(pady=5)

        self.bind("<space>", lambda e: self.toggle_timer())
        self.bind("<Escape>", lambda e: self.stop_timer())

        self.after(200, self.update_loop)

    def toggle_timer(self):
        if not self.timer.running and self.timer.remaining == self.timer.total_time:
            try:
                minutes = int(self.min_entry.get() or 0)
                seconds = int(self.sec_entry.get() or 0)
            except ValueError:
                self.label.configure(text="Invalid")
                return

            total = minutes * 60 + seconds
            if total <= 0:
                self.label.configure(text="Enter time")
                return

            self.timer.set_time(total)
            self.done_played = False

        if self.timer.running:
            self.timer.pause()
            self.start_btn.configure(text="Resume")
        else:
            self.timer.resume()
            self.start_btn.configure(text="Pause")

    def stop_timer(self):
        self.timer.reset()
        self.done_played = False

        self.label.configure(text="00:00")
        self.progress.set_progress(0)

        self.start_btn.configure(text="Start")

    def update_loop(self):
        result = self.timer.tick()

        if result == "done":
            if not self.done_played:
                self.play_sound()
                self.done_played = True
        else:
            mins = result // 60
            secs = result % 60
            self.label.configure(text=f"{mins:02}:{secs:02}")

        self.progress.set_progress(self.timer.get_progress())

        self.after(1000, self.update_loop)

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
