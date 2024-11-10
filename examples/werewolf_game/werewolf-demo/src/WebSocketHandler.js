import { useState, useEffect } from 'react';

const useWebSocket = (url) => {
  const [dialogue, setDialogue] = useState([]);
  const [ws, setWs] = useState(null);

  useEffect(() => {
    const websocket = new WebSocket(url);
    
    websocket.onmessage = (event) => {
      const newMessage = JSON.parse(event.data);
      setDialogue(prev => [...prev, newMessage]);
    };

    setWs(websocket);

    return () => {
      websocket.close();
    };
  }, [url]);

  return dialogue;
};

export default useWebSocket;