import tkinter as tk
from image_viewer import ImageViewer
from text_viewer import TextViewer
from views_adapter import ViewsAdapter
'''
def select_file():

    file_path = filedialog.askopenfilename(title="Open Image File", filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp *.ico")])
    return file_path

def display_image(image_label):
    file_path = select_file()
    image = Image.open(file_path)
    photo = ImageTk.PhotoImage(image)
    image_label.config(image=photo)
    image_label.photo = photo
    

def main():
    # Create the main window
    root = tk.Tk()
    root.title("Simple Image Viewer")
    text_widget = tk.Text(root, wrap=tk.WORD, height=15, width=35)
    
    image_label = tk.Label(root) 
    image_label.pack(padx=20, pady=20)

    open_button = tk.Button(root, text="Open Image", command=lambda: display_image(image_label))
    open_button.pack(padx=20, pady=10)
    
    status_label = tk.Label(root, text="", padx=20, pady=10)
    status_label.pack()
    root.mainloop()

'''

def main():
    root = tk.Tk()
    root.title("Text and Image Viewer")

    paned = tk.PanedWindow(root, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
    paned.pack(fill=tk.BOTH, expand=True)

    left_frame = tk.Frame(paned)
    right_frame = tk.Frame(paned)

    paned.add(left_frame, minsize=200)
    paned.add(right_frame, minsize=200)

    text_viewer = TextViewer(left_frame)
    image_viewer = ImageViewer(right_frame)

    views_adapter = ViewsAdapter(image_viewer, text_viewer)
    
    root.mainloop()

if __name__ == "__main__":
    main()