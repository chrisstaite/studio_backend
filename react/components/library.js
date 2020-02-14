import React, { useState, useEffect, forwardRef, useImperativeHandle } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Card from '@material-ui/core/Card';
import Typography from '@material-ui/core/Typography';
import CardHeader from '@material-ui/core/CardHeader';
import CardContent from '@material-ui/core/CardContent';
import CardActions from '@material-ui/core/CardActions';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TablePagination from '@material-ui/core/TablePagination';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import LibraryMusicIcon from '@material-ui/icons/LibraryMusic';
import CloseIcon from '@material-ui/icons/Close';
import PlayIcon from '@material-ui/icons/PlayArrow';
import StopIcon from '@material-ui/icons/Stop';
import EditIcon from '@material-ui/icons/Edit';
import CircularProgress from '@material-ui/core/CircularProgress';
import Input from '@material-ui/core/Input';
import InputLabel from '@material-ui/core/InputLabel';
import InputAdornment from '@material-ui/core/InputAdornment';
import IconButton from '@material-ui/core/IconButton';
import FormControl from '@material-ui/core/FormControl';
import { Droppable, Draggable } from "react-beautiful-dnd";
import useDebouncedEffect from 'use-debounced-effect';
import Time from './time.js';
import LibraryRoots from './library-roots.js';
import { fetchPut, fetchGet } from './fetch-wrapper.js';

const useStyles = makeStyles({
    row: {
        transform: 'none !important',
    },
    hidden: {
        display: 'none !important',
    },
    table: {
        display: 'table',
    },
    edit: {
        width: '0.5em',
        verticalAlign: 'bottom',
        cursor: 'pointer',
        paddingRight: '0.2em',
    },
});

const LibraryHeader = () => (
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
        <TableCell />
    </TableRow>
);

const Track = ({row, player, index, provided, ...props}) => {
    const classes = useStyles();
    const [ state, setState ] = useState('stopped');
    const [ editing, setEditing ] = useState(false);
    const [ artist, setArtist ] = useState(row.artist);
    const [ title, setTitle ] = useState(row.title);

    const play = () => {
        setState('loading');
        player.src = '/library/track/' + row.id;
        player.load();
        let promise = player.play();
        if (promise !== undefined) {
            promise
                .then(() => setState('playing'))
                .catch(() => setState('stopped'));
        }
    };

    const stop = () => {
        setState('stopped');
        player.src = '';
    };

    useEffect(() => {
        if (!editing && (row.artist != artist || row.title != title))
        {
            fetchPut('/library/track/' + row.id, {'artist': artist, 'title': title})
                .catch(e => console.error(e));
        }
    }, [editing, row, artist, title]);

    return (
        <TableRow ref={provided ? provided.innerRef : null}
                {...(provided ? provided.draggableProps : null)}
                {...(provided ? provided.dragHandleProps : null)}
                {...props}>
            <TableCell>
                <EditIcon className={classes.edit} onClick={() => setEditing(editing => !editing)} />
                {editing &&
                    <FormControl>
                        <InputLabel>Artist</InputLabel>
                        <Input value={artist} onChange={e => setArtist()}/>
                    </FormControl>}
                {!editing && artist}
            </TableCell>
            <TableCell>
                {editing &&
                    <FormControl>
                        <InputLabel>Title</InputLabel>
                        <Input value={title} onChange={e => setTitle()}/>
                    </FormControl>}
                {!editing && title}
            </TableCell>
            <TableCell>
                <Time time={row.length} />
            </TableCell>
            <TableCell>
                {state == 'stopped' &&
                    <Tooltip title="Play">
                        <Fab color="primary" size="small" onClick={play}>
                            <PlayIcon />
                        </Fab>
                    </Tooltip>}
                {state == 'loading' &&
                    <CircularProgress />}
                {state == 'playing' &&
                    <Tooltip title="Stop">
                        <Fab color="primary" size="small" onClick={stop}>
                            <StopIcon />
                        </Fab>
                    </Tooltip>}
            </TableCell>
        </TableRow>
    );
};

const DragTrack = ({row, player, index}) => {
    const classes = useStyles();

    const TrackItem = (provided, snapshot) => {
        return (
            <React.Fragment>
                <Track row={row} player={player} index={index} provided={provided}
                    className={snapshot.isDragging ? classes.table : classes.row} />
                {snapshot.isDragging && <Track row={row} player={player} index={index} />}
            </React.Fragment>
        );
    };

    return (
        <Draggable draggableId={'track-' + row.id} index={index}>
            {TrackItem}
        </Draggable>
    );
};

const Search = ({ search, setSearch }) => (
    <FormControl>
        <InputLabel>Search</InputLabel>
        <Input value={search} onChange={e => setSearch(e.target.value)}
            endAdornment={
                <InputAdornment position="end">
                    <IconButton
                            onClick={() => (search != '' && setSearch(''))}
                            onMouseDown={e => e.preventDefault()}>
                        <CloseIcon />
                    </IconButton>
                </InputAdornment>
            }
        />
    </FormControl>
);

const Library = forwardRef((props, ref) => {
    const [ search, setSearch ] = useState('');
    const [ rows, setRows ] = useState([]);
    const [ count, setCount ] = useState(0);
    const [ page, setPage ] = useState(0);
    const [ rowsPerPage, setRowsPerPage ] = useState(10);
    const [ player ] = useState(new Audio());
    const [ libraryRoots, setLibraryRoots ] = useState(false);
    const classes = useStyles();

    const handleChangeRowsPerPage = event => {
        setRowsPerPage(parseInt(event.target.value, 10));
        setPage(0);
    };

    const loadTracks = () => {
        fetchGet(`/library/track?results=${rowsPerPage}&page=${page}&query=${search}`)
            .then(({count, tracks}) => { setRows(tracks); setCount(count); })
            .catch(e => console.error(e));
    };
    useEffect(loadTracks, []);
    useDebouncedEffect(loadTracks, 100, [ search, page ]);

    useImperativeHandle(ref, () => ({
        getTrack(index) {
            return rows[index];
        },
    }));

    return (
        <Card style={{width: '50%', display: 'table-cell'}}>
            <CardContent>
                <Typography component="h5" variant="h5">
                    Library
                </Typography>
                <Search search={search} setSearch={setSearch} />
                <Paper>
                    <TableContainer>
                        <Table size='medium'>
                            <TableHead>
                                <LibraryHeader />
                            </TableHead>
                            <Droppable droppableId='library' isDropDisabled={true}>
                                {(provided, snapshot) =>
                                    <TableBody ref={provided.innerRef}>
                                        {rows.map((row, index) => <DragTrack row={row} player={player} index={index} key={row.id} />)}
                                    </TableBody>
                                }
                            </Droppable>
                        </Table>
                    </TableContainer>
                    <TablePagination
                      rowsPerPageOptions={[5, 10, 25, 100]}
                      component="div"
                      count={count}
                      rowsPerPage={rowsPerPage}
                      page={page}
                      onChangePage={(event, newPage) => setPage(newPage)}
                      onChangeRowsPerPage={handleChangeRowsPerPage}
                    />
                </Paper>
            </CardContent>
            <CardActions>
                <Tooltip title="Manage the root directories">
                    <Fab color="primary" size="small" onClick={_ => setLibraryRoots(true)}>
                        <LibraryMusicIcon />
                    </Fab>
                </Tooltip>
                <LibraryRoots open={libraryRoots} onClose={_ => setLibraryRoots(false)} />
            </CardActions>
        </Card>
    );
});

export default Library;