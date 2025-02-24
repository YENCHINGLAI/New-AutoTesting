import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import subprocess
import json
import os

class DediProgGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DediProg Programmer")

        # --- Variables ---
        self.dpcmd_path = tk.StringVar(root, value=r'.\Tool\DediProg\dpcmd')
        self.rootpath_var = tk.StringVar(root, value=r'.\Tool\FW')
        self.bin_var = tk.StringVar(root, value='Avoip_20F9_AMX_V1.6.6.bin')
        self.ic_var = tk.StringVar(root, value='MX25U51245G')
        self.device_ids = self.get_device_ids()
        self.device_var = tk.StringVar(root)
        self.programming_mode_var = tk.StringVar(root, value='-z')  # Default mode
        
        # --- GUI Elements ---
        # dpcmd Path
        ttk.Label(root, text="dpcmd Path:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.dpcmd_path_entry = ttk.Entry(root, textvariable=self.dpcmd_path, width=50)
        self.dpcmd_path_entry.grid(row=0, column=1, sticky=tk.EW, padx=5, pady=5)
        self.dpcmd_browse_button = ttk.Button(root, text="Browse", command=self.browse_dpcmd)
        self.dpcmd_browse_button.grid(row=0, column=2, padx=5, pady=5)

        # Parameters
        ttk.Label(root, text="Root Path:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.rootpath_entry = ttk.Entry(root, textvariable=self.rootpath_var, width=50)
        self.rootpath_entry.grid(row=1, column=1, sticky=tk.EW, padx=5, pady=5)
        self.rootpath_browse_button = ttk.Button(root, text="Browse", command=self.browse_rootpath)
        self.rootpath_browse_button.grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(root, text="BIN File:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.bin_entry = ttk.Entry(root, textvariable=self.bin_var, width=50)
        self.bin_entry.grid(row=2, column=1, sticky=tk.EW, padx=5, pady=5)
        self.bin_browse_button = ttk.Button(root, text="Browse", command=self.browse_bin)
        self.bin_browse_button.grid(row=2, column=2, padx=5, pady=5)

        ttk.Label(root, text="IC Type:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=5)
        ic_choices = ["MX25U51245G"] # Add more IC options if needed
        self.ic_combo = ttk.Combobox(root, textvariable=self.ic_var, values=ic_choices)
        self.ic_combo.grid(row=3, column=1, sticky=tk.EW, padx=5, pady=5)

        # Device Selection
        ttk.Label(root, text="Device:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=5)
        self.device_combo = ttk.Combobox(root, textvariable=self.device_var, values=self.device_ids)
        self.device_combo.grid(row=4, column=1, sticky=tk.EW, padx=5, pady=5)

        # Programming Mode
        ttk.Label(root, text="Programming Mode:").grid(row=5, column=0, sticky=tk.W, padx=5, pady=5)
        modes = [("-z", "Erase and Program"), ("-v -e -p", "Erase, Program, Verify")]
        self.mode_combo = ttk.Combobox(root, textvariable=self.programming_mode_var, values=[m[0] for m in modes])
        self.mode_combo.grid(row=5, column=1, sticky=tk.EW, padx=5, pady=5)

        # Buttons
        self.program_button = ttk.Button(root, text="Program", command=self.run_dediprog)
        self.program_button.grid(row=6, column=0, columnspan=3, pady=10)

        # Configuration Management
        config_frame = ttk.LabelFrame(root, text="Configurations")
        config_frame.grid(row=7, column=0, columnspan=3, padx=5, pady=5, sticky=tk.EW)

        self.save_button = ttk.Button(config_frame, text="Save Config", command=self.save_config)
        self.save_button.grid(row=0, column=0, padx=5, pady=5)

        self.load_button = ttk.Button(config_frame, text="Load Config", command=self.load_config)
        self.load_button.grid(row=0, column=1, padx=5, pady=5)

        self.config_list_var = tk.StringVar(value=[])
        self.config_listbox = tk.Listbox(config_frame, listvariable=self.config_list_var, height=5)
        self.config_listbox.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky=tk.EW)

        self.delete_button = ttk.Button(config_frame, text="Delete Config", command=self.delete_config)
        self.delete_button.grid(row=2, column=0, columnspan=2, padx=5, pady=5)

        self.load_configurations_list()

        # Menu
        menubar = tk.Menu(root)
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Save Configuration", command=self.save_config)
        filemenu.add_command(label="Load Configuration", command=self.load_config)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=root.quit)
        menubar.add_cascade(label="File", menu=filemenu)

        root.config(menu=menubar)
        root.columnconfigure(1, weight=1)

    def get_device_ids(self):
        dpcmd_path = self.dpcmd_path.get()
        try:
            process = subprocess.run([dpcmd_path, "--list-device-id", "0"], capture_output=True, text=True, check=True)
            output = process.stdout
            device_ids = []
            found_engine_version = False
            for line in output.splitlines():
                if "Engine Version:" in line:
                    found_engine_version = True
                elif found_engine_version and line.startswith("1.\t"):
                    device_id = line.split("1.\t")[1].strip()
                    device_ids.append(device_id)
                    break  # Assuming only one device ID is listed this way
            return device_ids
        except FileNotFoundError:
            messagebox.showerror("Error", "dpcmd not found. Make sure the path is correct.")
            return []
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error listing devices: {e}")
            return []

    def browse_dpcmd(self):
        filepath = filedialog.askopenfilename(title="Select dpcmd executable", filetypes=(("dpcmd", "*dpcmd*"), ("all files", "*.*")))
        if filepath:
            self.dpcmd_path.set(filepath)
            self.device_ids = self.get_device_ids()
            self.device_combo['values'] = self.device_ids
            if self.device_ids:
                self.device_var.set(self.device_ids[0])

    def browse_rootpath(self):
        dirpath = filedialog.askdirectory(title="Select Root Path")
        if dirpath:
            self.rootpath_var.set(dirpath + "/")

    def browse_bin(self):
        filepath = filedialog.askopenfilename(title="Select BIN File", filetypes=(("BIN files", "*.bin"), ("all files", "*.*")))
        if filepath:
            self.bin_var.set(os.path.basename(filepath))
            self.rootpath_var.set(os.path.dirname(filepath) + "/")

    def run_dediprog(self):
        dpcmd = self.dpcmd_path.get()
        ic = self.ic_var.get()
        bin_path = os.path.join(self.rootpath_var.get(), self.bin_var.get())
        device_index = self.device_combo.current() # Get the index of the selected item
        selected_device = self.device_var.get()
        programming_mode = self.programming_mode_var.get().split()

        command = [dpcmd, '-d', ic, '-s']
        command.extend(programming_mode)
        command.append(bin_path)

        if device_index >= 0 and self.device_ids: # Check if a device is selected
            command.extend(['--device-SN',selected_device])

        try:
            # 使用 subprocess.Popen 並設定 creationflags
            if os.name == 'nt':  # Windows 系統
                subprocess.Popen(
                    command,
                    creationflags=subprocess.CREATE_NEW_CONSOLE  # 創建新的控制台窗口
                )
            else:  # Unix/Linux/Mac 系統
                subprocess.Popen(
                    command,
                    start_new_session=True  # 創建新的會話
                )
        except FileNotFoundError:
            messagebox.showerror("Error", "dpcmd not found. Make sure the path is correct.")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {e}")

    def save_config(self):
        config_name = simpledialog.askstring("Save Configuration", "Enter configuration name:")
        if config_name:
            config = {
                "dpcmd_path": self.dpcmd_path.get(),
                "rootpath": self.rootpath_var.get(),
                "bin": self.bin_var.get(),
                "ic": self.ic_var.get(),
                "device": self.device_var.get(),
                "programming_mode": self.programming_mode_var.get()
            }
            try:
                with open("dediprog_configs.json", "r+") as f:
                    try:
                        data = json.load(f)
                    except json.JSONDecodeError:
                        data = {}
                    data[config_name] = config
                    f.seek(0)
                    json.dump(data, f, indent=4)
            except FileNotFoundError:
                with open("dediprog_configs.json", "w") as f:
                    json.dump({config_name: config}, f, indent=4)
            self.load_configurations_list()

    def load_config(self):
        selected_config = self.config_listbox.get(tk.ANCHOR)
        if selected_config:
            try:
                with open("dediprog_configs.json", "r") as f:
                    data = json.load(f)
                    config = data.get(selected_config)
                    if config:
                        self.dpcmd_path.set(config["dpcmd_path"])
                        self.rootpath_var.set(config["rootpath"])
                        self.bin_var.set(config["bin"])
                        self.ic_var.set(config["ic"])
                        self.device_var.set(config["device"])
                        self.programming_mode_var.set(config["programming_mode"])
                    else:
                        messagebox.showerror("Error", f"Configuration '{selected_config}' not found.")
            except FileNotFoundError:
                messagebox.showerror("Error", "Configuration file not found.")
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Error reading configuration file.")

    def load_configurations_list(self):
        try:
            with open("dediprog_configs.json", "r") as f:
                data = json.load(f)
                self.config_list_var.set(list(data.keys()))
        except FileNotFoundError:
            self.config_list_var.set([])
        except json.JSONDecodeError:
            self.config_list_var.set([])

    def delete_config(self):
        selected_config = self.config_listbox.get(tk.ANCHOR)
        if selected_config:
            if messagebox.askyesno("Delete Configuration", f"Are you sure you want to delete '{selected_config}'?"):
                try:
                    with open("dediprog_configs.json", "r+") as f:
                        data = json.load(f)
                        if selected_config in data:
                            del data[selected_config]
                            f.seek(0)
                            f.truncate()
                            json.dump(data, f, indent=4)
                            self.load_configurations_list()
                        else:
                            messagebox.showerror("Error", f"Configuration '{selected_config}' not found.")
                except FileNotFoundError:
                    messagebox.showerror("Error", "Configuration file not found.")
                except json.JSONDecodeError:
                    messagebox.showerror("Error", "Error reading configuration file.")

if __name__ == "__main__":
    root = tk.Tk()
    gui = DediProgGUI(root)
    root.mainloop()