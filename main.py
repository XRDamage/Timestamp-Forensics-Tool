import customtkinter as ctk
from tkinter import filedialog
from PIL import Image, ImageTk  # Make sure to install Pillow

class Timestamp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Timestamp Forensics Tool")
        self.geometry("700x500")

        # Create a wider frame on the left side
        self.left_frame = ctk.CTkFrame(self, width=200)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)

        # Initial icon for no file selected
        self.icon_image = ctk.CTkImage(Image.open("empty_file.png"), size=(50, 50))  # Initial icon
        self.icon_label = ctk.CTkLabel(self.left_frame, image=self.icon_image, text="")  # Empty text
        self.icon_label.pack(pady=(10, 5))

        # Add a label to display the selected file name
        self.file_name_label = ctk.CTkLabel(self.left_frame, text="No file selected")
        self.file_name_label.pack(pady=(5, 10))  # Adjust padding

        # Select FIle button
        self.file = ctk.CTkButton(self.left_frame, text="Select File", command=self.selectFile)
        self.file.pack(pady=10)  # Increase padding to move it further down

        # Add a button to scan the file, with padding from the bottom
        self.scan = ctk.CTkButton(self.left_frame, text="Scan File", command=self.scanFile)
        self.scan.pack(side="bottom", pady=(0, 10))

        # Create a list box on the right side
        self.properties_listbox = ctk.CTkTextbox(self, width=200, height=500)
        self.properties_listbox.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        self.properties_listbox.configure(state="disabled")  # Make the textbox non-editable

        self.selected_file = None  # Variable to store the selected file path

    def selectFile(self):
        # Open a file dialog to select a file
        file_path = filedialog.askopenfilename(title="Select a File")
        if file_path:
            self.selected_file = file_path
            file_name = self.selected_file.split("/")[-1]  # Get the file name from the path
            self.file_name_label.configure(text=file_name)  # Update the label with the file name
            
            # Change the icon to selected_file.png
            self.icon_image = ctk.CTkImage(Image.open("file_selected.png"), size=(50, 50))
            self.icon_label.configure(image=self.icon_image)  # Update the icon image
            
            print(f"Selected file: {self.selected_file}")
            self.updatePropertiesList()  # Update properties when a file is selected

    def scanFile(self):
        if self.selected_file:
            print(f"Scanning File: {self.selected_file}")
        else:
            print("No file selected for scanning.")

    def updatePropertiesList(self):
        # This is where you would add text to the listbox
        self.properties_listbox.configure(state="normal")  # Temporarily enable editing
        self.properties_listbox.delete(1.0, ctk.END)  # Clear the current content
        self.properties_listbox.insert(ctk.END, f"Properties of: {self.selected_file}\n")  # Example text
        # Add more properties as needed here
        self.properties_listbox.configure(state="disabled")  # Disable editing again

# Create and run the application
app = Timestamp()
app.mainloop()
