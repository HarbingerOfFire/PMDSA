import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import os
import csv

from measure import measure, Star
from star_find import find
from FITS import fits


class StarAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Star Analyzer")
        self.results = []
        self.errors = []
        self.lock = threading.Lock()

        # Use ttk style for modern look
        style = ttk.Style()
        style.theme_use('clam')  # clam is clean, you can try 'default', 'alt', 'classic'

        self._build_gui()

    def _build_gui(self):
        # Top frame container
        top_frame = ttk.Frame(self.root, padding=(8, 6))
        top_frame.pack(fill="x")

        # Row 0: Directory Label, Entry, Browse Button (all in one row)
        ttk.Label(top_frame, text="Directory:", width=8).grid(row=0, column=0, sticky="w")
        self.dir_entry = ttk.Entry(top_frame)
        self.dir_entry.grid(row=0, column=1, columnspan=5, sticky="ew", padx=(0, 6))
        ttk.Button(top_frame, text="Browse", command=self.browse_directory, width=8).grid(row=0, column=6, pady=2)

        # Expand column 1 (directory entry) when resizing
        top_frame.columnconfigure(1, weight=1)

        # Row 1: RA/DEC inputs and buttons
        ttk.Label(top_frame, text="RA:", width=3).grid(row=1, column=0, sticky="e", padx=(0, 2))
        self.ra_entry = ttk.Entry(top_frame)
        self.ra_entry.grid(row=1, column=1, sticky="ew", padx=(0, 10))

        ttk.Label(top_frame, text="DEC:", width=4).grid(row=1, column=2, sticky="ew", padx=(0, 2))
        self.dec_entry = ttk.Entry(top_frame)
        self.dec_entry.grid(row=1, column=3, sticky="ew", padx=(0, 10))

        ttk.Button(top_frame, text="Process", command=self.thread_process, width=10).grid(row=1, column=4, padx=3)
        ttk.Button(top_frame, text="Export CSV", command=self.export_csv, width=10).grid(row=1, column=5, padx=3)
        ttk.Button(top_frame, text="View Errors", command=self.show_error_log, width=10).grid(row=1, column=6, padx=3)

        # Optional: add some columnconfigure to balance layout on row 1
        for col in range(7):
            top_frame.columnconfigure(col, weight=0)
        top_frame.columnconfigure(1, weight=1)  # Let RA entry expand if needed

        # Treeview table
        columns = ("Idx", "Filename", "Separation", "Angle", "DeltaMag", "Plot")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", selectmode="none", height=18)
        self.tree.pack(fill="both", expand=True, padx=8, pady=(2,8))

        # Define column headers and widths
        col_widths = [40, 220, 90, 90, 90, 60]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")

        # Bind clicks on the "Plot" button column
        self.tree.bind("<Button-1>", self.on_tree_click)


    def browse_directory(self):
        directory = filedialog.askdirectory()
        if directory:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, directory)

    def thread_process(self):
        t = threading.Thread(target=self.process_files, daemon=True)
        t.start()

    def process_files(self):
        self.tree.delete(*self.tree.get_children())
        self.results.clear()
        self.errors.clear()

        directory = self.dir_entry.get().strip()
        ra_str = self.ra_entry.get().strip()
        dec_str = self.dec_entry.get().strip()

        try:
            ra = float(ra_str) if ra_str else None
            dec = float(dec_str) if dec_str else None
        except ValueError:
            self._async_msgbox("Invalid Input", "RA and DEC must be numeric.")
            return

        if not os.path.isdir(directory):
            self._async_msgbox("Error", "Invalid directory path.")
            return

        files = [f for f in os.listdir(directory) if f.lower().endswith(".fits")]

        for idx, filename in enumerate(files):
            full_path = os.path.join(directory, filename)
            try:
                with open(full_path, 'rb') as f:
                    fits_file = fits.FITS(f)

                if ra is not None and dec is not None:
                    x, y = fits_file.wcs.world_to_pixel(ra, dec)
                else:
                    x = y = None

                finder = find.StarFinder(sigma=1.0, window_size=3)
                coords = finder.find_stars(fits_file.data)
                stars = finder.analyze_stars(fits_file.data, coords, (x, y))

                if len(stars) < 2:
                    raise ValueError("Fewer than two stars found.")

                star1, star2 = (Star(x, y, flux, aperture_radius, distance)
                                for x, y, flux, aperture_radius, distance in stars[:2])
                if star1.flux < star2.flux:
                    star1, star2 = star2, star1

                m = measure(fits_file.wcs)
                sep = m.separation(star1, star2)
                angle = m.position_angle(star1, star2)
                dmag = m.delta_mag(star1, star2)

                with self.lock:
                    self.results.append((idx, filename, sep, angle, dmag, fits_file, star1))

                # Insert row in main thread
                self.root.after(0, self.insert_row, idx, filename, sep, angle, dmag)

            except Exception as e:
                self.errors.append((filename, str(e)))

    def insert_row(self, idx, filename, sep, angle, dmag):
        # Add Plot as clickable text, will be handled in click handler
        self.tree.insert("", "end", iid=idx, values=(idx, filename, f"{sep:.2f}", f"{angle:.2f}", f"{dmag:.2f}", "Show Plot"))

    def on_tree_click(self, event):
        # Detect if user clicked on "Show" in Plot column
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        col = self.tree.identify_column(event.x)
        row = self.tree.identify_row(event.y)
        if not row:
            return

        # Plot column is the 6th column (#6), 1-indexed => "#6"
        if col == "#6":
            idx = int(row)
            try:
                _, _, _, _, _, fits_file, star1 = self.results[idx]
                self.plot_star(fits_file.data, star1)
            except Exception as e:
                messagebox.showerror("Plot Error", str(e))

    def export_csv(self):
        if not self.results:
            messagebox.showinfo("No Data", "No data to export.")
            return

        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not path:
            return

        with open(path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Index", "Filename", "Separation", "Position Angle", "Delta Mag"])
            for row in self.results:
                idx, filename, sep, angle, dmag, *_ = row
                writer.writerow([idx, filename, f"{sep:.2f}", f"{angle:.2f}", f"{dmag:.2f}"])

        messagebox.showinfo("Export", f"Data exported to {path}")

    def show_error_log(self):
        if not self.errors:
            messagebox.showinfo("No Errors", "No errors logged.")
            return

        log_win = tk.Toplevel(self.root)
        log_win.title("Error Log")
        log_text = tk.Text(log_win, wrap="word", height=20, width=80)
        log_text.pack(padx=8, pady=8, fill="both", expand=True)

        for fname, err in self.errors:
            log_text.insert("end", f"{fname}: {err}\n")

        # Make text read-only
        log_text.config(state="disabled")

    def plot_star(self, image, star):
        import matplotlib.pyplot as plt
        zoom = 15
        x, y = int(star.x), int(star.y)
        cutout = image[max(y - zoom, 0): y + zoom, max(x - zoom, 0): x + zoom]

        plt.imshow(cutout, cmap="gray", origin="lower")
        plt.title(f"Star Zoom - x:{x}, y:{y}")
        plt.colorbar()
        plt.show()

    def _async_msgbox(self, title, message):
        self.root.after(0, lambda: messagebox.showerror(title, message))


if __name__ == "__main__":
    root = tk.Tk()
    app = StarAnalyzerApp(root)
    root.geometry("740x480")  # Compact starting size
    root.mainloop()
