import React, { createContext, useContext, useState, useCallback } from 'react';

interface FoldingContextType {
  foldedLines: Set<number>;
  toggleFold: (lineIndex: number) => void;
  foldToLevel: (level: number) => void;
  unfoldAll: () => void;
  isLineFolded: (lineIndex: number) => boolean;
  isLineVisible: (lineIndex: number, allLines: any[]) => boolean;
}

const FoldingContext = createContext<FoldingContextType | null>(null);

export const useFolding = () => {
  const context = useContext(FoldingContext);
  if (!context) {
    throw new Error('useFolding must be used within a FoldingProvider');
  }
  return context;
};

interface FoldingProviderProps {
  children: React.ReactNode;
  lines: string[];
}

export const FoldingProvider: React.FC<FoldingProviderProps> = ({ children, lines }) => {
  const [foldedLines, setFoldedLines] = useState<Set<number>>(new Set());

  const toggleFold = useCallback((lineIndex: number) => {
    setFoldedLines(prev => {
      const newSet = new Set(prev);
      if (newSet.has(lineIndex)) {
        newSet.delete(lineIndex);
      } else {
        newSet.add(lineIndex);
      }
      return newSet;
    });
  }, []);

  const foldToLevel = useCallback((targetLevel: number) => {
    const newFolded = new Set<number>();
    
    lines.forEach((line, index) => {
      const level = Math.floor((line.match(/^ */)?.[0]?.length || 0) / 4);
      
      // Check if this line has children
      const hasChildren = index < lines.length - 1 && 
        lines.slice(index + 1).some(nextLine => {
          const nextLevel = Math.floor((nextLine.match(/^ */)?.[0]?.length || 0) / 4);
          return nextLevel > level;
        });
      
      // Fold lines at or above the target level that have children
      if (hasChildren && level >= targetLevel) {
        newFolded.add(index);
      }
    });
    
    setFoldedLines(newFolded);
  }, [lines]);

  const unfoldAll = useCallback(() => {
    setFoldedLines(new Set());
  }, []);

  const isLineFolded = useCallback((lineIndex: number) => {
    return foldedLines.has(lineIndex);
  }, [foldedLines]);

  const isLineVisible = useCallback((lineIndex: number, allLines: any[]) => {
    if (lineIndex >= allLines.length) return false;
    
    const currentLevel = allLines[lineIndex].level;
    
    // Check if any parent line is folded
    for (let i = lineIndex - 1; i >= 0; i--) {
      const parentLine = allLines[i];
      if (parentLine.level < currentLevel && foldedLines.has(i)) {
        return false; // This line is hidden under a folded parent
      }
      if (parentLine.level >= currentLevel) {
        break; // Found a sibling or moved up levels
      }
    }
    
    return true;
  }, [foldedLines]);

  const value: FoldingContextType = {
    foldedLines,
    toggleFold,
    foldToLevel,
    unfoldAll,
    isLineFolded,
    isLineVisible,
  };

  return (
    <FoldingContext.Provider value={value}>
      {children}
    </FoldingContext.Provider>
  );
};