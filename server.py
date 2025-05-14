from socket import *
from threading import Thread
import pickle
import random
import time

USER_ID="users.pkl"


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

def load_users():
    try:
        with open(USER_ID, 'rb') as f:
            return pickle.load(f)
    except FileNotFoundError:
        return {}
def save_users(users):
    with open(USER_ID, 'wb') as f:
        pickle.dump(users, f)

def scoreboard():
    users = load_users()
    mx = -1
    arr=[]
    for x,y in users.items():
        
        if y['score']:
            mx1 = max(y['score'])
            if mx1 > mx:
                mx = mx1
                arr = [x]
            elif mx1 == mx:
                arr.append(x)
    if mx == -1:
        return "No one has taken the quiz yet"
    else:
        return f"Highest score is {mx} by {', '.join(arr)}"
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
        users = load_users()
        Data_user = connectionSocket.recv(4096)
        user,passs = pickle.loads(Data_user)

        if user in users:
            if users[user]['password'] != passs:
                connectionSocket.send(pickle.dumps("Incorrect password"))
                connectionSocket.close()
                return
            if users[user]['score']:
                last_score = users[user]['score'][-1]
                connectionSocket.send(pickle.dumps(f"Welcome back, {user}! Your last score was: {last_score}/5"))
            else:
                connectionSocket.send(pickle.dumps(f"Welcome back, {user}! You haven't taken a quiz yet."))
        else:
            users[user] = {'password': passs, 'score': []}
            connectionSocket.send(pickle.dumps("New user created"))
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
        users[user]['score'].append(score)
        save_users(users)
        result = f"Your score: {score}/5"
        # Send score result
        connectionSocket.send(pickle.dumps(result))

        # Send scoreboard
        scoreboard_data = scoreboard()
        connectionSocket.send(pickle.dumps(scoreboard_data))

        
    except timeout:
        error_msg = "Time's up! Quiz not submitted in time."
        connectionSocket.send(pickle.dumps(error_msg))
    except Exception as e:
        print(f"Error: {e}")
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
