import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { useInputs } from './input-store.js';
import Dialog from '@material-ui/core/Dialog';
import DialogTitle from '@material-ui/core/DialogTitle';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import { FixedSizeList } from 'react-window';
import { fetchGet } from './fetch-wrapper.js';

function inputItem({ data, index, style }) {
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

function NewInputDialog({ onClose, open }) {
    const [devices, setDevices] = useState([]);
    const inputs = useInputs();

    const handleClose = () => {
        onClose(null);
    };

    const handleListItemClick = value => {
        onClose(value);
    };

    // Get the list of available devices
    useEffect(() => {
        if (open == true) {
            fetchGet('/audio/input/devices')
                .then(devices => devices.filter(device => inputs.findIndex(item => item.name == device) == -1))
                .then(devices => setDevices(devices))
                .catch(e => console.error(e));
        }
    }, [open]);

    return (
        <Dialog onClose={handleClose} open={open}>
            <DialogTitle>Add Input</DialogTitle>
            <FixedSizeList height={400} width={300} itemSize={46} itemCount={devices.length}
                    itemData={{devices: devices, handleListItemClick: handleListItemClick}}>
                {inputItem}
            </FixedSizeList>
        </Dialog>
    );
}

NewInputDialog.propTypes = {
    onClose: PropTypes.func.isRequired,
    open: PropTypes.bool.isRequired,
};

export default NewInputDialog;