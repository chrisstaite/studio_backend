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
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import FormControl from '@material-ui/core/FormControl';
import MenuItem from '@material-ui/core/MenuItem';
import { useInputs } from './input-store.js';
import useServerValue from './server-value.js'

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

const Output = ({output}) => {
    const updateOutput = (name, value) => {
        const data = new FormData();
        data.append(name, value);
        fetch('/audio/output/' + output.id, {method: 'PUT', body: data});
    };
    const updateName = name => updateOutput('display_name', name);
    const updateInput = input => updateOutput('input', input);

    const classes = useStyles();
    const [displayName, setDisplayName] = useServerValue(output.display_name, updateName);
    const [input, setInput] = useServerValue(output.input_id, updateInput);
    const inputs = useInputs();

    const removeOutput = () => fetch('/audio/output/' + output.id, {method: 'DELETE'});

    return (
        <Card className={classes.card}>
            <CardContent>
                <Typography component="h5" variant="h5">
                    {title(output)}
                </Typography>
                <TextField label="Name" value={displayName} onChange={e => setDisplayName(e.target.value)} />
            </CardContent>
            <CardContent>
                <Typography>{output.name}</Typography>
            </CardContent>
            <CardContent>
                <FormControl>
                    <InputLabel>Input device</InputLabel>
                    <Select value={input} onChange={event => setInput(event.target.value)}>
                        {inputs.map(input => <MenuItem value={input.id} key={input.id}>{input.display_name}</MenuItem>)}
                    </Select>
                    <FormHelperText>The device to input from</FormHelperText>
                </FormControl>
            </CardContent>
            <CardActions>
                <Tooltip title="Remove this device">
                    <Fab color="primary" size="small" onClick={removeOutput}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>
            </CardActions>
        </Card>
    );
}

export default Output;