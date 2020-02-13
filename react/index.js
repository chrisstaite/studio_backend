import React from 'react';
import ReactDOM from 'react-dom';
import 'typeface-roboto';
import Button from '@material-ui/core/Button';
import Mixers from './components/mixers.js';
import Inputs from './components/inputs.js';
import Outputs from './components/outputs.js';
import Playlists from './components/playlists.js';
import Contexts from './components/contexts.js';

const App = () => (
    <Contexts>
        <Playlists />
        <Mixers />
        <Inputs />
        <Outputs />
    </Contexts>
);

ReactDOM.render(<App />, document.querySelector('#app'));