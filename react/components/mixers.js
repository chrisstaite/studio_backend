import React from 'react';
import { useMixers } from './mixer-store.js';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Fab from '@material-ui/core/Fab';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import Mixer from './mixer.js';

const useStyles = makeStyles({
    mixer_list: {
        position: 'relative',
        'min-height': '200px',
        'padding-bottom': '20px',
    },
    add_button: {
        position: 'absolute',
        right: '5px',
        bottom: '10px',
    },
});

const Mixers = () => {
    const classes = useStyles();
    const mixers = useMixers();

    const addMixer = () => {
        let newMixer = { 'display_name': 'New Mixer', 'channels': 2 };
        fetch('/audio/mixer', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify(newMixer)
                })
            .then(response => response.json())
            .catch(e => console.error(e));
    };

    return (
        <div className={classes.mixer_list}>
            {mixers.map(mixer => <Mixer mixer={mixer} key={mixer.id} />)}
            <Tooltip title="Add a mixer">
                <Fab size="small" color="primary" className={classes.add_button} onClick={addMixer}>
                    <AddIcon />
                </Fab>
            </Tooltip>
        </div>
    );
};

export default Mixers;