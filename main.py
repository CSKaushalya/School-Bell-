import tkinter as tk
from tkinter import messagebox, filedialog
import time
import threading
from datetime import datetime
import os
import pygame  # For playing sound


class SchoolBellScheduler:
    def __init__(self, root):
        self.root = root
        self.root.title("School Bell Ringer")
        self.root.geometry("600x650")

        self.periods = []

        # Initialize pygame mixer for sound playing
        pygame.mixer.init()

        # GUI Components
        self.create_widgets()

        # Start the bell ringing process in a separate thread
        self.running = True
        threading.Thread(target=self.run_scheduler, daemon=True).start()

    def create_widgets(self):
        # Title
        title_label = tk.Label(self.root, text="School Bell Ringer", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=4, pady=10)

        # Time Input with hint
        tk.Label(self.root, text="Set Time (HH:MM)").grid(row=1, column=0)
        self.time_entry = tk.Entry(self.root)
        self.time_entry.insert(0, "08:30")
        self.time_entry.grid(row=1, column=1, padx=5, pady=5)

        # Day Selection
        tk.Label(self.root, text="Select Days").grid(row=2, column=0)
        self.days = {
            "Monday": tk.BooleanVar(),
            "Tuesday": tk.BooleanVar(),
            "Wednesday": tk.BooleanVar(),
            "Thursday": tk.BooleanVar(),
            "Friday": tk.BooleanVar(),

        }
        days_frame = tk.Frame(self.root)
        days_frame.grid(row=2, column=1, padx=5, pady=5)
        for day, var in self.days.items():
            tk.Checkbutton(days_frame, text=day, variable=var).pack(side=tk.LEFT)

        # Sound Selection
        tk.Label(self.root, text="Select Sound").grid(row=3, column=0)
        self.sound_file = tk.StringVar()
        self.sound_file.set("No file selected")
        sound_frame = tk.Frame(self.root)
        sound_frame.grid(row=3, column=1, padx=5, pady=5)
        tk.Label(sound_frame, textvariable=self.sound_file).pack(side=tk.LEFT)
        tk.Button(sound_frame, text="Browse", command=self.browse_sound).pack(side=tk.LEFT)

        # Comment Input
        tk.Label(self.root, text="Add Comment").grid(row=4, column=0)
        self.comment_entry = tk.Entry(self.root)
        self.comment_entry.grid(row=4, column=1, padx=5, pady=5)

        # Add Period Button
        tk.Button(self.root, text="Add Bell Time", command=self.add_period).grid(row=5, column=1, padx=5, pady=5)

        # Listbox to display periods
        self.period_listbox = tk.Listbox(self.root)
        self.period_listbox.grid(row=6, column=0, columnspan=4, sticky="nsew", padx=5, pady=10)

        self.root.grid_rowconfigure(6, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # Edit and Delete Buttons
        tk.Button(self.root, text="Edit Selected", command=self.edit_period).grid(row=7, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Delete Selected", command=self.delete_period).grid(row=7, column=2, padx=5, pady=5)

        # Status label
        self.status_label = tk.Label(self.root, text="Scheduler running...", fg="green")
        self.status_label.grid(row=8, column=0, columnspan=4, pady=10)

    def browse_sound(self):
        sound_path = filedialog.askopenfilename(
            filetypes=[("Audio Files", "*.mp3 *.wav")]
        )
        if sound_path:
            self.sound_file.set(os.path.basename(sound_path))
            self.selected_sound = sound_path

    def add_period(self):
        time_str = self.time_entry.get()
        selected_days = [day for day, var in self.days.items() if var.get()]
        sound_file = getattr(self, 'selected_sound', None)
        comment = self.comment_entry.get().strip()

        if self.validate_time(time_str) and selected_days and sound_file:
            self.periods.append((time_str, selected_days, sound_file, comment))
            self.update_period_listbox()
            self.clear_inputs()
        else:
            messagebox.showerror("Invalid Input",
                                 "Please enter a valid time, select at least one day, and choose a sound.")

    def update_period_listbox(self):
        self.period_listbox.delete(0, tk.END)
        for i, period in enumerate(self.periods, 1):
            time_str, days, sound, comment = period
            display_text = f"Bell {i}: {time_str} on {', '.join(days)} (Sound: {os.path.basename(sound)})"
            if comment:
                display_text += f" - {comment}"
            self.period_listbox.insert(tk.END, display_text)

    def validate_time(self, time_str):
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    def ring_bell(self, sound_file):
        # Play the selected sound file
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():  # Wait until the sound finishes playing
            time.sleep(1)

    def run_scheduler(self):
        while self.running:
            current_time = datetime.now().strftime("%H:%M")
            current_day = datetime.now().strftime("%A")

            for time_str, days, sound_file, comment in self.periods:
                if current_time == time_str and current_day in days:
                    self.ring_bell(sound_file)

            time.sleep(60)  # Check every minute

    def on_close(self):
        self.running = False
        pygame.mixer.quit()  # Close the sound mixer
        self.root.destroy()

    def clear_inputs(self):
        self.time_entry.delete(0, tk.END)
        self.time_entry.insert(0, "08:30")
        self.comment_entry.delete(0, tk.END)
        for var in self.days.values():
            var.set(False)
        self.sound_file.set("No file selected")

    def edit_period(self):
        selected_index = self.period_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            time_str, days, sound_file, comment = self.periods[index]

            # Fill the inputs with the selected period's details
            self.time_entry.delete(0, tk.END)
            self.time_entry.insert(0, time_str)
            self.comment_entry.delete(0, tk.END)
            self.comment_entry.insert(0, comment)
            for day in days:
                self.days[day].set(True)
            self.sound_file.set(os.path.basename(sound_file))
            self.selected_sound = sound_file

            # Remove the selected period for re-editing
            del self.periods[index]
            self.update_period_listbox()
        else:
            messagebox.showwarning("No Selection", "Please select a period to edit.")

    def delete_period(self):
        selected_index = self.period_listbox.curselection()
        if selected_index:
            index = selected_index[0]
            del self.periods[index]
            self.update_period_listbox()
        else:
            messagebox.showwarning("No Selection", "Please select a period to delete.")


if __name__ == "__main__":
    root = tk.Tk()
    app = SchoolBellScheduler(root)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
