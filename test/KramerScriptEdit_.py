import tkinter as tk
from tkinter import ttk, messagebox, filedialog

class TestStep:
    def __init__(self, line_number, name, limits, unit, delay, repeat, critical, comments="", other_lines=""):
        self.line_number = line_number
        self.name = name.strip()
        self.limits = limits.strip()
        self.unit = unit.strip()
        self.delay = delay.strip()
        self.repeat = repeat.strip()
        self.critical = critical.strip()
        self.comments = comments.strip()
        self.other_lines = other_lines.strip()

    def __str__(self):
         return f":{self.line_number}. {self.name}"
    def __repr__(self):
         return f":{self.line_number}. {self.name}"

def parse_test_file(filename):
    test_steps = []
    try:
        with open(filename, 'r') as f:
            lines = f.readlines()
            i = 0
            while i < len(lines):
                line = lines[i].strip()
                if line.startswith('#'):
                  if test_steps:
                    test_steps[-1].comments += line + "\n"
                  else:
                    test_steps.append(TestStep("","","","","","","",line + "\n"))
                  i+=1
                  continue
                if line.startswith(':'):
                    try:
                      parts = line.split('.', 1)
                      line_number = parts[0].replace(':','')
                      name = parts[1]
                      i+=1
                      limits = ""
                      unit = ""
                      repeat = ""
                      delay = ""
                      critical = ""
                      comments = ""
                      other_lines = ""

                      while i < len(lines):
                         current_line = lines[i].strip()
                         if current_line.startswith('#'):
                            comments += current_line + "\n"
                            i+=1
                            continue
                         if current_line.startswith("Limits"):
                           parts = current_line.split("Limits ",1)
                           limits = parts[1] if len(parts) > 1 and parts[1] and parts[1].strip() else ""
                         elif current_line.startswith("Unit"):
                           parts = current_line.split("Unit ",1)
                           unit = parts[1] if len(parts) > 1 and parts[1] and parts[1].strip() else ""
                         elif current_line.startswith("Repeat"):
                           parts = current_line.split("Repeat ",1)
                           repeat = parts[1] if len(parts) > 1 and parts[1] and parts[1].strip() else ""
                         elif current_line.startswith("Delay"):
                           parts = current_line.split("Delay ",1)
                           delay = parts[1] if len(parts) > 1 and parts[1] and parts[1].strip() else ""
                         elif current_line.startswith("Critical"):
                           parts = current_line.split("Critical",1)     
                           critical = parts[1].strip()
                           while i+1 < len(lines) and not lines[i+1].strip().startswith(':') and not lines[i+1].strip().startswith("Limits") and not lines[i+1].strip().startswith("Unit") and not lines[i+1].strip().startswith("Repeat") and not lines[i+1].strip().startswith("Critical") and not lines[i+1].strip().startswith("#"):
                            i+=1
                            critical = critical + "\n" +lines[i].replace("\t","    ") # replace tab with 4 space for better view
                           break
                         elif not current_line.startswith(":") :
                             other_lines += current_line + "\n"
                             i+=1
                         else:
                           break
                      test_steps.append(TestStep(line_number, name, limits, unit, delay, repeat, critical, comments,other_lines))
                    except Exception as e:
                        messagebox.showerror("Parsing Error", f"Error parsing line {line}: {e}")
                        test_steps.append(TestStep("","","","","","","","", line + "\n"))
                        i+=1
                        continue
                else:
                   if test_steps:
                    test_steps[-1].other_lines += line + "\n"
                   else:
                    test_steps.append(TestStep("","","","","","","", "",line + "\n"))
                   i+=1
    except FileNotFoundError:
        messagebox.showerror("File Not Found", f"The file '{filename}' was not found.")
        return None
    return test_steps

def save_test_file(filename, test_steps):
    try:
      with open(filename, 'w') as f:
        for step in test_steps:
            if step.comments:
                f.write(step.comments)
            if step.other_lines:
                f.write(step.other_lines)
            if step.line_number:
               f.write(f":{step.line_number}. {step.name}\n")
               f.write(f"Limits {step.limits}\n")
               f.write(f"Unit {step.unit}\n")
               f.write(f"Delay {step.delay}\n")
               f.write(f"Repeat {step.repeat}\n")
               f.write(f"Critical{step.critical}\n")
            f.write("\n")
    except Exception as e:
        messagebox.showerror("Error Saving File", f"Error saving file: {e}")

class TestEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Test Procedure Editor")

        self.test_steps = []
        self.filename = None

        self.listbox = tk.Listbox(root, width=100, height=20)
        self.listbox.pack(pady=10)

        self.add_button = ttk.Button(root, text="Add Step", command=self.add_test_step)
        self.add_button.pack(side=tk.LEFT, padx=5)

        self.delete_button = ttk.Button(root, text="Delete Step", command=self.delete_test_step)
        self.delete_button.pack(side=tk.LEFT, padx=5)

        self.up_button = ttk.Button(root, text="Move Up", command=self.move_up)
        self.up_button.pack(side=tk.LEFT, padx=5)

        self.down_button = ttk.Button(root, text="Move Down", command=self.move_down)
        self.down_button.pack(side=tk.LEFT, padx=5)

        self.edit_frame = ttk.LabelFrame(root, text="Edit Step Details")
        self.edit_frame.pack(pady=10, padx=10, fill=tk.X)

        ttk.Label(self.edit_frame, text="Line Number:").grid(row=0, column=0, sticky=tk.W)
        self.line_number_entry = ttk.Entry(self.edit_frame, width=50)
        self.line_number_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(self.edit_frame, text="Name:").grid(row=1, column=0, sticky=tk.W)
        self.name_entry = ttk.Entry(self.edit_frame, width=50)
        self.name_entry.grid(row=1, column=1, sticky=tk.W)
        
        ttk.Label(self.edit_frame, text="Limits:").grid(row=2, column=0, sticky=tk.W)
        self.limits_entry = ttk.Entry(self.edit_frame, width=50)
        self.limits_entry.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(self.edit_frame, text="Unit:").grid(row=3, column=0, sticky=tk.W)
        self.unit_entry = ttk.Entry(self.edit_frame, width=50)
        self.unit_entry.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(self.edit_frame, text="Delay:").grid(row=4, column=0, sticky=tk.W)
        self.delay_entry = ttk.Entry(self.edit_frame, width=50)
        self.delay_entry.grid(row=4, column=1, sticky=tk.W)

        ttk.Label(self.edit_frame, text="Repeat:").grid(row=5, column=0, sticky=tk.W)
        self.repeat_entry = ttk.Entry(self.edit_frame, width=50)
        self.repeat_entry.grid(row=5, column=1, sticky=tk.W)

        ttk.Label(self.edit_frame, text="Critical:").grid(row=6, column=0, sticky=tk.W)
        self.critical_entry = tk.Text(self.edit_frame, height=5)
        self.critical_entry.grid(row=6, column=1, sticky=tk.W)

        self.update_button = ttk.Button(self.edit_frame, text="Update Step", command=self.update_selected_step)
        self.update_button.grid(row=7, column=1, sticky=tk.E)

        self.load_button = ttk.Button(root, text="Load File", command=self.load_file)
        self.load_button.pack(side=tk.LEFT, padx=5)

        self.save_button = ttk.Button(root, text="Save File", command=self.save_file)
        self.save_button.pack(side=tk.LEFT, padx=5)


        self.listbox.bind('<<ListboxSelect>>', self.on_select)

    def load_file(self):
        self.filename = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if self.filename:
            self.test_steps = parse_test_file(self.filename)
            if self.test_steps:
                self.update_listbox()
    
    def save_file(self):
      if not self.filename:
        self.filename = filedialog.asksaveasfilename(defaultextension=".txt",filetypes=[("Text Files", "*.txt")])
      if self.filename:
        save_test_file(self.filename,self.test_steps)
        messagebox.showinfo("Success","File saved successfully!")


    def add_test_step(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add New Test Step")

        ttk.Label(add_window, text="Line Number:").grid(row=0, column=0, sticky=tk.W)
        line_number_entry = ttk.Entry(add_window)
        line_number_entry.grid(row=0, column=1, sticky=tk.W)

        ttk.Label(add_window, text="Name:").grid(row=1, column=0, sticky=tk.W)
        name_entry = ttk.Entry(add_window)
        name_entry.grid(row=1, column=1, sticky=tk.W)

        ttk.Label(add_window, text="Limits:").grid(row=2, column=0, sticky=tk.W)
        limits_entry = ttk.Entry(add_window)
        limits_entry.grid(row=2, column=1, sticky=tk.W)

        ttk.Label(add_window, text="Unit:").grid(row=3, column=0, sticky=tk.W)
        unit_entry = ttk.Entry(add_window)
        unit_entry.grid(row=3, column=1, sticky=tk.W)

        ttk.Label(add_window, text="Delay:").grid(row=4, column=0, sticky=tk.W)
        delay_entry = ttk.Entry(add_window)
        delay_entry.grid(row=4, column=1, sticky=tk.W)
        
        ttk.Label(add_window, text="Repeat:").grid(row=5, column=0, sticky=tk.W)
        repeat_entry = ttk.Entry(add_window)
        repeat_entry.grid(row=5, column=1, sticky=tk.W)

        ttk.Label(add_window, text="Critical:").grid(row=6, column=0, sticky=tk.W)
        critical_entry = tk.Text(add_window, height=5)
        critical_entry.grid(row=6, column=1, sticky=tk.W)

        def add_step_to_list():
             try:
                new_step = TestStep(
                   line_number_entry.get(),
                    name_entry.get(),
                    limits_entry.get(),
                    unit_entry.get(),
                    delay_entry.get(),
                    repeat_entry.get(),
                    critical_entry.get("1.0",tk.END)
                )
                selected_index = self.listbox.curselection()
                if selected_index:
                    self.test_steps.insert(selected_index[0], new_step)
                else:
                    self.test_steps.append(new_step)
                self.update_listbox()
                add_window.destroy()
             except Exception as e:
                 messagebox.showerror("Input Error", f"Could not create a test step with current values, please check all fields: {e}")

        add_button = ttk.Button(add_window, text="Add Step", command=add_step_to_list)
        add_button.grid(row=7, column=1, sticky=tk.E)


    def delete_test_step(self):
        selected_index = self.listbox.curselection()
        if selected_index:
            del self.test_steps[selected_index[0]]
            self.update_listbox()

    def move_up(self):
        selected_index = self.listbox.curselection()
        if selected_index and selected_index[0] > 0:
            index = selected_index[0]
            self.test_steps[index], self.test_steps[index-1] = self.test_steps[index-1], self.test_steps[index]
            self.update_listbox()
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(index-1)
            self.listbox.activate(index-1)

    def move_down(self):
        selected_index = self.listbox.curselection()
        if selected_index and selected_index[0] < len(self.test_steps) -1:
             index = selected_index[0]
             self.test_steps[index], self.test_steps[index+1] = self.test_steps[index+1], self.test_steps[index]
             self.update_listbox()
             self.listbox.selection_clear(0, tk.END)
             self.listbox.selection_set(index+1)
             self.listbox.activate(index+1)

    def update_selected_step(self):
      selected_index = self.listbox.curselection()
      if selected_index:
         try:
          selected_index = selected_index[0]
          self.test_steps[selected_index].line_number = self.line_number_entry.get()
          self.test_steps[selected_index].name = self.name_entry.get()
          self.test_steps[selected_index].limits = self.limits_entry.get()
          self.test_steps[selected_index].unit = self.unit_entry.get()
          self.test_steps[selected_index].delay = self.delay_entry.get()
          self.test_steps[selected_index].repeat = self.repeat_entry.get()
          self.test_steps[selected_index].critical = self.critical_entry.get("1.0",tk.END)
          self.update_listbox()
          messagebox.showinfo("Success","Test step updated successfully!")
         except Exception as e:
            messagebox.showerror("Update Error",f"Error updating the step {e}")

    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for step in self.test_steps:
            self.listbox.insert(tk.END, step)
    
    def on_select(self, event):
        selected_index = self.listbox.curselection()
        if selected_index:
            selected_step = self.test_steps[selected_index[0]]
            self.line_number_entry.delete(0,tk.END)
            self.line_number_entry.insert(0,selected_step.line_number)
            self.name_entry.delete(0,tk.END)
            self.name_entry.insert(0,selected_step.name)
            self.limits_entry.delete(0,tk.END)
            self.limits_entry.insert(0,selected_step.limits)
            self.unit_entry.delete(0,tk.END)
            self.unit_entry.insert(0,selected_step.unit)
            self.delay_entry.delete(0,tk.END)
            self.delay_entry.insert(0,selected_step.delay)
            self.repeat_entry.delete(0,tk.END)
            self.repeat_entry.insert(0,selected_step.repeat)
            self.critical_entry.delete("1.0",tk.END)
            self.critical_entry.insert("1.0",selected_step.critical)

if __name__ == "__main__":
    root = tk.Tk()
    editor = TestEditor(root)
    root.mainloop()