import React, { useRef, useEffect } from 'react';
import Hls from 'hls.js';
import { useApp } from '../AppContext';
import styled from 'styled-components';

const Container = styled.div`
  width: ${(props) => props.width};
  height: ${(props) => props.height};
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #000;
`;

const Message = styled.div`
  color: #fff;
  font-size: 16px;
  text-align: center;
`;

const StyledVideo = styled.video`
  width: 100%;
  height: 100%;
  object-fit: cover;
  background-color: #000;
`;

const VideoPlayer = ({
  autoPlay = true,
  controls = true
}) => {
  const width = '412.875px' // 세로 영상 가로 크기
  const height = '640px'// 세로 영상 세로 크기
  const videoRef = useRef(null);
  const { category_map, selectedCategory, selectedChannel } = useApp();

  const src = selectedChannel
    ? `http://localhost:1700/db/${category_map[selectedCategory]}_${selectedChannel}/${category_map[selectedCategory]}_${selectedChannel}_data/output.m3u8`
    : null;

  useEffect(() => {
    if (!selectedChannel) return; // 채널이 없으면 실행하지 않음

    const video = videoRef.current;

    if (!video) return;

    if (Hls.isSupported()) {
      const hls = new Hls();

      hls.loadSource(src);
      hls.attachMedia(video);

      hls.on(Hls.Events.ERROR, (event, data) => {
        if (data.fatal) {
          console.error('Fatal HLS error:', data);
          if (data.type === Hls.ErrorTypes.NETWORK_ERROR) {
            console.warn('Recovering from network error...');
            hls.startLoad();
          } else if (data.type === Hls.ErrorTypes.MEDIA_ERROR) {
            console.warn('Recovering from media error...');
            hls.recoverMediaError();
          } else {
            console.error('Unrecoverable error, destroying HLS instance.');
            hls.destroy();
          }
        }
      });

      const interval = setInterval(() => {
        hls.startLoad();
      }, 5000);

      return () => {
        clearInterval(interval);
        hls.destroy();
      };
    } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
      video.src = src;
    } else {
      console.warn('HLS is not supported in this browser.');
    }
  }, [src, selectedChannel]);

  if (!selectedChannel) {
    return (
      <Container width={width} height={height}>
        <Message>해당 카테고리에 영상이 없습니다.</Message>
      </Container>
    );
  }

  return (
    <Container width={width} height={height}>
      <StyledVideo
        ref={videoRef}
        autoPlay={autoPlay}
        controls={controls}
      />
    </Container>
  );
};

export default VideoPlayer;
