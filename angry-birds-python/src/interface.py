import tkinter as tk

def toggle_fullscreen(event=None):
    root.attributes('-fullscreen', not root.attributes('-fullscreen'))

def logo1_clicked(event):
    import main as angry_birds
    angry_birds.game()

def logo2_clicked(event):
    print("Logo 2 clicked")

root = tk.Tk()

canvas = tk.Canvas(root, bg="white")
canvas.pack(fill=tk.BOTH, expand=True)

# Load and place your content here

# Load logo images
dnt_logo_path = "/home/radhika/VirtualMouse_openCV/DNT_logo.png"
logo1_path = "/home/radhika/VirtualMouse_openCV/angry_birds.png"
logo2_path = "/home/radhika/VirtualMouse_openCV/hill_climb_racing.png"

dnt_logo = tk.PhotoImage(file=dnt_logo_path)
logo1 = tk.PhotoImage(file=logo1_path)
logo2 = tk.PhotoImage(file=logo2_path)

# Create labels for logos
dnt_logo_label = tk.Label(canvas, image=dnt_logo, bg="white")
logo1_label = tk.Label(canvas, image=logo1, bg="white")
logo2_label = tk.Label(canvas, image=logo2, bg="white")

# Calculate the spacing between logos
spacing = 400  # You can adjust this value as needed

# Place the "DNT" logo at the top center
dnt_logo_label.place(relx=0.5, rely=0.1, anchor=tk.N)

# Place logo1 and logo2 side by side without spacing
logo1_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER, x=-logo1.width()//2 - spacing // 2)
logo2_label.place(relx=0.5, rely=0.5, anchor=tk.CENTER, x=logo2.width()//2 + spacing// 2)

# Bind click events to the logo labels
logo1_label.bind("<Button-1>", logo1_clicked)
logo2_label.bind("<Button-1>", logo2_clicked)

exit_button = tk.Button(root, text="Exit Full Screen", command=toggle_fullscreen)
exit_button.pack()

root.bind("<Escape>", toggle_fullscreen)
root.mainloop()
