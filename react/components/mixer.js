import React, { useState, useEffect } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import Fab from '@material-ui/core/Fab';
import Typography from '@material-ui/core/Typography';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import RemoveIcon from '@material-ui/icons/Remove';
import AddIcon from '@material-ui/icons/Add';
import Tooltip from '@material-ui/core/Tooltip';
import TextField from '@material-ui/core/TextField';
import useServerValue from './server-value.js';
import MixerChannel from './mixer-channel.js';

const useStyles = makeStyles({
    card: {
        display: 'inline-block',
        margin: '10px',
    },
});

const Mixer = ({mixer}) => {
    const updateName = name => {
        const data = new FormData();
        data.append('display_name', name);
        fetch('/audio/mixer/' + mixer.id, {method: 'PUT', body: data});
    };

    const classes = useStyles();
    const [displayName, setDisplayName] = useServerValue(mixer.display_name, updateName);
    const removeMixer = () => fetch('/audio/mixer/' + mixer.id, {method: 'DELETE'});
    const addChannel = () => fetch('/audio/mixer/' + mixer.id + '/channel', {method: 'POST'});

    return (
        <Card className={classes.card}>
            <CardContent>
                <TextField label="Name" value={displayName} onChange={e => setDisplayName(e.target.value)} />
            </CardContent>
            <CardContent>
                {mixer.hasOwnProperty('channels') ? mixer.channels.map(channel => <MixerChannel mixer={mixer} channel={channel} key={channel.id} />) : null}
            </CardContent>
            <CardActions>
                <Tooltip title="Add a channel">
                    <Fab color="primary" size="small" onClick={addChannel}>
                        <AddIcon />
                    </Fab>
                </Tooltip>
                <Tooltip title="Remove this mixer">
                    <Fab color="primary" size="small" onClick={removeMixer}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>
            </CardActions>
        </Card>
    );
}

export default Mixer;