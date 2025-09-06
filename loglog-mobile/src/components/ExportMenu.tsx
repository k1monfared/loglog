import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  StyleSheet,
  Modal,
  Alert,
} from 'react-native';
import { FileMetadata } from '../services/FileManager';
import { ShareService, ShareFormat } from '../services/ShareService';

interface ExportMenuProps {
  visible: boolean;
  file: FileMetadata | null;
  onClose: () => void;
}

export const ExportMenu: React.FC<ExportMenuProps> = ({
  visible,
  file,
  onClose,
}) => {
  const handleExport = async (format: ShareFormat) => {
    if (!file) return;

    try {
      await ShareService.shareFile(file, format);
      onClose();
    } catch (error) {
      console.error('Export error:', error);
      Alert.alert(
        'Export Failed', 
        `Unable to export file: ${error instanceof Error ? error.message : 'Unknown error'}`
      );
    }
  };

  const exportOptions: Array<{
    format: ShareFormat;
    title: string;
    description: string;
    icon: string;
  }> = [
    {
      format: 'loglog',
      title: 'Loglog Format',
      description: 'Original format with indentation',
      icon: '📝',
    },
    {
      format: 'markdown',
      title: 'Markdown',
      description: 'Convert to Markdown with headers',
      icon: '📄',
    },
    {
      format: 'html',
      title: 'Interactive HTML',
      description: 'Web page with folding features',
      icon: '🌐',
    },
  ];

  return (
    <Modal
      visible={visible}
      animationType="slide"
      presentationStyle="pageSheet"
      onRequestClose={onClose}
    >
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>Export Document</Text>
          <TouchableOpacity onPress={onClose} style={styles.closeButton}>
            <Text style={styles.closeButtonText}>✕</Text>
          </TouchableOpacity>
        </View>

        <View style={styles.content}>
          <Text style={styles.subtitle}>
            Choose format to export "{file?.name || 'Untitled'}"
          </Text>

          <View style={styles.optionsList}>
            {exportOptions.map((option) => (
              <TouchableOpacity
                key={option.format}
                style={styles.exportOption}
                onPress={() => handleExport(option.format)}
              >
                <View style={styles.optionIcon}>
                  <Text style={styles.iconText}>{option.icon}</Text>
                </View>
                <View style={styles.optionContent}>
                  <Text style={styles.optionTitle}>{option.title}</Text>
                  <Text style={styles.optionDescription}>{option.description}</Text>
                </View>
                <Text style={styles.optionArrow}>→</Text>
              </TouchableOpacity>
            ))}
          </View>

          <View style={styles.infoSection}>
            <Text style={styles.infoTitle}>💡 Export Tips</Text>
            <Text style={styles.infoText}>
              • <Text style={styles.bold}>Loglog:</Text> Keep original format for editing{'\n'}
              • <Text style={styles.bold}>Markdown:</Text> Share with others or publish{'\n'}
              • <Text style={styles.bold}>HTML:</Text> Interactive web page with folding
            </Text>
          </View>
        </View>
      </View>
    </Modal>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 20,
    paddingVertical: 16,
    backgroundColor: '#f8f9fa',
    borderBottomWidth: 1,
    borderBottomColor: '#e9ecef',
  },
  title: {
    fontSize: 20,
    fontWeight: '600',
    color: '#333',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#6c757d',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  content: {
    flex: 1,
    padding: 20,
  },
  subtitle: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
    textAlign: 'center',
  },
  optionsList: {
    marginBottom: 30,
  },
  exportOption: {
    flexDirection: 'row',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#f8f9fa',
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#e9ecef',
  },
  optionIcon: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#fff',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 3,
  },
  iconText: {
    fontSize: 24,
  },
  optionContent: {
    flex: 1,
  },
  optionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333',
    marginBottom: 2,
  },
  optionDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 18,
  },
  optionArrow: {
    fontSize: 20,
    color: '#007bff',
    fontWeight: 'bold',
  },
  infoSection: {
    backgroundColor: '#e7f3ff',
    padding: 16,
    borderRadius: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#007bff',
  },
  infoTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#004085',
    marginBottom: 8,
  },
  infoText: {
    fontSize: 14,
    color: '#004085',
    lineHeight: 20,
  },
  bold: {
    fontWeight: '600',
  },
});