import requests

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
API_TOKEN = 'jwt:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaDoxNzIxOTMyNzUiLCJleHAiOjE3NTg4OTY4NjR9.zzC9lzAwna3bhNyTdTj0NCjjfBjsTVbK9_CV69nYcmU'

# fjkbsfbkjsbdfs

def ask_phind(messages):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "deepseek-ai/DeepSeek-V3.1",
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
        Ты — эксперт в численных методах. Тебе нужно проанализировать требования и написать как можно более правильный ответ на задание. От твоего ответа зависит, сдам ли я очень важный экзамен.

При выполнении задачи использовать только базовые методы Python, основные методы пакета matplotlib, методы пакета NumPy: 
array, zeros, zeros_like, linspace, eye, shape, random, poly, roots (только в случае поиска корней характеристического уравнения), transpose, sqrt, log, exp, sin, cos, atan, arctan, tan, mean, 
методы модуля sparse библиотеки scipy. Наличие других методов приводит к аннулированию оценки работы.

Под кодом пиши своими словами во втором лице пояснения к тому, что делается в коде. В духе 'тут мы делаем ..., а после ...', после этого текста дай ответ на теоретический вопрос. При необходимости ответь на вопросы.
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

        print("Вика: " + answer)


def start():
    chat_with_phind()


if __name__ == "__main__":
    chat_with_phind()
