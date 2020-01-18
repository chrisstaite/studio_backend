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
import useDebouncedEffect from 'use-debounced-effect';

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

const removeInput = (id) =>
    fetch('/audio/input/' + id, {method: 'DELETE'});

const updateName = (id, name) => {
    const data = new FormData();
    data.append('display_name', name);
    fetch('/audio/input/' + id, {method: 'PUT', body: data});
}

const Input = ({input}) => {
    const classes = useStyles();
    const [serverDisplayName, setServerDisplayName] = useState(input.display_name);
    const [displayName, setDisplayName] = useState(input.display_name);

    useDebouncedEffect(
        () => {
            if (serverDisplayName != displayName) {
                updateName(input.id, displayName);
            }
        },
        600,
        [input.id, displayName]
    );

    useEffect(() => {
        setServerDisplayName(input.display_name);
        setDisplayName(input.display_name);
    }, [input.display_name]);

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
                    <Fab color="primary" size="small" onClick={() => removeInput(input.id)}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>
            </CardActions>
        </Card>
    );
}

export default Input;