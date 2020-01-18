import React from 'react';
import ReactDOM from 'react-dom';
import 'typeface-roboto';
import Button from '@material-ui/core/Button';
import Inputs from './components/inputs.js';
import Outputs from './components/outputs.js';
import { InputStore } from './components/input-store.js';
import { OutputStore } from './components/output-store.js';
import { Socket } from './components/socket.js';

const App = () => (
    <Socket>
        <InputStore>
            <OutputStore>
                <Inputs />
                <Outputs />
            </OutputStore>
        </InputStore>
    </Socket>
);

ReactDOM.render(<App />, document.querySelector('#app'));