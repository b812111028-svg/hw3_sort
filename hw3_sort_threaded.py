import tkinter as tk
from tkinter import ttk, messagebox
import random
import threading
import time

N = 5000                 
MAX_VALUE = 200000   
UPDATE_EVERY = 200      


def make_random_unique_numbers(n, max_value):
    if n > max_value:
        raise ValueError("N must be <= MAX_VALUE")

    used = set()
    arr = []
    while len(arr) < n:
        x = random.randint(1, max_value)
        if x not in used:
            used.add(x)
            arr.append(x)
    return arr


def selection_sort(arr, progress_callback):
    n = len(arr)
    total_steps = n

    for i in range(n - 1):
        min_index = i
        for j in range(i + 1, n):
            if arr[j] < arr[min_index]:
                min_index = j

        if min_index != i:
            arr[i], arr[min_index] = arr[min_index], arr[i]

        if i % UPDATE_EVERY == 0 or i == n - 2:
            progress_callback((i + 1) / total_steps * 100)

    progress_callback(100)
    return arr


def insertion_sort(arr, progress_callback):
    n = len(arr)
    total_steps = n

    for i in range(1, n):
        key = arr[i]
        j = i - 1

        while j >= 0 and arr[j] > key:
            arr[j + 1] = arr[j]
            j -= 1

        arr[j + 1] = key

        if i % UPDATE_EVERY == 0 or i == n - 1:
            progress_callback((i + 1) / total_steps * 100)

    progress_callback(100)
    return arr


def quick_sort(arr, progress_callback):
    n = len(arr)
    finished_partitions = 0
    lock = threading.Lock()

    def partition(start, end):
        pivot_value = arr[start]
        left = start
        right = end

        while left < right:
            while left < right and arr[right] >= pivot_value:
                right -= 1
            while left < right and arr[left] <= pivot_value:
                left += 1
            if left < right:
                arr[left], arr[right] = arr[right], arr[left]

        arr[start], arr[right] = arr[right], arr[start]
        return right

    def recursive_qs(start, end):
        nonlocal finished_partitions
        if start >= end:
            return

        pivot_index = partition(start, end)

        with lock:
            finished_partitions += 1
            if finished_partitions % UPDATE_EVERY == 0:
                progress_callback(min(finished_partitions / n * 100, 99))

        recursive_qs(start, pivot_index - 1)
        recursive_qs(pivot_index + 1, end)

    recursive_qs(0, n - 1)
    progress_callback(100)
    return arr


class SortGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Sorting Algorithm Efficiency Comparison (Threaded)")
        self.root.geometry("850x560")
        self.root.resizable(False, False)

        self.results = {}
        self.threads = []
        self.running = False

        title = tk.Label(root, text="Sorting Algorithms Efficiency", font=("Arial", 18, "bold"))
        title.pack(pady=15)

        input_frame = tk.Frame(root)
        input_frame.pack(pady=5)

        tk.Label(input_frame, text="N:", font=("Arial", 11)).grid(row=0, column=0, padx=5)
        self.n_entry = tk.Entry(input_frame, width=10)
        self.n_entry.insert(0, str(N))
        self.n_entry.grid(row=0, column=1, padx=5)

        self.status_label = tk.Label(root, text="Ready", font=("Arial", 11))
        self.status_label.pack(pady=5)

        self.frame = tk.Frame(root)
        self.frame.pack(pady=10)

        self.algorithms = ["Selection Sort", "Insertion Sort", "Quick Sort"]
        self.progress_bars = {}
        self.percent_labels = {}
        self.time_labels = {}

        for row, name in enumerate(self.algorithms):
            tk.Label(self.frame, text=name + ":", width=16, anchor="w", font=("Arial", 11)).grid(row=row, column=0, padx=10, pady=5)
            bar = ttk.Progressbar(self.frame, length=430, maximum=100)
            bar.grid(row=row, column=1, padx=10, pady=5)
            pct = tk.Label(self.frame, text="0%", width=8, font=("Arial", 11))
            pct.grid(row=row, column=2, padx=10)

            self.progress_bars[name] = bar
            self.percent_labels[name] = pct

        runtime_title = tk.Label(root, text="Total runtime (seconds):", font=("Arial", 12, "bold"))
        runtime_title.pack(anchor="w", padx=30, pady=(20, 5))

        runtime_frame = tk.Frame(root)
        runtime_frame.pack(anchor="w", padx=30)

        for row, name in enumerate(self.algorithms):
            tk.Label(runtime_frame, text=name + ":", width=16, anchor="w", font=("Arial", 11)).grid(row=row, column=0)
            label = tk.Label(runtime_frame, text="-", width=16, anchor="w", font=("Arial", 11))
            label.grid(row=row, column=1)
            self.time_labels[name] = label

        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", padx=40, pady=25)

        self.start_button = tk.Button(
        button_frame,
        text="Start Simulations",
        command=self.start_simulation,
        width=20,
        height=2,
        font=("Arial", 12, "bold")
    )
        self.start_button.pack(side="left", padx=10)

        self.quit_button = tk.Button(
        button_frame,
        text="Quit",
        command=root.destroy,
        width=12,
        height=2,
        font=("Arial", 12, "bold")
    )
        self.quit_button.pack(side="right", padx=10)

    def safe_update_progress(self, name, value):
        self.root.after(0, self.update_progress, name, value)

    def update_progress(self, name, value):
        value = max(0, min(100, value))
        self.progress_bars[name]["value"] = value
        self.percent_labels[name].config(text=f"{value:.0f}%")

    def run_algorithm(self, name, func, arr):
        start_time = time.perf_counter()
        func(arr, lambda p: self.safe_update_progress(name, p))
        end_time = time.perf_counter()

        elapsed = end_time - start_time
        self.results[name] = elapsed

        self.root.after(0, lambda: self.time_labels[name].config(text=f"{elapsed:.4f}"))
        self.root.after(0, self.check_all_finished)

    def check_all_finished(self):
        if len(self.results) == len(self.algorithms):
            self.running = False
            self.start_button.config(state="normal")
            self.status_label.config(text="Finished")

    def start_simulation(self):
        if self.running:
            return

        try:
            n = int(self.n_entry.get())
            if n <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter a positive integer for N.")
            return

        self.running = True
        self.results = {}
        self.threads = []
        self.start_button.config(state="disabled")
        self.status_label.config(text="Running...")

        for name in self.algorithms:
            self.progress_bars[name]["value"] = 0
            self.percent_labels[name].config(text="0%")
            self.time_labels[name].config(text="-")

        original = make_random_unique_numbers(n, max(MAX_VALUE, n * 20))

        jobs = [
            ("Selection Sort", selection_sort, original.copy()),
            ("Insertion Sort", insertion_sort, original.copy()),
            ("Quick Sort", quick_sort, original.copy()),
        ]

        for name, func, arr in jobs:
            t = threading.Thread(target=self.run_algorithm, args=(name, func, arr), daemon=True)
            self.threads.append(t)
            t.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = SortGUI(root)
    root.mainloop()
