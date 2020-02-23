import React, { useState, useEffect } from 'react';
import makeStyles from '@material-ui/core/styles/makeStyles';
import Typography from '@material-ui/core/Typography';
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableContainer from '@material-ui/core/TableContainer';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import TextField from '@material-ui/core/TextField';
import PlayIcon from '@material-ui/icons/PlayArrow';
import PauseIcon from '@material-ui/icons/Pause';
import LoopIcon from '@material-ui/icons/Loop';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import SkipNextIcon from '@material-ui/icons/SkipNext';
import CancelIcon from '@material-ui/icons/Cancel';
import ToggleButton from '@material-ui/lab/ToggleButton';
import ToggleButtonGroup from '@material-ui/lab/ToggleButtonGroup';
import Tooltip from '@material-ui/core/Tooltip';
import Fab from '@material-ui/core/Fab';
import Skeleton from '@material-ui/lab/Skeleton';
import Autocomplete from '@material-ui/lab/Autocomplete';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { useSocket } from './socket.js';
import { fetchGet, fetchPut } from './fetch-wrapper.js';
import { usePlayers } from './player-store.js';
import Time from './time.js';

const useStyles = makeStyles({
    live_player: {
        minHeight: '200px',
        paddingBottom: '20px',
        padding: '10px',
    },
    table: {
        display: 'table',
    },
    track_button: {
        float: 'right',
    },
    play_button: {
        float: 'right',
    },
});

