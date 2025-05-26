import tkinter as tk
from tkinter import messagebox
from socket import *
import pickle

class QuizClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Quiz System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)
        self.root.configure(bg="#E8ECEF")

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.server_ip = "127.0.0.1"
        self.server_port = 12000
        self.quiz = []
        self.answers = []
        self.current_question = 0

        self.create_login_screen()

    def create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius=20, **kwargs):
        """Draw a rounded rectangle on the canvas using lines and arcs."""
        # Separate kwargs for line/arc (use 'fill' for color) and polygon (use 'outline')
        line_arc_kwargs = {k: v for k, v in kwargs.items() if k in ['fill', 'width']}
        polygon_kwargs = {k: v for k, v in kwargs.items() if k in ['fill', 'outline']}

        # Corners (using arcs)
        canvas.create_arc(x1, y1, x1 + 2 * radius, y1 + 2 * radius, start=90, extent=90, style="arc", **line_arc_kwargs)  # Top-left
        canvas.create_arc(x2 - 2 * radius, y1, x2, y1 + 2 * radius, start=0, extent=90, style="arc", **line_arc_kwargs)  # Top-right
        canvas.create_arc(x1, y2 - 2 * radius, x1 + 2 * radius, y2, start=180, extent=90, style="arc", **line_arc_kwargs)  # Bottom-left
        canvas.create_arc(x2 - 2 * radius, y2 - 2 * radius, x2, y2, start=270, extent=90, style="arc", **line_arc_kwargs)  # Bottom-right
        # Sides (using lines)
        canvas.create_line(x1 + radius, y1, x2 - radius, y1, **line_arc_kwargs)  # Top
        canvas.create_line(x1 + radius, y2, x2 - radius, y2, **line_arc_kwargs)  # Bottom
        canvas.create_line(x1, y1 + radius, x1, y2 - radius, **line_arc_kwargs)  # Left
        canvas.create_line(x2, y1 + radius, x2, y2 - radius, **line_arc_kwargs)  # Right
        # Fill (using a polygon to approximate the filled area)
        points = [
            x1 + radius, y1,  # Top-left corner start
            x2 - radius, y1,  # Top-right corner start
            x2, y1, x2, y1 + radius,  # Top-right corner
            x2, y2 - radius,  # Bottom-right corner start
            x2 - radius, y2,  # Bottom-right corner
            x1 + radius, y2,  # Bottom-left corner
            x1, y2, x1, y2 - radius,  # Bottom-left corner
            x1, y1 + radius,  # Top-left corner
            x1 + radius, y1  # Close the loop
        ]
        canvas.create_polygon(points, smooth=True, **polygon_kwargs)

    def create_login_screen(self):
        self.clear_window()

        # Main canvas for rounded rectangle
        canvas = tk.Canvas(self.root, bg="#E8ECEF", highlightthickness=0)
        canvas.place(relx=0.5, rely=0.5, anchor="center", width=450, height=400)

        # Draw rounded rectangle
        self.create_rounded_rectangle(canvas, 10, 10, 440, 390, radius=20, fill="#F5F6F5", outline="#CCCCCC", width=2)

        # Main frame for widgets
        frame = tk.Frame(canvas, bg="#F5F6F5", bd=0)
        frame.place(relx=0.5, rely=0.5, anchor="center", width=430, height=380)

        # Title label
        tk.Label(frame, text="Welcome to the Quiz System!", font=("Helvetica", 18, "bold"),
                 bg="#F5F6F5", fg="#333333").pack(pady=20)

        # Subtitle label
        tk.Label(frame, text="Log in to start your quiz journey", font=("Helvetica", 12),
                 bg="#F5F6F5", fg="#555555").pack(pady=10)

        # Username label and entry
        tk.Label(frame, text="Username", font=("Helvetica", 12), bg="#F5F6F5", fg="#333333").pack(pady=(10, 5))
        self.username_entry = tk.Entry(frame, font=("Helvetica", 12), relief="flat", bg="#FFFFFF",
                                      fg="#000000", insertbackground="#000000",
                                      borderwidth=1, highlightthickness=1, highlightbackground="#CCCCCC")
        self.username_entry.pack(pady=5, padx=20, fill="x", ipady=5)
        self.username_entry.insert(0, "Enter your username")
        self.username_entry.config(fg="#888888")
        self.username_entry.bind("<FocusIn>",
                                lambda event: self.clear_placeholder(self.username_entry, "Enter your username"))
        self.username_entry.bind("<FocusOut>",
                                lambda event: self.restore_placeholder(self.username_entry, "Enter your username"))

        # Password label and entry
        tk.Label(frame, text="Password", font=("Helvetica", 12), bg="#F5F6F5", fg="#333333").pack(pady=(10, 5))
        self.password_entry = tk.Entry(frame, font=("Helvetica", 12), relief="flat", bg="#FFFFFF",
                                      fg="#000000", insertbackground="#000000",
                                      borderwidth=1, highlightthickness=1, highlightbackground="#CCCCCC")
        self.password_entry.pack(pady=5, padx=20, fill="x", ipady=5)
        self.password_entry.insert(0, "Enter your password")
        self.password_entry.config(fg="#888888")
        self.password_entry.bind("<FocusIn>",
                                lambda event: self.clear_placeholder(self.password_entry, "Enter your password"))
        self.password_entry.bind("<FocusOut>",
                                lambda event: self.restore_placeholder(self.password_entry, "Enter your password"))

        # Show/hide password checkbox
        self.show_password_var = tk.BooleanVar()
        tk.Checkbutton(frame, text="Show Password", variable=self.show_password_var,
                       command=self.toggle_password, bg="#F5F6F5", fg="#333333",
                       font=("Helvetica", 10)).pack(pady=5)

        # Error message label
        self.error_label = tk.Label(frame, text="", font=("Helvetica", 10), bg="#F5F6F5", fg="#D32F2F")
        self.error_label.pack(pady=5)

        # Login button
        tk.Button(frame, text="Log In", font=("Helvetica", 12, "bold"), bg="#4A90E2", fg="white",
                  activebackground="#357ABD", activeforeground="white", relief="flat",
                  borderwidth=0, command=self.handle_login).pack(pady=15, padx=20, fill="x", ipady=8)

        # Forgot password link
        forgot_label = tk.Label(frame, text="Forgot Password?", font=("Helvetica", 10, "underline"),
                                bg="#F5F6F5", fg="#4A90E2", cursor="hand2")
        forgot_label.pack(pady=5)
        forgot_label.bind("<Button-1>", lambda e: self.forgot_password())

    def clear_placeholder(self, entry, placeholder):
        if entry.get() == placeholder:
            entry.delete(0, tk.END)
            entry.config(fg="#000000")
            if entry == self.password_entry:
                entry.config(show="*")

    def restore_placeholder(self, entry, placeholder):
        if not entry.get():
            entry.insert(0, placeholder)
            entry.config(fg="#888888")
            if entry == self.password_entry:
                entry.config(show="")

    def toggle_password(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            if self.password_entry.get() != "Enter your password":
                self.password_entry.config(show="*")

    def forgot_password(self):
        messagebox.showinfo("Forgot Password", "Please contact support to reset your password.")

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.root.configure(bg="#E8ECEF")

    def handle_login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username == "Enter your username" or password == "Enter your password" or not username or not password:
            self.error_label.config(text="Please enter both username and password")
            return

        try:
            self.client_socket.connect((self.server_ip, self.server_port))
            self.client_socket.send(pickle.dumps((username, password)))
            response = pickle.loads(self.client_socket.recv(1024))
            if "success" in response.lower():
                serialized_quiz = self.client_socket.recv(4096)
                self.quiz = pickle.loads(serialized_quiz)
                self.answers = [None] * len(self.quiz)
                self.current_question = 0
                self.show_quiz_screen()
            else:
                self.error_label.config(text=response)
        except Exception as e:
            self.error_label.config(text=f"Connection failed: {str(e)}")
            self.client_socket.close()

    def show_quiz_screen(self):
        self.clear_window()

        if self.current_question < len(self.quiz):
            # Canvas for rounded frame
            canvas = tk.Canvas(self.root, bg="#E8ECEF", highlightthickness=0)
            canvas.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)
            self.create_rounded_rectangle(canvas, 10, 10, 590, 490, radius=20, fill="#F5F6F5", outline="#CCCCCC", width=2)

            # Frame for quiz content
            frame = tk.Frame(canvas, bg="#F5F6F5", bd=0)
            frame.place(relx=0.5, rely=0.5, anchor="center", width=580, height=480)

            # Progress indicator
            tk.Label(frame, text=f"Question {self.current_question + 1} of {len(self.quiz)}",
                     font=("Helvetica", 12, "bold"), bg="#F5F6F5", fg="#333333").pack(pady=10)

            # Question
            question_data = self.quiz[self.current_question]
            question_text = f"Q{self.current_question + 1}: {question_data[0]}"
            tk.Label(frame, text=question_text, font=("Helvetica", 14, "bold"), bg="#F5F6F5",
                     fg="#333333", wraplength=500, justify="left").pack(pady=20, padx=20)

            # Answer options
            self.selected_answer = tk.IntVar(value=-1)
            for i, choice in enumerate(question_data[1]):
                rb = tk.Radiobutton(frame, text=choice, font=("Helvetica", 12), bg="#F5F6F5", fg="#333333",
                                    selectcolor="#E8ECEF", activebackground="#F5F6F5", anchor="w",
                                    variable=self.selected_answer, value=i)
                rb.pack(pady=5, padx=30, fill="x")

            # Error label for quiz
            self.quiz_error_label = tk.Label(frame, text="", font=("Helvetica", 10), bg="#F5F6F5", fg="#D32F2F")
            self.quiz_error_label.pack(pady=10)

            # Navigation frame
            navigation_frame = tk.Frame(frame, bg="#F5F6F5")
            navigation_frame.pack(pady=20)

            if self.current_question > 0:
                tk.Button(navigation_frame, text="Previous", font=("Helvetica", 12, "bold"), bg="#4A90E2",
                          fg="white", activebackground="#357ABD", activeforeground="white", relief="flat",
                          command=self.previous_question).pack(side="left", padx=10, ipady=5)

            tk.Button(navigation_frame, text="Next" if self.current_question < len(self.quiz) - 1 else "Submit",
                      font=("Helvetica", 12, "bold"), bg="#4A90E2", fg="white",
                      activebackground="#357ABD", activeforeground="white", relief="flat",
                      command=self.next_question).pack(side="left", padx=10, ipady=5)
        else:
            self.submit_quiz()

    def previous_question(self):
        self.current_question -= 1
        self.show_quiz_screen()

    def next_question(self):
        if self.selected_answer.get() == -1:
            self.quiz_error_label.config(text="Please select an answer")
            return

        self.answers[self.current_question] = self.selected_answer.get()
        self.current_question += 1
        self.show_quiz_screen()

    def submit_quiz(self):
        if messagebox.askyesno("Submit Quiz", "Are you sure you want to submit the quiz?"):
            try:
                self.client_socket.send(pickle.dumps(self.answers))
                result = pickle.loads(self.client_socket.recv(4096))
                scoreboard = pickle.loads(self.client_socket.recv(4096))

                self.clear_window()
                # Canvas for results
                canvas = tk.Canvas(self.root, bg="#E8ECEF", highlightthickness=0)
                canvas.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)
                self.create_rounded_rectangle(canvas, 10, 10, 590, 490, radius=20, fill="#F5F6F5", outline="#CCCCCC", width=2)

                # Frame for results content
                frame = tk.Frame(canvas, bg="#F5F6F5", bd=0)
                frame.place(relx=0.5, rely=0.5, anchor="center", width=580, height=480)

                tk.Label(frame, text="Quiz Results", font=("Helvetica", 16, "bold"), bg="#F5F6F5",
                         fg="#333333").pack(pady=20)
                tk.Label(frame, text=result, font=("Helvetica", 12), bg="#F5F6F5", fg="#333333",
                         wraplength=500).pack(pady=10)
                tk.Label(frame, text="Scoreboard:", font=("Helvetica", 12, "bold"), bg="#F5F6F5",
                         fg="#333333").pack(pady=10)
                tk.Label(frame, text=scoreboard, font=("Helvetica", 12), bg="#F5F6F5", fg="#333333",
                         wraplength=500).pack(pady=10)
                tk.Button(frame, text="Exit", font=("Helvetica", 12, "bold"), bg="#4A90E2", fg="white",
                          activebackground="#357ABD", activeforeground="white", relief="flat",
                          command=self.exit).pack(pady=20, padx=20, fill="x", ipady=8)

            except Exception as e:
                messagebox.showerror("Error", f"Error submitting quiz: {str(e)}")
                self.client_socket.close()

    def exit(self):
        self.client_socket.close()
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizClient(root)
    root.mainloop()
