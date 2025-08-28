import requests

# ---------------- Настройки ----------------
PROXY_BASE_URL = "https://11b6257d4a8e.ngrok-free.app"
PROXY_SECRET = "dns"

MODEL = "deepseek-ai/DeepSeek-V3.1"

SYSTEM_PROMPT = '''
Ты — эксперт в численных методах. Тебе нужно проанализировать требования и написать как можно более правильный ответ на задание. От твоего ответа зависит, сдам ли я очень важный экзамен.

При выполнении задачи использовать только базовые методы Python, основные методы пакета matplotlib, методы пакета NumPy: 
array, zeros, zeros_like, linspace, eye, shape, random, poly, roots (только в случае поиска корней характеристического уравнения), transpose, sqrt, log, exp, sin, cos, atan, arctan, tan, mean, 
методы модуля sparse библиотеки scipy. Наличие других методов приводит к аннулированию оценки работы.

Под кодом пиши своими словами во втором лице пояснения к тому, что делается в коде. В духе 'тут мы делаем ..., а после ...', после этого текста дай ответ на теоретический вопрос. При необходимости ответь на вопросы.
'''


# ------------------------------------------

def start():
    """
    Запускает полноценный интерактивный чат с моделью.
    Вводишь запросы через input(), exit для выхода.
    """
    conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            print("Выход из чата.")
            break

        conversation_history.append({"role": "user", "content": user_input})

        # Отправка запроса через прокси
        url = f"{PROXY_BASE_URL}/api/proxy"
        headers = {"X-Proxy-Secret": PROXY_SECRET, "Content-Type": "application/json"}
        data = {"messages": conversation_history, "model": MODEL}

        try:
            resp = requests.post(url, headers=headers, json=data, timeout=200)
            if resp.status_code == 200:
                j = resp.json()
                answer = j.get("text") or j.get("upstream")
            else:
                answer = f"Ошибка прокси {resp.status_code}: {resp.text}"
        except Exception as e:
            answer = f"Ошибка при отправке запроса: {e}"

        conversation_history.append({"role": "assistant", "content": answer})
        print("Чернышенко: " + answer)
