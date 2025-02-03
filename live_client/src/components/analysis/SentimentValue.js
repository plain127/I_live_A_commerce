import React from 'react';
import { useApp } from '../../AppContext';

const SentimentValue = () => {
  const { sentimentScores, selectedCategory, selectedChannel } = useApp()
  const sentimentScore = sentimentScores[selectedCategory]?.[selectedChannel]
  const color =  sentimentScore > 0.5 ? 'green' : 'red';
  
  return (
    <div style={{ margin: '10px', color }}>
      댓글 감성 분석 값: {sentimentScore? sentimentScore : '분석 중'}
    </div>
  );
}

export default SentimentValue;
