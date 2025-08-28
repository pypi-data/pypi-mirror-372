import requests

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
API_TOKEN = 'jwt:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaDoxNjY1MzcyMzkiLCJleHAiOjE3NTMzNTQwNzV9.QKdE15memSb9qkqpTnO-PDP-p7NU0ymmaqTpc-YY_7s'

# fjkbsfbkjsbdfs

def ask_phind(messages):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/DeepSeek-R1-0528",
        "messages": messages
    }
    response = requests.post(API_URL, headers=headers, json=data)

    if response.status_code == 200:
        response_json = response.json()

        try:
            return response_json["choices"][0]["message"]["content"]
        except (KeyError, IndexError) as e:
            return "Error: Unable to extract response content. Please check the response structure."
    else:
        return f"Error: {response.status_code}, {response.text}"


def chat_with_phind():
    conversation_history = [
        {"role": "system", "content": '''
    Ты - эксперт в машинном обучении. Отвечай подробно и доходчиво.
'''},

    ]

    while True:
        question = input("You: ")
        if question.lower() == 'exit':
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": question})

        answer = ask_phind(conversation_history)

        conversation_history.append({"role": "assistant", "content": answer})

        print("Ответ: " + answer)


def start():
    chat_with_phind()


if __name__ == "__main__":
    chat_with_phind()
