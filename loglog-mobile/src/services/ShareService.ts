import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';
import { FileMetadata, FileManager } from './FileManager';

export type ShareFormat = 'loglog' | 'markdown' | 'html';

export class ShareService {
  /**
   * Share a file in the specified format
   */
  static async shareFile(file: FileMetadata, format: ShareFormat = 'loglog'): Promise<void> {
    try {
      // Get the exported content
      const content = await FileManager.exportFile(file, format);
      const filename = FileManager.getExportFilename(file, format);
      
      // Create temporary file
      const tempPath = `${FileSystem.documentDirectory}temp_${filename}`;
      await FileSystem.writeAsStringAsync(tempPath, content);
      
      // Check if sharing is available
      const isAvailable = await Sharing.isAvailableAsync();
      if (!isAvailable) {
        throw new Error('Sharing is not available on this device');
      }
      
      // Share the file
      await Sharing.shareAsync(tempPath, {
        mimeType: this.getMimeType(format),
        dialogTitle: `Share ${file.name}`,
      });
      
      // Clean up temporary file
      setTimeout(async () => {
        try {
          await FileSystem.deleteAsync(tempPath);
        } catch (error) {
          console.warn('Failed to clean up temporary file:', error);
        }
      }, 5000); // Delete after 5 seconds
      
    } catch (error) {
      console.error('Error sharing file:', error);
      throw error;
    }
  }

  /**
   * Save exported file to device storage
   */
  static async saveToDevice(file: FileMetadata, format: ShareFormat = 'loglog'): Promise<string> {
    try {
      // Get the exported content
      const content = await FileManager.exportFile(file, format);
      const filename = FileManager.getExportFilename(file, format);
      
      // Save to documents directory
      const filePath = `${FileSystem.documentDirectory}exports/${filename}`;
      
      // Ensure exports directory exists
      const exportsDir = `${FileSystem.documentDirectory}exports/`;
      const dirInfo = await FileSystem.getInfoAsync(exportsDir);
      if (!dirInfo.exists) {
        await FileSystem.makeDirectoryAsync(exportsDir, { intermediates: true });
      }
      
      // Write the file
      await FileSystem.writeAsStringAsync(filePath, content);
      
      return filePath;
    } catch (error) {
      console.error('Error saving file to device:', error);
      throw error;
    }
  }

  /**
   * Share multiple files as a zip archive (future enhancement)
   */
  static async shareMultipleFiles(files: FileMetadata[], format: ShareFormat = 'loglog'): Promise<void> {
    // For now, share the first file. In the future, could create a zip archive
    if (files.length > 0) {
      await this.shareFile(files[0], format);
    }
  }

  /**
   * Get MIME type for the format
   */
  private static getMimeType(format: ShareFormat): string {
    switch (format) {
      case 'loglog':
        return 'text/plain';
      case 'markdown':
        return 'text/markdown';
      case 'html':
        return 'text/html';
      default:
        return 'text/plain';
    }
  }

  /**
   * Get formatted content for sharing
   */
  static async getShareableContent(file: FileMetadata, format: ShareFormat): Promise<{
    content: string;
    filename: string;
    mimeType: string;
  }> {
    const content = await FileManager.exportFile(file, format);
    const filename = FileManager.getExportFilename(file, format);
    const mimeType = this.getMimeType(format);
    
    return { content, filename, mimeType };
  }

  /**
   * Copy content to clipboard (future enhancement)
   */
  static async copyToClipboard(file: FileMetadata, format: ShareFormat = 'loglog'): Promise<void> {
    // This would require expo-clipboard
    // For now, throw an error to indicate it's not implemented
    throw new Error('Clipboard functionality not yet implemented');
  }
}