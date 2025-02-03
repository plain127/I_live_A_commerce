import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../AppContext';

const ChartContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 20px;
  padding: 10px;
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  background-color: ${(props) => props.theme.colors.surface};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
`;

const StyledImage = styled.img`
  width: 100%;
  max-width: 800px;
  height: auto;
  border-radius: 8px;
  border: 1px solid ${(props) => props.theme.colors.border};
`;

const PlaceholderContainer = styled.div`
  width: 100%;
  max-width: 800px;
  height: auto;
  aspect-ratio: 16 / 9; /* 비율을 유지하기 위해 aspect-ratio 추가 */
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  border: 1px solid ${(props) => props.theme.colors.border};
  background-color: ${(props) => props.theme.colors.background};
  color: ${(props) => props.theme.colors.textSecondary};
  font-size: 16px;
  text-align: center;
`;

const HighlightChart = () => {
  const { category_map, selectedCategory, selectedChannel } = useApp();

  const src = `http://localhost:1700/db/${category_map[selectedCategory]}_${selectedChannel}/${category_map[selectedCategory]}_${selectedChannel}_graph.png`;

  return (
    <ChartContainer>
      {selectedChannel ? <StyledImage src={src} alt="Highlight Chart" /> : <PlaceholderContainer>아직 이미지가 생성되지 않았습니다.</PlaceholderContainer>}

    </ChartContainer>
  );
};

export default HighlightChart;
