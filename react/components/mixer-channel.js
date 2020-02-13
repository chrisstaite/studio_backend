import React from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Slider from '@material-ui/core/Slider';
import Select from '@material-ui/core/Select';
import MenuItem from '@material-ui/core/MenuItem';
import Fab from '@material-ui/core/Fab';
import RemoveIcon from '@material-ui/icons/Remove';
import Tooltip from '@material-ui/core/Tooltip';
import { confirmAlert } from 'react-confirm-alert';
import 'react-confirm-alert/src/react-confirm-alert.css';
import useServerValue from './server-value.js';
import { useMixers } from './mixer-store.js';
import { useInputs } from './input-store.js';

const useStyles = makeStyles({
    slider: {
        height: '90px',
        'text-align': 'center',
    },
    removeChannel: {
        'text-align': 'right',
    },
    input: {
        width: '100%',
    },
});

const MixerChannel = ({mixer, channel, className}) => {
    const classes = useStyles();
    const mixers = useMixers();
    const inputs = useInputs();

    const updateVolume = volume => {
        const data = new FormData();
        data.append('volume', volume);
        fetch('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {method: 'PUT', body: data});
    };
    const [volume, setVolume] = useServerValue(channel.volume, updateVolume, 100);

    const removeChannel = () => confirmAlert({
        title: 'Delete mixer channel',
        message: 'Are you sure you want to delete the channel?',
        buttons: [
            {
                label: 'Yes',
                onClick: () => fetch('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {method: 'DELETE'}),
            },
            {
                label: 'No',
            }
        ]
    });
    const setInput = input => {
        const data = new FormData();
        data.append('input', input);
        fetch('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {method: 'PUT', body: data});
    };

    return (
        <div className={className}>
            <div className={classes.slider}>
                <Slider min={0} max={2} step={0.01} orientation="vertical" value={volume}
                    onChange={(event, value) => setVolume(value)} />
            </div>
            <Select className={classes.input} displayEmpty={true}
                    value={channel.input == null ? '' : channel.input}
                    onChange={event => setInput(event.target.value)}>
                <MenuItem value="">None</MenuItem>
                {inputs.map(input => <MenuItem value={input.id} key={input.id}>{input.display_name}</MenuItem>)}
                {mixers.filter(x => x.id != mixer.id).map(
                        mixer => <MenuItem value={mixer.id} key={mixer.id}>{mixer.display_name}</MenuItem>
                    )}
            </Select>
            <div className={classes.removeChannel}>
                <Tooltip title="Remove channel">
                    <Fab color="primary" size="small" onClick={removeChannel}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>
            </div>
        </div>
    );
};

export default MixerChannel;