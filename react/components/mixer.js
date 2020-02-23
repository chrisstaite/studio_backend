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
import { confirmAlert } from 'react-confirm-alert';
import 'react-confirm-alert/src/react-confirm-alert.css';
import useServerValue from './server-value.js';
import MixerChannel from './mixer-channel.js';
import { fetchPut, fetchDelete, fetchPost } from './fetch-wrapper.js';

const useStyles = makeStyles({
    card: {
        display: 'inline-block',
        margin: '10px',
        'min-height': '370px',
    },
    content: {
        position: 'relative',
        overflow: 'auto',
    },
    channel: {
        float: 'left',
        'min-width': '150px',
    },
    addChannel: {
        'text-align': 'right',
    },
});

const Mixer = ({mixer}) => {
    const updateName = name => {
        fetchPut('/audio/mixer/' + mixer.id, {'display_name': name});
    };

    const classes = useStyles();
    const [displayName, setDisplayName] = useServerValue(mixer.display_name, updateName);
    const removeMixer = () => confirmAlert({
        title: 'Delete mixer',
        message: 'Are you sure you want to delete the mixer?',
        buttons: [
            {
                label: 'Yes',
                onClick: () => fetchDelete('/audio/mixer/' + mixer.id),
            },
            {
                label: 'No',
            }
        ]
    });
    const addChannel = () => fetchPost('/audio/mixer/' + mixer.id + '/channel').catch(e => console.error(e));

    return (
        <Card className={classes.card}>
            <CardContent>
                <TextField label="Name" value={displayName} onChange={e => setDisplayName(e.target.value)} />
            </CardContent>
            <CardContent className={classes.content}>
                {mixer.hasOwnProperty('channels') ? mixer.channels.map(channel => <MixerChannel mixer={mixer} channel={channel} key={channel.id} className={classes.channel} />) : null}
                <div className={classes.addChannel}>
                    <Tooltip title="Add a channel">
                        <Fab color="primary" size="small" onClick={addChannel}>
                            <AddIcon />
                        </Fab>
                    </Tooltip>
                </div>
            </CardContent>
            <CardActions>
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