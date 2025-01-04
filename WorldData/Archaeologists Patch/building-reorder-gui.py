import json
import tkinter as tk
from tkinter import filedialog, messagebox


class JSONReorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("JSON Reorder Tool")

        # Allow the window to be resized
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Initialize variables
        self.json_data = None
        self.json_file_path = None
        self.current_list = None
        self.current_list_name = None
        self.sub_records = None

        # GUI elements
        self.load_button = tk.Button(root, text="Load JSON File", command=self.load_json_file)
        self.load_button.pack(pady=10)

        self.listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=100, height=30)
        self.listbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.up_button = tk.Button(root, text="Move Up", command=self.move_up)
        self.up_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.down_button = tk.Button(root, text="Move Down", command=self.move_down)
        self.down_button.pack(side=tk.LEFT, padx=5, pady=5)

        self.save_button = tk.Button(root, text="Save Changes", command=self.save_changes)
        self.save_button.pack(side=tk.RIGHT, padx=5, pady=5)

    def load_json_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")]
        )
        if not file_path:
            return

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                self.json_data = json.load(file)
                self.json_file_path = file_path
                self.load_listbox()
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Failed to decode JSON file.")
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

    def load_listbox(self):
        # Populate the listbox with BuildingDataList by default
        self.listbox.delete(0, tk.END)
        if "RmbBlock" in self.json_data and "FldHeader" in self.json_data["RmbBlock"] and "BuildingDataList" in self.json_data["RmbBlock"]["FldHeader"]:
            self.current_list = self.json_data["RmbBlock"]["FldHeader"]["BuildingDataList"]
            self.sub_records = self.json_data["RmbBlock"].get("SubRecords", [])
            self.current_list_name = "BuildingDataList"
            for i, item in enumerate(self.current_list):
                faction_id = item.get("FactionId", "N/A")
                building_type = item.get("BuildingType", "N/A")
                quality = item.get("Quality", "N/A")
                self.listbox.insert(tk.END, f"Index {i}: FactionId={faction_id}, BuildingType={building_type}, Quality={quality}")
        else:
            messagebox.showinfo("Info", "BuildingDataList not found in the JSON file.")

    def move_up(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
        selected_index = selected_index[0]

        if selected_index > 0:
            # Swap BuildingDataList entries
            self.current_list[selected_index], self.current_list[selected_index - 1] = (
                self.current_list[selected_index - 1],
                self.current_list[selected_index],
            )
            # Swap SubRecords entries
            self.sub_records[selected_index], self.sub_records[selected_index - 1] = (
                self.sub_records[selected_index - 1],
                self.sub_records[selected_index],
            )
            self.refresh_listbox()
            self.listbox.select_set(selected_index - 1)

    def move_down(self):
        selected_index = self.listbox.curselection()
        if not selected_index:
            return
        selected_index = selected_index[0]

        if selected_index < len(self.current_list) - 1:
            # Swap BuildingDataList entries
            self.current_list[selected_index], self.current_list[selected_index + 1] = (
                self.current_list[selected_index + 1],
                self.current_list[selected_index],
            )
            # Swap SubRecords entries
            self.sub_records[selected_index], self.sub_records[selected_index + 1] = (
                self.sub_records[selected_index + 1],
                self.sub_records[selected_index],
            )
            self.refresh_listbox()
            self.listbox.select_set(selected_index + 1)

    def refresh_listbox(self):
        self.listbox.delete(0, tk.END)
        for i, item in enumerate(self.current_list):
            faction_id = item.get("FactionId", "N/A")
            building_type = item.get("BuildingType", "N/A")
            quality = item.get("Quality", "N/A")
            self.listbox.insert(tk.END, f"Index {i}: FactionId={faction_id}, BuildingType={building_type}, Quality={quality}")

    def save_changes(self):
        if not self.json_file_path or not self.json_data:
            messagebox.showerror("Error", "No JSON file loaded.")
            return

        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as file:
                json.dump(self.json_data, file, indent=4)
            messagebox.showinfo("Success", "Changes saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save changes: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = JSONReorderApp(root)
    root.mainloop()

