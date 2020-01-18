import React, {useState, useEffect} from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import Fab from '@material-ui/core/Fab';
import Typography from '@material-ui/core/Typography';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import RemoveIcon from '@material-ui/icons/Remove';
import Tooltip from '@material-ui/core/Tooltip';
import TextField from '@material-ui/core/TextField';
import useServerValue from './server-value.js'

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
    const updateName = name => {
        const data = new FormData();
        data.append('display_name', name);
        fetch('/audio/input/' + input.id, {method: 'PUT', body: data});
    };

    const classes = useStyles();
    const [displayName, setDisplayName] = useServerValue(output.display_name, updateName);

    const removeInput = () => fetch('/audio/input/' + input.id, {method: 'DELETE'});

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