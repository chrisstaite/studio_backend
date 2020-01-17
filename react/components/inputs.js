import React, {useState, useEffect} from 'react';
import PropTypes from 'prop-types';
import Input from './input.js';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Fab from '@material-ui/core/Fab';
import Tooltip from '@material-ui/core/Tooltip';
import AddIcon from '@material-ui/icons/Add';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import { FixedSizeList } from 'react-window';
import SocketContext from './socket.js';

const useStyles = makeStyles({
    input_list: {
        position: 'relative',
        'min-height': '200px',
        'padding-bottom': '20px',
    },
    add_button: {
        position: 'absolute',
        right: '5px',
        bottom: '10px',
    },
});

function inputItem(props) {
    const { data, index, style } = props;
    const { handleListItemClick, devices } = data;

    return (
        <ListItem button style={style} key={index} onClick={() => handleListItemClick(devices[index])}>
            <ListItemText primary={devices[index]} />
        </ListItem>
    );
}

inputItem.propTypes = {
    data: PropTypes.object.isRequired,
    index: PropTypes.number.isRequired,
    style: PropTypes.object.isRequired,
};

function NewInputDialog(props) {
    const { onClose, open } = props;
    const [devices, setDevices] = useState([]);

    const handleClose = () => {
        onClose(null);
    };

    const handleListItemClick = value => {
        onClose(value);
    };

    // Get the list of available devices
    useEffect(() => {
        if (open == true) {
            fetch('/audio/input/devices')
                .then(response => response.json())
                .then(devices => setDevices(devices))
                .catch(e => console.error(e));
        }
    }, [open]);

    return (
        <Dialog onClose={handleClose} open={open}>
            <DialogTitle>Add Input</DialogTitle>
            <FixedSizeList height={400} width={300} itemSize={46} itemData={{devices: devices, handleListItemClick: handleListItemClick}} itemCount={devices.length}>
                {inputItem}
            </FixedSizeList>
        </Dialog>
    );
}

NewInputDialog.propTypes = {
    onClose: PropTypes.func.isRequired,
    open: PropTypes.bool.isRequired,
};

const InputsWithSocket = (props) => {
    const classes = useStyles();
    const [inputs, setInputs] = useState([]);
    const [open, setOpen] = useState(false);

    const handleClose = input => {
        if (input != null) {
            let new_device = { 'type': 'device', 'display_name': input, 'name': input };
            fetch('/audio/input', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(new_device)})
                .then(response => response.json())
                .catch(e => console.error(e));
        }
        setOpen(false);
    };

    // Set up the automatic update
    const created = (data) => setInputs(inputs => inputs.concat(data));
    const updated = (data) =>
        setInputs(inputs => inputs.map(input => input.id == data.id ? Object.assign(input, data) : input));
    const remove = (data) => setInputs(inputs => inputs.filter(x => x.id != data.id));

    useEffect(() => {
        props.socket.on('input_create', created);
        props.socket.on('input_update', updated);
        props.socket.on('input_remove', remove);
        return () => {
            props.socket.off('input_create', created);
            props.socket.off('input_update', updated);
            props.socket.off('input_remove', remove);
        };
    }, [props.socket]);

    // Get the initial state by requesting it
    useEffect(() => {
        fetch('/audio/input')
            .then(response => response.json())
            .then(inputs => setInputs(inputs))
            .catch(e => console.error(e));
    }, []);

    return (
        <div className={classes.input_list}>
            {inputs.map(input => <Input input={input} key={input.id} />)}
            <Tooltip title="Add an input device">
                <Fab size="small" color="primary" onClick={event => setOpen(true)} className={classes.add_button}>
                    <AddIcon />
                </Fab>
            </Tooltip>
            <NewInputDialog open={open} onClose={handleClose} />
        </div>
    );
};

const Inputs = (props) => (
    <SocketContext.Consumer>
        {socket => <InputsWithSocket {...props} socket={socket} />}
    </SocketContext.Consumer>
);

export default Inputs;