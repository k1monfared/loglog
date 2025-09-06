# LogLog Mobile Technical Architecture

## System Overview

LogLog Mobile is a React Native application built with Expo that implements a hierarchical note-taking system using gesture-based interactions. The architecture follows modern React Native patterns with emphasis on performance, maintainability, and user experience.

## Architecture Patterns

### 1. Component-Based Architecture
The application follows a hierarchical component structure with clear separation of concerns:

```
App (Root Container)
├── EditorScreen (Main Interface)
│   ├── GestureEditor (Core Editor)
│   │   ├── GestureToolbar (Action Controls)
│   │   └── LineRenderer (Individual Lines)
│   └── ExportMenu (Format Selection)
└── Modal Components (File Operations)
```

### 2. Service Layer Pattern
Business logic is encapsulated in service modules:

- **FileManager**: Handles persistence and file operations
- **ConversionService**: Manages format conversion and export
- **ShareService**: Integrates with native sharing capabilities
- **Performance utilities**: Optimize real-time operations

### 3. Custom Hook Architecture
Complex state management is abstracted into reusable hooks:

- **useUndoRedo**: History management with configurable size
- **useThrottledUndoRedo**: Performance-optimized version
- **useDebounce/useThrottle**: Rate limiting for expensive operations
- **useMemoizedLines**: Cached parsing for large documents

## Core Components Deep Dive

### GestureEditor (`src/components/GestureEditor.tsx`)

**Responsibilities:**
- Real-time text parsing and tree structure management
- Multi-modal gesture recognition (long-press, swipe, double-tap)
- Visual feedback and animation coordination
- Line-based rendering with folding capabilities

**Key Technical Features:**
```typescript
interface GestureEditorProps {
  initialContent?: string;
  onContentChange?: (content: string, tree: TreeNode) => void;
}

// Gesture recognition with PanResponder
const panResponder = PanResponder.create({
  onStartShouldSetPanResponder: () => gestureState.isSelecting && gestureState.selectedLines.length > 0,
  onMoveShouldSetPanResponder: (evt, gestureState) => {
    return Math.abs(gestureState.dx) > 10 && gestureState.dy < 30;
  },
  // ... gesture handling logic
});
```

**State Management:**
- `DocumentState`: Content, tree structure, modification status
- `GestureState`: Selection mode, selected lines, interaction state
- `Folding state`: Set-based tracking of folded line indices
- `Animation state`: Drag offset and visual feedback management

### TreeNode (`src/core/TreeNode.ts`)

**Core Data Structure:**
```typescript
class TreeNode {
  id: string;
  content: string;
  level: number;
  type: 'item' | 'todo' | 'note';
  children: TreeNode[];
  parent: TreeNode | null;

  // Methods for tree manipulation
  addChild(child: TreeNode): void;
  toMd(): string;  // Markdown conversion with shallowest leaf depth
  toData(): any;   // Serialization for storage
  static fromData(data: any): TreeNode; // Deserialization
  findById(id: string): TreeNode | null;
}
```

**Design Decisions:**
- **Immutable operations**: Tree modifications create new instances
- **Bidirectional references**: Parent-child relationships maintained
- **Type safety**: Full TypeScript integration with strict typing
- **Serialization**: JSON-compatible data format for persistence

### FileManager (`src/services/FileManager.ts`)

**Storage Architecture:**
```typescript
interface FileMetadata {
  id: string;
  name: string;
  createdAt: string;
  modifiedAt: string;
  size: number;
}

class FileManager {
  // AsyncStorage abstraction
  private static readonly STORAGE_PREFIX = '@LogLog:';
  private static readonly METADATA_KEY = 'file_metadata';
  
  // Core operations
  async saveFile(id: string, name: string, content: string): Promise<void>;
  async loadFile(id: string): Promise<string>;
  async deleteFile(id: string): Promise<void>;
  async listFiles(): Promise<FileMetadata[]>;
}
```

**Key Features:**
- **Atomic operations**: File saves are transactional
- **Metadata management**: Separate storage for file information
- **Search capabilities**: Content and name-based search
- **Recent files**: Automatically maintained recent access list

## Performance Architecture

### 1. Real-Time Parsing Optimization

**Problem**: Continuous text parsing during user input causes performance degradation.

**Solution**: Multi-layer optimization strategy:

```typescript
// Debounced content updates (300ms delay)
const debouncedUpdateContent = useDebounce((newLines: string[]) => {
  const newContent = newLines.join('\n');
  try {
    const tree = buildTreeFromString(newContent);
    setDocumentState({ content: newContent, tree, isModified: true });
    undoRedo.addToHistory(newContent);
    onContentChange?.(newContent, tree);
  } catch (error) {
    console.warn('Parse error:', error);
  }
}, 300);

// Memoized line processing
const { lines } = useMemoizedLines(documentState.content);
```

### 2. Gesture Performance Optimization

**Problem**: Real-time gesture recognition impacts frame rate during interactions.

