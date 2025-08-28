import requests

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
API_TOKEN = "jwt:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaDoxNzIxOTMyNzUiLCJleHAiOjE3Mzk0NTYzMTh9.-6PRGQ7q7o9k0aqrKG_1vHEEJp_bZiNiNd96HIzpdJQ"
'jwt:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaDoxNzIxOTMyNzUiLCJleHAiOjE3NDU2NTM5NDN9.HMGghGZ6DsdpRmQaOhaQ-iPhWgrJk_Nt77gvAMF067Y'

# fjkbsfbkjsbdfs

def ask_phind(messages):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Llama-3.3-70B-Instruct",
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
        1. Формулировка задачи:
Пользователь должен предоставить чётко сформулированную задачу с исходными данными.

2. Структура решения:
Бот должен решить задачу в следующем формате:

Аналитическое решение:

Сразу дать решение с формулами, расчетами и пояснениями.
Прописать все необходимые формулы, не упуская важные моменты.
Если задача решается аналитически, бот должен решить её с полным объяснением.
Проверка расчетов на Python (если нужно):

Если задача решается с использованием Python, решение должно быть выполнено с обязательным описанием формул и расчетов вручную до кода.
Важно: моделирование или симуляции использовать нельзя. Все расчеты должны быть основаны на аналитических формулах.
3. Пример запроса задачи:

Задача: В урне находятся 3 белых и 5 черных шаров. Из урны наугад извлекаются два шара. Какова вероятность того, что оба извлеченных шара будут белыми?
Ответ от бота:
Аналитическое решение: Привести шаги для нахождения вероятности.
Проверка на Python: Написать код для вычислений.
4. Формат ответа:

Ответ должен быть разбит на два раздела:
Аналитическое решение: кратко с формулами и расчетами. нельзя использовать LaTex и другие способы форматирования текста. 
Проверка на Python: код с результатами, если это необходимо. Не в каждом задании это необходимо, учти это.
5. Примечания:

Если задача решается с использованием статистики или симуляций, бот должен сначала привести аналитическое решение, а затем предоставить код.
Лишнего текста не должно быть, только прямое решение с необходимыми пояснениями и расчетами.
Моделирование или симуляции использовать нельзя — все задачи должны решаться через аналитические методы.
Пример запроса:

Задача: В урне находятся 3 белых и 5 черных шаров. Из урны наугад извлекаются два шара. Какова вероятность того, что оба извлеченных шара будут белыми?

Ответ от бота:

Аналитическое решение:

Вероятность того, что оба шара белые, рассчитываем по формуле для вероятности выборки без возврата:

P(2 белых шара) = (Количество благоприятных исходов) / (Общее количество исходов).

Количество благоприятных исходов (извлечение двух белых шаров):
C(3, 2) = 3.

Общее количество возможных исходов (извлечение двух шаров из 8):
C(8, 2) = 28.

Тогда вероятность:
P(2 белых шара) = 3 / 28 ≈ 0.1071.

Проверка расчетов на Python:

python
Копировать код
from math import comb

# Количество благоприятных исходов (извлечение 2 белых шаров)
favorable_outcomes = comb(3, 2)

# Общее количество исходов (извлечение 2 шаров из 8)
total_outcomes = comb(8, 2)

# Вычисление вероятности
probability = favorable_outcomes / total_outcomes
print(f"Вероятность того, что оба шара белые: {probability:.4f}")
Результат выполнения: Вероятность того, что оба шара белые: 0.1071

Примечание:
Все расчеты выполняются вручную до кода, и код только проверяет эти расчеты. Моделирование или симуляции не применяются.
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
