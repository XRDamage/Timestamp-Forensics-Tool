import os
import time
import subprocess
import winreg
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk  
from datetime import datetime

class Timestamp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Timestamp Forensics Tool")
        self.geometry("700x500")

        # Added Left side panel
        self.left_frame = ctk.CTkFrame(self, width=150, height=500)  
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.left_frame.pack_propagate(False)  

        # Added button to select file
        self.file = ctk.CTkButton(self.left_frame, text="Select File", command=self.selectFile)
        self.file.pack(pady=(10, 5), anchor="n")  

        # Added a centering frame
        self.center_frame = ctk.CTkFrame(self.left_frame, fg_color="transparent")
        self.center_frame.pack(expand=True)  

        # Added logos/images for file selection
        self.icon_image = ctk.CTkImage(Image.open("empty_file.png"), size=(50, 50))  
        self.icon_label = ctk.CTkLabel(self.center_frame, image=self.icon_image, text="")  
        self.icon_label.pack(pady=(10, 5))

        # Added label to show file name
        self.file_name_label = ctk.CTkLabel(self.center_frame, text="No file selected")
        self.file_name_label.pack(pady=(5, 10))  

        # Added button to remove file
        self.remove_file_button = ctk.CTkButton(self.left_frame, text="Remove File", command=self.removeFile)
        self.remove_file_button.pack(side="bottom", pady=10)

        # Added a textbox to view the results and properties
        self.properties_listbox = ctk.CTkTextbox(self, width=200, height=400)  
        self.properties_listbox.pack(side="top", fill="both", expand=True, padx=10, pady=(10, 10))  
        self.properties_listbox.configure(state="disabled")  

        # Added button to scan the file
        self.scan = ctk.CTkButton(self, text="Scan File", command=self.scanFile, height=40)  
        self.scan.pack(side="bottom", pady=(0, 20), padx=10, fill="x")  

        self.selected_file = None  
        self.file_metadata = None  

    def selectFile(self):
        # Selecting the file
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            self.selected_file = file_path
            file_name = self.selected_file.split("/")[-1]  
            self.file_name_label.configure(text=file_name)  
            
            self.icon_image = ctk.CTkImage(Image.open("file_selected.png"), size=(50, 50))
            self.icon_label.configure(image=self.icon_image)  
            
            print(f"Selected file: {self.selected_file}")
            self.show_file_properties(self.selected_file)
    
    def show_file_properties(self, file_path):
        self.file_metadata = os.stat(file_path)

        creation_time = time.ctime(self.file_metadata.st_birthtime)
        modification_time = time.ctime(self.file_metadata.st_mtime)
        access_time = time.ctime(self.file_metadata.st_atime)

        # Listing the file properties
        self.properties_listbox.configure(state="normal")  
        self.properties_listbox.delete(1.0, ctk.END)  
        self.properties_listbox.insert(ctk.END, f"File: {file_path}\n")
        self.properties_listbox.insert(ctk.END, f"Creation Time: {creation_time}\n")
        self.properties_listbox.insert(ctk.END, f"Modification Time: {modification_time}\n")
        self.properties_listbox.insert(ctk.END, f"Access Time: {access_time}\n")
        self.properties_listbox.configure(state="disabled")  

    def scanFile(self):
        # Performing the toolmark scan
        if self.selected_file and self.file_metadata:
            print(f"Scanning File: {self.selected_file}")

            # Check for timestamp alterations
            issues = self.check_for_timestomp(self.selected_file)
        
            # Check for Timestomp executable presence
            timestomp_check = self.check_timestomp_executable()
        
            # Check for suspicious registry entries
            registry_entries = self.check_registry_entries()  # This should return a list of entries or None

            self.properties_listbox.configure(state="normal")
            self.properties_listbox.insert(ctk.END, "\nScan Results:\n")
            self.properties_listbox.insert(ctk.END, "-----------------\n")

            # Display timestamp issues
            if issues:
                self.properties_listbox.insert(ctk.END, "Potential Issues Detected:\n")
                for issue in issues:
                    self.properties_listbox.insert(ctk.END, f"- {issue}\n")
            else:
                self.properties_listbox.insert(ctk.END, "No issues detected for timestamps.\n")

            # Display Timestomp executable check results
            if timestomp_check:
                self.properties_listbox.insert(ctk.END, "Timestomp executable found on the system.\n")
            else:
                self.properties_listbox.insert(ctk.END, "No Timestomp executable found.\n")

            # Display registry check results
            if registry_entries:  # Ensure this captures entries correctly
                for entry in registry_entries:
                    self.properties_listbox.insert(ctk.END, f"Registry entry found: {entry}\n")
            else:
                self.properties_listbox.insert(ctk.END, "No suspicious registry entries found.\n")

            self.properties_listbox.configure(state="disabled")
        else:
            print("No file selected or file metadata not available for scanning.")

    def check_for_timestomp(self, file_path):
        # Checking for variability of timestamps
        issues = []
        try:
            if self.file_metadata.st_mtime < self.file_metadata.st_birthtime:
                issues.append("Warning: Modification time is earlier than creation time!")
            if self.file_metadata.st_atime < self.file_metadata.st_birthtime:
                issues.append("Warning: Access time is earlier than creation time!")

            if self.file_metadata.st_birthtime == self.file_metadata.st_mtime == self.file_metadata.st_atime:
                issues.append("Potential Timestomp Detected: All timestamps are identical!")

            current_time = time.time()
            if self.file_metadata.st_birthtime > current_time or self.file_metadata.st_mtime > current_time or self.file_metadata.st_atime > current_time:
                issues.append("Suspicious Timestamps: Future dates detected!")
            if self.file_metadata.st_birthtime < 0 or self.file_metadata.st_mtime < 0 or self.file_metadata.st_atime < 0:
                issues.append("Suspicious Timestamps: Negative timestamp values detected!")
        except Exception as e:
            issues.append(f"Error checking timestamps: {str(e)}")

        return issues

    def check_timestomp_executable(self):
        # Scanning for Timestomp Executable
        common_locations = [
            "C:\\Windows\\System32\\Timestomp.exe",
            "C:\\Users\\xavie\\Downloads\\Timestomp.exe",  
        ]
        for location in common_locations:
            if os.path.exists(location):
                print(f"Timestomp executable found at: {location}")
                return True
        return False

    def check_registry_entries(self):
        # Checking Windows Registry for Timestamp manipulation
        entries_found = []
        try:
            registry_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, registry_path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            if "Timestomp" in display_name:
                                entries_found.append(display_name)
                        except FileNotFoundError:
                            continue
        except Exception as e:
            print(f"Error accessing the registry: {e}")

        return entries_found

    def removeFile(self):
        # Remove file from program
        if self.selected_file:
            self.selected_file = None
            self.file_name_label.configure(text="No file selected")
            
            self.icon_image = ctk.CTkImage(Image.open("empty_file.png"), size=(50, 50))
            self.icon_label.configure(image=self.icon_image)  
            
            self.properties_listbox.configure(state="normal")
            self.properties_listbox.delete(1.0, ctk.END)
            self.properties_listbox.configure(state="disabled")
            print("File removed.")
        else:
            print("No file to remove.")

app = Timestamp()
app.mainloop()
