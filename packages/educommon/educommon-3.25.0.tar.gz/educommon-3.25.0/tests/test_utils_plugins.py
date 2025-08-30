from django.test.testcases import (
    SimpleTestCase,
)

from educommon.utils.plugins import (
    extender_for,
)


class Window:
    def __init__(self):
        self._init_components()
        self._do_layout()

    def _init_components(self):
        self.items = []
        self.field1 = type('', (), {})()

    def _do_layout(self):
        self.items.append(self.field1)

    def set_params(self, params):
        self.field1.width = 100


@extender_for(Window)
class WindowExtender1:
    extends_methods = ('_init_components', '_do_layout', 'set_params')

    @staticmethod
    def _init_components(window, result):
        window.field2 = type('', (), {})()

        return result

    @staticmethod
    def _do_layout(window, result):
        window.items.insert(0, window.field2)

        return result

    @staticmethod
    def set_params(window, result, params):
        window.field1.width = 200
        window.field2.width = 200

        return result


@extender_for(Window)
class WindowExtender2:
    extends_methods = ('set_params',)

    @staticmethod
    def set_params(window, result, params):
        for item in window.items:
            for name, value in params.items():
                setattr(item, name, value)

        return result


@extender_for(Window)
class WindowExtender3:
    priority = -1
    extends_methods = ('set_params',)

    @staticmethod
    def set_params(window, result, params):
        window.field2.width = 300
        return result


class TestCase(SimpleTestCase):
    """Проверка работы инструментария для ширения классов."""

    def test(self):
        win = Window()
        win.set_params({'anchor': '100%'})

        self.assertIsInstance(win.items, list)
        self.assertEquals(len(win.items), 2)

        self.assertIn(win.field1, win.items)
        self.assertEquals(win.field1.width, 200)

        self.assertIn(win.field2, win.items)
        self.assertEquals(win.field2.width, 300)

        for item in win.items:
            self.assertTrue(hasattr(item, 'anchor'))
            self.assertEquals(item.anchor, '100%')
