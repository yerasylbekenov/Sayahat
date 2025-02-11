# test.py

from ai_2 import GigaChatClient

def main():
    client = GigaChatClient()
    
    user_id = '1'  # Укажите уникальный идентификатор пользователя
    
    print("Добро пожаловать в чат с GigaChat!")
    print("Для выхода напишите '/exit'.")
    
    while True:
        message = input("Введите ваше сообщение: ")
        
        if message == "/exit":
            break
            
        response = client.process_message(user_id, message)
        print(f"GigaChat: {response}")

if __name__ == "__main__":
    main()