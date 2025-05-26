from socket import *
import pickle
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import ttkthemes
import time

class QuizClient:
    def __init__(self, root):
        self.root = root
        self.root.title("Online Quiz System")
        self.root.geometry("800x600")
        self.root.resizable(False, False)

        # Apply modern theme
        self.style = ttkthemes.ThemedStyle(self.root)
        self.style.set_theme("arc")

        # Add logo frame in top left corner
        # self.logo_frame = ttk.Frame(self.root, width=100, height=100)
        # self.logo_frame.place(x=10, y=10)
        # # You can add your logo image here using:
        # # self.logo_image = tk.PhotoImage(file="C:\Users\hanyo\Downloads\Networks_project-main\Networks_project-main\logo_imag.png")
        # # logo_label = ttk.Label(self.logo_frame, image=self.logo_image)
        # # logo_label.pack()

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.server_ip = "127.0.0.1"
        self.server_port = 12000
        self.quiz = []
        self.answers = []
        self.current_question = 0
        self.time_left = 300  # 5 minutes in seconds

        self.create_login_screen()

    def create_login_screen(self):
        self.clear_window()

        # Recreate logo frame after clearing window
        # self.logo_frame = ttk.Frame(self.root, width=100, height=100)
        # self.logo_frame.place(x=10, y=10)
        # # Uncomment and modify these lines to add your logo
        # # self.logo_image = tk.PhotoImage(file="C:\Users\hanyo\Downloads\Networks_project-main\Networks_project-main\logo_imag.png")
        # # logo_label = ttk.Label(self.logo_frame, image=self.logo_image)
        # # logo_label.pack()

        # Create a modern container frame
        container = ttk.Frame(self.root)
        container.place(relx=0.5, rely=0.5, anchor="center")
        
        # Create a modern card-like frame
        frame = ttk.Frame(container)
        frame.pack(padx=30, pady=30)
        
        # Add shadow effect and rounded corners using canvas
        canvas = tk.Canvas(frame, width=400, height=500, bg='white', highlightthickness=0)
        canvas.pack()
        
        # Modern login content
        title_label = ttk.Label(frame, text="Online Quiz System", font=("Helvetica", 24, "bold"))
        title_label.place(relx=0.5, rely=0.1, anchor="center")

        # Username container
        username_container = ttk.Frame(frame)
        username_container.place(relx=0.5, rely=0.3, anchor="center")
        
        username_label = ttk.Label(username_container, text="Username", font=("Helvetica", 12))
        username_label.pack()
        
        self.username_entry = ttk.Entry(username_container, font=("Helvetica", 12), width=30)
        self.username_entry.pack(pady=5)
        self.username_entry.configure(style='Modern.TEntry')

        # Password container
        password_container = ttk.Frame(frame)
        password_container.place(relx=0.5, rely=0.5, anchor="center")
        
        password_label = ttk.Label(password_container, text="Password", font=("Helvetica", 12))
        password_label.pack()
        
        self.password_entry = ttk.Entry(password_container, show="•", font=("Helvetica", 12), width=30)
        self.password_entry.pack(pady=5)
        self.password_entry.configure(style='Modern.TEntry')

        # Regular button (not modern styled)
        login_button = tk.Button(frame, text="Login", command=self.handle_login,
                               font=("Helvetica", 12), bg="#5275E6", fg="white",
                               relief="raised", width=20, height=1)
        login_button.place(relx=0.5, rely=0.7, anchor="center")

    def show_quiz_screen(self):
        self.clear_window()

        # Recreate logo frame after clearing window
        # self.logo_frame = ttk.Frame(self.root, width=100, height=100)
        # self.logo_frame.place(x=10, y=10)
        # # Uncomment and modify these lines to add your logo
        # # self.logo_image = tk.PhotoImage(file="C:\Users\hanyo\Downloads\Networks_project-main\Networks_project-main\logo_imag.png")
        # # logo_label = ttk.Label(self.logo_frame, image=self.logo_image)
        # # logo_label.pack()

        # Create main container
        main_frame = ttk.Frame(self.root, style='Card.TFrame')
        main_frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Add timer label
        self.timer_label = ttk.Label(main_frame, text="Time left: 5:00", font=("Helvetica", 14))
        self.timer_label.pack(pady=10)
        self.update_timer()

        if self.current_question < len(self.quiz):
            question_data = self.quiz[self.current_question]
            question_text = f"Question {self.current_question + 1} of {len(self.quiz)}"
            
            # Progress bar
            progress = ttk.Progressbar(main_frame, length=300, mode='determinate')
            progress['value'] = (self.current_question + 1) / len(self.quiz) * 100
            progress.pack(pady=10)

            ttk.Label(main_frame, text=question_text, font=("Helvetica", 14, "bold")).pack(pady=10)
            ttk.Label(main_frame, text=question_data[0], font=("Helvetica", 12), wraplength=600).pack(pady=10)

            self.selected_answer = tk.IntVar(value=-1)
            for i, choice in enumerate(question_data[1]):
                ttk.Radiobutton(main_frame, text=choice, variable=self.selected_answer, 
                               value=i, style='TRadiobutton').pack(anchor="w", padx=40, pady=5)

            button_text = "Next" if self.current_question < len(self.quiz) - 1 else "Submit"
            ttk.Button(main_frame, text=button_text, command=self.next_question, 
                      style='Accent.TButton').pack(pady=20)

    def update_timer(self):
        if hasattr(self, 'start_time') == False:
            self.start_time = time.time()
            self.time_left = 300  # 5 minutes in seconds
            
        elapsed_time = int(time.time() - self.start_time)
        self.time_left = max(300 - elapsed_time, 0)
        
        if self.time_left > 0:
            minutes = self.time_left // 60
            seconds = self.time_left % 60
            self.timer_label.config(text=f"Time left: {minutes}:{seconds:02d}")
            self.root.after(1000, self.update_timer)
        else:
            messagebox.showwarning("Time's up!", "Your time has expired!")
            self.submit_quiz()
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

            serialized_quiz = self.client_socket.recv(4096)
            self.quiz = pickle.loads(serialized_quiz)
            self.answers = [None] * len(self.quiz)
            self.current_question = 0
            self.show_quiz_screen()

        except Exception as e:
            messagebox.showerror("Error", f"Connection failed: {e}")
            self.client_socket.close()

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
            
            # Recreate logo frame after clearing window
            # self.logo_frame = ttk.Frame(self.root, width=100, height=100)
            # self.logo_frame.place(x=10, y=10)
            # # Uncomment and modify these lines to add your logo
            # # self.logo_image = tk.PhotoImage(file="path_to_your_logo.png")
            # # logo_label = ttk.Label(self.logo_frame, image=self.logo_image)
            # # logo_label.pack()
            
            # Create results container
            results_frame = ttk.Frame(self.root, style='Card.TFrame')
            results_frame.pack(expand=True, fill='both', padx=40, pady=40)

            ttk.Label(results_frame, text="Quiz Results", font=("Helvetica", 24, "bold")).pack(pady=20)
            ttk.Label(results_frame, text=result, font=("Helvetica", 14)).pack(pady=10)
            ttk.Label(results_frame, text="Scoreboard", font=("Helvetica", 16, "bold")).pack(pady=10)
            
            # Create scrollable scoreboard
            scoreboard_frame = ttk.Frame(results_frame)
            scoreboard_frame.pack(fill='both', expand=True, pady=10)
            
            ttk.Label(scoreboard_frame, text=scoreboard, font=("Helvetica", 12), 
                     wraplength=600).pack(pady=10)
            
            ttk.Button(results_frame, text="Exit", command=self.exit, 
                      style='Accent.TButton').pack(pady=20)

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