const PlaylistHeader = () => (
    <TableRow>
        <TableCell>
            Start
        </TableCell>
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

const DateTime = ({ time }) => {
    if (!time) {
        return (<span />);
    }
    let date = new Date(time * 1000);
    let now = new Date();
    let justDate = new Date(date.getFullYear(), date.getMonth(), date.getDate());
    let justDateNow = new Date(now.getFullYear(), now.getMonth(), now.getDate());
    let days = (justDate.getTime() - justDateNow.getTime()) / (1000 * 60 * 60 * 24);
    return (
        <span>
            {date.getHours().toString().padStart(2, '0')}:
            {date.getMinutes().toString().padStart(2, '0')}:
            {date.getSeconds().toString().padStart(2, '0')}
            {days > 0 && ` +${days} day`}
        </span>
    );
};

const PlaylistItem = React.forwardRef(
        ({ index, item, setType, startTime, setLength, time, skip, remove, ...props }, ref) => {
    const classes = useStyles();
    const [ track, setTrack ] = useState(false);

    useEffect(() => {
        fetchGet('/library/track/' + item.id + '/info')
            .then(track => { setTrack(track); setLength(track.length); })
            .catch(e => console.error(e));
    }, [item.id]);

    const toggleType = () => {
        let type = '';
        if (item.type == 'play_next') {
            type = 'pause_after';
        } else if (item.type == 'pause_after') {
            type = 'loop';
        } else {
            type = 'play_next';
        }
        setType(type);
    };

    let percent = 0.0;
    if (track) {
        percent = time * 100 / track.length;
    }
    const style = {
        background: 'linear-gradient(to right, #dedede ' + percent + '%, transparent 0%)',
    };

    return (
        <TableRow style={style} ref={ref} {...props}>
            <TableCell>
                {index > 0 && <DateTime time={startTime} />}
            </TableCell>
            <TableCell>
                {!track && <Skeleton variant="text" />}
                {track && track.artist}
            </TableCell>
            <TableCell>
                {!track && <Skeleton variant="text" />}
                {track && track.title}
            </TableCell>
            <TableCell>
                {!track && <Skeleton variant="text" />}
                {track && <Time time={track.length} />}
            </TableCell>
            <TableCell>
                <ToggleButtonGroup value={item.type} exclusive onChange={(e, type) => setType(type)}>
                    <ToggleButton value='play_next'>
                        <ExpandMoreIcon />
                    </ToggleButton>
                    <ToggleButton value='pause_after'>
                        <PauseIcon />
                    </ToggleButton>
                    <ToggleButton value='loop'>
                        <LoopIcon />
                    </ToggleButton>
                </ToggleButtonGroup>
                <div className={classes.track_button}>
                    {skip && <Tooltip title="Skip to next">
                        <Fab color="primary" size="small" onClick={skip}>
                            <SkipNextIcon />
                        </Fab>
                    </Tooltip>}
                    {remove && <Tooltip title="Remove track">
                        <Fab color="primary" size="small" onClick={remove}>
                            <CancelIcon />
                        </Fab>
                    </Tooltip>}
                </div>
            </TableCell>
        </TableRow>
    );
});

const DraggablePlaylistItem = ({ index, ...props }) => {
    const classes = useStyles();

    if (index == 0) {
        return (<PlaylistItem index={index} {...props}/>);
    }

    return (
        <Draggable draggableId={'track-' + index} index={index}>
            {(provided, snapshot) =>
                <PlaylistItem
                    className={snapshot.isDragging ? classes.table : ''}
                    ref={provided.innerRef}
                    index={index}
                    {...provided.draggableProps}
                    {...provided.dragHandleProps}
                    {...props}/>}
        </Draggable>
    );
};

const SearchBox = ({ addTrack }) => {
    const [ search, setSearch ] = useState('');
    const [ options, setOptions ] = useState([]);
    const [ loading, setLoading ] = useState(false);

    useEffect(() => {
        if (search == '') {
            setOptions([]);
            setLoading(false);
        } else {
            setLoading(true);
            fetchGet(`/library/track?results=10&page=0&query=${search}`)
                .then(({count, tracks}) => { setOptions(tracks); setLoading(false); })
                .catch(e => { console.error(e); setLoading(false); });
        }
    }, [search]);

    const inputChange = (event, value, reason) => {
        setSearch(reason == 'input' ? value : '');
    };

    return (
        <Autocomplete
            onInputChange={inputChange}
            onChange={(event, value) => {value && addTrack(value.id);}}
            inputValue={search}
            options={options}
            getOptionLabel={option => `${option.artist} - ${option.title}`}
            loading={loading}
            style={{ width: 300, float: 'left' }}
            renderInput={params => (
                <TextField {...params} label="Add track" variant="outlined" fullWidth />
            )}/>
    );
};

const PlaylistBox = ({ addPlaylist }) => {
    const [ search, setSearch ] = useState('');
    const [ playlists, setPlaylists ] = useState([]);
    const [ loading, setLoading ] = useState(true);

    useEffect(() => {
        fetchGet('/playlist')
            .then(playlists => setPlaylists(playlists))
            .then(() => setLoading(false))
            .catch(e => console.error(e));
    }, []);

    const inputChange = (event, value, reason) => {
        setSearch(reason == 'input' ? value : '');
    };

    return (
        <Autocomplete
            onInputChange={inputChange}
            onChange={(event, value) => {value && addPlaylist(value.id);}}
            options={playlists}
            inputValue={search}
            getOptionLabel={option => option.name}
            loading={loading}
            style={{ width: 300, float: 'left' }}
            renderInput={params => (
                <TextField {...params} label="Add playlist" variant="outlined" fullWidth />
            )}/>
    );
};

const LivePlayer = ({ player_id }) => {
    const classes = useStyles();
    const socket = useSocket();
    const [ name, setName ] = useState('Live Player ' + player_id);
    const [ tracks, setTracks ] = useState([]);
    const [ jingleCount, setJingleCount ] = useState(0);
    const [ state, setState ] = useState('paused');
    const [ jinglePlaylist, setJinglePlaylist ] = useState('');
    const [ currentTime, setCurrentTime ] = useState(0.0);
    const [ startTime, setStartTime ] = useState(0);
    const [ trackLengths, setTrackLengths ] = useState([]);

    useEffect(() => {
        fetchGet('/player/' + player_id)
            .then(player => setName(player.name))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/jingle_count')
            .then(count => setJingleCount(count))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/state')
            .then(state => setState(state))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/tracks')
            .then(tracks => setTracks(tracks))
            .catch(e => console.error(e));
        fetchGet('/player/' + player_id + '/jingle_playlist')
            .then(playlist => setJinglePlaylist(playlist))
            .catch(e => console.error(e));
    }, [player_id]);

    const updatePlayer = ({id, name}) => {
        if (id == player_id) {
            setName(name);
        }
    };

    useEffect(() => {
        socket.on('player_update', updatePlayer);
        socket.on('player_jinglecount_' + player_id, setJingleCount);
        socket.on('player_jingles_' + player_id, setJinglePlaylist);
        socket.on('player_tracks_' + player_id, setTracks);
        socket.on('player_state_' + player_id, setState);
        socket.on('player_tracktime_' + player_id, setCurrentTime);
        return () => {
            socket.off('player_update', updatePlayer);
            socket.off('player_jinglecount_' + player_id, setJingleCount);
            socket.off('player_jingles_' + player_id, setJinglePlaylist);
            socket.off('player_tracks_' + player_id, setTracks);
            socket.off('player_state_' + player_id, setState);
            socket.off('player_tracktime_' + player_id, setCurrentTime);
        };
    }, [socket, player_id]);

    const putTracks = tracks => {
        let allTracks = {tracks: tracks.map(x => x.id), types: tracks.map(x => x.type)};
        fetchPut('/player/' + player_id + '/tracks', allTracks)
            .catch(e => console.error(e));
    };

    const addTrack = trackId => {
        let newTracks = tracks.slice(0);
        newTracks.splice(tracks.length > 0 ? 1 : 0, 0, {id: trackId, type: 'play_next'});
        putTracks(newTracks);
    };

    const addPlaylist = playlistId => {
        fetchGet('/playlist/' + playlistId)
            .then(playlistTracks => putTracks(
                tracks.concat(playlistTracks.map(track => ({id: track.id, type: 'play_next'}))))
            )
            .catch(e => console.error(e));
    };

    const putState = state => {
        fetchPut('/player/' + player_id + '/state', {state: state})
            .catch(e => console.error(e));
    };

    const setType = (index, type) => {
        let updated = tracks.slice(0);
        updated[index].type = type;
        putTracks(updated);
    };

    const remove = index => {
        let newTracks = tracks.slice(0);
        newTracks.splice(index, 1);
        putTracks(newTracks);
    };

    const skip = () => {
        putTracks(tracks.slice(1));
    };

    const onDragEnd = ({ source, destination }) => {
        if (destination == null ||
                destination.index == 0 ||
                source.index == destination.index) {
            return;
        }
        setTracks(tracks => {
            const newTracks = tracks.slice(0);
            newTracks.splice(destination.index, 0, newTracks.splice(source.index, 1)[0]);
            putTracks(newTracks);
            return newTracks;
        });
    };

    const setTrackLength = (index, length) => {
        setTrackLengths(lengths => {
            var newArray;
            if (lengths.length <= index) {
                newArray = lengths.fill(0, lengths.length, index);
            } else {
                newArray = lengths.slice(0);
            }
            newArray[index] = length;
            return newArray;
        });
    };

    const updateTime = () =>
        setStartTime(Math.floor(new Date().getTime() / 1000) - Math.round(currentTime));

    useEffect(updateTime, [currentTime]);

    useEffect(() => {
        if (state == 'playing') {
            return;
        }
        let interval = setInterval(updateTime, 1000);
        return () => {
            clearInterval(interval);
        };
    }, [state]);

    const getStartTime = index => {
        return trackLengths.slice(0, index).reduce((a, b) => a + b, startTime);
    };

    return (
        <Paper className={classes.live_player}>
            <Typography component="h5" variant="h5">
                {name}
            </Typography>
            <Paper>
                <SearchBox addTrack={addTrack} />
                <PlaylistBox addPlaylist={addPlaylist} />
                {state == 'paused' &&
                    <Tooltip title="Play">
                        <Fab color="primary"
                             size="small"
                             onClick={() => putState('playing')}
                             className={classes.play_button}>
                            <PlayIcon />
                        </Fab>
                    </Tooltip>}
                {state == 'playing' &&
                    <Tooltip title="Pause">
                        <Fab color="primary"
                             size="small"
                             onClick={() => putState('paused')}
                             className={classes.play_button}>
                            <PauseIcon />
                        </Fab>
                    </Tooltip>}
                <TableContainer>
                    <Table size='medium'>
                        <TableHead>
                            <PlaylistHeader />
                        </TableHead>
                        <DragDropContext onDragEnd={onDragEnd}>
                            <Droppable droppableId={`live_player_${player_id}`}>
                                {(provided, snapshot) =>
                                    <TableBody ref={provided.innerRef}
                                            className={classes.relative}
                                            {...provided.droppableProps}>
                                        {tracks.map((track, index) =>
                                            <DraggablePlaylistItem
                                                item={track}
                                                setType={type => setType(index, type)}
                                                time={index == 0 ? currentTime : 0.0}
                                                skip={index == 0 ? skip : undefined}
                                                remove={index == 0 ? undefined : () => remove(index)}
                                                startTime={getStartTime(index)}
                                                setLength={length => setTrackLength(index, length)}
                                                index={index}
                                                key={index} />)}
                                        {provided.placeholder}
                                    </TableBody>
                                }
                            </Droppable>
                        </DragDropContext>
                    </Table>
                </TableContainer>
            </Paper>
        </Paper>
    );
};

export default LivePlayer;
