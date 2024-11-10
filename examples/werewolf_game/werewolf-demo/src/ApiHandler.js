import { useState, useEffect } from 'react';

const useApiDialogue = (apiUrl) => {
  const [dialogue, setDialogue] = useState([]);

  const fetchDialogue = async () => {
    try {
      const response = await fetch(apiUrl);
      const data = await response.json();
      setDialogue(data);
    } catch (error) {
      console.error('Error fetching dialogue:', error);
    }
  };

  useEffect(() => {
    // 定期轮询获取新数据
    const interval = setInterval(fetchDialogue, 1000); // 每秒更新一次
    return () => clearInterval(interval);
  }, []);

  return dialogue;
};

export default useApiDialogue;