**Solution**: Throttled gesture updates with visual feedback:

```typescript
// Throttled gesture updates for 60fps performance
const GESTURE_THROTTLE_MS = 16; // ~60fps

// Clamped drag distance for consistent visual feedback
const clampedDx = Math.max(-100, Math.min(100, gestureState.dx));
dragOffsetX.setValue(clampedDx);
```

### 3. Memory Management

**TextProcessor Cache Implementation:**
```typescript
class TextProcessor {
  private static lineCache = new Map<string, any>();
  private static readonly CACHE_SIZE_LIMIT = 1000;
  
  static parseLinesCached(content: string) {
    const cacheKey = content.length < 10000 ? content : content.substring(0, 100) + content.length;
    
    if (this.lineCache.has(cacheKey)) {
      return this.lineCache.get(cacheKey);
    }
    
    // Parse and cache result
    const result = this.parseLines(content);
    
    // LRU eviction
    if (this.lineCache.size >= this.CACHE_SIZE_LIMIT) {
      const firstKey = this.lineCache.keys().next().value;
      this.lineCache.delete(firstKey);
    }
    
    this.lineCache.set(cacheKey, result);
    return result;
  }
}
```

## State Management Architecture

### 1. Component-Level State

**Local State Pattern:**
- `useState` for simple component state
- `useRef` for imperative DOM operations and gesture tracking
- `useCallback` for event handler optimization
- `useMemo` for expensive computations

### 2. Cross-Component Communication

**Props-Down Pattern:**
```typescript
// Parent component manages shared state
const [documentState, setDocumentState] = useState<DocumentState>({
  content: initialContent,
  tree: buildTreeFromString(initialContent),
  isModified: false,
});

// Child components receive state and callbacks
<GestureEditor 
  initialContent={documentState.content}
  onContentChange={(content, tree) => {
    setDocumentState({ content, tree, isModified: true });
    fileManager.autoSave(content);
  }}
/>
```

### 3. History Management

**Undo/Redo Implementation:**
```typescript
interface HistoryState {
  content: string;
  timestamp: number;
}

// Configurable history with automatic cleanup
const useUndoRedo = (initialContent: string, maxHistorySize: number = 50) => {
  const historyRef = useRef<HistoryState[]>([{ content: initialContent, timestamp: Date.now() }]);
  const currentIndexRef = useRef<number>(0);
  
  // Throttled version for performance
  const addToHistory = useCallback((content: string) => {
    // Remove redo history when adding new content
    // Maintain max history size with LRU eviction
    // Update state flags for UI feedback
  }, [maxHistorySize]);
};
```

## Export System Architecture

### 1. Format-Agnostic Conversion

**Strategy Pattern Implementation:**
```typescript
interface ExportFormat {
  name: string;
  extension: string;
  mimeType: string;
  convert(tree: TreeNode): string;
}

class ConversionService {
  private static formats: Map<string, ExportFormat> = new Map([
    ['loglog', new LoglogFormat()],
    ['markdown', new MarkdownFormat()],
    ['html', new HTMLFormat()],
  ]);
  
  static async exportAs(tree: TreeNode, format: string): Promise<string> {
    const formatter = this.formats.get(format);
    if (!formatter) throw new Error(`Unsupported format: ${format}`);
    return formatter.convert(tree);
  }
}
```

### 2. Interactive HTML Generation

**Self-Contained Export:**
```typescript
class HTMLFormat implements ExportFormat {
  convert(tree: TreeNode): string {
    return `
<!DOCTYPE html>
<html>
<head>
  <style>${this.getEmbeddedCSS()}</style>
</head>
<body>
  ${this.renderTree(tree)}
  <script>${this.getEmbeddedJavaScript()}</script>
</body>
</html>`;
  }
  
  private getEmbeddedJavaScript(): string {
    // Theme toggle functionality
    // Folding/unfolding logic
    // LocalStorage persistence
    return `
      function toggleTheme() { /* theme switching logic */ }
      function toggleFold(element) { /* folding logic */ }
      // Initialize on load
      document.addEventListener('DOMContentLoaded', initializeFeatures);
    `;
  }
}
```

## Testing Architecture

### 1. Unit Testing Strategy

**Component Testing:**
```typescript
describe('GestureEditor', () => {
  it('should handle swipe gestures correctly', () => {
    const mockOnContentChange = jest.fn();
    const { result } = renderHook(() => 
      useGestureEditor({ onContentChange: mockOnContentChange })
    );
    
    // Simulate swipe gesture
    act(() => {
      result.current.handleSwipeIndent('right');
    });
    
    expect(mockOnContentChange).toHaveBeenCalledWith(
      expect.stringContaining('    ') // Indented content
    );
  });
});
```

