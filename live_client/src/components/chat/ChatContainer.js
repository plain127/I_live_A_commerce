import React from 'react';
import styled from 'styled-components';
import ChatInput from './ChatInput';
import SendChatButton from './SendChatButton';
import ChatWindow from './ChatWindow';
import Chatbot from './Chatbot';

// 전체 컨테이너 중앙 정렬
const ChatContainerWrapper = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background-color: ${(props) => props.theme.colors.surface || '#ffffff'};
  border: 1px solid ${(props) => props.theme.colors.border || '#ddd'};
  border-radius: 8px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  width: 50%;
  margin: 60px 10px 10px 0px;
`;

// 제목 스타일
const Title = styled.h2`
  margin: 0;
  margin-bottom: 20px;
  font-size: 1.5rem;
  font-weight: bold;
  color: ${(props) => props.theme.colors.primary || '#007bff'};
  text-align: center;
`;

const InputContainer = styled.div`
  margin-top: 10px;
  display: flex;
  align-items: stretch;
  justify-content: space-between;
  border: none;
  width:100%;
  background-color: #f9f9f9;
`;

const ChatContainer = () => {
    return (
        <ChatContainerWrapper>
            <Title>네쇼라 챗봇</Title> {/* 제목 추가 */}
            <Chatbot />
            <ChatWindow />
            <InputContainer>
                <ChatInput />
                <SendChatButton />
            </InputContainer>  
        </ChatContainerWrapper>
    );
};

export default ChatContainer;
