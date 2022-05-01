from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle, PushMatrix, Rotate, PopMatrix, Translate
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image


class ImageImg(Image):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.source = 'graphics/airplaneIcon.png'
        self.bind(center=self._update)

        with self.canvas.before:
            PushMatrix()
            self.rot = Rotate()

        with self.canvas:
            PopMatrix()

    def on_touch_down(self, touch):
        self.rot.angle += 20
        return True

    def _update(self, instance, value):
        self.rot.origin = instance.center


class ImageLayout(FloatLayout):
    def __init__(self, **kwargs):
        super(ImageLayout, self).__init__(**kwargs)
        self.bind(pos=self._update, size=self._update)

        with self.canvas.before:
            Color(1, .5, 1, 1)
            self.bg = Rectangle(pos=self.pos, size=self.size)

    def _update(self, instance, value):
        self.bg.pos = instance.pos
        self.bg.size = instance.size


class ImageExample(App):
    def __init__(self, **kwargs):
        super(ImageExample, self).__init__(**kwargs)
        self.img = None
        Window.size = (300, 300)

    def build(self, **kwargs):
        self.root = ImageLayout()
        self.img = ImageImg()
        self.root.add_widget(self.img)
        self.root.bind(pos=self._update, size=self._update)
        return self.root

    def _update(self, instance, value):
        self.root.pos = instance.pos
        self.root.size = instance.size


if __name__ == '__main__':
    app = ImageExample()
    app.run()