**Performance Testing:**
```typescript
describe('performance utilities', () => {
  it('should debounce function calls correctly', () => {
    jest.useFakeTimers();
    const mockFn = jest.fn();
    const { result } = renderHook(() => useDebounce(mockFn, 100));
    
    // Multiple rapid calls
    act(() => {
      result.current('test1');
      result.current('test2');
      result.current('test3');
    });
    
    // Should not call immediately
    expect(mockFn).not.toHaveBeenCalled();
    
    // Should call once after delay
    act(() => jest.advanceTimersByTime(100));
    expect(mockFn).toHaveBeenCalledTimes(1);
    expect(mockFn).toHaveBeenLastCalledWith('test3');
  });
});
```

### 2. Integration Testing Approach

**File Operations Testing:**
```typescript
describe('FileManager integration', () => {
  it('should handle complete file lifecycle', async () => {
    const fileManager = new FileManager();
    
    // Create file
    const fileId = await fileManager.createFile('test.loglog', 'Test content');
    expect(fileId).toBeDefined();
    
    // Load file
    const content = await fileManager.loadFile(fileId);
    expect(content).toBe('Test content');
    
    // Update file
    await fileManager.saveFile(fileId, 'test.loglog', 'Updated content');
    const updatedContent = await fileManager.loadFile(fileId);
    expect(updatedContent).toBe('Updated content');
    
    // Delete file
    await fileManager.deleteFile(fileId);
    const files = await fileManager.listFiles();
    expect(files.find(f => f.id === fileId)).toBeUndefined();
  });
});
```

## Security Architecture

### 1. Data Protection

**Local Storage Security:**
- No sensitive data stored in plain text
- File content encrypted at rest (future enhancement)
- User data remains on device (no cloud sync by default)

**Input Validation:**
```typescript
// Parser with malformed input handling
export function parseLine(line: string): ParsedLine {
  try {
    const indentMatch = line.match(/^( *)/);
    const indentLevel = Math.floor((indentMatch?.[0]?.length || 0) / 4);
    const content = line.trim();
    
    // Validate indentation limits
    if (indentLevel > 10) {
      console.warn('Excessive indentation detected, capping at level 10');
      return { level: 10, content, type: 'item' };
    }
    
    return { level: indentLevel, content, type: detectType(content) };
  } catch (error) {
    console.warn('Line parsing error:', error);
    return { level: 0, content: line, type: 'item' };
  }
}
```

### 2. Export Security

**Safe HTML Generation:**
```typescript
private sanitizeContent(content: string): string {
  return content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}
```

## Platform Integration

### 1. Native Feature Integration

**Haptic Feedback:**
```typescript
import * as Haptics from 'expo-haptics';

export class HapticFeedback {
  static swipeIndent() {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
  }
  
  static doubleTap() {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
  }
  
  static longPress() {
    Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
  }
}
```

**Native Sharing:**
```typescript
import * as Sharing from 'expo-sharing';
import * as FileSystem from 'expo-file-system';

export class ShareService {
  static async shareContent(content: string, filename: string, mimeType: string): Promise<void> {
    const fileUri = FileSystem.documentDirectory + filename;
    await FileSystem.writeAsStringAsync(fileUri, content);
    
    if (await Sharing.isAvailableAsync()) {
      await Sharing.shareAsync(fileUri, {
        mimeType,
        dialogTitle: `Share ${filename}`,
      });
    }
  }
}
```

## Deployment Architecture

### 1. Build Configuration

**Expo Configuration (`app.json`):**
```json
{
  "expo": {
    "name": "LogLog Mobile",
    "slug": "loglog-mobile",
    "platforms": ["ios", "android"],
    "version": "1.0.0",
    "orientation": "portrait",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "android": {
      "package": "com.loglog.mobile",
      "permissions": [
        "WRITE_EXTERNAL_STORAGE",
        "READ_EXTERNAL_STORAGE"
      ]
    }
  }
}
```

### 2. Performance Monitoring

**Metrics Collection:**
```typescript
// Performance monitoring hooks
const usePerformanceMonitoring = () => {
  useEffect(() => {
    const startTime = Date.now();
    
    return () => {
      const endTime = Date.now();
      const duration = endTime - startTime;
      
      // Log performance metrics
      console.log(`Component lifecycle: ${duration}ms`);
      
      // Send to analytics (if configured)
      Analytics.track('component_performance', { duration });
    };
  }, []);
};
```

## Future Architecture Considerations

### 1. Scalability Enhancements
- **Cloud synchronization**: Service layer abstraction for remote storage
- **Collaborative editing**: Real-time collaboration infrastructure
- **Plugin system**: Extensible architecture for custom functionality

### 2. Performance Improvements
- **Web Workers**: Background processing for large document operations
- **Native modules**: Performance-critical operations in native code
- **Bundle optimization**: Code splitting and lazy loading

### 3. Platform Extensions
- **Web version**: React Native Web compatibility
- **Desktop version**: Electron wrapper for cross-platform desktop
- **Browser extension**: LogLog format support in web browsers

This technical architecture provides a solid foundation for current functionality while maintaining flexibility for future enhancements and platform extensions.