import React from 'react';

import Button from '@material-ui/core/Button';
import LinearProgress from '@material-ui/core/LinearProgress';
import MaterialTable from 'material-table';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import LinearProgressWithLabel from './LinearProgressWithLabel';
import api from '../api';

import moment from 'moment';

import { forwardRef } from 'react';

import AddBox from '@material-ui/icons/AddBox';
import ArrowDownward from '@material-ui/icons/ArrowDownward';
import Refresh from '@material-ui/icons/Refresh';
import Check from '@material-ui/icons/Check';
import ChevronLeft from '@material-ui/icons/ChevronLeft';
import ChevronRight from '@material-ui/icons/ChevronRight';
import Clear from '@material-ui/icons/Clear';
import DeleteOutline from '@material-ui/icons/DeleteOutline';
import Edit from '@material-ui/icons/Edit';
import FilterList from '@material-ui/icons/FilterList';
import FirstPage from '@material-ui/icons/FirstPage';
import LastPage from '@material-ui/icons/LastPage';
import Remove from '@material-ui/icons/Remove';
import SaveAlt from '@material-ui/icons/SaveAlt';
import Search from '@material-ui/icons/Search';
import ViewColumn from '@material-ui/icons/ViewColumn';

const tableIcons = {
  Add: forwardRef((props, ref) => <AddBox {...props} ref={ref} />),
  Check: forwardRef((props, ref) => <Check {...props} ref={ref} />),
  Clear: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
  Refresh: forwardRef((props, ref) => <Refresh {...props} ref={ref} />),  
  Delete: forwardRef((props, ref) => <DeleteOutline {...props} ref={ref} />),
  DetailPanel: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
  Edit: forwardRef((props, ref) => <Edit {...props} ref={ref} />),
  Export: forwardRef((props, ref) => <SaveAlt {...props} ref={ref} />),
  Filter: forwardRef((props, ref) => <FilterList {...props} ref={ref} />),
  FirstPage: forwardRef((props, ref) => <FirstPage {...props} ref={ref} />),
  LastPage: forwardRef((props, ref) => <LastPage {...props} ref={ref} />),
  NextPage: forwardRef((props, ref) => <ChevronRight {...props} ref={ref} />),
  PreviousPage: forwardRef((props, ref) => <ChevronLeft {...props} ref={ref} />),
  ResetSearch: forwardRef((props, ref) => <Clear {...props} ref={ref} />),
  Search: forwardRef((props, ref) => <Search {...props} ref={ref} />),
  SortArrow: forwardRef((props, ref) => <ArrowDownward {...props} ref={ref} />),
  ThirdStateCheck: forwardRef((props, ref) => <Remove {...props} ref={ref} />),
  ViewColumn: forwardRef((props, ref) => <ViewColumn {...props} ref={ref} />)
};

export default class BatchResultTable extends React.Component {
  constructor(props) {
    super(props);
  }
  
  render () {
    const tableRef = React.createRef();
    return (
      <MaterialTable
        icons={tableIcons}
        title="Batch Processes"
        tableRef={tableRef}
        options={{
          search: false,
          sorting: false,
          exportButton: false,
          pageSize: 5,
        }}          
        actions={[
          {
            icon: Refresh,
            tooltip: 'Refresh Data',
            isFreeAction: true,
            onClick: () => tableRef.current && tableRef.current.onQueryChange(),
          }
        ]}          
        columns={[
          { title: 'Name',
            field: 'name',
            render: data => {
              return data.batch_process.name;
            }
          },
          { title: 'Ran At',
            field: 'batch_process_time',
            render: data => {
              return moment(Date.parse(data.batch_process_time)).format('LL LTS');
            }
            },
            { title: 'Total Samples',
              field: 'total_samples',
            },
            { title: 'Processed Samples',
              field: 'processed_samples',
            },
            { title: 'Status', render: data => {
              if (data.status === 1) { // If running,
                let progress = 0;
                if (data.total_samples > 0)
                  progress = (data.processed_samples / data.total_samples) * 100
                return (
                  <LinearProgressWithLabel variant="determinate" value={progress} />
                );
              } else if (data.status === 0) { // If error,
                return (
                  <div style={{ color: 'red' }}>
                    Failed
                    <div>
                      {data.message}
                    </div>
                  </div>
                );
              } else if (data.status === 2) { // If complete,
                return (
                  <LinearProgressWithLabel variant="determinate" value={100} />
                );
              } else if (data.status === 3) { // If queued,
                return (
                  <LinearProgressWithLabel label="Queued" />
                );
              }
            }},
            {
              title: '',
              render: data => {
                return (
                  <Link to={"/batch-process/" + data.batch_process_id}>
                    <Button variant="outlined"
                            color="primary"
                            style={{ marginRight: '10px' }}>
                      View
                    </Button>
                  </Link>
                )
              }
            }
          ]}
          data={query =>
                new Promise((resolve, reject) => {
                  api.post('batch_process_results', { 'page_size':   query.pageSize,
                                                      'page_number': query.page,
                                                      'system_id':   this.props.system_id})
                    .then(result => {
                      resolve({
                        data: result.data,
                        page: result.page,
                        totalCount: result.total,
                      })
                    })
                })
               }
        />        
    );
  }
}
