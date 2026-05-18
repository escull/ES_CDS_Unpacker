import zlib
import json
import csv
import os
import tkinter as tk, tkinter.ttk as ttk # Import ttk for Progressbar
from tkinter import filedialog, scrolledtext
import threading

def extract_to_csv(input_file, output_csv, log_callback=None, progress_callback=None):
    def log(msg):
        if log_callback:
            log_callback(msg)
        else:
            print(msg) # This print will only be used if no log_callback is provided, e.g., if run without GUI.
            
    log(f"Analysing {input_file}...")
    
    if not os.path.exists(input_file):
        log(f"Error: File '{input_file}' not found.")
        return

    with open(input_file, 'rb') as f:
        data = f.read()

    magic_bytes = b'\x1f\x8b\x08'
    start_indexes = []
    index = data.find(magic_bytes)
    
    while index != -1:
        start_indexes.append(index)
        index = data.find(magic_bytes, index + 1)

    total_frames = len(start_indexes) # Get total frames
    log(f"Found {total_frames} data frames. Extracting...")

    all_frames_data = []
    headers = set()

    for i, start_idx in enumerate(start_indexes):
        if progress_callback: # Report progress
            progress_callback(i + 1, total_frames)

        stream_data = data[start_idx:]
        try:
            # Decompress the block
            decompressed_bytes = zlib.decompress(stream_data, 31)
            
            # Decode bytes to ASCII/UTF-8 string
            json_string = decompressed_bytes.decode('utf-8', errors='ignore')
            
            # Clean up any trailing null bytes or garbage that might break JSON parsing
            json_string = json_string.strip('\x00')
            
            # Parse the JSON
            frame_data = json.loads(json_string)
            
            # Extract the actual sensor readings for this frame
            row_data = {}
            if 'items' in frame_data:
                for item in frame_data['items']:
                    sensor_name = f"{item.get('name', 'Unknown')} ({item.get('unit', '')})"
                    sensor_value = item.get('value', '')
                    
                    row_data[sensor_name] = sensor_value
                    headers.add(sensor_name)
                    
            all_frames_data.append(row_data)

        except (zlib.error, json.JSONDecodeError) as e:
            # Silently skip broken blocks (common at the very end of a live data stream)
            continue

    # Write the compiled data to CSV
    if all_frames_data:
        sorted_headers = sorted(list(headers))
        
        with open(output_csv, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=sorted_headers)
            writer.writeheader()
            for row in all_frames_data:
                writer.writerow(row)
                
        log(f"Success! Data exported to {output_csv}")
    else:
        log("No valid JSON telemetry found to export.")

class UnpackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("CDS Unpacker") 
        self.root.geometry("600x450") # Slightly increased height for progress bar
        
        self.input_file = None
        
        # Setup UI layout
        self.top_frame = tk.Frame(root)
        self.top_frame.pack(pady=10, padx=10, fill=tk.X)
        
        self.open_btn = tk.Button(self.top_frame, text="Open File", command=self.open_file)
        self.open_btn.pack(side=tk.LEFT, padx=5)
        
        self.file_lbl = tk.Label(self.top_frame, text="No file selected")
        self.file_lbl.pack(side=tk.LEFT, padx=5)
        
        self.process_btn = tk.Button(self.top_frame, text="Process", command=self.process_file, state=tk.DISABLED)
        self.process_btn.pack(side=tk.RIGHT, padx=5)
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress_bar.pack(pady=5, padx=10, fill=tk.X)
        self.progress_bar['value'] = 0 # Initialize to 0
        
        self.log_text = scrolledtext.ScrolledText(root, width=60, height=20, state=tk.DISABLED)
        self.log_text.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def log(self, message):
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def open_file(self):
        filename = filedialog.askopenfilename(filetypes=[("Binary Files", "*.bin"), ("All Files", "*.*")])
        if filename:
            self.input_file = filename
            self.file_lbl.config(text=os.path.basename(filename))
            self.process_btn.config(state=tk.NORMAL)
            self.log(f"Selected file: {self.input_file}")
            self.progress_bar['value'] = 0 # Reset progress bar on new file selection

    def process_file(self):
        if not self.input_file:
            return
        
        output_csv = os.path.splitext(self.input_file)[0] + '.csv'
        
        self.process_btn.config(state=tk.DISABLED)
        self.open_btn.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0 # Reset progress bar at start of processing
        
        def update_progress(current, total):
            if total > 0:
                percentage = (current / total) * 100
                self.root.after(0, lambda: self.progress_bar.config(value=percentage))
            else:
                self.root.after(0, lambda: self.progress_bar.config(value=0))
        
        def extraction_task():
            # Thread-safe log updating via .after()
            extract_to_csv(self.input_file, output_csv, 
                           log_callback=lambda msg: self.root.after(0, self.log, msg),
                           progress_callback=update_progress) # Pass the progress callback
            self.root.after(0, lambda: self.process_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.open_btn.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.progress_bar.config(value=100)) # Set to 100% on completion
            self.root.after(1000, lambda: self.progress_bar.config(value=0)) # Reset after a short delay
            
        # Run as daemon so it dies if the user closes the window mid-process
        threading.Thread(target=extraction_task, daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = UnpackerApp(root)
    root.mainloop()