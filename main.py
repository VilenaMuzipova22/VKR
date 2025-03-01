from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.camera import Camera
from kivy.clock import Clock
from kivy.uix.button import Button
from kivy.graphics import Color, Rectangle
import requests
from PIL import Image as PILImage
from io import BytesIO

# Указываем бэкенд для камеры
from kivy.config import Config
Config.set('kivy', 'camera', 'opencv')  # Используйте 'opencv' или 'ffpyplayer'

class MainApp(App):
    def build(self):
        # Основной layout
        self.layout = BoxLayout(orientation='vertical')

        # Виджет камеры
        self.camera = Camera(resolution=(640, 480), play=True)
        self.layout.add_widget(self.camera)

        # Метка для отображения результата
        self.result_label = Label(
            text="Наведите камеру на объект",
            size_hint=(1, 0.1),
            color=(1, 1, 1, 1),  # Белый цвет текста
            bold=True
        )
        self.layout.add_widget(self.result_label)

        # Кнопка для ручного захвата изображения
        self.capture_button = Button(
            text="Сделать снимок",
            size_hint=(1, 0.1),
            background_color=(0, 0.7, 0.3, 1)  # Зеленый цвет кнопки
        )
        self.capture_button.bind(on_press=self.capture_and_analyze)
        self.layout.add_widget(self.capture_button)

        # Запуск периодического анализа изображения (например, каждые 5 секунд)
        Clock.schedule_interval(self.analyze_frame, 5)

        return self.layout

    def capture_and_analyze(self, instance):
        """Захват изображения и его анализ."""
        self.analyze_frame()

    def analyze_frame(self, *args):
        """Анализ текущего кадра с камеры."""
        if not self.camera.texture:
            return

        # Получаем текстуру камеры и преобразуем её в изображение
        texture = self.camera.texture
        image_data = texture.pixels
        size = texture.size
        pil_image = PILImage.frombytes("RGB", size, image_data)

        # Сохраняем изображение в байтовый поток
        image_bytes = BytesIO()
        pil_image.save(image_bytes, format='jpeg')
        image_bytes.seek(0)

        # Отправляем изображение на сервер
        self.send_to_server(image_bytes)

    def send_to_server(self, image_bytes):
        """Отправка изображения на сервер и получение результата."""
        url = "http://127.0.0.1:8000/predict/"  # URL вашего FastAPI-сервера
        files = {'file': ('image.jpg', image_bytes, 'image/jpeg')}

        try:
            response = requests.post(url, files=files)
            if response.status_code == 200:
                result = response.json()
                self.result_label.text = f"Распознанный объект: {result['recognized_object']}"
            else:
                self.result_label.text = "Ошибка распознавания"
        except Exception as e:
            self.result_label.text = f"Ошибка: {str(e)}"

if __name__ == '__main__':
    MainApp().run()