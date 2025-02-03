import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../AppContext';

const StyledButton = styled.button`
  padding: 5px 10px;
  font-size: 15px;
  font-weight: bold;
  color: #ffffff;
  background-color: ${(props) => props.theme.colors.primaryDark};
  border: none;
  border-radius: 8px;
  cursor: pointer;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;

  &:hover {
    background-color: ${(props) => props.theme.colors.primary};
    transform: translateY(-1px);
    box-shadow: 0 6px 8px rgba(0, 0, 0, 0.2);
  }

  &:active {
    background-color: ${(props) => props.theme.colors.primaryLight};
    transform: translateY(0);
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  }
`;

function SendChatButton() {
  const { handleSendMessage } = useApp()
  return <StyledButton onClick={handleSendMessage}>전송</StyledButton>;
}

export default SendChatButton;
