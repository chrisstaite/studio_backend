import React from 'react';
import ReactDOM from 'react-dom';
import * as io from 'socket.io-client';
import Button from '@material-ui/core/Button';
import Inputs from './components/inputs.js';
import SocketContext from './components/socket.js';

const socket = io();

const App = () => (
    <SocketContext.Provider value={socket}>
        <Inputs />
    </SocketContext.Provider>
);

ReactDOM.render(<App />, document.querySelector('#app'));
