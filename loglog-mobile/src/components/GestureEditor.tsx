import React, { useState, useCallback, useRef } from 'react';
import {
  View,
  Text,
  ScrollView,
  StyleSheet,
  Dimensions,
  TouchableOpacity,
  PanResponder,
  GestureResponderEvent,
  PanResponderGestureState,
  Animated,
} from 'react-native';
import { TreeNode } from '../core/TreeNode';
import { buildTreeFromString, parseLine } from '../core/parser';
import { DocumentState, GestureState } from '../types';
import { HapticFeedback } from '../utils/haptics';
import { GestureToolbar } from './GestureToolbar';
import { useDebounce, useMemoizedLines } from '../utils/performance';
import { useThrottledUndoRedo } from '../utils/undoRedo';

interface GestureEditorProps {
  initialContent?: string;
  onContentChange?: (content: string, tree: TreeNode) => void;
}

interface LineData {
  content: string;
  level: number;
  index: number;
  isSelected: boolean;
  isFolded: boolean;
  hasChildren: boolean;
}

const SWIPE_THRESHOLD = 50; // Minimum distance for swipe recognition
const DOUBLE_TAP_DELAY = 300; // Maximum time between taps for double tap

export const GestureEditor: React.FC<GestureEditorProps> = ({
  initialContent = '',
  onContentChange,
}) => {
  const [documentState, setDocumentState] = useState<DocumentState>({
    content: initialContent,
    tree: buildTreeFromString(initialContent),
    isModified: false,
  });

  const [gestureState, setGestureState] = useState<GestureState>({
    isSelecting: false,
    selectedLines: [],
    startLine: -1,
    endLine: -1,
  });

  const [foldedLines, setFoldedLines] = useState<Set<number>>(new Set());
  const [lastTap, setLastTap] = useState<{ lineIndex: number; time: number } | null>(null);
  
  const undoRedo = useThrottledUndoRedo(initialContent, 50, 2000);
  
  const dragOffsetX = useRef(new Animated.Value(0)).current;
  const swipeDirection = useRef<'left' | 'right' | null>(null);
  const isDragging = useRef(false);

  const { lines } = useMemoizedLines(documentState.content);
  const lineData: LineData[] = lines.map((line, index) => {
    const parsed = parseLine(line);
    const hasChildren = index < lines.length - 1 && 
      lines.slice(index + 1).some(nextLine => {
        const nextParsed = parseLine(nextLine);
        return nextParsed.level > parsed.level;
      });
    
    return {
      content: line,
      level: parsed.level,
      index,
      isSelected: gestureState.selectedLines.includes(index),
      isFolded: foldedLines.has(index),
      hasChildren,
    };
  });

  // Filter out folded children
  const visibleLines = lineData.filter((lineData, index) => {
    for (let i = index - 1; i >= 0; i--) {
      const parentLine = lineData[i];
      if (parentLine.level < lineData.level && parentLine.isFolded) {
        return false; // This line is hidden under a folded parent
      }
      if (parentLine.level >= lineData.level) {
        break; // Found a sibling or moved up levels
      }
    }
    return true;
  });

  const debouncedUpdateContent = useDebounce((newLines: string[]) => {
    const newContent = newLines.join('\n');
    try {
      const tree = buildTreeFromString(newContent);
      const newState: DocumentState = {
        content: newContent,
        tree,
        isModified: true,
      };
      
      setDocumentState(newState);
      undoRedo.addToHistory(newContent);
      onContentChange?.(newContent, tree);
    } catch (error) {
      console.warn('Parse error:', error);
    }
  }, 300);

  const updateContent = useCallback((newLines: string[]) => {
    debouncedUpdateContent(newLines);
  }, [debouncedUpdateContent]);

  const handleSwipeIndent = useCallback((direction: 'left' | 'right') => {
    if (gestureState.selectedLines.length === 0) return;

    HapticFeedback.swipeIndent();

    const newLines = [...lines];
    gestureState.selectedLines.forEach(lineIndex => {
      if (direction === 'right') {
        // Indent - add 4 spaces
        newLines[lineIndex] = '    ' + newLines[lineIndex];
      } else {
        // Outdent - remove up to 4 spaces
        const line = newLines[lineIndex];
        if (line.startsWith('    ')) {
          newLines[lineIndex] = line.substring(4);
        } else if (line.startsWith('  ')) {
          newLines[lineIndex] = line.substring(2);
        } else if (line.startsWith(' ')) {
          newLines[lineIndex] = line.substring(1);
        }
      }
    });

    updateContent(newLines);
  }, [gestureState.selectedLines, lines, updateContent]);

  const handleDoubleTap = useCallback((lineIndex: number) => {
    const lineData = visibleLines.find(l => l.index === lineIndex);
    if (!lineData?.hasChildren) return;

    HapticFeedback.doubleTap();

    setFoldedLines(prev => {
      const newSet = new Set(prev);
      if (newSet.has(lineIndex)) {
        newSet.delete(lineIndex); // Unfold
      } else {
        newSet.add(lineIndex); // Fold
      }
      return newSet;
    });
  }, [visibleLines]);

  const handleLinePress = useCallback((lineIndex: number) => {
    const now = Date.now();
    
    if (lastTap && lastTap.lineIndex === lineIndex && now - lastTap.time < DOUBLE_TAP_DELAY) {
      // Double tap detected
      handleDoubleTap(lineIndex);
      setLastTap(null);
    } else {
      // Single tap
      setLastTap({ lineIndex, time: now });
      
      if (gestureState.isSelecting) {
        // Toggle selection
        setGestureState(prev => ({
          ...prev,
          selectedLines: prev.selectedLines.includes(lineIndex)
            ? prev.selectedLines.filter(i => i !== lineIndex)
            : [...prev.selectedLines, lineIndex].sort((a, b) => a - b),
        }));
      }
    }
  }, [gestureState.isSelecting, lastTap, handleDoubleTap]);

  const handleLongPress = useCallback((lineIndex: number) => {
    HapticFeedback.longPress();
    
    setGestureState({
      isSelecting: true,
      selectedLines: [lineIndex],
      startLine: lineIndex,
      endLine: lineIndex,
    });
  }, []);

  const clearSelection = useCallback(() => {
    setGestureState({
      isSelecting: false,
      selectedLines: [],
      startLine: -1,
      endLine: -1,
    });
  }, []);

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => gestureState.isSelecting && gestureState.selectedLines.length > 0,
    onMoveShouldSetPanResponder: (evt, gestureState) => {
      return Math.abs(gestureState.dx) > 10 && gestureState.dy < 30;
    },
    
    onPanResponderGrant: () => {
      isDragging.current = true;
      swipeDirection.current = null;
    },
    
    onPanResponderMove: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {
      if (!isDragging.current) return;
      
      // Limit drag distance for visual feedback
      const clampedDx = Math.max(-100, Math.min(100, gestureState.dx));
      dragOffsetX.setValue(clampedDx);
      
      // Determine swipe direction
      if (Math.abs(gestureState.dx) > SWIPE_THRESHOLD) {
        swipeDirection.current = gestureState.dx > 0 ? 'right' : 'left';
      }
    },
    
    onPanResponderRelease: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {
      isDragging.current = false;
      
      // Animate back to neutral position
      Animated.spring(dragOffsetX, {
        toValue: 0,
        useNativeDriver: true,
      }).start();
      
      // Execute swipe action if threshold was met
      if (swipeDirection.current && Math.abs(gestureState.dx) > SWIPE_THRESHOLD) {
        handleSwipeIndent(swipeDirection.current);
      }
      
      swipeDirection.current = null;
    },
  });

  const renderLine = (lineData: LineData) => {
    const indentLevel = lineData.level;
    const paddingLeft = 16 + (indentLevel * 20);
    
    const animatedStyle = gestureState.selectedLines.includes(lineData.index) ? {
      transform: [{ translateX: dragOffsetX }],
    } : {};

    return (
      <Animated.View
        key={lineData.index}
        style={[animatedStyle]}
        {...(gestureState.isSelecting ? panResponder.panHandlers : {})}
      >
        <TouchableOpacity
          style={[
            styles.lineContainer,
            { paddingLeft },
            lineData.isSelected && styles.selectedLine,
          ]}
          onPress={() => handleLinePress(lineData.index)}
          onLongPress={() => handleLongPress(lineData.index)}
          delayLongPress={300}
        >
          <View style={styles.lineContent}>
            {/* Fold indicator */}
            {lineData.hasChildren && (
              <Text style={styles.foldIndicator}>
                {lineData.isFolded ? '▶' : '▼'}
              </Text>
            )}
            
            <Text style={styles.lineText}>
              {lineData.content.trim() || '\u00A0'}
            </Text>
          </View>
          
          {/* Swipe direction indicator */}
          {lineData.isSelected && isDragging.current && (
            <View style={styles.swipeIndicator}>
              <Text style={styles.swipeIndicatorText}>
                {swipeDirection.current === 'left' ? '◀ Outdent' : 
                 swipeDirection.current === 'right' ? 'Indent ▶' : '↔ Swipe'}
              </Text>
            </View>
          )}
        </TouchableOpacity>
      </Animated.View>
    );
  };

  return (
    <View style={styles.container}>
      {/* Main editor area */}
      <ScrollView style={styles.scrollView}>
        {visibleLines.map(renderLine)}
      </ScrollView>

      {/* Gesture toolbar */}
      <GestureToolbar
        isSelecting={gestureState.isSelecting}
        selectedCount={gestureState.selectedLines.length}
        onFoldLevel={(level) => {
          // Fold to level functionality
          const newFolded = new Set<number>();
          lines.forEach((line, index) => {
            const lineLevel = Math.floor((line.match(/^ */)?.[0]?.length || 0) / 4);
            const hasChildren = index < lines.length - 1 && 
              lines.slice(index + 1).some(nextLine => {
                const nextLevel = Math.floor((nextLine.match(/^ */)?.[0]?.length || 0) / 4);
                return nextLevel > lineLevel;
              });
            if (hasChildren && lineLevel >= level) {
              newFolded.add(index);
            }
          });
          setFoldedLines(newFolded);
          HapticFeedback.fold();
        }}
        onUnfoldAll={() => {
          setFoldedLines(new Set());
          HapticFeedback.unfold();
        }}
        onClearSelection={clearSelection}
        onIndent={() => handleSwipeIndent('right')}
        onOutdent={() => handleSwipeIndent('left')}
        canUndo={undoRedo.canUndo}
        canRedo={undoRedo.canRedo}
        onUndo={() => {
          const undoneContent = undoRedo.undo();
          if (undoneContent !== null) {
            setDocumentState(prev => ({
              ...prev,
              content: undoneContent,
              tree: buildTreeFromString(undoneContent),
              isModified: true,
            }));
          }
        }}
        onRedo={() => {
          const redoneContent = undoRedo.redo();
          if (redoneContent !== null) {
            setDocumentState(prev => ({
              ...prev,
              content: redoneContent,
              tree: buildTreeFromString(redoneContent),
              isModified: true,
            }));
          }
        }}
      />

      {/* Status bar */}
      <View style={styles.statusBar}>
        <Text style={styles.statusText}>
          {documentState.isModified ? '● Modified' : '○ Saved'} | 
          {gestureState.isSelecting ? ' Selection Mode' : ' Edit Mode'} | 
          {visibleLines.length}/{lines.length} lines
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  scrollView: {
    flex: 1,
  },
  lineContainer: {
    paddingVertical: 8,
    paddingRight: 16,
    borderBottomWidth: 0.5,
    borderBottomColor: '#f0f0f0',
    minHeight: 44,
    justifyContent: 'center',
  },
  selectedLine: {
    backgroundColor: '#e3f2fd',
    borderLeftWidth: 4,
    borderLeftColor: '#2196f3',
  },
  lineContent: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  foldIndicator: {
    fontSize: 12,
    color: '#666',
    marginRight: 8,
    width: 16,
    textAlign: 'center',
  },
  lineText: {
    fontSize: 16,
    lineHeight: 22,
    fontFamily: 'monospace',
    color: '#333',
    flex: 1,
  },
  swipeIndicator: {
    position: 'absolute',
    right: 16,
    top: 0,
    bottom: 0,
    justifyContent: 'center',
    backgroundColor: 'rgba(33, 150, 243, 0.1)',
    paddingHorizontal: 8,
    borderRadius: 4,
  },
  swipeIndicatorText: {
    fontSize: 12,
    color: '#2196f3',
    fontWeight: '600',
  },
  selectionControls: {
    backgroundColor: '#f5f5f5',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  instructionText: {
    fontSize: 14,
    color: '#666',
    textAlign: 'center',
    marginBottom: 8,
    fontStyle: 'italic',
  },
  controlRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  selectionInfo: {
    fontSize: 14,
    color: '#666',
    fontFamily: 'monospace',
  },
  clearButton: {
    backgroundColor: '#2196f3',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  helpBar: {
    backgroundColor: '#f9f9f9',
    paddingVertical: 8,
    paddingHorizontal: 16,
  },
  helpText: {
    fontSize: 12,
    color: '#888',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  statusBar: {
    height: 32,
    backgroundColor: '#f5f5f5',
    justifyContent: 'center',
    paddingHorizontal: 16,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  statusText: {
    fontSize: 12,
    color: '#666',
    fontFamily: 'monospace',
  },
});