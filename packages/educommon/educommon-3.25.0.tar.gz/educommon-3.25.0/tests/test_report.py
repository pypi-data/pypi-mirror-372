from django.test import (
    TestCase,
)

from educommon.report import (
    AbstractDataProvider,
    CompositeDataProvider,
    DependentCompositeProvider,
    FlatDataProviderAdapter,
    NestedDataProviderAdapter,
)


class Provider01(AbstractDataProvider):
    """Тестовый провайдер #1."""

    def init(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c

    @property
    def param01(self):
        return self._a

    @property
    def param02(self):
        return self._b

    @property
    def param03(self):
        return self._c


class Provider02(AbstractDataProvider):
    """Тестовый провайдер #2."""

    def init(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c

    @property
    def param01(self):
        return self._a

    @property
    def param02(self):
        return self._b

    @property
    def param03(self):
        return self._c

    @property
    def param04(self):
        return self._a + self._b + self._c


class Provider03(AbstractDataProvider):
    """Тестовый провайдер #3."""

    def init(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c

    @property
    def param01(self):
        return self._a

    @property
    def param02(self):
        return self._b

    @property
    def param03(self):
        return self._c


class Provider04(AbstractDataProvider):
    """Тестовый провайдер #4."""

    def init(self, a, b, c):
        self._a = a
        self._b = b
        self._c = c

    @property
    def param01(self):
        return self._a

    @property
    def param02(self):
        return self._b

    @property
    def param03(self):
        return self._c


# значения для теста свойств провайдеров
A, B, C = 1, 2, 3
D = A + B + C
BAR, FOO = 42, 2128506

# число параметров во всём дереве провайдеров
PARAMS_COUNT = 15


class MainDataProvider(CompositeDataProvider):
    """Композитный тестовый провайдер #1."""

    provider_name = 'Main'

    @property
    def bar(self):
        return BAR


class SuperDataProvider(CompositeDataProvider):
    """Композитный тестовый провайдер #2."""

    @property
    def foo(self):
        return FOO


def setup_provider():
    sub_provider = MainDataProvider(
        [
            Provider01,
            Provider02,
        ]
    )

    provider = SuperDataProvider(
        [
            sub_provider,
            Provider03,
            Provider04,
        ]
    )

    provider.init(a=A, b=B, c=C)
    provider.load_data()

    return provider


class FlatAdapterTestCase(TestCase):
    """Тестирование "плоского" адаптера."""

    def setUp(self):
        provider = setup_provider()
        self.adapter = FlatDataProviderAdapter(provider, splitter='__')

    def test_common(self):
        adapter = self.adapter
        self.assertTrue(adapter)
        self.assertEquals(len(self.adapter), PARAMS_COUNT)
        self.assertEqual(adapter.get('foo'), FOO)
        self.assertEqual(adapter.get('foo42', 42), 42)

    def test_contains(self):
        adapter = self.adapter
        self.assertIn('Provider03__param01', adapter)
        self.assertIn('Provider03__param02', adapter)
        self.assertIn('Provider03__param03', adapter)
        self.assertIn('Provider04__param01', adapter)
        self.assertIn('Provider04__param02', adapter)
        self.assertIn('Provider04__param03', adapter)
        self.assertIn('Main__Provider01__param01', adapter)
        self.assertIn('Main__Provider01__param02', adapter)
        self.assertIn('Main__Provider01__param03', adapter)
        self.assertIn('Main__Provider02__param01', adapter)
        self.assertIn('Main__Provider02__param02', adapter)
        self.assertIn('Main__Provider02__param03', adapter)
        self.assertIn('Main__bar', adapter)
        self.assertIn('foo', adapter)

        self.assertEquals(adapter['Provider03__param01'], A)
        self.assertEquals(adapter['Provider03__param02'], B)
        self.assertEquals(adapter['Provider03__param03'], C)
        self.assertEquals(adapter['Provider04__param01'], A)
        self.assertEquals(adapter['Provider04__param02'], B)
        self.assertEquals(adapter['Provider04__param03'], C)
        self.assertEquals(adapter['Main__Provider01__param01'], A)
        self.assertEquals(adapter['Main__Provider01__param02'], B)
        self.assertEquals(adapter['Main__Provider01__param03'], C)
        self.assertEquals(adapter['Main__Provider02__param01'], A)
        self.assertEquals(adapter['Main__Provider02__param02'], B)
        self.assertEquals(adapter['Main__Provider02__param03'], C)
        self.assertEquals(adapter['Main__Provider02__param04'], D)
        self.assertEquals(adapter['Main__bar'], BAR)
        self.assertEquals(adapter['foo'], FOO)

    def test_iter(self):
        adapter = self.adapter

        keys = list(adapter.keys())
        iter_keys = [k for k in adapter]
        self.assertEqual(keys, iter_keys)
        self.assertEqual(len(keys), PARAMS_COUNT)

        iteritems = [x for x in adapter.items()]
        self.assertEqual(len(iteritems), PARAMS_COUNT)
        for key, value in iteritems:
            self.assertEqual(value, adapter[key])

        items = list(adapter.items())
        for key, value in items:
            self.assertEqual(value, adapter[key])

        values = list(adapter.values())
        iter_values = [v for v in adapter.values()]
        self.assertEqual(values, iter_values)
        self.assertEqual(len(values), PARAMS_COUNT)


class NestedAdapterTestCase(TestCase):
    """Тестирование иерархического адаптера."""

    def setUp(self):
        provider = setup_provider()
        self.adapter = NestedDataProviderAdapter(provider)

    def test_common(self):
        adapter = self.adapter
        self.assertTrue(adapter)
        self.assertEquals(len(adapter), 4)
        self.assertEquals(len(adapter['Main']), 3)
        self.assertEquals(len(adapter['Main']['Provider01']), 3)
        self.assertEquals(len(adapter['Main']['Provider02']), 4)
        self.assertEquals(len(adapter['Provider03']), 3)
        self.assertEquals(len(adapter['Provider04']), 3)
        self.assertEqual(adapter.get('foo'), FOO)
        self.assertEqual(adapter.get('foo42', 42), 42)

    def test_contains(self):
        adapter = self.adapter
        self.assertIn('foo', adapter)
        self.assertIn('Main', adapter)
        self.assertIn('Provider01', adapter['Main'])
        self.assertIn('Provider02', adapter['Main'])
        self.assertIn('Provider03', adapter)
        self.assertIn('Provider04', adapter)

        self.assertEquals(adapter['Provider03']['param01'], A)
        self.assertEquals(adapter['Provider03']['param02'], B)
        self.assertEquals(adapter['Provider03']['param03'], C)
        self.assertEquals(adapter['Provider04']['param01'], A)
        self.assertEquals(adapter['Provider04']['param02'], B)
        self.assertEquals(adapter['Provider04']['param03'], C)
        self.assertEquals(adapter['Main']['Provider01']['param01'], A)
        self.assertEquals(adapter['Main']['Provider01']['param02'], B)
        self.assertEquals(adapter['Main']['Provider01']['param03'], C)
        self.assertEquals(adapter['Main']['Provider02']['param01'], A)
        self.assertEquals(adapter['Main']['Provider02']['param02'], B)
        self.assertEquals(adapter['Main']['Provider02']['param03'], C)
        self.assertEquals(adapter['Main']['Provider02']['param04'], D)
        self.assertEquals(adapter['Main']['bar'], BAR)
        self.assertEquals(adapter['foo'], FOO)

    def test_iter(self):
        adapter = self.adapter

        keys = list(adapter.keys())
        iter_keys = [k for k in adapter]
        self.assertEqual(keys, iter_keys)
        self.assertEqual(len(keys), 4)

        main_keys = list(adapter['Main'].keys())
        main_iter_keys = [k for k in adapter['Main']]
        self.assertEqual(main_keys, main_iter_keys)
        self.assertEqual(len(main_keys), 3)

        p3_keys = list(adapter['Provider03'].keys())
        p3_iter_keys = [k for k in adapter['Provider03']]
        self.assertEqual(p3_keys, p3_iter_keys)
        self.assertEqual(len(p3_keys), 3)

        p4_keys = list(adapter['Provider04'].keys())
        p4_iter_keys = [k for k in adapter['Provider04']]
        self.assertEqual(p4_keys, p4_iter_keys)
        self.assertEqual(len(p4_keys), 3)

        iteritems = [x for x in adapter.items()]
        self.assertEqual(len(iteritems), 4)
        for key, value in iteritems:
            self.assertEqual(value, adapter[key])

        items = list(adapter.items())
        self.assertEqual(len(items), 4)
        for key, value in items:
            self.assertEqual(value, adapter[key])

        main_iteritems = [x for x in adapter['Main'].items()]
        self.assertEqual(len(main_iteritems), 3)
        for key, value in main_iteritems:
            self.assertEqual(value, adapter['Main'][key])

        main_items = list(adapter['Main'].items())
        self.assertEqual(len(main_items), 3)
        for key, value in main_items:
            self.assertEqual(value, adapter['Main'][key])

        p3_iteritems = [x for x in adapter['Provider03'].items()]
        self.assertEqual(len(p3_iteritems), 3)
        for key, value in p3_iteritems:
            self.assertEqual(value, adapter['Provider03'][key])

        p3_items = [x for x in adapter['Provider03'].items()]
        self.assertEqual(len(p3_items), 3)
        for key, value in p3_items:
            self.assertEqual(value, adapter['Provider03'][key])

        p4_iteritems = [x for x in adapter['Provider04'].items()]
        self.assertEqual(len(p4_iteritems), 3)
        for key, value in p4_iteritems:
            self.assertEqual(value, adapter['Provider04'][key])

        p4_items = [x for x in adapter['Provider04'].items()]
        self.assertEqual(len(p4_items), 3)
        for key, value in p4_items:
            self.assertEqual(value, adapter['Provider04'][key])

        values = list(adapter.values())
        iter_values = [v for v in adapter.values()]
        self.assertEqual(values, iter_values)
        self.assertEqual(len(values), 4)

        main_values = list(adapter['Main'].values())
        main_iter_values = [k for k in adapter['Main'].values()]
        self.assertEqual(main_values, main_iter_values)
        self.assertEqual(len(main_values), 3)

        p1_values = list(adapter['Main']['Provider01'].values())
        p1_iter_values = [k for k in adapter['Main']['Provider01'].values()]
        self.assertEqual(p1_values, p1_iter_values)
        self.assertEqual(len(p1_values), 3)

        p2_values = list(adapter['Main']['Provider02'].values())
        p2_iter_values = [k for k in adapter['Main']['Provider02'].values()]
        self.assertEqual(p2_values, p2_iter_values)
        self.assertEqual(len(p2_values), 4)

        p3_values = list(adapter['Provider03'].values())
        p3_iter_values = [k for k in adapter['Provider03'].values()]
        self.assertEqual(p3_values, p3_iter_values)
        self.assertEqual(len(p3_values), 3)

        p4_values = list(adapter['Provider04'].values())
        p4_iter_values = [k for k in adapter['Provider04'].values()]
        self.assertEqual(p4_values, p4_iter_values)
        self.assertEqual(len(p4_values), 3)


# -----------------------------------------------------------------------------
# Тест зависимого провайдера


class LowLevel01(AbstractDataProvider):
    """Простой подпродвайдер."""

    data = None  # данные будут здесь

    def init(self, a, b, c, **params):
        self._a = a
        self._b = b
        self._c = c

    def load_data(self):
        self.data = self._a + self._b + self._c


class LowLevel02(AbstractDataProvider):
    """Простой подпродвайдер."""

    data = None  # данные будут здесь

    def init(self, d, e, **params):
        self._d = d
        self._e = e

    def load_data(self):
        self.data = self._d + self._e


class LowLevelDependent03(AbstractDataProvider):
    """
    Простой подпродвайдер.

    Зависит от данных LowLevel01.data и LowLevel02.data
    """

    def init(self, f, **params):
        self._f = f
        # придет снаружи
        self.a_b_c = None
        self.d_e = None

    def load_data(self):
        self.data = self.a_b_c + self.d_e + self._f


class HighLevelProvider(DependentCompositeProvider):
    """Композитный провайдер с описанием подпровайдеров."""

    providers_order = (
        ('_low_level_01', LowLevel01),
        ('_low_level_02', LowLevel02),
        ('_low_level_03', LowLevelDependent03),
    )

    _dependence_map = {
        '_low_level_03': {
            'a_b_c': ('_low_level_01', 'data'),
            'd_e': ('_low_level_02', 'data'),
        }
    }

    def init(self, g, **params):
        super(HighLevelProvider, self).init(**params)
        self._g = g

    def load_data(self):
        super(HighLevelProvider, self).load_data()
        self.data = self._g + self._low_level_03.data


class DependentProviderTestCase(TestCase):
    """Тестирование композитного провайдера с описанием подпровайдеров."""

    def setUp(self):
        self._initial_data = {
            'a': 1,
            'b': 2,
            'c': 3,
            'd': 4,
            'e': 5,
            'f': 6,
            'g': 7,
        }
        self.provider = HighLevelProvider()
        self.provider.init(**self._initial_data)

    def test_sum(self):
        """
        Сверка суммы.

        Подпровайдеры занимались суммой переданных им значений.
        Один из подпровайдеров (LowLevelDependent03) - зависим от данных
        LowLevel01 и LowLevel02
        """
        self.provider.load_data()

        self.assertEquals(self.provider.data, sum(self._initial_data.values()))
