import tkinter as tk
from tkinter import ttk

class UI:
    def __init__(self, master):
        self.master = master
        self.configure_styles()
        self.flashcard_mode = False
        self.flashcards = []
        self.current_flashcard = None

    def configure_styles(self):
        style = ttk.Style()
        style.theme_use('clam')

        # Configure colors
        style.configure(".", background="#f0f0f0", foreground="#333333")
        style.configure("TFrame", background="#f0f0f0")
        style.configure("TButton", background="#4a7abc", foreground="white", font=("Arial", 10), padding=5)
        style.map("TButton", background=[('active', '#3a5a8c')])
        style.configure("TEntry", font=("Arial", 10))
        style.configure("TLabel", font=("Arial", 12), background="#f0f0f0")
        style.configure("Treeview", rowheight=25, font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        style.configure("Info.TLabel", background="#e1f5fe", foreground="#01579b", padding=10, font=("Arial", 10))

    def create_main_frame(self):
        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Subject frame (left side)
        subject_frame = ttk.Frame(main_frame, padding="5")
        subject_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False)

        subject_label = ttk.Label(subject_frame, text="Subjects")
        subject_label.pack(pady=(0, 5))

        self.subject_tree = ttk.Treeview(subject_frame, columns=("subjects",), show="tree", height=15)
        self.subject_tree.pack(fill=tk.BOTH, expand=True)

        subject_entry_frame = ttk.Frame(subject_frame)
        subject_entry_frame.pack(fill=tk.X, pady=5)

        self.subject_entry = ttk.Entry(subject_entry_frame)
        self.subject_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        add_button = ttk.Button(subject_entry_frame, text="Add")
        add_button.pack(side=tk.LEFT, padx=(5, 0))

        remove_button = ttk.Button(subject_entry_frame, text="Remove")
        remove_button.pack(side=tk.LEFT, padx=(5, 0))

        self.subject_info = ttk.Label(subject_frame, style="Info.TLabel", wraplength=200)
        self.subject_info.pack(fill=tk.X, pady=(5, 0))

        # Note frame (right side)
        note_frame = ttk.Frame(main_frame, padding="5")
        note_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        note_label = ttk.Label(note_frame, text="Notes")
        note_label.pack(pady=(0, 5))

        self.note_text = tk.Text(note_frame, wrap=tk.WORD, font=("Arial", 11))
        self.note_text.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(note_frame)
        button_frame.pack(fill=tk.X, pady=5)

        save_button = ttk.Button(button_frame, text="Save Note")
        save_button.pack(side=tk.LEFT)

        clear_button = ttk.Button(button_frame, text="Clear Note")
        clear_button.pack(side=tk.LEFT, padx=(5, 0))

        flashcard_button = ttk.Button(button_frame, text="Generate Flashcards", command=self.start_flashcard_mode)
        flashcard_button.pack(side=tk.RIGHT)

        self.note_info = ttk.Label(note_frame, style="Info.TLabel", wraplength=400)
        self.note_info.pack(fill=tk.X, pady=(5, 0))

        return (self.subject_tree, self.subject_entry, add_button, remove_button, 
                self.note_text, save_button, clear_button, flashcard_button)

    def show_subject_info(self, message):
        self.subject_info.config(text=message)
        self.master.after(3000, lambda: self.subject_info.config(text=""))

    def show_note_info(self, message):
        self.note_info.config(text=message)
        self.master.after(3000, lambda: self.note_info.config(text=""))

    def start_flashcard_mode(self):
        self.flashcard_mode = True
        self.flashcards = self.extract_flashcards()
        self.show_next_flashcard()
        self.master.bind("<Right>", self.know_flashcard)
        self.master.bind("<Left>", self.dont_know_flashcard)

    def extract_flashcards(self):
        text = self.note_text.get(1.0, tk.END).strip()
        flashcards = []
        for line in text.split("\n"):
            if " - " in line:
                term, definition = line.split(" - ", 1)
                flashcards.append((term.strip(), definition.strip()))
        return flashcards

    def show_next_flashcard(self):
        if self.flashcards:
            self.current_flashcard = self.flashcards.pop(0)
            self.note_text.delete(1.0, tk.END)
            self.note_text.insert(tk.END, self.current_flashcard[0])
        else:
            self.flashcard_mode = False
            self.note_text.delete(1.0, tk.END)
            self.note_text.insert(tk.END, "All flashcards completed!")
            self.master.unbind("<Right>")
            self.master.unbind("<Left>")

    def know_flashcard(self, event):
        self.show_next_flashcard()

    def dont_know_flashcard(self, event):
        self.flashcards.append(self.current_flashcard)
        self.show_next_flashcard()
