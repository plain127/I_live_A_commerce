import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../AppContext';

// 채팅 창 스타일
const WindowContainer = styled.div`
  padding: 10px;
  border: 1px solid #ddd;
  height: 100%;
  width: 100%;
  overflow-y: auto;
  background-color: #f9f9f9;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 10px;
`;

// 메시지 컨테이너 스타일
const MessageContainer = styled.div`
  display: flex;
  justify-content: ${(props) => (props.isUser ? 'flex-end' : 'flex-start')};
`;

// 말풍선 스타일
const Message = styled.div`
  padding: 10px 15px;
  border-radius: 20px;
  background-color: ${(props) => (props.isUser ? '#d1f7c4' : '#ffffff')};
  color: #000000;
  font-size: 14px;
  max-width: 70%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  position: relative;

  /* 말풍선 꼬리 */
  &:after {
    content: '';
    position: absolute;
    top: 50%;
    ${(props) =>
      props.isUser
        ? `
          right: -5px;
          border-width: 10px 0 10px 10px;
          border-color: transparent transparent transparent #d1f7c4;
        `
        : `
          left: -5px;
          border-width: 10px 10px 10px 0;
          border-color: transparent #ffffff transparent transparent;
        `};
    border-style: solid;
    transform: translateY(-50%);
  }
`;

const ChatWindow = () => {
  const { messages } = useApp();

  return (
    <WindowContainer>
      {messages.map((msg, index) => (
        <MessageContainer key={index} isUser={msg.isUser}>
          <Message isUser={msg.isUser}>{msg.text}</Message>
        </MessageContainer>
      ))}
    </WindowContainer>
  );
};

export default ChatWindow;
