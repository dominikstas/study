import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class NoteManagerApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Subject-based Note Manager")
        self.master.geometry("800x600")

        self.create_db()
        self.create_widgets()
        self.load_subjects()

    def create_db(self):
        self.conn = sqlite3.connect("notes.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS subjects
                              (id INTEGER PRIMARY KEY, name TEXT UNIQUE)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS notes
                              (id INTEGER PRIMARY KEY, subject_id INTEGER, content TEXT,
                               FOREIGN KEY (subject_id) REFERENCES subjects(id))''')
        self.conn.commit()

    def create_widgets(self):
        # Left frame for subjects
        left_frame = ttk.Frame(self.master, padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Subject list
        self.subject_listbox = tk.Listbox(left_frame, width=30)
        self.subject_listbox.pack(fill=tk.BOTH, expand=True)
        self.subject_listbox.bind('<<ListboxSelect>>', self.load_notes)

        # Subject entry and buttons
        subject_entry_frame = ttk.Frame(left_frame)
        subject_entry_frame.pack(fill=tk.X, pady=5)

        self.subject_entry = ttk.Entry(subject_entry_frame)
        self.subject_entry.pack(side=tk.LEFT, expand=True, fill=tk.X)

        ttk.Button(subject_entry_frame, text="Add", command=self.add_subject).pack(side=tk.LEFT)
        ttk.Button(subject_entry_frame, text="Remove", command=self.remove_subject).pack(side=tk.LEFT)

        # Right frame for notes
        right_frame = ttk.Frame(self.master, padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Note text area
        self.note_text = tk.Text(right_frame, wrap=tk.WORD)
        self.note_text.pack(fill=tk.BOTH, expand=True)

        # Note buttons
        note_button_frame = ttk.Frame(right_frame)
        note_button_frame.pack(fill=tk.X, pady=5)

        ttk.Button(note_button_frame, text="Save Note", command=self.save_note).pack(side=tk.LEFT)
        ttk.Button(note_button_frame, text="Clear Note", command=self.clear_note).pack(side=tk.LEFT)
        ttk.Button(note_button_frame, text="Generate Flashcards", command=self.generate_flashcards).pack(side=tk.RIGHT)

    def load_subjects(self):
        self.subject_listbox.delete(0, tk.END)
        self.cursor.execute("SELECT name FROM subjects ORDER BY name")
        for subject in self.cursor.fetchall():
            self.subject_listbox.insert(tk.END, subject[0])

    def add_subject(self):
        subject = self.subject_entry.get().strip()
        if subject:
            try:
                self.cursor.execute("INSERT INTO subjects (name) VALUES (?)", (subject,))
                self.conn.commit()
                self.load_subjects()
                self.subject_entry.delete(0, tk.END)
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "Subject already exists!")
        else:
            messagebox.showerror("Error", "Subject name cannot be empty!")

    def remove_subject(self):
        selection = self.subject_listbox.curselection()
        if selection:
            subject = self.subject_listbox.get(selection[0])
            confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{subject}' and all its notes?")
            if confirm:
                self.cursor.execute("DELETE FROM notes WHERE subject_id = (SELECT id FROM subjects WHERE name = ?)", (subject,))
                self.cursor.execute("DELETE FROM subjects WHERE name = ?", (subject,))
                self.conn.commit()
                self.load_subjects()
                self.clear_note()
        else:
            messagebox.showerror("Error", "Please select a subject to remove!")

    def load_notes(self, event):
        selection = self.subject_listbox.curselection()
        if selection:
            subject = self.subject_listbox.get(selection[0])
            self.cursor.execute("SELECT content FROM notes WHERE subject_id = (SELECT id FROM subjects WHERE name = ?)", (subject,))
            note = self.cursor.fetchone()
            self.note_text.delete(1.0, tk.END)
            if note:
                self.note_text.insert(tk.END, note[0])

    def save_note(self):
        selection = self.subject_listbox.curselection()
        if selection:
            subject = self.subject_listbox.get(selection[0])
            content = self.note_text.get(1.0, tk.END).strip()
            self.cursor.execute("INSERT OR REPLACE INTO notes (subject_id, content) VALUES ((SELECT id FROM subjects WHERE name = ?), ?)", (subject, content))
            self.conn.commit()
            messagebox.showinfo("Success", "Note saved successfully!")
        else:
            messagebox.showerror("Error", "Please select a subject to save the note!")

    def clear_note(self):
        self.note_text.delete(1.0, tk.END)

    def generate_flashcards(self):
        messagebox.showinfo("Future Feature", "Flashcard generation will be implemented in a future update!")

    def __del__(self):
        self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = NoteManagerApp(root)
    root.mainloop()