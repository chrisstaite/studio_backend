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
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import MenuItem from '@material-ui/core/MenuItem';
import { useInputs } from './input-store.js';

const useStyles = makeStyles({
  card: {
    display: 'inline-block',
    margin: '10px',
  },
});

function title(output) {
    const titles = {
        'device': 'Output device',
        'icecast': 'Icecast source',
        'multiplex': 'Multiplexed output',
        'file': 'Rolling file',
    };
    return titles[output.type];
}

const removeOutput = (id) =>
    fetch('/audio/output/' + id, {method: 'DELETE'});

const updateName = (id, name) => {
    const data = new FormData();
    data.append('display_name', name);
    fetch('/audio/output/' + id, {method: 'PUT', body: data});
}

const Output = ({output}) => {
    const classes = useStyles();
    const [serverDisplayName, setServerDisplayName] = useState(output.display_name);
    const [displayName, setDisplayName] = useState(output.display_name);
    const [input, setInput] = useState(output.input_id);
    const inputs = useInputs();

    useDebouncedEffect(
        () => {
            if (serverDisplayName != displayName) {
                updateName(output.id, displayName);
            }
        },
        600,
        [output.id, displayName]
    );

    const handleInputChange = event => setInput(event.target.value);

    useEffect(() => {
        setServerDisplayName(output.display_name);
        setDisplayName(output.display_name);
    }, [output.display_name]);

    return (
        <Card className={classes.card}>
            <CardContent>
                <Typography component="h5" variant="h5">
                    {title(output)}
                </Typography>
                <TextField label="Name" value={displayName} onChange={e => setDisplayName(e.target.value)} />
            </CardContent>
            <CardContent>
                {output.name}
            </CardContent>
            <CardContent>
                <FormControl>
                    <InputLabel>Input device</InputLabel>
                    <Select value={input} onChange={handleInputChange}>
                        {inputs.map(input => <MenuItem value={input.id} key={input.id}>{input.display_name}</MenuItem>)}
                    </Select>
                    <FormHelperText>The device to input from</FormHelperText>
                </FormControl>
            </CardContent>
            <CardActions>
                <Tooltip title="Remove this device">
                    <Fab color="primary" size="small" onClick={() => removeOutput(output.id)}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>
            </CardActions>
        </Card>
    );
}

export default Output;