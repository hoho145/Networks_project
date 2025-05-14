from socket import *
from threading import Thread
import pickle
import random
import time

# Sample questions: each is [question, [choices], correct_answer_index]
questions = [
    ["What is 2+2?", ["1", "2", "3", "4"], 3],
    ["Which is a fruit?", ["Carrot", "Apple", "Broccoli", "Potato"], 1],
    ["What color is the sky?", ["Red", "Blue", "Green", "Yellow"], 1],
    ["How many days in a week?", ["5", "6", "7", "8"], 2],
    ["What is H2O?", ["Sugar", "Salt", "Water", "Oil"], 2],
    ["What is 5x3?", ["10", "15", "20", "25"], 1],
    ["Which planet is closest to the Sun?", ["Earth", "Mars", "Mercury", "Venus"], 2],
    ["What is the capital of France?", ["Paris", "London", "Berlin", "Madrid"], 0],
    ["How many legs does a spider have?", ["6", "8", "10", "12"], 1],
    ["What is 10-4?", ["4", "5", "6", "7"], 2]
]

def generate_quiz():
    # Pick 5 random questions
    return random.sample(questions, 5)

def grade_quiz(quiz, answers):
    score = 0
    for i, question in enumerate(quiz):
        if answers[i] == question[2]:  # Compare answer with correct_answer_index
            score += 1
    return score

def handle_client(connectionSocket, client_addr):
    print(f"New client connected: {client_addr}")
    try:
        # Generate and send quiz
        quiz = generate_quiz()
        quiz_data = pickle.dumps(quiz)
        connectionSocket.send(quiz_data)
        
        # Set 2-minute timeout for receiving answers
        connectionSocket.settimeout(120)
        serialized_answers = connectionSocket.recv(4096)
        answers = pickle.loads(serialized_answers)
        
        # Grade the quiz
        score = grade_quiz(quiz, answers)
        result = f"Your score: {score}/5"
        connectionSocket.send(pickle.dumps(result))
        
    except timeout:
        error_msg = "Time's up! Quiz not submitted in time."
        connectionSocket.send(pickle.dumps(error_msg))
    except Exception as e:
        error_msg = "Error processing quiz."
        connectionSocket.send(pickle.dumps(error_msg))
    finally:
        connectionSocket.close()
        print(f"Client {client_addr} disconnected")

# Server setup
serverIP = "127.0.0.1"
serverPort = 12000
serverSocket = socket(AF_INET, SOCK_STREAM)
serverSocket.bind((serverIP, serverPort))
serverSocket.listen(5)
print(f"Server ready at {serverIP}:{serverPort}")

while True:
    connectionSocket, client_addr = serverSocket.accept()
    # Start a new thread for each client
    client_thread = Thread(target=handle_client, args=(connectionSocket, client_addr))
    client_thread.start()