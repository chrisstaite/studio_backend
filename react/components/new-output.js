import React, {useState, useEffect} from 'react';
import PropTypes from 'prop-types';
import { makeStyles } from '@material-ui/core/styles';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import DialogTitle from '@material-ui/core/DialogTitle';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Typography from '@material-ui/core/Typography';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormHelperText from '@material-ui/core/FormHelperText';
import Input from '@material-ui/core/Input';
import FormControl from '@material-ui/core/FormControl';
import MenuItem from '@material-ui/core/MenuItem';
import Dialog from '@material-ui/core/Dialog';
import Fab from '@material-ui/core/Fab';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import { FixedSizeList } from 'react-window';
import { useOutputs } from './output-store.js';

const useStyles = makeStyles(theme => ({
    heading: {
        fontSize: theme.typography.pxToRem(15),
        flexBasis: '33.33%',
        flexShrink: 0,
    },
    secondaryHeading: {
        fontSize: theme.typography.pxToRem(15),
        color: theme.palette.text.secondary,
    },
}));

function outputItem({ data, index, style }) {
    const { handleListItemClick, devices } = data;

    return (
        <ListItem button style={style} key={index} onClick={() => handleListItemClick('device', devices[index])}>
            <ListItemText primary={devices[index]} />
        </ListItem>
    );
}

outputItem.propTypes = {
    data: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
    style: PropTypes.object.isRequired,
};

const CreateDevice = ({ createOutput, devices }) => {
    const [ device, setDevice ] = useState('');

    const handleChange = event => setDevice(event.target.value);
    const create = () => {
        if (device != '') {
            createOutput({type: 'device', name: device, display_name: device});
        }
    };

    return (
        <div>
            <FormControl>
                <InputLabel>Output device</InputLabel>
                <Select value={device} onChange={handleChange}>
                    {devices.map((device, index) => <MenuItem value={device} key={index}>{device}</MenuItem>)}
                </Select>
                <FormHelperText>The device to output to</FormHelperText>
            </FormControl>
            <Tooltip title="Create output device">
                <Fab size="small" color="primary" onClick={create}>
                    <AddIcon />
                </Fab>
            </Tooltip>
        </div>
    );
};

const CreateMultiplexer = ({ createOutput }) => {
    const [device, setDevice] = useState('');
    const [channels, setChannels] = useState('');
    const devices = useOutputs();

    const create = () => {
        if (device != '' && channels != '') {
            let name = devices.filter(parent => parent.id == device)[0].display_name;
            createOutput({type: 'multiplex', display_name: name, parent_id: device, channels: channels});
        }
    };

    return (
        <div>
            <FormControl>
                <InputLabel>Output device</InputLabel>
                <Select value={device} onChange={event => setDevice(event.target.value)}>
                    {devices.filter(device => device.type == 'device').map(
                        (device, index) => <MenuItem value={device.id} key={index}>{device.display_name}</MenuItem>
                    )}
                </Select>
                <FormHelperText>The device to multiplex</FormHelperText>
            </FormControl>
            <Input placeholder="Channels (e.g. 1 - mono, 2 - stereo)" onChange={event => setChannels(event.target.value)}/>
            <Tooltip title="Create Icecast server">
                <Fab size="small" color="primary" onClick={create}>
                    <AddIcon />
                </Fab>
            </Tooltip>
        </div>
    );
};

const CreateIcecast = ({ createOutput }) => {
    const [server, setServer] = useState('');
    const [password, setPassword] = useState('');

    const create = () => {
        if (server != '') {
            createOutput({type: 'icecast', endpoint: server, display_name: server, password: password});
        }
    };

    return (
        <div>
            <Input placeholder="Icecast server and mount point" onChange={event => setServer(event.target.value)}/>
            <Input placeholder="Source password" onChange={event => setPassword(event.target.value)}/>
            <Tooltip title="Create Icecast server">
                <Fab size="small" color="primary" onClick={create}>
                    <AddIcon />
                </Fab>
            </Tooltip>
        </div>
    );
};

const CreateFile = ({ createOutput }) => {
    const [file, setFile] = useState('');

    const create = () => {
        if (file != '') {
            createOutput({type: 'file', path: file, display_name: 'Live recording'});
        }
    };

    return (
        <div>
            <Input placeholder="The file to record to" onChange={event => setFile(event.target.value)}/>
            <Tooltip title="Create rolling file">
                <Fab size="small" color="primary" onClick={create}>
                    <AddIcon />
                </Fab>
            </Tooltip>
        </div>
    );
};

function NewOutputDialog({ onClose, open }) {
    const classes = useStyles();
    const outputs = useOutputs();
    const [expanded, setExpanded] = useState(false);
    const [devices, setDevices] = useState([]);

    const handleClose = () => onClose(null);
    const createOutput = (device) => onClose(device);

    // Get the list of available devices
    useEffect(() => {
        if (open == true) {
            fetch('/audio/output/devices')
                .then(response => response.json())
                .then(devices => devices.filter(
                    device => outputs.findIndex(item => item.type == 'device' && item.name == device) == -1))
                .then(devices => setDevices(devices))
                .catch(e => console.error(e));
        }
    }, [open]);

    const handleChange = panel => (event, isExpanded) => {
        setExpanded(isExpanded ? panel : false);
    };

    return (
        <Dialog fullWidth={true} onClose={handleClose} open={open}>
            <DialogTitle>Add Output</DialogTitle>
            <ExpansionPanel expanded={expanded === 'device'} onChange={handleChange('device')}>
                <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography className={classes.heading}>Output Device</Typography>
                    <Typography className={classes.secondaryHeading}>Add a physical output device</Typography>
                </ExpansionPanelSummary>
                <ExpansionPanelDetails>
                    <CreateDevice createOutput={createOutput} devices={devices} />
                </ExpansionPanelDetails>
            </ExpansionPanel>
            <ExpansionPanel expanded={expanded === 'multiplexer'} onChange={handleChange('multiplexer')}>
                <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography className={classes.heading}>Multiplexer</Typography>
                    <Typography className={classes.secondaryHeading}>Make pseudo devices for a multi channel output device</Typography>
                </ExpansionPanelSummary>
                <ExpansionPanelDetails>
                    <CreateMultiplexer createOutput={createOutput} />
                </ExpansionPanelDetails>
            </ExpansionPanel>
            <ExpansionPanel expanded={expanded === 'icecast'} onChange={handleChange('icecast')}>
                <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography className={classes.heading}>Icecast server</Typography>
                    <Typography className={classes.secondaryHeading}>Create an Icecast stream</Typography>
                </ExpansionPanelSummary>
                <ExpansionPanelDetails>
                    <CreateIcecast createOutput={createOutput} />
                </ExpansionPanelDetails>
            </ExpansionPanel>
            <ExpansionPanel expanded={expanded === 'file'} onChange={handleChange('file')}>
                <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
                    <Typography className={classes.heading}>Rolling file</Typography>
                    <Typography className={classes.secondaryHeading}>Create an output that records to a file which rolls every hour</Typography>
                </ExpansionPanelSummary>
                <ExpansionPanelDetails>
                    <CreateFile createOutput={createOutput} />
                </ExpansionPanelDetails>
            </ExpansionPanel>
        </Dialog>
    );
}

NewOutputDialog.propTypes = {
    onClose: PropTypes.func.isRequired,
    open: PropTypes.bool.isRequired,
};

export default NewOutputDialog;