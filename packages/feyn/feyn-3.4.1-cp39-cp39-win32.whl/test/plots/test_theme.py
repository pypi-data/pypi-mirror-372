import unittest

from feyn import Theme


class TestTheme(unittest.TestCase):

    def test_cycler_returns_list_of_colors(self):
        colors = Theme.cycler()

        self.assertEqual(len(colors), 7)

    def test_cycler_cycles(self):
        colors = Theme.cycler()
        max_len = len(colors)

        color = Theme.cycler(0)
        self.assertEqual(color, "#4646E6")

        color = Theme.cycler(1)
        self.assertEqual(color, "#FF1EC8")

        color = Theme.cycler(max_len)
        self.assertEqual(color, "#4646E6")

    def test_set_theme(self):
        theme = Theme._get_current()
        self.assertEqual(type(theme).__name__, "FeynTheme")
        self.assertEqual(theme.dark_mode, False)

        self.assertEqual(Theme._theme, "default")

        light = Theme.color("light")
        dark = Theme.color("dark")
        self.assertEqual(light, "#FAFAFA")
        self.assertEqual(dark, "#1E1E1E")

        Theme.set_theme("dark")

        self.assertEqual(Theme._theme, "dark")

        theme = Theme._get_current()
        self.assertEqual(type(theme).__name__, "FeynTheme")
        self.assertEqual(theme.dark_mode, True)

        light = Theme.color("light")
        dark = Theme.color("dark")
        self.assertEqual(dark, "#FAFAFA")
        self.assertEqual(light, "#1E1E1E")

    def test_flip_cmap(self):
        cmap = Theme._get_current().cmaps["feyn-diverging"]

        Theme.flip_cmap("feyn-diverging")

        flipped_cmap = Theme._get_current().cmaps["feyn-diverging"]

        self.assertEqual(cmap[::-1], flipped_cmap)
