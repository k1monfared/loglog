import { useRef, useCallback, useState } from 'react';

export interface HistoryState {
  content: string;
  timestamp: number;
}

export interface UndoRedoState {
  canUndo: boolean;
  canRedo: boolean;
}

export function useUndoRedo(initialContent: string = '', maxHistorySize: number = 50) {
  const historyRef = useRef<HistoryState[]>([{ content: initialContent, timestamp: Date.now() }]);
  const currentIndexRef = useRef<number>(0);
  const [undoRedoState, setUndoRedoState] = useState<UndoRedoState>({
    canUndo: false,
    canRedo: false,
  });

  const updateState = useCallback(() => {
    setUndoRedoState({
      canUndo: currentIndexRef.current > 0,
      canRedo: currentIndexRef.current < historyRef.current.length - 1,
    });
  }, []);

  const addToHistory = useCallback((content: string) => {
    const now = Date.now();
    const currentIndex = currentIndexRef.current;
    const history = historyRef.current;
    
    // Don't add if content hasn't changed
    if (history[currentIndex]?.content === content) {
      return;
    }
    
    // Remove any redo history when adding new content
    if (currentIndex < history.length - 1) {
      historyRef.current = history.slice(0, currentIndex + 1);
    }
    
    // Add new state
    historyRef.current.push({ content, timestamp: now });
    
    // Maintain max history size
    if (historyRef.current.length > maxHistorySize) {
      historyRef.current = historyRef.current.slice(-maxHistorySize);
      currentIndexRef.current = historyRef.current.length - 1;
    } else {
      currentIndexRef.current = historyRef.current.length - 1;
    }
    
    updateState();
  }, [maxHistorySize, updateState]);

  const undo = useCallback((): string | null => {
    if (currentIndexRef.current > 0) {
      currentIndexRef.current -= 1;
      updateState();
      return historyRef.current[currentIndexRef.current].content;
    }
    return null;
  }, [updateState]);

  const redo = useCallback((): string | null => {
    if (currentIndexRef.current < historyRef.current.length - 1) {
      currentIndexRef.current += 1;
      updateState();
      return historyRef.current[currentIndexRef.current].content;
    }
    return null;
  }, [updateState]);

  const getCurrentContent = useCallback((): string => {
    return historyRef.current[currentIndexRef.current]?.content || '';
  }, []);

  const clearHistory = useCallback(() => {
    historyRef.current = [{ content: initialContent, timestamp: Date.now() }];
    currentIndexRef.current = 0;
    updateState();
  }, [initialContent, updateState]);

  const getHistoryInfo = useCallback(() => {
    return {
      currentIndex: currentIndexRef.current,
      totalStates: historyRef.current.length,
      history: historyRef.current.map((state, index) => ({
        index,
        timestamp: state.timestamp,
        isCurrent: index === currentIndexRef.current,
      })),
    };
  }, []);

  return {
    addToHistory,
    undo,
    redo,
    getCurrentContent,
    clearHistory,
    getHistoryInfo,
    ...undoRedoState,
  };
}

/**
 * Throttled version of addToHistory for performance
 */
export function useThrottledUndoRedo(
  initialContent: string = '',
  maxHistorySize: number = 50,
  throttleMs: number = 1000
) {
  const undoRedo = useUndoRedo(initialContent, maxHistorySize);
  const lastAddTime = useRef<number>(0);
  const pendingContent = useRef<string>('');
  const timeoutRef = useRef<NodeJS.Timeout>();

  const throttledAddToHistory = useCallback((content: string) => {
    const now = Date.now();
    pendingContent.current = content;
    
    if (now - lastAddTime.current >= throttleMs) {
      lastAddTime.current = now;
      undoRedo.addToHistory(content);
    } else {
      // Clear existing timeout and set new one
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        lastAddTime.current = Date.now();
        undoRedo.addToHistory(pendingContent.current);
      }, throttleMs - (now - lastAddTime.current));
    }
  }, [undoRedo, throttleMs]);

  return {
    ...undoRedo,
    addToHistory: throttledAddToHistory,
  };
}