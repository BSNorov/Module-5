import random
import requests
from functools import partial
from pywebio.input import select
from pywebio.output import put_image, toast, put_button, use_scope, clear, put_text
from pywebio import start_server

api_info = {
    "cat": {
        "api_key": "CAT_API_KEY",  # <-- сюда вставить реальный ключ
        "api_url": "https://api.thecatapi.com/v1"
    },
    "dog": {
        "api_key": "DOG_API_KEY",  # <-- сюда вставить реальный ключ
        "api_url": "https://api.thedogapi.com/v1"
    }
}

def get_random_animal():
    """Получение случайного животного (кот или собака)"""
    animal_type = random.choice(list(api_info.keys()))
    api_method = f'{api_info[animal_type]["api_url"]}/images/search'

    try:
        response = requests.get(api_method)
        response.raise_for_status()
        data = response.json()[0]
        data["source"] = animal_type
        return data
    except Exception as e:
        print(f"Ошибка при загрузке изображения: {e}")
        return None

def show_random_animal():
    clear("scope")
    with use_scope("scope"):
        data = get_random_animal()
        if data:
            try:
                img_data = requests.get(data["url"]).content
                put_image(img_data, width='500px')
                all_buttons(data)
            except Exception:
                put_text("Не удалось загрузить изображение :(")
        else:
            toast('Не удалось загрузить изображение :(')

def all_buttons(data):
    put_button(label='➡️ Random', onclick=show_random_animal)
    put_button(label='➕ Add to Favourites', onclick=partial(add_to_favorites, data))
    put_button(label='❤️ Favourites', onclick=choose_category)

def add_to_favorites(data):
    """Добавление изображения в избранное"""
    source = data.get("source", "cat")
    api_method = f'{api_info[source]["api_url"]}/favourites'
    headers = {'x-api-key': api_info[source]["api_key"]}

    payload = {'image_id': data["id"]}
    try:
        response = requests.post(api_method, headers=headers, json=payload)
        response.raise_for_status()
        with use_scope("scope"):
            put_text('❤️ Добавлено в избранное!')
    except Exception as e:
        with use_scope("scope"):
            put_text(f"Ошибка добавления в избранное: {e}")

def show_favorites(animal_type):
    """Показ избранных изображений"""
    clear("scope")
    api_method = f'{api_info[animal_type]["api_url"]}/favourites'
    headers = {'x-api-key': api_info[animal_type]["api_key"]}

    try:
        response = requests.get(api_method, headers=headers)
        response.raise_for_status()
        favorites = response.json()

        with use_scope("scope"):
            if not favorites:
                put_text('У вас пока нет избранных изображений.')
            for favorite in favorites:
                try:
                    img_url = favorite['image']['url']
                    img_data = requests.get(img_url).content
                    put_image(img_data, width='300px', height='300px')
                    put_text(" ")
                except Exception:
                    put_text("Ошибка загрузки картинки")
            random_button()
    except Exception as e:
        with use_scope("scope"):
            put_text(f"Ошибка загрузки избранных: {e}")

def choose_category():
    clear("scope")
    with use_scope("scope"):
        action = select('Выберите животное', ['Кошки', 'Собаки'])
        if action == "Кошки":
            show_favorites("cat")
        else:
            show_favorites("dog")

def random_button():
    put_button(label='➡️ Random', onclick=show_random_animal)

if __name__ == "__main__":
    start_server(show_random_animal, port=8080)
