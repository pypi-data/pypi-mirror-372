from feyn.plots._render._truncate_inputs import truncate_input_names, _compare, _spool, _is_region_cross_safe, isolate_interesting_regions
import unittest

class TestTruncateInputs(unittest.TestCase):

    def test_truncate_input_names(self):
        with self.subTest('truncate_input_names returns the best unique input names among a list of inputs'):
            inputs = ['Hello world',
                        'Hell freezes over',
                        'Hello kitty']

            lookback = 2
            truncs = truncate_input_names(inputs, trunc_size=4, lb=lookback)

            first_trunc = "..o wo.."
            second_trunc = "..ll f.."
            third_trunc = "..o ki.."


            self.assertEqual(first_trunc, truncs[0])
            self.assertEqual(second_trunc, truncs[1])
            self.assertEqual(third_trunc, truncs[2])

        with self.subTest('truncate_input_names does not add ellipses to start of names'):
            inputs = ['Hello world',
                        'Hell freezes over',
                        'Jello world']

            lookback = 2
            truncs = truncate_input_names(inputs, trunc_size=4, lb=lookback)

            first_trunc = "Hell.."
            second_trunc = "..ll f.."
            third_trunc = "Jell.."


            self.assertEqual(first_trunc, truncs[0])
            self.assertEqual(second_trunc, truncs[1])
            self.assertEqual(third_trunc, truncs[2])

        with self.subTest('truncate_input_names does not add .. suffix if it leads to longer string than original input name'):
            inputs = ['ABCDEFGH', 'ABCDEFGHI', 'ABCDEFGHIJ', 'ABCDEFGHIJK']
            truncs = truncate_input_names(inputs, trunc_size=8)
            self.assertEqual(truncs[0], inputs[0])
            self.assertEqual(truncs[1], inputs[1])
            self.assertEqual(truncs[2], inputs[2])
            self.assertEqual(truncs[3], "ABCDEFGH..")


    def test_isolate_interesting_regions(self):
        with self.subTest('isolate_interesting_regions finds the best unique regions of a input to show across other inputs'):
            inputs = ['Hello world',
                        'Hell freezes over',
                        'Hello kitty']

            lookback = 2
            regions = isolate_interesting_regions(inputs, trunc_size=4, lb=lookback)

            first_expected_region = 6 - lookback
            second_expected_region = 4 - lookback
            third_expected_region = 6 - lookback

            self.assertEqual(first_expected_region, regions[0])
            self.assertEqual(second_expected_region, regions[1])
            self.assertEqual(third_expected_region, regions[2])

        with self.subTest('isolate_interesting_regions defaults back to 0 if input names are equal'):
            inputs = ['Hello world',
                        'Hello world']

            lookback = 2
            regions = isolate_interesting_regions(inputs, trunc_size=4, lb=lookback)

            first_expected_region = 0
            second_expected_region = 0

            self.assertEqual(first_expected_region, regions[0])
            self.assertEqual(second_expected_region, regions[1])

        with self.subTest('isolate_interesting_regions defaults back to 0 if no cross-safe regions are found among strings'):
            inputs = ['Hello world',
                        'Hell freezes over',
                        'Jello world']

            lookback = 2
            regions = isolate_interesting_regions(inputs, trunc_size=4, lb=lookback)

            first_expected_region = 0
            second_expected_region = 4 - lookback
            third_expected_region = 0

            self.assertEqual(first_expected_region, regions[0])
            self.assertEqual(second_expected_region, regions[1])
            self.assertEqual(third_expected_region, regions[2])


    def test_is_region_cross_safe(self):
        with self.subTest('is_region_cross_safe returns False if the region is not unique across all strings'):
            first  = "Hello world"
            second = "Hell freezes over"
            third  = "Jello world"

            start_region = _spool(first, second, lb=2)
            self.assertEqual(2, start_region)

            self.assertFalse(_is_region_cross_safe(first, [second, third], start_region, trunc_size=4))

        with self.subTest('is_region_cross_safe returns True if the region is unique across all strings'):
            first  = "Hello world"
            second = "Hell freezes over"
            third  = "Jelly world"

            start_region = _spool(first, second, lb=2)
            self.assertEqual(2, start_region)

            self.assertTrue(_is_region_cross_safe(first, [second, third], start_region, trunc_size=4))

    def test_spool(self):
        with self.subTest('Spool fast-forwards to the first region of difference, and rewinds to the lookback'):
            first = "Hello world"
            other = "Hell freezes over"
            lookback = 1
            region_start = 4 - lookback
            self.assertEqual(region_start, _spool(first, other, lb=lookback))

        with self.subTest('Spool returns 0 if strings are equal'):
            first = "Hello world"
            other = "Hello world"
            lookback = 1
            region_start = 0
            self.assertEqual(region_start, _spool(first, other, lb=lookback))

        with self.subTest('Spool returns 0 if position is early and lookback is further than beginning'):
            first = "Hello world"
            other = "Hola mundo"
            lookback = 2
            region_start = 0
            self.assertEqual(region_start, _spool(first, other, lb=lookback))

        with self.subTest('Spool returns 0 if words are completely different'):
            first = "Hello world"
            other = "Saluton mundo"
            lookback = 2
            region_start = 0
            self.assertEqual(region_start, _spool(first, other, lb=lookback))

    def test_compare(self):
        with self.subTest('Compare returns -1 if equal'):
            me = "Hello"
            other = "Hello"
            self.assertEqual(-1, _compare(me, other, trunc_size=8))
        with self.subTest('Compare returns 0 if the beginnings are different'):
            me = "Hello"
            other = "World"
            self.assertEqual(0, _compare(me, other, trunc_size=8))

        with self.subTest('Compare returns 1 if the beginnings are equal'):
            me = "Hello"
            other = "Hell"
            beginning_size = 4
            self.assertEqual(1, _compare(me, other, trunc_size=beginning_size))
