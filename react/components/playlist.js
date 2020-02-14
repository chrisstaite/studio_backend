import React, { useEffect, useState, forwardRef, useImperativeHandle } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import Typography from '@material-ui/core/Typography';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Select from '@material-ui/core/Select';
import InputLabel from '@material-ui/core/InputLabel';
import FormControl from '@material-ui/core/FormControl';
import MenuItem from '@material-ui/core/MenuItem';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import AddIcon from '@material-ui/icons/Add';
import RemoveIcon from '@material-ui/icons/Remove';
import { Droppable, Draggable } from 'react-beautiful-dnd';
import useDebouncedEffect from 'use-debounced-effect';
import { confirmAlert } from 'react-confirm-alert';
import 'react-confirm-alert/src/react-confirm-alert.css';
import Time from './time.js';
import NewPlaylistDialog from './new-playlist.js';
import { fetchGet, fetchPost, fetchPut, fetchDelete } from './fetch-wrapper.js';

const useStyles = makeStyles({
    placeholder: {
        color: 'grey',
        textAlign: 'center',
    },
    table: {
        display: 'table',
    },
    select: {
        minWidth: 120,
    },
});

const PlaylistHeader = () => (
    <TableRow>
        <TableCell>
            Artist
        </TableCell>
        <TableCell>
            Title
        </TableCell>
        <TableCell>
            Length
        </TableCell>
    </TableRow>
);

const Track = ({row, index, provided, ...props}) => {
    return (
        <TableRow ref={provided.innerRef} {...provided.draggableProps} {...provided.dragHandleProps} {...props}>
            <TableCell>
                {row.artist}
            </TableCell>
            <TableCell>
                {row.title}
            </TableCell>
            <TableCell>
                <Time time={row.length} />
            </TableCell>
        </TableRow>
    );
};

const DragTrack = ({row, player, index}) => {
    const classes = useStyles();

    const TrackItem = (provided, snapshot) => (
        <Track row={row} className={snapshot.isDragging ? classes.table : ''} index={index} provided={provided} />
    );

    return (
        <Draggable draggableId={'playlist_track-' + row.unique_id} index={index}>
            {TrackItem}
        </Draggable>
    );
};

const Playlist = forwardRef((props, ref) => {
    const [ rows, setRows ] = useState([]);
    const classes = useStyles();
    const [ playlists, setPlaylists ] = useState([]);
    const [ playlist, setPlaylist ] = useState('');
    const [ playlistLoading, setPlaylistLoading ] = useState(false);
    const [ nextId, setNextId ] = useState(0);
    const [ open, setOpen ] = useState(false);

    useImperativeHandle(ref, () => ({
        addTrack(index, track) {
            setRows(rows => {
                const newRows = Array.from(rows);
                track.unique_id = nextId;
                setNextId(nextId => nextId + 1);
                newRows.splice(index, 0, track);
                return newRows;
            });
        },
        moveTrack(destinationIndex, sourceIndex) {
            setRows(rows => {
                const newRows = Array.from(rows);
                newRows.splice(destinationIndex, 0, newRows.splice(sourceIndex, 1)[0]);
                return newRows;
            })
        },
        removeTrack(index) {
            setRows(rows => rows.filter((_, i) => i !== index));
        },
    }));

    useEffect(() => {
        fetchGet('/playlist')
            .then(playlists => setPlaylists(playlists))
            .catch(e => console.error(e));
    }, []);

    useEffect(() => {
        if (playlist == '') {
            setRows([]);
            setNextId(0);
        } else {
            fetchGet('/playlist/' + playlist)
                .then(tracks => {
                    let id = 0;
                    setPlaylistLoading(true);
                    setRows(tracks.map(track => {
                        track.unique_id = id;
                        id += 1;
                        return track;
                    }));
                    setNextId(id);
                })
                .catch(e => console.error(e));
        }
    }, [playlist]);

    const handleClose = (playlist) => {
        if (playlist !== null) {
            fetchPost('/playlist', {'name': playlist})
                .then(response => setPlaylists(playlists => {
                    var playlists = playlists.concat([{ 'id': response, 'name': playlist }]);
                    setPlaylistLoading(true);
                    setRows([]);
                    setNextId(0);
                    setPlaylist(response);
                    return playlists;
                }))
                .catch(e => console.error(e));
        }
        setOpen(false);
    };

    useDebouncedEffect(
        () => {
            if (playlistLoading) {
                setPlaylistLoading(false);
                return;
            }
            if (playlist == '') {
                return;
            }
            fetchPut('/playlist/' + playlist, {'tracks': rows.map(row => row.id)})
                .catch(e => console.error(e));
        },
        200,
        [playlist, rows]
    );

    const deletePlaylist = () => {
        const deletePlaylist = playlist;
        confirmAlert({
            title: 'Delete playlist',
            message: 'Are you sure you want to delete the playlist?',
            buttons: [
                {
                    label: 'Yes',
                    onClick: () => {
                        setPlaylist('');
                        fetchDelete('/playlist/' + deletePlaylist)
                            .then(_ => setPlaylists(playlists => playlists.filter(x => x['id'] != deletePlaylist)))
                            .catch(e => console.error(e));
                    },
                },
                {
                    label: 'No',
                }
            ]
        });
    };

    return (
        <Card style={{width: '50%', display: 'table-cell'}}>
            <CardContent>
                <Typography component="h5" variant="h5">
                    Playlist
                </Typography>
                <FormControl className={classes.select}>
                    <InputLabel>Playlist</InputLabel>
                    <Select autoWidth={true} value={playlist} onChange={event => setPlaylist(event.target.value)}>
                        {playlists.map(playlist => <MenuItem value={playlist.id} key={playlist.id}>{playlist.name}</MenuItem>)}
                    </Select>
                </FormControl>
                <Tooltip title="New playlist">
                    <Fab color="primary" size="small" onClick={e => setOpen(true)}>
                        <AddIcon />
                    </Fab>
                </Tooltip>
                {playlist != '' && <Tooltip title="Delete playlist">
                    <Fab color="primary" size="small" onClick={e => deletePlaylist()}>
                        <RemoveIcon />
                    </Fab>
                </Tooltip>}
                <NewPlaylistDialog open={open} onClose={handleClose} />
                {playlist != "" &&
                <Paper>
                    <TableContainer>
                        <Table size='medium'>
                            <Droppable droppableId='playlist'>
                                {(provided, snapshot) =>
                                    <React.Fragment>
                                        <TableHead>
                                            <PlaylistHeader />
                                        </TableHead>
                                        <TableBody ref={provided.innerRef} className={classes.relative} {...provided.droppableProps}>
                                            {rows.length == 0 && !snapshot.isDraggingOver && <TableRow>
                                                <TableCell colSpan={3} className={classes.placeholder}>
                                                    Drop tracks here
                                                </TableCell>
                                            </TableRow>}
                                            {rows.map((row, index) =>
                                                <DragTrack row={row} index={index} key={row.unique_id} />)}
                                            {provided.placeholder}
                                        </TableBody>
                                    </React.Fragment>
                                }
                            </Droppable>
                        </Table>
                    </TableContainer>
                </Paper>}
            </CardContent>
        </Card>
    );
});

export default Playlist;
