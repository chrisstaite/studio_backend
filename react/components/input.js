import React, { useState, useEffect } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import Fab from '@material-ui/core/Fab';
import Typography from '@material-ui/core/Typography';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import RemoveIcon from '@material-ui/icons/Remove';
import Tooltip from '@material-ui/core/Tooltip';
import TextField from '@material-ui/core/TextField';
import { confirmAlert } from 'react-confirm-alert';
import 'react-confirm-alert/src/react-confirm-alert.css';
import useServerValue from './server-value.js';
import { fetchGet, fetchDelete } from './fetch-wrapper.js';

const useStyles = makeStyles({
    card: {
        display: 'inline-block',
        margin: '10px',
    },
});

function title(input) {
    if (input.type == 'device') {
        return 'Input device';
    }
}

const Input = ({input}) => {
    const updateName = name =>
        fetchPut('/audio/input/' + input.id, {'display_name': name});

    const classes = useStyles();
    const [displayName, setDisplayName] = useServerValue(input.display_name, updateName);
    const removeInput = () => confirmAlert({
        title: 'Delete input',
        message: 'Are you sure you want to delete the input?',
        buttons: [
            {
                label: 'Yes',
                onClick: () => fetchDelete('/audio/input/' + input.id),
            },
            {
                label: 'No',
            }
        ]
    });

    return (
        <Card className={classes.card}>
            <CardContent>
                <Typography component="h5" variant="h5">
                    {title(input)}
                </Typography>
                <TextField label="Name" value={displayName} onChange={e => setDisplayName(e.target.value)} />
            </CardContent>
            <CardContent>
                <Typography>{input.name}</Typography>
            </CardContent>
            <CardActions>
                <Tooltip title="Remove this device">
                    <Fab color="primary" size="small" onClick={removeInput}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>
            </CardActions>
        </Card>
    );
}

export default Input;