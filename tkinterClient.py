from socket import *
import pickle
import tkinter as tk
from tkinter import messagebox

class QuizClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Quiz System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.server_ip = "127.0.0.1"
        self.server_port = 12000
        self.quiz = []
        self.answers = []
        self.current_question = 0

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_window()

        # Create a frame to hold login widgets, centered in the window
        frame = tk.Frame(self.root, bg="#323132", relief="groove", borderwidth=2)
        frame.place(relx=0.5, rely=0.5, anchor="center")  # Center frame in window

        # Login widgets in the frame using pack
        tk.Label(frame, text="Online Quiz System", font=("Arial", 16, "bold"), bg="#323132").pack(pady=20)
        tk.Label(frame, text="Username:", font=("Arial", 12), bg="#323132").pack()
        self.username_entry = tk.Entry(frame, font=("Arial", 12))
        self.username_entry.pack(pady=5)
        tk.Label(frame, text="Password:", font=("Arial", 12), bg="#323132").pack()
        self.password_entry = tk.Entry(frame, show="*", font=("Arial", 12))
        self.password_entry.pack(pady=5)
        tk.Button(frame, text="Login", font=("Arial", 12), command=self.handle_login).pack(pady=20)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password")
            return

        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_socket.send(pickle.dumps((username, password)))
            response = pickle.loads(self.client_socket.recv(1024))
            messagebox.showinfo("Login", response)

            # Receive quiz
            serialized_quiz = self.client_socket.recv(4096)
            self.quiz = pickle.loads(serialized_quiz)
            self.answers = [None] * len(self.quiz)
            self.current_question = 0
            self.show_quiz_screen()

        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")
            self.client_socket.close()

    def show_quiz_screen(self):
        self.clear_window()

        if self.current_question < len(self.quiz):
            question_data = self.quiz[self.current_question]
            question_text = f"Q{self.current_question + 1}: {question_data[0]}"
            tk.Label(self.root, text=question_text, font=("Arial", 14), wraplength=500).pack(pady=20)

            self.selected_answer = tk.IntVar(value=-1)
            for i, choice in enumerate(question_data[1]):
                tk.Radiobutton(self.root, text=choice, font=("Arial", 12),
                               variable=self.selected_answer, value=i).pack(anchor="w", padx=20)

            tk.Button(self.root, text="Next" if self.current_question < len(self.quiz) - 1 else "Submit",
                      font=("Arial", 12), command=self.next_question).pack(pady=20)
        else:
            self.submit_quiz()

    def next_question(self):
        if self.selected_answer.get() == -1:
            messagebox.showerror("Error", "Please select an answer")
            return

        self.answers[self.current_question] = self.selected_answer.get()
        self.current_question += 1
        if self.current_question < len(self.quiz):
            self.show_quiz_screen()
        else:
            self.submit_quiz()

    def submit_quiz(self):
        try:
            self.client_socket.send(pickle.dumps(self.answers))
            result = pickle.loads(self.client_socket.recv(4096))
            scoreboard = pickle.loads(self.client_socket.recv(4096))

            self.clear_window()
            tk.Label(self.root, text="Quiz Results", font=("Arial", 16, "bold")).pack(pady=20)
            tk.Label(self.root, text=result, font=("Arial", 12)).pack(pady=10)
            tk.Label(self.root, text="Scoreboard:", font=("Arial", 12, "bold")).pack(pady=10)
            tk.Label(self.root, text=scoreboard, font=("Arial", 12), wraplength=500).pack(pady=10)
            tk.Button(self.root, text="Exit", font=("Arial", 12), command=self.exit).pack(pady=20)

        except Exception as e:
            messagebox.showerror("Error", f"Error submitting quiz: {e}")
            self.client_socket.close()

    def exit(self):
        self.client_socket.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizClient(root)
    root.mainloop()
