import AsyncStorage from '@react-native-async-storage/async-storage';

export interface FileMetadata {
  id: string;
  name: string;
  content: string;
  lastModified: Date;
  created: Date;
}

const STORAGE_KEY = '@loglog_files';
const RECENT_FILES_KEY = '@loglog_recent';

export class FileManager {
  /**
   * Save a file to storage
   */
  static async saveFile(file: FileMetadata): Promise<void> {
    try {
      const existingFiles = await this.getAllFiles();
      const updatedFiles = existingFiles.filter(f => f.id !== file.id);
      updatedFiles.push({
        ...file,
        lastModified: new Date(),
      });
      
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(updatedFiles));
      await this.updateRecentFiles(file.id);
    } catch (error) {
      console.error('Error saving file:', error);
      throw error;
    }
  }

  /**
   * Load a file by ID
   */
  static async loadFile(fileId: string): Promise<FileMetadata | null> {
    try {
      const files = await this.getAllFiles();
      const file = files.find(f => f.id === fileId);
      
      if (file) {
        await this.updateRecentFiles(fileId);
        return file;
      }
      
      return null;
    } catch (error) {
      console.error('Error loading file:', error);
      return null;
    }
  }

  /**
   * Get all files
   */
  static async getAllFiles(): Promise<FileMetadata[]> {
    try {
      const filesData = await AsyncStorage.getItem(STORAGE_KEY);
      if (filesData) {
        const files = JSON.parse(filesData);
        // Convert date strings back to Date objects
        return files.map((file: any) => ({
          ...file,
          lastModified: new Date(file.lastModified),
          created: new Date(file.created),
        }));
      }
      return [];
    } catch (error) {
      console.error('Error getting all files:', error);
      return [];
    }
  }

  /**
   * Delete a file
   */
  static async deleteFile(fileId: string): Promise<void> {
    try {
      const files = await this.getAllFiles();
      const updatedFiles = files.filter(f => f.id !== fileId);
      await AsyncStorage.setItem(STORAGE_KEY, JSON.stringify(updatedFiles));
      
      // Remove from recent files
      const recentFiles = await this.getRecentFiles();
      const updatedRecent = recentFiles.filter(id => id !== fileId);
      await AsyncStorage.setItem(RECENT_FILES_KEY, JSON.stringify(updatedRecent));
    } catch (error) {
      console.error('Error deleting file:', error);
      throw error;
    }
  }

  /**
   * Create a new file
   */
  static async createNewFile(name: string, content: string = ''): Promise<FileMetadata> {
    const now = new Date();
    const file: FileMetadata = {
      id: this.generateId(),
      name,
      content,
      lastModified: now,
      created: now,
    };
    
    await this.saveFile(file);
    return file;
  }

  /**
   * Get recent files (by ID)
   */
  static async getRecentFiles(): Promise<string[]> {
    try {
      const recentData = await AsyncStorage.getItem(RECENT_FILES_KEY);
      return recentData ? JSON.parse(recentData) : [];
    } catch (error) {
      console.error('Error getting recent files:', error);
      return [];
    }
  }

  /**
   * Update recent files list
   */
  private static async updateRecentFiles(fileId: string): Promise<void> {
    try {
      let recentFiles = await this.getRecentFiles();
      
      // Remove if already exists
      recentFiles = recentFiles.filter(id => id !== fileId);
      
      // Add to beginning
      recentFiles.unshift(fileId);
      
      // Keep only last 10
      recentFiles = recentFiles.slice(0, 10);
      
      await AsyncStorage.setItem(RECENT_FILES_KEY, JSON.stringify(recentFiles));
    } catch (error) {
      console.error('Error updating recent files:', error);
    }
  }

  /**
   * Generate unique ID
   */
  private static generateId(): string {
    return Date.now().toString(36) + Math.random().toString(36).substr(2);
  }

  /**
   * Export file content in various formats
   */
  static async exportFile(file: FileMetadata, format: 'loglog' | 'markdown' | 'html'): Promise<string> {
    const { ConversionService } = await import('./ConversionService');
    
    switch (format) {
      case 'loglog':
        return file.content;
      case 'markdown':
        return ConversionService.toMarkdown(file.content);
      case 'html':
        return ConversionService.toHtml(file.content, { title: file.name });
      default:
        return file.content;
    }
  }

  /**
   * Get export filename with appropriate extension
   */
  static getExportFilename(file: FileMetadata, format: 'loglog' | 'markdown' | 'html'): string {
    const baseName = file.name.replace(/\.[^/.]+$/, ''); // Remove existing extension
    
    switch (format) {
      case 'loglog':
        return `${baseName}.txt`;
      case 'markdown':
        return `${baseName}.md`;
      case 'html':
        return `${baseName}.html`;
      default:
        return `${baseName}.txt`;
    }
  }

  /**
   * Import file from content
   */
  static async importFile(name: string, content: string): Promise<FileMetadata> {
    return await this.createNewFile(name, content);
  }

  /**
   * Search files by content or name
   */
  static async searchFiles(query: string): Promise<FileMetadata[]> {
    try {
      const allFiles = await this.getAllFiles();
      const lowerQuery = query.toLowerCase();
      
      return allFiles.filter(file => 
        file.name.toLowerCase().includes(lowerQuery) ||
        file.content.toLowerCase().includes(lowerQuery)
      );
    } catch (error) {
      console.error('Error searching files:', error);
      return [];
    }
  }
}