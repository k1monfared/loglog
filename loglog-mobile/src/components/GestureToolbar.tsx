import React from 'react';
import {
  View,
  TouchableOpacity,
  Text,
  StyleSheet,
} from 'react-native';

interface GestureToolbarProps {
  isSelecting: boolean;
  selectedCount: number;
  onFoldLevel: (level: number) => void;
  onUnfoldAll: () => void;
  onClearSelection: () => void;
  onIndent: () => void;
  onOutdent: () => void;
  canUndo?: boolean;
  canRedo?: boolean;
  onUndo?: () => void;
  onRedo?: () => void;
}

export const GestureToolbar: React.FC<GestureToolbarProps> = ({
  isSelecting,
  selectedCount,
  onFoldLevel,
  onUnfoldAll,
  onClearSelection,
  onIndent,
  onOutdent,
  canUndo = false,
  canRedo = false,
  onUndo,
  onRedo,
}) => {
  if (isSelecting) {
    return (
      <View style={styles.toolbar}>
        <View style={styles.selectionSection}>
          <TouchableOpacity style={styles.actionButton} onPress={onOutdent}>
            <Text style={styles.actionButtonText}>◀ Out</Text>
          </TouchableOpacity>
          
          <TouchableOpacity style={styles.actionButton} onPress={onIndent}>
            <Text style={styles.actionButtonText}>In ▶</Text>
          </TouchableOpacity>
          
          <Text style={styles.selectionCount}>
            {selectedCount} selected
          </Text>
          
          <TouchableOpacity style={styles.doneButton} onPress={onClearSelection}>
            <Text style={styles.doneButtonText}>Done</Text>
          </TouchableOpacity>
        </View>
        
        <View style={styles.instructionSection}>
          <Text style={styles.instructionText}>
            💡 Swipe left/right on selected lines to indent/outdent
          </Text>
        </View>
      </View>
    );
  }

  return (
    <View style={styles.toolbar}>
      <View style={styles.foldingSection}>
        <Text style={styles.sectionLabel}>Fold Level:</Text>
        
        <View style={styles.foldButtons}>
          {[1, 2, 3, 4].map(level => (
            <TouchableOpacity
              key={level}
              style={styles.foldButton}
              onPress={() => onFoldLevel(level)}
            >
              <Text style={styles.foldButtonText}>{level}</Text>
            </TouchableOpacity>
          ))}
          
          <TouchableOpacity style={styles.unfoldButton} onPress={onUnfoldAll}>
            <Text style={styles.unfoldButtonText}>All</Text>
          </TouchableOpacity>
        </View>
      </View>
      
      <View style={styles.actionRow}>
        <TouchableOpacity 
          style={[styles.undoButton, !canUndo && styles.disabledButton]} 
          onPress={onUndo}
          disabled={!canUndo}
        >
          <Text style={[styles.undoButtonText, !canUndo && styles.disabledText]}>↶ Undo</Text>
        </TouchableOpacity>
        
        <TouchableOpacity 
          style={[styles.undoButton, !canRedo && styles.disabledButton]} 
          onPress={onRedo}
          disabled={!canRedo}
        >
          <Text style={[styles.undoButtonText, !canRedo && styles.disabledText]}>↷ Redo</Text>
        </TouchableOpacity>
      </View>
      
      <View style={styles.helpSection}>
        <Text style={styles.helpText}>
          Long press to select • Double tap to fold/unfold
        </Text>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  toolbar: {
    backgroundColor: '#f8f9fa',
    borderTopWidth: 1,
    borderTopColor: '#e9ecef',
    paddingHorizontal: 16,
    paddingVertical: 12,
  },
  selectionSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  actionButton: {
    backgroundColor: '#007bff',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 6,
    marginHorizontal: 4,
  },
  actionButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  selectionCount: {
    fontSize: 14,
    color: '#6c757d',
    fontFamily: 'monospace',
    flex: 1,
    textAlign: 'center',
  },
  doneButton: {
    backgroundColor: '#28a745',
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
  },
  doneButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  instructionSection: {
    alignItems: 'center',
  },
  instructionText: {
    fontSize: 12,
    color: '#6c757d',
    fontStyle: 'italic',
    textAlign: 'center',
  },
  foldingSection: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 8,
  },
  sectionLabel: {
    fontSize: 14,
    color: '#495057',
    fontWeight: '500',
    marginRight: 12,
  },
  foldButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  foldButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#6c757d',
    justifyContent: 'center',
    alignItems: 'center',
  },
  foldButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  unfoldButton: {
    paddingHorizontal: 12,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#17a2b8',
    justifyContent: 'center',
    alignItems: 'center',
  },
  unfoldButtonText: {
    color: '#fff',
    fontSize: 12,
    fontWeight: '600',
  },
  helpSection: {
    alignItems: 'center',
  },
  helpText: {
    fontSize: 12,
    color: '#6c757d',
    textAlign: 'center',
    fontStyle: 'italic',
  },
  actionRow: {
    flexDirection: 'row',
    justifyContent: 'center',
    gap: 12,
    marginBottom: 8,
  },
  undoButton: {
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderRadius: 6,
    backgroundColor: '#6c757d',
  },
  undoButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: '600',
  },
  disabledButton: {
    backgroundColor: '#dee2e6',
  },
  disabledText: {
    color: '#6c757d',
  },
});