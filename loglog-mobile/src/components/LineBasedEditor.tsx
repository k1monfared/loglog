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
} from 'react-native';
import { TreeNode } from '../core/TreeNode';
import { buildTreeFromString, parseLine } from '../core/parser';
import { DocumentState, GestureState } from '../types';

interface LineBasedEditorProps {
  initialContent?: string;
  onContentChange?: (content: string, tree: TreeNode) => void;
}

interface LineData {
  content: string;
  level: number;
  index: number;
  isSelected: boolean;
}

export const LineBasedEditor: React.FC<LineBasedEditorProps> = ({
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

  const [editingLine, setEditingLine] = useState<number | null>(null);
  const [editingText, setEditingText] = useState('');
  const scrollViewRef = useRef<ScrollView>(null);

  const lines = documentState.content.split('\n');
  const lineData: LineData[] = lines.map((line, index) => {
    const parsed = parseLine(line);
    return {
      content: line,
      level: parsed.level,
      index,
      isSelected: gestureState.selectedLines.includes(index),
    };
  });

  const updateContent = useCallback((newLines: string[]) => {
    const newContent = newLines.join('\n');
    try {
      const tree = buildTreeFromString(newContent);
      const newState: DocumentState = {
        content: newContent,
        tree,
        isModified: true,
      };
      
      setDocumentState(newState);
      onContentChange?.(newContent, tree);
    } catch (error) {
      console.warn('Parse error:', error);
    }
  }, [onContentChange]);

  const handleLinePress = useCallback((lineIndex: number) => {
    if (gestureState.isSelecting) {
      // Toggle selection
      setGestureState(prev => ({
        ...prev,
        selectedLines: prev.selectedLines.includes(lineIndex)
          ? prev.selectedLines.filter(i => i !== lineIndex)
          : [...prev.selectedLines, lineIndex].sort((a, b) => a - b),
      }));
    } else {
      // Start editing
      setEditingLine(lineIndex);
      setEditingText(lines[lineIndex]);
    }
  }, [gestureState.isSelecting, lines]);

  const handleLongPress = useCallback((lineIndex: number) => {
    setGestureState({
      isSelecting: true,
      selectedLines: [lineIndex],
      startLine: lineIndex,
      endLine: lineIndex,
    });
  }, []);

  const handleIndentSelected = useCallback(() => {
    if (gestureState.selectedLines.length === 0) return;

    const newLines = [...lines];
    gestureState.selectedLines.forEach(lineIndex => {
      newLines[lineIndex] = '    ' + newLines[lineIndex]; // Add 4 spaces
    });

    updateContent(newLines);
  }, [gestureState.selectedLines, lines, updateContent]);

  const handleOutdentSelected = useCallback(() => {
    if (gestureState.selectedLines.length === 0) return;

    const newLines = [...lines];
    gestureState.selectedLines.forEach(lineIndex => {
      const line = newLines[lineIndex];
      if (line.startsWith('    ')) {
        newLines[lineIndex] = line.substring(4); // Remove 4 spaces
      } else if (line.startsWith('  ')) {
        newLines[lineIndex] = line.substring(2); // Remove 2 spaces
      } else if (line.startsWith(' ')) {
        newLines[lineIndex] = line.substring(1); // Remove 1 space
      }
    });

    updateContent(newLines);
  }, [gestureState.selectedLines, lines, updateContent]);

  const clearSelection = useCallback(() => {
    setGestureState({
      isSelecting: false,
      selectedLines: [],
      startLine: -1,
      endLine: -1,
    });
  }, []);

  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => gestureState.isSelecting,
    onMoveShouldSetPanResponder: () => gestureState.isSelecting,
    onPanResponderGrant: () => {},
    onPanResponderMove: (evt: GestureResponderEvent, gestureState: PanResponderGestureState) => {
      // Handle drag selection here
      // This is a simplified version - in production you'd calculate which lines are being dragged over
    },
    onPanResponderRelease: () => {},
  });

  const renderLine = (lineData: LineData) => {
    const indentLevel = lineData.level;
    const paddingLeft = 16 + (indentLevel * 20); // Base padding + level spacing
    
    return (
      <TouchableOpacity
        key={lineData.index}
        style={[
          styles.lineContainer,
          { paddingLeft },
          lineData.isSelected && styles.selectedLine,
        ]}
        onPress={() => handleLinePress(lineData.index)}
        onLongPress={() => handleLongPress(lineData.index)}
        delayLongPress={300}
      >
        <Text style={styles.lineText}>
          {lineData.content.trim() || '\u00A0'} {/* Non-breaking space for empty lines */}
        </Text>
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {/* Main editor area */}
      <ScrollView
        ref={scrollViewRef}
        style={styles.scrollView}
        {...panResponder.panHandlers}
      >
        {lineData.map(renderLine)}
      </ScrollView>

      {/* Selection controls */}
      {gestureState.isSelecting && (
        <View style={styles.selectionControls}>
          <TouchableOpacity style={styles.controlButton} onPress={handleOutdentSelected}>
            <Text style={styles.controlButtonText}>◀ Outdent</Text>
          </TouchableOpacity>
          
          <Text style={styles.selectionInfo}>
            {gestureState.selectedLines.length} lines selected
          </Text>
          
          <TouchableOpacity style={styles.controlButton} onPress={handleIndentSelected}>
            <Text style={styles.controlButtonText}>Indent ▶</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.clearButton} onPress={clearSelection}>
            <Text style={styles.clearButtonText}>✕</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Status bar */}
      <View style={styles.statusBar}>
        <Text style={styles.statusText}>
          {documentState.isModified ? '● Modified' : '○ Saved'} | 
          {gestureState.isSelecting ? ' Selection Mode' : ' Edit Mode'} | 
          {lines.length} lines
        </Text>
      </View>
    </View>
  );
};

const { width } = Dimensions.get('window');

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
    minHeight: 40,
    justifyContent: 'center',
  },
  selectedLine: {
    backgroundColor: '#e3f2fd',
    borderLeftWidth: 3,
    borderLeftColor: '#2196f3',
  },
  lineText: {
    fontSize: 16,
    lineHeight: 22,
    fontFamily: 'monospace',
    color: '#333',
  },
  selectionControls: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f5f5f5',
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  controlButton: {
    backgroundColor: '#2196f3',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  controlButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  clearButton: {
    backgroundColor: '#f44336',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
  },
  clearButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  selectionInfo: {
    fontSize: 14,
    color: '#666',
    fontFamily: 'monospace',
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