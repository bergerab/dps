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

        def get_json(self, r, removes=None):
            if removes:
                return self.remove_fields(r.json(), removes)
            return self.remove_fields(r.json())            

        def remove_fields(self, d0, removes=['created_at', 'updated_at']):
            d1 = {}
            for key in d0:
                if key in removes: continue
                val = d0[key]
                if isinstance(val, dict):
                    val = self.remove_fields(val, removes)
                d1[key] = val
            return d1
            
        def delete_object(self, kind, id_name, response):
            self.validate_status_code(client.DELETE(kind + '/' + str(response.json()[id_name])))

        def assertObjectEqual(self, id_name, obj, expected_obj):
            skip = ['created_at', 'updated_at', id_name]
            d0 = self.remove_fields(obj, removes=skip)
            d1 = self.remove_fields(expected_obj)
            for key in expected_obj:
                if key in skip: continue
                d1[key] = expected_obj[key]
            self.assertEqual(d0, d1)
            self.assertGreater(obj[id_name], 0)
        
        def validate_status_code(self, response):
            if not 300 > response.status_code >= 200:
                if response.headers.get('content-type') == 'application/json':
                    print(response.json())
                else:
                    print(response)
            self.assertTrue(300 > response.status_code >= 200)

        # def test_get_and_post_systems(self):
        #     # Test with no KPIs and no parameters (just a name)
        #     r = client.POST('system', {
        #         'name': 'My Name',
        #     })
        #     self.validate_status_code(r)
        #     id = r.json()['system_id']
        #     self.assertObjectEqual('system_id', r.json(), {
        #         'name': 'My Name',
        #         'kpis': [],
        #         'parameters': [],
        #     })
        #     get_r = client.GET('system/' + str(id))
        #     self.validate_status_code(get_r)
        #     self.assertEqual(self.get_json(get_r), {
        #         'system_id': id,
        #         'name': 'My Name',
        #         'kpis': [],
        #         'parameters': [],
        #     })
        #     self.delete_object('system', 'system_id', r)

        #     # Test with one KPI
        #     r = client.POST('system', {
        #         'name': 'System With KPIs',
        #         'kpis': [ KPI1 ]
        #     })
        #     self.validate_status_code(r)
        #     id = r.json()['system_id']                        
        #     self.assertObjectEqual('system_id', r.json(), {
        #         'name': 'System With KPIs',
        #         'kpis': [ KPI1 ],
        #         'parameters': [],
        #     })
        #     get_r = client.GET('system/' + str(id))
        #     self.validate_status_code(get_r)
        #     self.assertEqual(get_r.json(), {
        #         'system_id': id,
        #         'name': 'System With KPIs',
        #         'kpis': [ KPI1 ],
        #         'parameters': [],
        #     })
        #     self.delete_object('system', 'system_id', r)

        #     # Test with KPIs and parameters
        #     r = client.POST('system', {
        #         'name': 'System With KPIs and parameters',
        #         'kpis': [
        #             KPI1,
        #             KPI2,
        #         ],
        #         'parameters': [
        #             PARAM1,
        #             PARAM2,
        #         ]
        #     })
        #     self.validate_status_code(r)
        #     id = r.json()['system_id']                                    
        #     self.assertObjectEqual('system_id', r.json(), {
        #         'name': 'System With KPIs and parameters',
        #         'kpis': [
        #             KPI1,
        #             KPI2,
        #         ],
        #         'parameters': [
        #             PARAM1,
        #             PARAM2,
        #         ],
        #     })
        #     get_r = client.GET('system/' + str(id))
        #     self.validate_status_code(get_r)
        #     self.assertEqual(get_r.json(), {
        #         'system_id': id,
        #         'name': 'System With KPIs and parameters',
        #         'kpis': [
        #             KPI1,
        #             KPI2,
        #         ],
        #         'parameters': [
        #             PARAM1,
        #             PARAM2,
        #         ],
        #     })
        #     self.delete_object('system', 'system_id', r)

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
            self.assertObjectEqual('system_id', self.get_json(r), {
                'name': 'Name 2',
                'kpis': [],
                'parameters': [],
            })
            get_r = client.GET('system/' + str(id))
            self.validate_status_code(get_r)
            self.assertEqual(self.get_json(get_r), {
                'system_id': id,
                'name': 'Name 2',
                'kpis': [],
                'parameters': [],
            })
            self.delete_object('system', 'system_id', r)

        # def test_get_and_post_batch_processes(self):
        #     system_r = client.POST('system', {
        #         'name': 'Name 1',
        #     })
        #     self.validate_status_code(system_r)
        #     system_id = system_r.json()['system_id']
            
        #     datetime_string1 = '2023-10-06 14:00:04.002000'
        #     datetime_string2 = '2023-10-08 14:00:04.002000'
        #     KPIS = [
        #         'KPI1', 'KPI2',
        #     ]
        #     INTERVAL = {
        #         'start': datetime_string1,
        #         'end': datetime_string2,
        #     }
        #     MAPPINGS = [
        #         {
        #             'key': 'A',
        #             'value': 'My A',
        #         },
        #         {
        #             'key': 'B',
        #             'value': 'My B',
        #         }
        #     ]
        #     r = client.POST('batch_process', {
        #         'system_id': system_id,
        #         'system': system_r.json(),
        #         'interval': INTERVAL,
        #         'kpis': KPIS,
        #         'mappings': MAPPINGS,                                     
        #     })
        #     self.validate_status_code(r)
        #     id = r.json()['batch_process_id']                                                
        #     self.assertObjectEqual('batch_process_id', r.json(), {
        #         'system_id': system_id,
        #         'system': self.get_json(system_r, ['created_at', 'updated_at', 'system_id']),
        #         'interval': INTERVAL,
        #         'kpis': KPIS,
        #         'mappings': MAPPINGS,                
        #     })
        #     get_r = client.GET('batch_process/' + str(id))
        #     self.validate_status_code(get_r)
        #     self.assertEqual(get_r.json(), {
        #         'system_id': system_id,
        #         'system': system_r.json(),                
        #         'batch_process_id': id,
        #         'interval': INTERVAL,
        #         'kpis': KPIS,
        #         'mappings': MAPPINGS,                     
        #     })
        #     self.delete_object('batch_process', 'batch_process_id', r)
        #     self.delete_object('system', 'system_id', system_r)            

        def test_get_and_post_progress(self):
            system_r = client.POST('system', {
                'name': 'Name 1',
            })
            self.validate_status_code(system_r)
            system_id = system_r.json()['system_id']
            
            datetime_string1 = '2023-10-06 14:00:04.002000'
            datetime_string2 = '2023-10-07 14:00:04.002000'
            datetime_string3 = '2023-10-08 14:00:04.002000'

            KPIS = [
                'KPI1', 'KPI2',
            ]
            MAPPINGS = [
                {
                    'key': 'B',
                    'value': 'My B',
                }
            ]

            # First make a batch process we can reference
            batch_process_r = client.POST('batch_process', {
                'system_id': system_id,
                'system': system_r.json(),                
                'kpis': KPIS,
                'mappings': MAPPINGS,                     
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
            self.assertEqual(self.get_json(get_r), {
                'progress_id': id,
                'state': 'anything',
                'time': datetime_string2,
                'batch_process_id': batch_process_id,
            })
            
            self.delete_object('progress', 'progress_id', r)
            self.delete_object('batch_process', 'batch_process_id', batch_process_r)
            self.delete_object('system', 'system_id', system_r)            

    return TestDPSManager
