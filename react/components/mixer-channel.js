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
import { usePlayers } from './player-store.js';
import { fetchPut, fetchDelete, fetchPost } from './fetch-wrapper.js';

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
    const players = usePlayers();

    const updateVolume = volume => {
        fetchPut('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {'volume': volume});
    };
    const [volume, setVolume] = useServerValue(channel.volume, updateVolume, 100);

    const removeChannel = () => confirmAlert({
        title: 'Delete mixer channel',
        message: 'Are you sure you want to delete the channel?',
        buttons: [
            {
                label: 'Yes',
                onClick: () => fetchDelete('/audio/mixer/' + mixer.id + '/channel/' + channel.id),
            },
            {
                label: 'No',
            }
        ]
    });
    const setInput = input => {
        fetchPut('/audio/mixer/' + mixer.id + '/channel/' + channel.id, {'input': input})
            .catch(e => console.error(e));
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
                {mixers.filter(x => x.id != mixer.id).map(
                        mixer => <MenuItem value={mixer.id} key={mixer.id}>{mixer.display_name}</MenuItem>
                    )}
                {players.map(player => <MenuItem value={player.id} key={player.id}>{player.name}</MenuItem>)}
                {inputs.map(input => <MenuItem value={input.id} key={input.id}>{input.display_name}</MenuItem>)}
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