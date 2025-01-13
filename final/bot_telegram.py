import telebot
from telebot.storage import StateMemoryStorage
import mysql.connector
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import io
import csv
from mysql.connector import pooling

#подключить MySQL исползует Laragon
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'price_tracker',
    'pool_name': 'mypool',
    'pool_size': 5
}
# Инициализация connection pool
connection_pool = mysql.connector.pooling.MySQLConnectionPool(**db_config)

# Инициализируем бота с помощью state storage
state_storage = StateMemoryStorage()
bot = telebot.TeleBot("8182290858:AAGKm9Obw4mvHiRrG-TI7SdMn_281ZZbewA", state_storage=state_storage)
# Инициализация базы данных
def init_db():
    connection = connection_pool.get_connection()
    cursor = connection.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255),
            url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX idx_name (name)
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS price_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            product_id INT,
            price_day_1 DECIMAL(15, 2),
            price_day_2 DECIMAL(15, 2),
            price_day_3 DECIMAL(15, 2),
            price_day_4 DECIMAL(15, 2),
            price_day_5 DECIMAL(15, 2),
            FOREIGN KEY (product_id) REFERENCES products(id),
            INDEX idx_product_time (product_id)
        )
    ''')

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS tracking_history (
            user_id BIGINT NOT NULL,
            product_id INT NOT NULL,
            PRIMARY KEY (user_id, product_id),
            FOREIGN KEY (product_id) REFERENCES products(id)
        )
    ''')
    connection.commit()
    cursor.close()
    connection.close()
# Command /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message,
                 "Добро пожаловать в Price Tracker Bot!\n"
                 "Использовать:\n"
                 "/track - Product Tracking\n"
                 "/track_id  - отслеживать продукт с дополнительным идентификатором\n"
                 "/list - Посмотреть список продуктов\n"
                 "/history <id>  - Посмотреть историю цен\n"
                 "/update <id> <giá> - Обновить новую цену\n"
                 "/tracking_history - Посмотреть историю отслеживания\n"
                 "/importcsv - Добавить продукты из CSV-файла")

# Command /track - Отображение списка продуктов для отслеживания
@bot.message_handler(commands=['track'])
def track_product(message):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    try:
        # Fetch the product list
        cursor.execute('''
            SELECT id, name
            FROM products
            ORDER BY created_at DESC 
            LIMIT 10
        ''')
        products = cursor.fetchall()
        if not products:
            bot.reply_to(message, "В настоящее время нет товаров для отслеживания.")
            return

        # Prepare chunks
        chunk_size = 5  # Number of products per chunk
        messages = []
        for i in range(0, len(products), chunk_size):
            chunk = products[i:i + chunk_size]
            response = "Список продуктов:\n\n"
            for prod in chunk:
                response += f"ID: {prod[0]} - Продукт: {prod[1]}\n"
            response += "\nВведите идентификатор продукта, который вы хотите отслеживать, например: `/track_id <id>`"
            messages.append(response)
        # Send each chunk as a separate message
        for msg in messages:
            bot.send_message(message.chat.id, msg)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при получении списка продуктов.")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

