import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';
import 'typeface-roboto';
import Button from '@material-ui/core/Button';
import Mixers from './components/mixers.js';
import Inputs from './components/inputs.js';
import Outputs from './components/outputs.js';
import Playlists from './components/playlists.js';
import LivePlayer from './components/live-player.js';
import Contexts from './components/contexts.js';
import { fetchGet, fetchPost } from './components/fetch-wrapper.js';

const App = () => {
    // TODO: Allow multiple live players
    const [ livePlayer, setLivePlayer ] = useState(false);
    useEffect(() => {
        fetchGet('/player')
            .then(players => {
                if (players.length > 0) {
                    setLivePlayer(players[0].id);
                } else {
                    fetchPost('/player', {'name': 'Live Player'})
                        .then(playerId => setLivePlayer(playerId))
                        .catch(e => console.error(e));
                }
            })
            .catch(e => console.error(e));
    }, []);

    return (
        <Contexts>
            {livePlayer && <LivePlayer player_id={livePlayer} />}
            <Playlists />
            <Mixers />
            <Inputs />
            <Outputs />
        </Contexts>
    );
};

ReactDOM.render(<App />, document.querySelector('#app'));