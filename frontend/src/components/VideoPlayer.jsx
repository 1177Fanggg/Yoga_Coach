import React from 'react';

const VideoPlayer = ({ src, poster }) => {
    return (
        <div className="w-full bg-black rounded-lg overflow-hidden shadow-lg">
            <video
                className="w-full aspect-video"
                controls
                playsInline
                poster={poster}
                src={src}
            >
                您的瀏覽器不支援影片播放。
            </video>
        </div>
    );
};

export default VideoPlayer;
