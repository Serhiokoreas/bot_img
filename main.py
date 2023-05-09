import telebot
import requests
import imghdr
import io
import zipfile
from bs4 import BeautifulSoup

# Создаем бота с токеном напрямую
bot = telebot.TeleBot("6062243664:AAFjJlzYwiZGADIcw9z5T6TW4plFaFyD7_M")


# Обрабатываем команду /start
@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(message.chat.id,
                     "Привет! Я бот, который может выводить картинки по ссылке в чат. Просто отправь мне одну или несколько ссылок на картинки.")


# Обрабатываем сообщения с ссылками
@bot.message_handler(regexp="https?://.+")
def save_image(message):
    # Получаем текст из сообщения
    text = message.text
    # Разделяем текст по пробелам на список слов
    words = text.split()
    # Фильтруем список слов, оставляя только те, которые начинаются с http:// или https://
    links = [word for word in words if word.startswith("http://") or word.startswith("https://")]

    # Если ссылок больше одной, то создаем ZIP-архив
    if len(links) > 1:
        # Создаем новый ZIP-архив в памяти
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as myzip:
            # Перебираем все ссылки в списке
            for i, url in enumerate(links):
                # Проверяем, что это действительно ссылка на сайт photo-screen.ru
                if "photo-screen.ru" in url:
                    # Получаем байтовый поток с картинкой и ее расширение
                    image_data, image_type = get_image_from_url(url)
                    # Добавляем файл в архив
                    myzip.writestr(f'image{i}.{image_type}', image_data.getvalue())
                else:
                    # Отправляем сообщение об ошибке
                    bot.send_message(message.chat.id, f"Это не ссылка на сайт photo-screen.ru: {url}. Попробуй другую.")
        # Отправляем ZIP-архив в чат
        zip_buffer.seek(0)
        bot.send_document(message.chat.id, ('images.zip', zip_buffer))
    else:
        # Перебираем все ссылки в списке (в данном случае только одну)
        for url in links:
            # Проверяем, что это действительно ссылка на сайт photo-screen.ru
            if "photo-screen.ru" in url:
                # Получаем байтовый поток с картинкой и ее расширение
                image_data, image_type = get_image_from_url(url)
                # Отправляем картинку в чат по байтовому потоку
                bot.send_photo(message.chat.id, photo=image_data)
            else:
                # Отправляем сообщение об ошибке
                bot.send_message(message.chat.id, f"Это не ссылка на сайт photo-screen.ru: {url}. Попробуй другую.")


def get_image_from_url(url):
    # Скачиваем содержимое по ссылке
    response = requests.get(url)
    # Разбираем HTML-код
    soup = BeautifulSoup(response.content, "html.parser")
    # Находим строку с тегом img и атрибутом id="screenshot"
    img_tag = soup.find("img", id="screenshot")
    # Получаем значение атрибута src, которое является ссылкой на картинку
    img_url = img_tag["src"]
    # Скачиваем содержимое по ссылке на картинку
    img_response = requests.get(img_url)
    # Определяем тип изображения по его содержимому
    img_type = imghdr.what(None, img_response.content)
    # Создаем байтовый поток с картинкой
    img_data = io.BytesIO(img_response.content)
    # Возвращаем байтовый поток с картинкой и ее расширение
    return img_data, img_type

# Запускаем бота
bot.polling()