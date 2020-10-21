from unittest import TestCase

import pandas as pd

from dplib.stream import Stream, SeriesStream

class TestStream(TestCase):
    def test_series_stream(self):
        stream = SeriesStream(pd.Series([1,2,3,4]))
        time, value = stream.get()
        self.assertEqual((time, value), (0, 1))
        time, value = stream.get()
        self.assertEqual((time, value), (1, 2))
        time, value = stream.get()
        self.assertEqual((time, value), (2, 3))
        self.assertTrue(stream.has_values())        
        time, value = stream.get()
        self.assertEqual((time, value), (3, 4))
        self.assertFalse(stream.has_values())
    
    def test_list_stream_get(self):
        stream = Stream(range(5))
        xs = []
        xs.append(stream.get())
        xs.append(stream.get())
        xs.append(stream.get())
        xs.append(stream.get())
        xs.append(stream.get())
        self.assertEqual(xs, list(range(5)))

    def test_list_stream_unget(self):
        stream = Stream('abc')
        xs = []
        xs.append(stream.get())
        xs.append(stream.get())
        stream.unget()        
        xs.append(stream.get())
        xs.append(stream.get())
        self.assertEqual(xs, ['a', 'b', 'b', 'c'])

    def test_list_stream_has_values(self):
        stream = Stream('a')
        self.assertTrue(stream.has_values())
        stream.get()
        self.assertFalse(stream.has_values())

    def test_list_stream_save_restore(self):
        stream = Stream('abcdefg')
        stream.get()
        stream.get()
        stream.save()
        stream.get()
        stream.get()
        stream.restore()
        self.assertEqual(stream.get(), 'c')

test_suite = TestStream
