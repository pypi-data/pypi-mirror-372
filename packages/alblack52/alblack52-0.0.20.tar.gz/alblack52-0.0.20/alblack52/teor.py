import requests

API_URL = "https://api.deepinfra.com/v1/openai/chat/completions"
API_TOKEN = "jwt:eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJnaDoxNzIxOTMyNzUiLCJleHAiOjE3MjA1MzM3NTh9.EbUJjFrb4mAqxzN-XvrWbstC_tNo70eBqhtaqnIa7IQ"


def ask_phind(messages, top_p=0.9, top_k=50, temperature=0.5):
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/Meta-Llama-3-70B-Instruct",
        "messages": messages,
        "top_p": top_p,
        "top_k": top_k,
        "temperature": temperature
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
        {"role": "system", "content": '''**Инструкция:**

1. **Цель:** Генерировать ответ на русском языке на теоретический вопрос по Python и библиотекам Python, связанным с работой с данными.
2. **Примерный объём ответа:** 150-200 слов.
3. **Требования к содержанию:**
    - Ответ должен быть исчерпывающим, кратким и чётким.
    - Ответ не должен содержать слишком большое количество кода.
    - Изложить главную информацию по теме.
    - Ответ должен быть точным и перепроверенным.
    - Не используй никакие языки кроме русского и в необходимых случаях английского.
    - Ответ не должен быть отправлен оборванным. Завершай то, что хотел написать.
    
4. **Структура ответа:**
    - **Введение:** Краткое описание темы (1-2 предложения).
    - **Основная часть:** Разъяснение ключевых понятий и функционала (5-6 предложений).
    - **Использование:** Применение. Если уместно, упоминание примеров использования (1-2 предложения).

**Процесс работы:**

1. Прочитай вопрос.
2. Перепроверь каждое сообщение перед отправкой.
3. Сформулируй ответ, используя структуру, указанную выше.
4. Убедись, что ответ чётко и кратко объясняет ключевые аспекты темы, завершён и написан НА РУССКОМ ЯЗЫКЕ без ошибок.
5. Отправь ответ.

**Пример вопроса:**

"Взаимодействие с Excel из Python с помощью XLWings: принципы работы и примеры использования."

**Пример ответа:**

XLWings — это популярная библиотека Python, которая позволяет взаимодействовать с Microsoft Excel,
обеспечивая интеграцию между Python и Excel для автоматизации задач, анализа данных и построения отчетов.

XLWings предоставляет удобный интерфейс для работы с Excel, позволяя управлять рабочими книгами,
листами, диапазонами и ячейками. Основные принципы работы включают возможность открытия, создания
и изменения файлов Excel, а также чтения и записи данных. Библиотека поддерживает взаимодействие
как с локальными, так и с облачными версиями Excel. XLWings также позволяет использовать Python
-функции как пользовательские функции в Excel (UDFs), что расширяет функциональность Excel,
делая анализ данных более мощным и гибким. Для этого требуется наличие установленного Excel
и соответствующих разрешений на использование COM интерфейса.

Пример использования XLWings включает чтение данных из Excel-файла,
выполнение вычислений в Python и запись результатов обратно в Excel:

```python
import xlwings as xw

# Открытие существующей рабочей книги
wb = xw.Book('example.xlsx')

# Выбор листа
sheet = wb.sheets['Sheet1']

# Чтение данных из диапазона
data = sheet.range('A1:B10').value

# Обработка данных в Python
processed_data = [x*2 for x in data]

# Запись данных обратно в Excel
sheet.range('C1').value = processed_data

# Сохранение и закрытие книги
wb.save()
wb.close()
```'''},
    ]

    while True:
        question = input("You: ")
        if question.lower() == 'exit':
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": question})

        answer = ask_phind(conversation_history)

        conversation_history.append({"role": "assistant", "content": answer})

        print("Ans: " + answer)


def start():
    chat_with_phind()


if __name__ == "__main__":
    chat_with_phind()
