import React from 'react';
import styled from 'styled-components';
import { useApp } from '../../AppContext';

// 컨테이너 스타일 (가로 배치)
const SettingContainer = styled.div`
  display: flex;
  align-items: center; /* 수직 정렬 */
  gap: 20px; /* 컴포넌트 간 간격 */
  padding-bottom: 10px;
`;

// 토글 버튼 스타일
const ToggleButton = styled.button`
  width: 50px;
  height: 25px;
  border-radius: 15px;
  border: none;
  background-color: ${(props) =>
    props.active ? props.theme.colors.primary : props.theme.colors.border};
  cursor: pointer;
  position: relative;
  outline: none;

  &::after {
    content: '';
    position: absolute;
    top: 2px;
    left: ${(props) => (props.active ? '25px' : '2px')};
    width: 21px;
    height: 21px;
    background-color: white;
    border-radius: 50%;
    transition: all 0.3s ease;
  }
`;

// 드롭다운 스타일
const VoiceSelect = styled.select`
  padding: 5px 10px;
  border: 1px solid ${(props) => props.theme.colors.border};
  border-radius: 4px;
  background-color: white;
  font-size: 14px;
  font-family: ${(props) => props.theme.fonts.base};
`;

const Label = styled.span`
  font-size: 14px;
  color: ${(props) => props.theme.colors.text};
  margin-right: 8px;
`;

function Chatbot() {
  const { useVoice, setUseVoice, voiceName, setVoiceName } = useApp();
  const voiceNames = ['잇섭', '아이유'];

  // 토글 상태 변경
  const handleToggle = () => {
    setUseVoice((prev) => !prev);
  };

  // 목소리 모드 변경
  const handleModeChange = (e) => {
    setVoiceName(e.target.value);
  };

  return (
    <SettingContainer>
      {/* 소리 토글 */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Label>챗봇 음성</Label>
        <ToggleButton active={useVoice? 'true' : undefined} onClick={handleToggle} />
      </div>

      {/* 목소리 모드 선택 */}
      <div style={{ display: 'flex', alignItems: 'center' }}>
        <Label>목소리</Label>
        <VoiceSelect value={voiceName} onChange={handleModeChange}>
          {voiceNames.map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </VoiceSelect>
      </div>
    </SettingContainer>
  );
}

export default Chatbot;
