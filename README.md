# **TradeWS**   
### **Реализация WebSocket-интеграции с Binance API**  

**TradeWS** — это Django-приложение для получения данных о сделках с Binance WebSocket API, их хранения в PostgreSQL и предоставления данных клиентам через REST API и WebSocket-сервер на Django Channels.  

## **Видео демонстрация** 


https://github.com/user-attachments/assets/1be0e383-e473-46fd-b0b8-099cda784cc5



## **Функциональность**  
✔ **Получение данных в реальном времени** через WebSocket Binance.  
✔ **Сохранение данных в Redis** для временного хранения.  
✔ **Агрегация и запись в PostgreSQL** каждую минуту через Celery.  
✔ **REST API** для получения истории цен.  
✔ **WebSocket API** для получения обновлений в реальном времени.  
✔ **Unit-тесты** для проверки работоспособности.  

---

## **Архитектура проекта**  
**TradeWS** использует **современный стек** Django и асинхронные технологии:  
- **Django + Django REST Framework** – основное API.  
- **Django Channels** – WebSocket-сервер для клиентов.  
- **Redis** – кеш и временное хранилище данных.  
- **Celery** – фоновая обработка и агрегация данных.  
- **PostgreSQL** – основное хранилище данных.  
- **pytest + Mock WebSocket** – тестирование.  

**Как работает процесс?**  
1. **WebSocket-клиент** подключается к Binance и слушает сделки в реальном времени.  
2. **Полученные данные записываются в Redis** (только за последнюю минуту).  
3. **Celery-задача раз в минуту** агрегирует данные и записывает в PostgreSQL.  
4. **REST API позволяет получать историю** цен из PostgreSQL.  
5. **Django Channels рассылает данные клиентам** по WebSocket.  

---

## **Установка и запуск проекта**  

### **1 Клонирование репозитория**  
```sh
git clone https://github.com/Erdaulet0341/TradeWS.git
cd TradeWS
```

### **2 Создание виртуального окружения**  
```sh
python -m venv venv
source venv/bin/activate  # Для Linux/Mac
venv\Scripts\activate  # Для Windows
```

### **3 Установка зависимостей**  
```sh
pip install -r requirements.txt
```

### **4 Настройка переменных окружения (.env)**  
Создайте файл `.env` и добавьте:  
```
SECRET_KEY=your_secret_key
DEBUG=True
ALLOWED_HOSTS=*
DATABASE_URL=postgres://user:password@localhost:5432/tradews
REDIS_URL=redis://localhost:6379/0
```

### **5 Настройка базы данных**  
```sh
python manage.py migrate
python manage.py createsuperuser
```

### **6 Запуск основных сервисов**  
📌 **Redis (если не запущен):**  
```sh
redis-server
```

📌 **Celery Worker:**  
```sh
celery -A TradeWS worker --loglevel=info
```

📌 **Celery Beat (для периодических задач):**  
```sh
celery -A TradeWS beat --loglevel=info
```

📌 **Django сервер:**  
```sh
python manage.py runserver
```

📌 **WebSocket-слушатель Binance:**  
```sh
python manage.py binance_listener
```

---

## **API-эндпоинты**

### **1 REST API (История цен с пагинацией)**  
📌 **Получить список записей с пагинацией:**  
```sh
GET /api/trades/?limit=10&offset=0
```
📌 **Параметры запроса:**  
- `limit` – количество записей на странице (по умолчанию 10).  
- `offset` – сдвиг (например, `offset=10` пропустит первые 10 записей).  

📌 **Пример ответа:**  
```json
{
    "count": 1000,
    "next": "/api/trades/?limit=10&offset=10",
    "previous": null,
    "results": [
        {
            "id": 1,
            "symbol": "BTCUSDT",
            "open_price": "65000.00",
            "high_price": "65050.00",
            "low_price": "64980.00",
            "close_price": "65010.00",
            "volume": "12.45",
            "timestamp": "2025-03-10T12:00:00Z"
        },
        {
            "id": 2,
            "symbol": "ETHUSDT",
            "open_price": "1919.09",
            "high_price": "1919.38",
            "low_price": "1919.08",
            "close_price": "1919.38",
            "volume": "18.37",
            "timestamp": "2025-03-10T12:01:00Z"
        }
    ]
}
```
🔹 **`count`** – общее количество записей в базе.  
🔹 **`next`** – ссылка на следующую страницу (если есть).  
🔹 **`previous`** – ссылка на предыдущую страницу (если есть).  
🔹 **`results`** – список записей текущей страницы.  

---

### **2 WebSocket API (Обновления цен в реальном времени)**  
📌 **Подключение к WebSocket-серверу:**  
```sh
ws://localhost:8000/ws/trades/
```
📌 **Пример ответа:**  
```json
{
    "symbol": "ETHUSDT",
    "open_price": "1919.09",
    "high_price": "1919.38",
    "low_price": "1919.08",
    "close_price": "1919.38",
    "volume": "18.37",
    "timestamp": "2025-03-10T12:02:00Z"
}
```

---

## **Тестирование**  
Запуск тестов:  
```sh
pytest
python manage.py test
```
📌 Тесты проверяют:  
- Подключение к Binance WebSocket.  
- Корректность работы Celery.  
- Функциональность REST API.  
- Работу WebSocket-сервера.  
