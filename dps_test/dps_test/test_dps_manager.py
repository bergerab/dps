from datetime import datetime
import unittest

KPI1 = {
    'name': 'KPI1',
    'computation': 'A + B',
}

KPI2 = {
    'name': 'KPI2',
    'computation': 'C',
    'description': 'Just C',
    'hidden': True,
}
PARAM1 = {
    'name': 'Ioc',
    'default': '2',
}
PARAM2 = {
    'name': 'Voc',
    'description': 'Blah',
}

def make_test_case(client):
    class TestDPSManager(unittest.TestCase):
        def __init__(self, *args, **kwargs):
            super(TestDPSManager, self).__init__(*args, **kwargs)
            self.maxDiff = None

        def delete_object(self, kind, id_name, response):
            self.validate_status_code(client.DELETE(kind + '/' + str(response.json()[id_name])))

        def assertObjectEqual(self, id_name, obj, expected_obj):
            d = {}
            for key in obj:
                if key != id_name:
                    d[key] = obj[key]
            self.assertEqual(d, expected_obj)
            self.assertGreater(obj[id_name], 0)
        
        def validate_status_code(self, response):
            if not 300 > response.status_code >= 200:
                if response.headers.get('content-type') == 'application/json':
                    print(response.json())
                else:
                    print(response)
            self.assertTrue(300 > response.status_code >= 200)

        def test_get_and_post_systems(self):
            # Test with no KPIs and no parameters (just a name)
            r = client.POST('system', {
                'name': 'My Name',
            })
            self.validate_status_code(r)
            id = r.json()['system_id']
            self.assertObjectEqual('system_id', r.json(), {
                'name': 'My Name',
                'kpis': [],
                'parameters': [],
            })
            get_r = client.GET('system/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(get_r.json(), {
                'system_id': id,
                'name': 'My Name',
                'kpis': [],
                'parameters': [],
            })
            self.delete_object('system', 'system_id', r)

            # Test with one KPI
            r = client.POST('system', {
                'name': 'System With KPIs',
                'kpis': [ KPI1 ]
            })
            self.validate_status_code(r)
            id = r.json()['system_id']                        
            self.assertObjectEqual('system_id', r.json(), {
                'name': 'System With KPIs',
                'kpis': [ KPI1 ],
                'parameters': [],
            })
            get_r = client.GET('system/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(get_r.json(), {
                'system_id': id,
                'name': 'System With KPIs',
                'kpis': [ KPI1 ],
                'parameters': [],
            })
            self.delete_object('system', 'system_id', r)

            # Test with KPIs and parameters
            r = client.POST('system', {
                'name': 'System With KPIs and parameters',
                'kpis': [
                    KPI1,
                    KPI2,
                ],
                'parameters': [
                    PARAM1,
                    PARAM2,
                ]
            })
            self.validate_status_code(r)
            id = r.json()['system_id']                                    
            self.assertObjectEqual('system_id', r.json(), {
                'name': 'System With KPIs and parameters',
                'kpis': [
                    KPI1,
                    KPI2,
                ],
                'parameters': [
                    PARAM1,
                    PARAM2,
                ],
            })
            get_r = client.GET('system/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(get_r.json(), {
                'system_id': id,
                'name': 'System With KPIs and parameters',
                'kpis': [
                    KPI1,
                    KPI2,
                ],
                'parameters': [
                    PARAM1,
                    PARAM2,
                ],
            })
            self.delete_object('system', 'system_id', r)

        def test_put_systems(self):
            r = client.POST('system', {
                'name': 'Name 1',
            })
            self.validate_status_code(r)
            self.assertObjectEqual('system_id', r.json(), {
                'name': 'Name 1',
                'kpis': [],
                'parameters': [],
            })
            r = client.PUT('system/' + str(r.json()['system_id']), {
                'name': 'Name 2',
            })
            self.validate_status_code(r)
            id = r.json()['system_id']                                                
            self.assertObjectEqual('system_id', r.json(), {
                'name': 'Name 2',
                'kpis': [],
                'parameters': [],
            })
            get_r = client.GET('system/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(get_r.json(), {
                'system_id': id,
                'name': 'Name 2',
                'kpis': [],
                'parameters': [],
            })
            self.delete_object('system', 'system_id', r)

        def test_get_and_post_batch_processes(self):
            datetime_string1 = '2023-10-06 14:00:04.002000'
            datetime_string2 = '2023-10-08 14:00:04.002000'
            KPIS = [
                KPI1, KPI2,
            ]
            INTERVAL = {
                'start': datetime_string1,
                'end': datetime_string2,
            }
            MAPPINGS = [
                {
                    'key': 'A',
                    'value': 'My A',
                },
                {
                    'key': 'B',
                    'value': 'My B',
                }
            ]
            r = client.POST('batch_process', {
                'interval': INTERVAL,
                'kpis': KPIS,
                'mappings': MAPPINGS,                                     
            })
            self.validate_status_code(r)            
            id = r.json()['batch_process_id']                                                
            self.assertObjectEqual('batch_process_id', r.json(), {
                'interval': INTERVAL,
                'kpis': KPIS,
                'mappings': MAPPINGS,                
            })
            get_r = client.GET('batch_process/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(get_r.json(), {
                'batch_process_id': id,
                'interval': INTERVAL,
                'kpis': KPIS,
                'mappings': MAPPINGS,                     
            })
            self.delete_object('batch_process', 'batch_process_id', r)

        def test_get_and_post_progress(self):
            datetime_string1 = '2023-10-06 14:00:04.002000'
            datetime_string2 = '2023-10-07 14:00:04.002000'
            datetime_string3 = '2023-10-08 14:00:04.002000'

            # First make a batch process we can reference
            batch_process_r = client.POST('batch_process', {
                'interval': {
                    'start': datetime_string1,
                    'end': datetime_string3,
                }
            })
            self.validate_status_code(batch_process_r)            
            batch_process_id = batch_process_r.json()['batch_process_id']                                                
            
            r = client.POST('progress', {
                'state': 'anything',
                'time': datetime_string2,
                'batch_process_id': batch_process_id,
            })
            self.validate_status_code(r)
            id = r.json()['progress_id']                                                
            self.assertObjectEqual('progress_id', r.json(), {
                'state': 'anything',
                'time': datetime_string2,
                'batch_process_id': batch_process_id,
            })
            get_r = client.GET('progress/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(get_r.json(), {
                'progress_id': id,
                'state': 'anything',
                'time': datetime_string2,
                'batch_process_id': batch_process_id,
            })
            
            self.delete_object('progress', 'progress_id', r)
            self.delete_object('batch_process', 'batch_process_id', batch_process_r)

    return TestDPSManager
