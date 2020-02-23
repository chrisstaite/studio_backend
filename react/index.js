import React, { useState, useEffect } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import ReactDOM from 'react-dom';
import 'typeface-roboto';
import Button from '@material-ui/core/Button';
import AppBar from '@material-ui/core/AppBar';
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import PlayIcon from '@material-ui/icons/PlayArrow';
import Mixers from './components/mixers.js';
import Inputs from './components/inputs.js';
import Outputs from './components/outputs.js';
import Playlists from './components/playlists.js';
import LivePlayer from './components/live-player.js';
import Contexts from './components/contexts.js';
import BrowserPlayer from './components/browser-player.js';
import { fetchGet, fetchPost } from './components/fetch-wrapper.js';

const useStyles = makeStyles({
    play_button: {
        position: 'absolute',
        right: '5px',
        top: '3px',
    },
});

const App = () => {
    const classes = useStyles();
    const [ stream, setStream ] = useState(false);

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

    const [value, setValue] = React.useState(0);

    const handleChange = (event, newValue) => {
        setValue(newValue);
    };

    return (
        <Contexts>
            <AppBar position="static">
                <Tabs value={value} onChange={handleChange}>
                    <Tab label="Live player" />
                    <Tab label="Playlists" />
                    <Tab label="Mixers" />
                    <Tab label="Inputs" />
                    <Tab label="Outputs" />
                </Tabs>
                <div className={classes.play_button}>
                    {stream && <BrowserPlayer />}
                    {!stream && <Tooltip title="Start a browser output">
                        <Fab color="primary" size="small" onClick={e => setStream(true)}>
                            <PlayIcon />
                        </Fab>
                    </Tooltip>}
                </div>
            </AppBar>
            {livePlayer && value == 0 && <LivePlayer player_id={livePlayer} />}
            {value == 1 && <Playlists />}
            {value == 2 && <Mixers />}
            {value == 3 && <Inputs />}
            {value == 4 && <Outputs />}
        </Contexts>
    );
};

ReactDOM.render(<App />, document.querySelector('#app'));