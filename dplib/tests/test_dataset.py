from unittest import TestCase
from datetime import datetime, timedelta

from dplib.testing import DatasetAssertions
from dplib.series import Series, Dataset

NOW = datetime.now()
def make_series(x):
    if not isinstance(x, list):
        x = [x]
    return Series(x, [NOW for i in x])

class TestDataset(TestCase, DatasetAssertions):
    def test_dataset_get(self):
        self.assertSeriesEqual(
            Dataset({
                'a': make_series(1),
                'b': make_series(2),                                
            }).get('a'), make_series(1))

        self.assertSeriesEqual(
            Dataset({
                'a': make_series(1),
                'b': make_series(2),                                
            }).get('b'), make_series(2))
    
    def test_dataset_has(self):
        self.assertTrue(
            Dataset({
                'a': make_series(1),
                'b': make_series(2),                                
            }).has('a'))

        self.assertFalse(
            Dataset({
                'a': make_series(1),
                'b': make_series(2),                                
            }).has('c'))
    
    def test_dataset_set(self):
        def make_dataset():
            return Dataset({
                'a': make_series(1),
            })

        self.assertDatasetEqual(
            make_dataset().set('b', make_series(2)),
            Dataset({
                'a': make_series(1),
                'b': make_series(2),                                
            }))

        self.assertDatasetEqual(
            make_dataset().set('a', make_series(2)),
            Dataset({
                'a': make_series(2),
            }))
    
    def test_dataset_merge(self):
        D1 = Dataset({
            'a': make_series(1),
            'b': make_series(2),
            'c': make_series(3),
        })
        
        D2 = Dataset({
            'd': make_series(4),
            'e': make_series(5),
            'f': make_series(6),
        })
        
        D3 = Dataset({
            'a': make_series(7),
            'b': make_series(8),
            'c': make_series(9),
        })
        
        self.assertDatasetEqual(
            D1.merge(D2),
            Dataset({
                'a': make_series(1),
                'b': make_series(2),
                'c': make_series(3),
                'd': make_series(4),
                'e': make_series(5),
                'f': make_series(6),
            }))

        self.assertDatasetEqual(
            D1.merge(D3),
            Dataset({
                'a': make_series([1, 7]),
                'b': make_series([2, 8]),
                'c': make_series([3, 9]),
            }))
    
    def test_dataset_select(self):
        D = Dataset({
            'a': Series([1]),
            'b': Series([2]),
            'c': Series([3]),                
        })
        self.assertDatasetEqual(
            D.select(['a', 'b']),
            Dataset({
                'a': Series([1]),
                'b': Series([2]),
            }))

        self.assertDatasetEqual(
            D.select(['c']),
            Dataset({
                'c': Series([3]),
            }))

        self.assertDatasetEqual(
            D.select([]),
            Dataset())

        self.assertDatasetEqual(
            D.select(['a', 'b', 'c']),
            Dataset({
                'a': Series([1]),
                'b': Series([2]),
                'c': Series([3]),                
            }))

    def test_dataset_rename(self):
        self.assertDatasetEqual(
            Dataset({
                'a': Series([1])
            }).rename({ 'a': 'b' }),
            Dataset({
                'b': Series([1])
            }))
    
    def test_dataset_eq(self):
        self.assertEqual(Dataset({
            'a': Series([1])
        }), Dataset({
            'a': Series([1])
        }))

        self.assertFalse(Dataset({
            'a': Series([3])
        }) == Dataset({
            'a': Series([1])
        }))

        self.assertFalse(Dataset({
            'a': Series([1])
        }) == Dataset({
            'b': Series([1])
        }))

test_suite = TestDataset
