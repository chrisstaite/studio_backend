import React from 'react';
import ReactDOM from 'react-dom';
import 'typeface-roboto';
import Button from '@material-ui/core/Button';
import Mixers from './components/mixers.js';
import Inputs from './components/inputs.js';
import Outputs from './components/outputs.js';
import { InputStore } from './components/input-store.js';
import { OutputStore } from './components/output-store.js';
import { MixerStore } from './components/mixer-store.js';
import { Socket } from './components/socket.js';

const App = () => (
    <Socket>
        <InputStore>
            <OutputStore>
                <MixerStore>
                    <Mixers />
                    <Inputs />
                    <Outputs />
                </MixerStore>
            </OutputStore>
        </InputStore>
    </Socket>
);

ReactDOM.render(<App />, document.querySelector('#app'));