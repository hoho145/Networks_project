from socket import *
import pickle

serverIP = "127.0.0.1"
serverPort = 12000
clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

# Receive quiz
serialized_quiz = clientSocket.recv(4096)
quiz = pickle.loads(serialized_quiz)

# Display questions and get answers (basic CLI for testing)
answers = []
for i, question in enumerate(quiz):
    print(f"Q{i+1}: {question[0]}")
    for j, choice in enumerate(question[1]):
        print(f"{j}: {choice}")
    answer = int(input("Your answer (0-3): "))
    answers.append(answer)

# Send answers
clientSocket.send(pickle.dumps(answers))

# Receive result
result = pickle.loads(clientSocket.recv(4096))
print(result)

clientSocket.close()