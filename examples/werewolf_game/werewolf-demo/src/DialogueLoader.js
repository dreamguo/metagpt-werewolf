import { useState, useEffect } from 'react';

const useDialogueLoader = (filePath) => {
  const [dialogue, setDialogue] = useState([]);

  const loadDialogue = async () => {
    try {
      const response = await fetch(filePath);
      const data = await response.json();
      setDialogue(data);
    } catch (error) {
      console.error('Error loading dialogue:', error);
    }
  };

  return { dialogue, loadDialogue };
};

export default useDialogueLoader;