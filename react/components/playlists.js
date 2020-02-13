import React, { useRef } from 'react';
import { DragDropContext } from 'react-beautiful-dnd';
import Library from './library.js';
import Playlist from './playlist.js';

const Playlists = () => {
    const playlist = useRef();
    const library = useRef();

    const onDragEnd = ({ source, destination }) => {
        // Check if removing
        if (source.droppableId === 'playlist' &&
                (destination === null || destination.droppableId !== 'playlist'))
        {
            playlist.current.removeTrack(source.index);
            return;
        }

        // Only interested in updating the playlists, not the libraries
        if (destination.droppableId !== 'playlist') {
            return;
        }

        if (source.droppableId === 'library') {
            // Add track to playlist
            playlist.current.addTrack(
                destination.index, library.current.getTrack(source.index)
            );
        } else {
            // Move track location
            playlist.current.moveTrack(destination.index, source.index);
        }
    };

    return (
        <DragDropContext onDragEnd={onDragEnd}>
            <Library ref={library} />
            <Playlist ref={playlist} />
        </DragDropContext>
    );
};

export default Playlists;