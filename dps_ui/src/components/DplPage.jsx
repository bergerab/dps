import React from 'react';

import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';

import {
  TimePicker,
} from '@material-ui/pickers';

import Box from './Box';
import Row from './Row';
import SignalChart from './Chart';
import SignalTable from './SignalTable';
import BarChart from './BarChart';
import Link from './Link';
import InputLabel from './InputLabel';
import PrettyTable from './PrettyTable';
import EntityTable from './EntityTable';
import DatasetSelect from './DatasetSelect';
import Loader from './Loader';

import NotFound from './NotFound';

import api from '../api';

export default class APIKeyPage extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Box header="Data Processing Language (DPL)">
        <p>
          DPL is a domain specific programming language for expressing computations on signals. It is based on Python, and has similar syntax, but different semantics. The semantics differ because DPL programs run within the context of a DPS System (the entities found on the "Systems" page). Systems tell DPL which symbols correspond with input parameters, the value of the input parameters, which symbols correspond with KPIs, and pass input signals into the DPL program.
        </p>
        <h2>Types</h2>
        <p>
          DPL includes typical built-in types as Python (e.g. number, boolean, string). But it also includes two special datatypes: aggregations and signals.
        </p>
        <h3>Signals</h3>        
        <p>
          Signals represent a stream if values that can have an arbitrary length. For example the list of 1, 2, 3, and 4 is a stream, and so is the list of whole numbers from 0 to infinity. In DPL, any free variable (a variable that is not a built-in, or defined within the system it is running as a parameter), denotes a signal. Signals are made up of datapoints which have a value, and an absolute timestamp. For example, the following program expresses addition between two signals.
        </p>
        <pre>
          <code>
            A + B
          </code>
        </pre>
        <p>
          The result of this program is a new signal which contains the addition of each value in the signals that has the same absolute timestamp. By looking at the code alone, it is unclear what the result will be, because it depends on the input data.
        </p>
        <h3>Aggregations</h3>
        <p>
          Aggregations are single value results which summarize some information about a signal. Aggregations are created by calling built-in functions such as "avg", "min", or "max" which take signals and produce aggregations. They are shown on the batch process view page in a table and serve as the final KPI value. When defining a system, ensure that any values that should be displayed on the final KPI table is an Aggregation. Otherwise, the values will not be shown on the table (because there is no single value to show -- only a signal of values).
        </p>
        <p>
          Aggregations propagate the signal values that they are aggregating on in a hidden signal. This value is shown on charts in the batch process view page. These charts show the aggregation's input signal value (and not the intermediate aggregation values). This is contrary to intuition (e.g. the chart for "min(A * B)" will show "A * B" over time -- and not the minimum of A * B over time). This is because aggregations do not save their intermediate aggregation values, only their intermediate input signal values. It was implemented this way because no KPIs we needed required behavior. The values must be propagated in order to allow composing aggregations with Signals, and aggregations with other aggregations. If needed, this behavior could be implemented to match the user's intuition.
        </p>
        <p>
          There is one special type of Aggregation that is created by the "values" builtin-in function. This Aggregation is special, as it produces several nested Aggregations. Instead of producing a typical line chart, it will produce a bar chart.
        </p>
        <h2>Built-in Operators</h2>
        Below is a list of all built-in operators in DPL that accept arguments of signals or aggregations. Many of these follow the same patterns (seen in the first five rows of the table). Note that for the "Input Types" column, order does not matter (e.g. row 2 shows the addition operator with input types "Signal, Aggregation". The function behaves the same if the inputs are given in reverse order "Aggregation, Signal"; therefore, those cases have been excluded from the table.
        <PrettyTable
          header={['Name', 'Input Types', 'Return Type', 'Description',]}
          rows={[
            ['+', 'Signal, Signal', 'Signal', 'Sums each datapoint in the first signal with one in the second signal where the absolute timestamps are equal.'],
            ['+', 'Signal, Aggregation', 'Signal', 'Sums each datapoint in the signal with the signal that was used to produce the aggregation where the absolute timestamps are equal (e.g. in "A + avg(B)", "avg(B)" is an aggregation, and the signal "B" is used for the addition -- not the average of B). This is contrary to intuition (which would tell us incorrectly that "A + avg(B)" is the average of B added to each datapoint in A). DPL works contrary to intuition because, that implementation would require two passes must be completed on the entire dataset (you would need to compute "avg(B)" over the entire dataset, and then do a second pass where that value is added to each datapoint). No KPIs in our set of required KPI computations needed this behavior; therefore, only single pass computations are possible. Then the question comes: "why are operators even defined for combining signals and aggregations, if they don\'t work as expected?". This behavior was implemented to make KPIs that display aggregations on the user interface composable as if they were signals. For example, if there is a KPI called "PowerOutput" defined as "avg(Voltage * Current)", and you wanted to create an efficiency KPI, you would define it as "Efficiency" with the computation of "PowerOutput/PowerInput" (assuming you have an input signal called "PowerInput"). This is an operation with an Aggregation and a signal. You could write it in one KPI as: "avg(Voltage * Current)/PowerInput".'],
            ['+', 'Signal, Number', 'Signal', 'Adds the number to each datapoint in the signal.'],
            ['+', 'Aggregation, Number', 'Signal', 'Adds the number to the final result of the aggregation (e.g. "avg(A) + 10" will be -- just as it reads -- the average of A plus ten).'],                                    
            ['+', 'Aggregation, Aggregation', 'Aggregation', 'Sums the final output values of both aggregations together.'],                        

            ['-', 'Signal, Signal', 'Signal', 'Same as row 1, but subtracts.'],
            ['-', 'Signal, Aggregation', 'Signal', 'Same as row 2, but subtracts.'],
            ['-', 'Signal, Number', 'Signal', 'Same as row 3, but subtracts.'],
            ['-', 'Aggregation, Number', 'Signal', 'Same as row 4, but subtracts.'],                        
            ['-', 'Aggregation, Aggregation', 'Aggregation', 'Same as row 5, but subtracts.'],

            ['*', 'Signal, Signal', 'Signal', 'Same as row 1, but multiplies.'],
            ['*', 'Signal, Aggregation', 'Signal', 'Same as row 2, but multiplies.'],
            ['*', 'Signal, Number', 'Signal', 'Same as row 3, but multiplies.'],
            ['*', 'Aggregation, Number', 'Signal', 'Same as row 4, but multiplies.'],                        
            ['*', 'Aggregation, Aggregation', 'Aggregation', 'Same as row 5, but multiplies.'],

            ['/', 'Signal, Signal', 'Signal', 'Same as row 1, but divides.'],
            ['/', 'Signal, Aggregation', 'Signal', 'Same as row 2, but divides.'],
            ['/', 'Signal, Number', 'Signal', 'Same as row 3, but divides.'],
            ['/', 'Aggregation, Number', 'Signal', 'Same as row 4, but divides.'],                        
            ['/', 'Aggregation, Aggregation', 'Aggregation', 'Same as row 5, but divides.'],

            ['//', 'Signal, Signal',           'Signal',      'Same as row 1, but floor-divides (divides, then floors the result).'],
            ['//', 'Signal, Aggregation',      'Signal',      'Same as row 2, but floor-divides.'],
            ['//', 'Signal, Number',           'Signal',      'Same as row 3, but floor-divides.'],
            ['//', 'Aggregation, Number',      'Signal',      'Same as row 4, but floor-divides.'],                        
            ['//', 'Aggregation, Aggregation', 'Aggregation', 'Same as row 5, but floor-divides.'],
            
            ['-', 'Signal', 'Signal', 'Negates each datapoint in the signals (e.g. a value of 1 becomes -1, a value of -23 becomes 23.).'],

            ['>', 'Signal, Signal', 'Signal', 'Same as row 1, but checks if the first argument is greater than the second and yields a Signal with boolean values.'],
            ['>', 'Signal, Aggregation', 'Signal', 'Same as row 2, but checks if the first argument is greater than the second and yields a Signal with boolean values.'],
            ['>', 'Signal, Number', 'Signal', 'Same as row 3, but checks if the first argument is greater than the second and yields a Signal with boolean values.'],

            ['<', 'Signal, Signal', 'Signal', 'Same as row 1, but checks if the first argument is less than the second and yields a Signal with boolean values.'],
            ['<', 'Signal, Aggregation', 'Signal', 'Same as row 2, but checks if the first argument is less than the second and yields a Signal with boolean values.'],
            ['<', 'Signal, Number', 'Signal', 'Same as row 3, but checks if the first argument is less than the second and yields a Signal with boolean values.'],

            ['>=', 'Signal, Signal', 'Signal', 'Same as row 1, but checks if the first argument is greater than or equal to the second and yields a Signal with boolean values.'],
            ['>=', 'Signal, Aggregation', 'Signal', 'Same as row 2, but checks if the first argument is greater than or equal to the second and yields a Signal with boolean values.'],
            ['>=', 'Signal, Number', 'Signal', 'Same as row 3, but checks if the first argument is greater than or equal to the second and yields a Signal with boolean values.'],
            
            ['<=', 'Signal, Signal', 'Signal', 'Same as row 1, but checks if the first argument is less than or equal to the second and yields a Signal with boolean values.'],
            ['<=', 'Signal, Aggregation', 'Signal', 'Same as row 2, but checks if the first argument is less than or equal to the second and yields a Signal with boolean values.'],
            ['<=', 'Signal, Number', 'Signal', 'Same as row 3, but checks if the first argument is less than or equal to the second and yields a Signal with boolean values.'],

            ['==', 'Signal, Signal', 'Signal', 'Same as row 1, but checks for equality of each datapoint and yields a Signal with boolean values.'],
            ['==', 'Signal, Aggregation', 'Signal', 'Same as row 2, but checks for equality of each datapoint and yields a Signal with boolean values.'],
            ['==', 'Signal, Number', 'Signal', 'Same as row 3, but checks for equality of each datapoint and yields a Signal with boolean values.'],

            ['!=', 'Signal, Signal', 'Signal', 'Same as row 1, but checks for inequality of each datapoint and yields a Signal with boolean values.'],
            ['!=', 'Signal, Aggregation', 'Signal', 'Same as row 2, but checks for inequality of each datapoint and yields a Signal with boolean values.'],
            ['!=', 'Signal, Number', 'Signal', 'Same as row 3, but checks for inequality of each datapoint and yields a Signal with boolean values.'],

            
          ]}>
        </PrettyTable>

        <h2>Built-in Expressions</h2>
        <PrettyTable
          header={['Expression', 'Input Types', 'Yielded Type', 'Description']}
          rows={[
            ['and', 'Signal, Signals',       ''],
            ['and', 'Signals, Number',       ''],
            ['and', 'Signals, Aggregation',  ''],
            ['or',  'Signals, Signals', 'Signals', ''],
            ['or',  'Signals, Number', 'Signals', ''],
            ['or',  'Signals, Aggregation', 'Signals',  ''],
            ['if',  'Series, Series, Series', 'Series',  ''],                                    
            ['if',  'Expression, Expression, Expression', 'Any',  'If the first expression evaluates to a truthy value (True, 1, etc...), evaluate the second expression. Otherwise evaluate the third. The final value is whichever value was last evaluated.'],
          ]}>
        </PrettyTable>

        <h2>Built-in Functions</h2>
        <PrettyTable
          header={['Function Signature', 'Return Type', 'Description']}
          rows={[
            ['cumsum(Signal)',                 'Aggregation',       ''],
            ['values((String, Aggregation)*)', 'Aggregation',       ''],
            ['window(Signal, Duration)',       'Signal of Signals', 'wioejfweoifjweoifwjeofij'],
            ['abs(Signal)',                    'Signal',            'wioejfweoifjweoifwjeofij'],
            ['abs(Aggregation)',               'Signal',            'wioejfweoifjweoifwjeofij'],
            ['avg(Signal of Signal)',          'Signal',            'wioejfweoifjweoifwjeofij'],            
            ['avg(Signal)',                    'Aggregation',       'wioejfweoifjweoifwjeofij'],
            ['sum(Signal of Signal)',          'Signal',            'wioejfweoifjweoifwjeofij'],            
            ['sum(Signal)',                    'Aggregation',       'wioejfweoifjweoifwjeofij'],
            ['min(Signal of Signal)',          'Signal',            'wioejfweoifjweoifwjeofij'],            
            ['min(Signal)',                    'Aggregation',       'wioejfweoifjweoifwjeofij'],
            ['max(Signal of Signal)',          'Signal',            'wioejfweoifjweoifwjeofij'],            
            ['max(Signal)',                    'Aggregation',       'wioejfweoifjweoifwjeofij'],
            ['thd(Series, Number)',            'Aggregation',       'wioejfweoifjweoifwjeofij'],
          ]}>
        </PrettyTable>
        
      </Box>
    );
  }
}
