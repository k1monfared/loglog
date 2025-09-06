import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  StyleSheet,
  Alert,
  TouchableOpacity,
  Text,
  Modal,
  TextInput,
} from 'react-native';
import { GestureEditor } from '../components/GestureEditor';
import { ExportMenu } from '../components/ExportMenu';
import { FileManager, FileMetadata } from '../services/FileManager';
import { TreeNode } from '../core/TreeNode';

export const EditorScreen: React.FC = () => {
  const [currentFile, setCurrentFile] = useState<FileMetadata | null>(null);
  const [showNewFileModal, setShowNewFileModal] = useState(false);
  const [showExportMenu, setShowExportMenu] = useState(false);
  const [newFileName, setNewFileName] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    // Load or create default file on mount
    loadDefaultFile();
  }, []);

  const loadDefaultFile = async () => {
    setIsLoading(true);
    try {
      // Try to load the most recent file
      const recentFiles = await FileManager.getRecentFiles();
      if (recentFiles.length > 0) {
        const file = await FileManager.loadFile(recentFiles[0]);
        if (file) {
          setCurrentFile(file);
          return;
        }
      }
      
      // Create a default file if none exists
      const defaultContent = `- Welcome to Loglog Mobile
    - This is your first loglog document
    - Start writing your thoughts here
        - Use 4 spaces for indentation
        - Everything is a list item
    - Try creating todo items
        [] This is a pending task
        [x] This is a completed task
        [?] This is an unknown status task
- Getting Started
    - Tap and hold any line to enter selection mode
    - Use indent/outdent buttons to change nesting
    - Long press to select multiple lines
    - Tap the + button to create new files`;

      const defaultFile = await FileManager.createNewFile('My First Document', defaultContent);
      setCurrentFile(defaultFile);
    } catch (error) {
      console.error('Error loading default file:', error);
      Alert.alert('Error', 'Failed to load document');
    } finally {
      setIsLoading(false);
    }
  };

  const handleContentChange = useCallback(async (content: string, tree: TreeNode) => {
    if (!currentFile) return;

    try {
      const updatedFile: FileMetadata = {
        ...currentFile,
        content,
        lastModified: new Date(),
      };
      
      setCurrentFile(updatedFile);
      // Auto-save after a delay (debounced)
      setTimeout(async () => {
        await FileManager.saveFile(updatedFile);
      }, 1000);
    } catch (error) {
      console.error('Error saving file:', error);
    }
  }, [currentFile]);

  const handleNewFile = async () => {
    if (!newFileName.trim()) {
      Alert.alert('Error', 'Please enter a file name');
      return;
    }

    try {
      const newFile = await FileManager.createNewFile(newFileName.trim(), '- New document\n    - Start writing here');
      setCurrentFile(newFile);
      setNewFileName('');
      setShowNewFileModal(false);
    } catch (error) {
      console.error('Error creating new file:', error);
      Alert.alert('Error', 'Failed to create new file');
    }
  };

  const handleSaveFile = async () => {
    if (!currentFile) return;

    try {
      await FileManager.saveFile(currentFile);
      Alert.alert('Success', 'File saved successfully');
    } catch (error) {
      console.error('Error saving file:', error);
      Alert.alert('Error', 'Failed to save file');
    }
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <Text style={styles.loadingText}>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>
          {currentFile?.name || 'Untitled Document'}
        </Text>
        <View style={styles.headerButtons}>
          <TouchableOpacity style={styles.headerButton} onPress={() => setShowNewFileModal(true)}>
            <Text style={styles.headerButtonText}>+</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton} onPress={handleSaveFile}>
            <Text style={styles.headerButtonText}>💾</Text>
          </TouchableOpacity>
          <TouchableOpacity style={styles.headerButton} onPress={() => setShowExportMenu(true)}>
            <Text style={styles.headerButtonText}>📤</Text>
          </TouchableOpacity>
        </View>
      </View>

      {/* Editor */}
      {currentFile && (
        <GestureEditor
          key={currentFile.id} // Force re-render when file changes
          initialContent={currentFile.content}
          onContentChange={handleContentChange}
        />
      )}

      {/* New File Modal */}
      <Modal
        visible={showNewFileModal}
        animationType="slide"
        presentationStyle="pageSheet"
      >
        <View style={styles.modalContainer}>
          <View style={styles.modalHeader}>
            <TouchableOpacity onPress={() => setShowNewFileModal(false)}>
              <Text style={styles.modalCancelButton}>Cancel</Text>
            </TouchableOpacity>
            <Text style={styles.modalTitle}>New Document</Text>
            <TouchableOpacity onPress={handleNewFile}>
              <Text style={styles.modalCreateButton}>Create</Text>
            </TouchableOpacity>
          </View>
          
          <View style={styles.modalContent}>
            <Text style={styles.inputLabel}>Document Name</Text>
            <TextInput
              style={styles.textInput}
              value={newFileName}
              onChangeText={setNewFileName}
              placeholder="Enter document name..."
              autoFocus
            />
          </View>
        </View>
      </Modal>

      {/* Export Menu */}
      <ExportMenu
        visible={showExportMenu}
        file={currentFile}
        onClose={() => setShowExportMenu(false)}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  loadingText: {
    fontSize: 18,
    color: '#666',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: '#f5f5f5',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  headerTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
    flex: 1,
  },
  headerButtons: {
    flexDirection: 'row',
    gap: 8,
  },
  headerButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#2196f3',
    justifyContent: 'center',
    alignItems: 'center',
  },
  headerButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  modalContainer: {
    flex: 1,
    backgroundColor: '#fff',
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingVertical: 16,
    backgroundColor: '#f5f5f5',
    borderBottomWidth: 1,
    borderBottomColor: '#e0e0e0',
  },
  modalTitle: {
    fontSize: 18,
    fontWeight: '600',
    color: '#333',
  },
  modalCancelButton: {
    fontSize: 16,
    color: '#666',
  },
  modalCreateButton: {
    fontSize: 16,
    color: '#2196f3',
    fontWeight: '600',
  },
  modalContent: {
    padding: 20,
  },
  inputLabel: {
    fontSize: 16,
    color: '#333',
    marginBottom: 8,
    fontWeight: '500',
  },
  textInput: {
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 12,
    fontSize: 16,
    backgroundColor: '#fff',
  },
});