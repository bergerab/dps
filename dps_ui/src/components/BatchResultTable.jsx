import React from 'react';

import Button from '@material-ui/core/Button';
import LinearProgress from '@material-ui/core/LinearProgress';
import MaterialTable from 'material-table';

import Box from './Box';
import Row from './Row';
import Link from './Link';
import LinearProgressWithLabel from './LinearProgressWithLabel';
import api from '../api';
import ConfirmationDialog from './ConfirmationDialog';

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
    this.tableRef = React.createRef();
  }

  componentDidMount() {
    // this.intervalId = setInterval(() => {
    //   this.tableRef.current.onQueryChange();
    // }, 10000);
  }

  componentWillUnmount() {
    // clearInterval(this.intervalId);
  }  
  
  render () {
    return (
      <MaterialTable
        icons={tableIcons}
        title="Batch Processes"
        tableRef={this.tableRef}
        options={{
          search: true,
          sorting: true,
          exportButton: false,
          pageSize: 5,
        }}          
        actions={[
          {
            icon: Refresh,
            tooltip: 'Refresh Data',
            isFreeAction: true,
            onClick: () => this.tableRef.current && this.tableRef.current.onQueryChange(),
          }
        ]}          
        columns={[
          { title: 'Name',
            field: 'name',
            render: data => {
              return data.batch_process.name;
            },
            sorting: false
          },
          { title: 'Ran At',
            field: 'batch_process_time',
            render: data => {
              return moment(Date.parse(data.batch_process_time)).format('LL LTS');
            },
            defaultSort: 'desc',
            sorting: false,
          },
          /* { title: 'Total Samples', */
          /*   field: 'total_samples', */
          /*   sorting: false, */
          /* }, */
          { title: 'Samples Processed',
            field: 'processed_samples',
            sorting: false,
            render: data => {
              if (!data.processed_samples) return data.processed_samples
              return data.processed_samples.toLocaleString();
            }
          },
          { title: 'Status',
            sorting: false,
            render: data => {
              if (data.status === 1) { // If running,
                let progress = 0;
                if (data.total_samples > 0)
                  progress = (data.processed_samples / data.total_samples) * 100
                return (
                  <LinearProgressWithLabel variant="determinate" value={progress} />
                );
              } else if (data.status === 0) { // If error,
                return (
                  <LinearProgressWithLabel variant="determinate" color="secondary" label={"Error"} value={100} />
                );
              } else if (data.status === 2) { // If complete,
                return (
                  <LinearProgressWithLabel variant="determinate" value={100} />
                );
              } else if (data.status === 3) { // If queued,
                return (
                  <LinearProgressWithLabel label="Queued" value={0} />
                );
              }
            }},
          {
            title: '',
            sorting: false,
            render: data => {
              return (
                <div style={{textAlign: 'right' }}>
                  <span style={{ display: 'inline-flex' }}>
                    <Link to={"/batch-process/" + data.batch_process_id}>
                      <Button variant="outlined"
                              color="primary"
                              style={{ marginRight: '10px' }}>
                        View
                      </Button>
                    </Link>

                    <ConfirmationDialog
	              header={`Delete "${data.batch_process.name}"?`}
                      deleteObj={() => {
                        api.delete_batch_process(data.batch_process_id).then(() => {
                          this.tableRef.current.onQueryChange();
                        });
                      }}
                    >
	              Are you sure you want to delete this batch process? This action is irreversible.
                    </ConfirmationDialog>

                  </span>

                </div>
              )
            }
          }
        ]}
        data={query =>
              new Promise((resolve, reject) => {
                api.post('batch_process_results', { 'page_size':       query.pageSize,
                                                    'page_number':     query.page,
                                                    'search':          query.search,
                                                    'system_id':       this.props.system_id,
                                                    'order_direction': query.orderDirection,
                                                  })
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
