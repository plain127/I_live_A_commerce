import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../AppContext';


const StyledInput = styled.input`
  flex: 1;
  padding: 10px;
  font-size: 14px;
  border: 1px solid #ccc;
  border-radius: 8px;
  outline: none;
  margin-right: 10px;
  background-color: #ffffff;

  &:focus {
    border-color: ${(props) => props.theme.colors.primaryLight};
    box-shadow: 0 0 5px ${(props) => props.theme.colors.primary};
  }
`;

function ChatInput() {
  const { currentMessage, setCurrentMessage, handleSendMessage } = useApp()
  const handleChange = (e) => {
    setCurrentMessage(e.target.value);
  };
  const handleEnter = (e) => {
    if (e.key === 'Enter'){
      handleSendMessage();
      
    }
  };

  return (
      <StyledInput
        type="text"
        value={currentMessage}
        onChange={handleChange}
        onKeyDown={handleEnter}
        placeholder="채팅을 입력하세요..."
      />
  );
}

export default ChatInput;