@bot.message_handler(commands=['track_id'])
def start_tracking(message):
    try:
        # Parse product ID from the message
        product_id = int(message.text.split()[1])  # Lấy ID sản phẩm từ lệnh
    except (IndexError, ValueError):
        bot.reply_to(message, "Использование: /track_id <id>\nПример: /track_id 1")
        return
    
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    
    try:
        # Проверить, существует ли продукт в базе данных
        cursor.execute('SELECT id, name FROM products WHERE id = %s', (product_id,))
        product = cursor.fetchone()
        
        if not product:
            bot.reply_to(message, "Товар не существует. Пожалуйста, проверьте ваш идентификатор еще раз.")
            return
        
       # Проверьте, подписался ли пользователь на продукт
        cursor.execute('SELECT * FROM tracking_history WHERE user_id = %s AND product_id = %s', (message.from_user.id, product_id))
        tracking_entry = cursor.fetchone()
        
        if tracking_entry:
            bot.reply_to(message, f"Вы уже подписаны на продукт {product[1]}!")
        else:
            # Сохраните информацию об отслеживании в таблице tracking_history
            cursor.execute('INSERT INTO tracking_history (user_id, product_id) VALUES (%s, %s)', (message.from_user.id, product_id))
            connection.commit()
            bot.reply_to(message, f"Вы начали отслеживать продукт: {product[1]}")
    
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при отслеживании товара.")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Command /importcsv - Импортируйте продукты из CSV-файла и обновляйте цены на каждый день.
@bot.message_handler(content_types=['document'])
def handle_csv_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    
   # Сохранить временный файл
    csv_file_path = f"{message.document.file_name}"
    with open(csv_file_path, 'wb') as f:
        f.write(downloaded_file)
    
    # Прочитать CSV-файл и сохранить продукты в БД
    try:
        products = []
        with open(csv_file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row.get('name')
                url = row.get('url', '')  # URL может не существовать
                # Получить цену каждого дня из столбцов price_day_1 по price_day_5
                prices = {
                    'price_day_1': row.get('price_day_1'),
                    'price_day_2': row.get('price_day_2'),
                    'price_day_3': row.get('price_day_3'),
                    'price_day_4': row.get('price_day_4'),
                    'price_day_5': row.get('price_day_5')
                }
                
               # Проверьте, указаны ли название Список продуктов:\n\nа, цена и даты
                if name and all(prices.values()):
                    # Преобразовать цену в действительное число
                    prices = {day: float(price) for day, price in prices.items()}
                    # Проверьте, существует ли продукт в базе данных
                    connection = connection_pool.get_connection()
                    cursor = connection.cursor()
                    cursor.execute('SELECT id FROM products WHERE name = %s', (name,))
                    existing_product = cursor.fetchone()
                    
                    if not existing_product:
                        # Если этот продукт не существует, добавьте его в базу данных
                        cursor.execute(''' 
                            INSERT INTO products (name, url) 
                            VALUES (%s, %s) 
                        ''', (name, url))
                        connection.commit()
                        # Получить идентификатор только что добавленного продукта
                        cursor.execute('SELECT id FROM products WHERE name = %s', (name,))
                        product_id = cursor.fetchone()[0]
                    else:
                        # Если продукт уже существует, получить идентификатор продукта
                        product_id = existing_product[0]
                    
                    # Затем добавьте цену за каждый день в таблицу price_history
                    cursor.execute('''
                        INSERT INTO price_history 
                        (product_id, price_day_1, price_day_2, price_day_3, price_day_4, price_day_5)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    ''', (product_id, prices['price_day_1'], prices['price_day_2'], prices['price_day_3'], prices['price_day_4'], prices['price_day_5']))
                    connection.commit()
                    cursor.close()
                    connection.close()
        # Если продукт и цена были успешно добавлены
        bot.reply_to(message, "Товары и цены успешно добавлены из CSV.")
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при обработке CSV-файла.")
        print(f"Error: {e}")

@bot.message_handler(commands=['list'])
def list_products(message):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(''' 
            SELECT p.id, p.name, p.url, h.price_day_1, h.price_day_2, h.price_day_3, h.price_day_4, h.price_day_5
            FROM products p
            LEFT JOIN (
                SELECT ph.product_id, ph.price_day_1, ph.price_day_2, ph.price_day_3, ph.price_day_4, ph.price_day_5
                FROM price_history ph
                INNER JOIN (
                    SELECT product_id, MAX(id) as max_id
                    FROM price_history
                    GROUP BY product_id
                ) latest ON ph.id = latest.max_id
            ) h ON p.id = h.product_id
        ''')
        products = cursor.fetchall()
        if not products:
            bot.reply_to(message, "В настоящее время нет товаров.")
            return
        
        # Prepare chunks
        chunk_size = 5  # Number of products per chunk
        messages = []
        for i in range(0, len(products), chunk_size):
            chunk = products[i:i + chunk_size]
            response = "Список продуктов:\n\n"
            for prod in chunk:
                response += f"ID: {prod[0]}\nпродукт: {prod[1]}\n"
                if prod[2]:  # Если есть URL
                    response += f"URL: {prod[2]}\n"
                if prod[3]:  # Цена за 1-й день
                    response += f"Цена за 1-й день: {float(prod[3]):,.0f}₫\n"
                if prod[4]:  # Цена за 2-й день
                    response += f"Цена за 2-й день: {float(prod[4]):,.0f}₫\n"
                if prod[5]:  # Цена за 3-й день
                    response += f"Цена за 3-й день: {float(prod[5]):,.0f}₫\n"
                if prod[6]:  # Цена за 4-й день
                    response += f"Цена за 4-й день: {float(prod[6]):,.0f}₫\n"
                if prod[7]:  # Цена за 5-й день
                    response += f"Цена за 5-й день: {float(prod[7]):,.0f}₫\n"
                response += "\n"
            messages.append(response)
        
        # Send each chunk as a separate message
        for msg in messages:
            bot.send_message(message.chat.id, msg)
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при получении списка продуктов.")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()
# Command /update - Обновить новую цену
@bot.message_handler(commands=['update'])
@bot.message_handler(commands=['update'])
def update_price(message):
    try:
        # Parse the command to extract product ID and new price
        _, product_id, price = message.text.split()
        product_id = int(product_id)
        price = float(price)
    except ValueError:
        bot.reply_to(message, "Использование: /update <id> <price>\Пример: /update 1 150000")
        return

    connection = connection_pool.get_connection()
    cursor = connection.cursor()

    try:
        # Проверьте, есть ли товар в таблице price_history
        cursor.execute(''' 
            SELECT id, price_day_1, price_day_2, price_day_3, price_day_4, price_day_5 
            FROM price_history 
            WHERE product_id = %s 
            ORDER BY id DESC LIMIT 1
        ''', (product_id,))
        price_history = cursor.fetchone()

        if not price_history:
            bot.reply_to(message, "У этого продукта пока нет истории цен.")
            return
        
        # Обновить цены с 1-го по 4-й день и новую цену на 5-й день
        new_price_history = (
            price_history[2],  # price_day_1 becomes price_day_2
            price_history[3],  # price_day_2 becomes price_day_3
            price_history[4],  # price_day_3 becomes price_day_4
            price_history[5],  # price_day_4 becomes price_day_5
            price  # new price goes to price_day_5
        )

        # Обновить таблицу price_history новой ценой
        cursor.execute('''
            UPDATE price_history
            SET price_day_1 = %s, price_day_2 = %s, price_day_3 = %s, price_day_4 = %s, price_day_5 = %s
            WHERE id = %s
        ''', (*new_price_history, price_history[0]))

        connection.commit()
        bot.reply_to(message, f"Цена на идентификатор продукта {product_id} успешно обновлена!")
        
    except Exception as e:
        connection.rollback()  # Rollback in case of error
        bot.reply_to(message, "Произошла ошибка при обновлении цены.")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


# Команда /history - Просмотр истории цен
@bot.message_handler(commands=['history'])
@bot.message_handler(commands=['history'])
def show_history(message):
    try:
        # Parse the command to extract the product ID
        _, product_id = message.text.split()
        product_id = int(product_id)
    except ValueError:
        bot.reply_to(message, "Использование: /history <id>\Пример: /history 1")
        return

    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    try:
        # Проверьте, подписан ли пользователь на этот продукт
        cursor.execute('SELECT 1 FROM tracking_history WHERE user_id = %s AND product_id = %s', (message.from_user.id, product_id))
        tracking = cursor.fetchone()

        if not tracking:
            bot.reply_to(message, "Вы не подписаны на этот продукт. Для отслеживания товара используйте /track_id <id>.")
            return

        # Если отслеживается, получить историю цен на продукт
        cursor.execute('''
            SELECT id, name FROM products WHERE id = %s
        ''', (product_id,))
        product = cursor.fetchone()
        
        if not product:
            bot.reply_to(message, "Идентификатор продукта не существует.")
            return

        cursor.execute('''
            SELECT price_day_1, price_day_2, price_day_3, price_day_4, price_day_5
            FROM price_history WHERE product_id = %s
        ''', (product_id,))
        price_history = cursor.fetchone()

        if not price_history:
            bot.reply_to(message, f"Продукт '{product[1]}' не имеет истории цен.")
            return

        # Prepare data for plotting
        days = [1, 2, 3, 4, 5]
        prices = list(price_history)

        # Plot the data as a bar chart
        plt.figure(figsize=(10, 6))
        plt.bar(days, prices, color='skyblue', width=0.5)

        # Add title and labels
        plt.title(f"История цен на продукт '{product[1]}'")
        plt.xlabel('Дата теста')
        plt.ylabel('Цена (руб.)')

        # Add grid lines and adjust ticks
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        plt.xticks(days)

        # Save the plot to a buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Send the plot to the user
        bot.send_photo(message.chat.id, photo=buf)

    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при получении истории цен.")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()


@bot.message_handler(commands=['tracking_history'])
def tracking_history(message):
    connection = connection_pool.get_connection()
    cursor = connection.cursor()
    try:
        # Запрос продуктов, на которые подписан пользователь
        cursor.execute('''
            SELECT p.id, p.name, p.created_at
            FROM products p
            JOIN tracking_history th ON p.id = th.product_id
            WHERE th.user_id = %s
            ORDER BY p.created_at DESC
        ''', (message.from_user.id,))
        
        tracked_products = cursor.fetchall()
        
        if not tracked_products:
            bot.reply_to(message, "Вы пока не подписались ни на один продукт.")
            return
        
        # Подготовка и отправка информации об отслеживаемых товарах
        response = "Продукты, на которые вы подписаны:\n\n"
        for product in tracked_products:
            response += f"ID: {product[0]}\nНазвание: {product[1]}\nДата выполнения: {product[2]}\n\n"
        
        # Если список слишком длинный, разделите его на несколько частей и отправьте
        chunk_size = 3500  # Telegram имеет ограничение на длину сообщения
        for i in range(0, len(response), chunk_size):
            bot.send_message(message.chat.id, response[i:i + chunk_size])
    
    except Exception as e:
        bot.reply_to(message, "Произошла ошибка при получении истории отслеживания.")
        print(f"Error: {e}")
    finally:
        cursor.close()
        connection.close()

# Запустить бота
if __name__ == "__main__":
    init_db()
    bot.infinity_polling()

