import socket
import threading
import time
from tkinter import *
from tkinter import ttk, filedialog, messagebox

# Common services
services = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP"
}

class PortScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Network Port Scanner")
        self.root.geometry("700x500")

        self.stop_flag = False
        self.open_ports = []
        self.threads = []
        self.total_ports = 0
        self.scanned_ports = 0

        self.create_widgets()

    def create_widgets(self):
        Label(self.root, text="Target Host:").pack()
        self.target_entry = Entry(self.root, width=30)
        self.target_entry.pack()

        Label(self.root, text="Start Port:").pack()
        self.start_port = Entry(self.root, width=10)
        self.start_port.pack()

        Label(self.root, text="End Port:").pack()
        self.end_port = Entry(self.root, width=10)
        self.end_port.pack()

        Button(self.root, text="Start Scan", command=self.start_scan).pack(pady=5)
        Button(self.root, text="Stop Scan", command=self.stop_scan).pack(pady=5)
        Button(self.root, text="Save Results", command=self.save_results).pack(pady=5)

        self.progress = ttk.Progressbar(self.root, length=400, mode='determinate')
        self.progress.pack(pady=10)

        self.status_label = Label(self.root, text="Idle")
        self.status_label.pack()

        self.result_box = Text(self.root, height=15, width=80)
        self.result_box.pack()

    def scan_port(self, target, port):
        if self.stop_flag:
            return
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5)
            result = sock.connect_ex((target, port))
            if result == 0:
                service = services.get(port, "Unknown")
                msg = f"Port {port} OPEN ({service})\n"
                self.open_ports.append(msg)
                self.result_box.insert(END, msg)
            sock.close()
        except:
            pass
        finally:
            self.scanned_ports += 1
            self.update_progress()

    def update_progress(self):
        if self.total_ports == 0:
            return
        progress_value = (self.scanned_ports / self.total_ports) * 100
        self.progress['value'] = progress_value
        self.status_label.config(text=f"Scanning... {int(progress_value)}%")

    def start_scan(self):
        self.stop_flag = False
        self.open_ports.clear()
        self.result_box.delete(1.0, END)

        target = self.target_entry.get()
        try:
            start = int(self.start_port.get())
            end = int(self.end_port.get())
        except:
            messagebox.showerror("Error", "Invalid port range")
            return

        self.total_ports = end - start + 1
        self.scanned_ports = 0
        self.progress['value'] = 0

        start_time = time.time()

        for port in range(start, end + 1):
            if self.stop_flag:
                break
            t = threading.Thread(target=self.scan_port, args=(target, port))
            self.threads.append(t)
            t.start()

            # Limit threads to 500
            if len(self.threads) >= 500:
                for thread in self.threads:
                    thread.join()
                self.threads.clear()

        for thread in self.threads:
            thread.join()

        elapsed = time.time() - start_time
        self.status_label.config(text=f"Completed in {elapsed:.2f}s")

    def stop_scan(self):
        self.stop_flag = True
        self.status_label.config(text="Scan Stopped")

    def save_results(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        if file:
            with open(file, "w") as f:
                for port in self.open_ports:
                    f.write(port)
            messagebox.showinfo("Saved", "Results saved successfully")

if __name__ == "__main__":
    root = Tk()
    app = PortScannerGUI(root)
    root.mainloop()