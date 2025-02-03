import React from 'react';
import styled, { ThemeProvider } from 'styled-components';
import CategorySelector from './components/CategorySelector';
import ChannelSelector from './components/ChannelSelector';
import VideoPlayer from './components/VideoPlayer';
import SentimentValue from './components/analysis/SentimentValue';
import { AppProvider } from './AppContext';
import ChatContainer from './components/chat/ChatContainer';
import HighlightChart from './components/analysis/HighlightChart';

const AppContainer = styled.div`
  display: flex;
  flex-direction: column;
  background-color: ${(props) => props.theme.colors.background};
  color: ${(props) => props.theme.colors.text};
  font-family: ${(props) => props.theme.fonts.base}; 
`;

const HeaderSection = styled.header`
  background-color: ${(props) => props.theme.colors.primary};
  padding: 12px 20px;
  color: #fff;
  display: flex;
  align-items: center;
`;

const MainSection = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 0 50px
`;

const TopSection = styled.div`
  display: flex;
  flex: 1;
  padding: 10px;
  box-sizing: border-box;
  justify-content: space-evenly
`;

const VideoContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 10px;
  align-item: start;
`;

const BottomSection = styled.div`
  flex: 1;
  margin-top: 20px;
  padding: 20px;
  box-sizing: border-box;
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 8px;
  background-color: ${(props) => props.theme.colors.surface};
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

function App() {
  return (
      <AppProvider>
        <AppContainer>
          <HeaderSection>
            <CategorySelector />
          </HeaderSection>

          <MainSection>
            <TopSection>
              <VideoContainer>
                <ChannelSelector />
                <VideoPlayer autoPlay={true} controls={true} />
              </VideoContainer>
              <ChatContainer />
            </TopSection>

            <BottomSection>
              <SentimentValue />
              <HighlightChart />
            </BottomSection>
          </MainSection>
        </AppContainer>
      </AppProvider>
  );
}

export default App;
