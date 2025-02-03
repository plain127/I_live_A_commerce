import React, { createContext, useContext, useEffect, useState } from 'react';
import axios from 'axios';

const AppContext = createContext();

const INITIAL_CATEGORIZED_CHANNELS = {
  '뷰티': [],
  '푸드': [],
  '패션': [],
  '라이프': [],
  '여행/체험': [],
  '키즈': [],
  '테크': [],
  '취미레저': [],
  '문화생활': []
};

const INITIAL_SENTIMENT_SCORES = {
  '뷰티': {},
  '푸드': {},
  '패션': {},
  '라이프': {},
  '여행/체험': {},
  '키즈': {},
  '테크': {},
  '취미레저': {},
  '문화생활': {}
}

const CATEGORY_MAP = {
  '뷰티': 1,
  '푸드': 2,
  '패션': 3,
  '라이프': 4,
  '여행/체험': 5,
  '키즈': 6,
  '테크': 7,
  '취미레저': 8,
  '문화생활': 9
};

export const AppProvider = ({ children }) => {
  const [messages, setMessages] = useState([]); // 채팅 메시지 목록
  const [currentMessage, setCurrentMessage] = useState(''); // 현재 입력된 메시지
  const [useVoice, setUseVoice] = useState(false); // 음성 사용 여부
  const [voiceName, setVoiceName] = useState('잇섭'); // 음성 이름
  const [selectedCategory, setSelectedCategory] = useState('뷰티'); // 선택된 카테고리
  const [selectedChannel, setSelectedChannel] = useState(null); // 선택된 채널
  const [sentimentScores, setSentimentScores] = useState(INITIAL_SENTIMENT_SCORES); // 감성 분석 점수
  const [categorizedChannels, setCategorizedChannels] = useState(INITIAL_CATEGORIZED_CHANNELS); // 채널 목록

  const initializeChannels = (data) => {
    const channels = {
      '뷰티': [],
      '푸드': [],
      '패션': [],
      '라이프': [],
      '여행/체험': [],
      '키즈': [],
      '테크': [],
      '취미레저': [],
      '문화생활': []
    };
    data.forEach((item) => {
      if (channels[item.Category]) {
        channels[item.Category].push(item.Channel);
      }
    });
    return channels;
  };

  const fetchChannels = async () => {
    try {
      const response = await axios.get('http://localhost:1700/home');
      const updatedChannels = initializeChannels(response.data);
      setCategorizedChannels(updatedChannels);
    } catch (error) {
      console.error('[Error] Fetching channels:', error.message);
      console.log('Full error object:', error);
    }
  };

  const fetchScores = async () => {
    try {
      const response = await axios.post('http://localhost:1700/sentiment', {
        category: selectedCategory,
        channel: selectedChannel,
      });
      const score = response.data?.score;
      if (score !== undefined) {
        setSentimentScores((prevScores) => ({
          ...prevScores,
          [selectedCategory]: {
            ...prevScores[selectedCategory],
            [selectedChannel]: score,
          }
        }));
      }
    } catch (error) {
      console.error("[Error] 감성 점수 가져오기 실패:", error.message);
    }
  }

  useEffect(() => {
    fetchChannels();
  }, []);

  const handleSendMessage = async () => {
    if (!currentMessage.trim()) return;

    setMessages((prevMessages) => [
      ...prevMessages,
      { isUser: true, text: currentMessage },
    ]);

    try {
      const response = await axios.post('http://localhost:1700/chat', {
        category: selectedCategory,
        channel: selectedChannel,
        text: currentMessage,
        voice: useVoice,
        who: voiceName,
      });

      if (response.data?.Text) {
        setMessages((prevMessages) => [
          ...prevMessages,
          { text: response.data.text, isUser: false },
        ]);
      }

      if (useVoice && response.data?.voice !== '/') {
        const audioSrc = `http://localhost:1700/db/${selectedCategory}_${selectedChannel}/voice.wav`
        console.log(audioSrc)
        const audio = new Audio(audioSrc);
        audio.play().catch((error) => {
          console.error('[Error] Playing audio:', error.message);
        });
      }
    } catch (error) {
      console.error('[Error] Sending message:', error.message);
    } finally {
      setCurrentMessage('');
    }
  };

  return (
    <AppContext.Provider
      value={{
        messages,
        setMessages,
        currentMessage,
        setCurrentMessage,
        handleSendMessage,
        useVoice,
        setUseVoice,
        voiceName,
        setVoiceName,
        selectedCategory,
        setSelectedCategory,
        selectedChannel,
        setSelectedChannel,
        sentimentScores,
        setSentimentScores,
        categorizedChannels,
        setCategorizedChannels,
        fetchChannels,
        category_map: CATEGORY_MAP,
        fetchScores
      }}
    >
      {children}
    </AppContext.Provider>
  );
};

export const useApp = () => useContext(AppContext);
