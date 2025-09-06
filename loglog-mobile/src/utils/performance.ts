import { useMemo, useCallback, useRef } from 'react';

/**
 * Debounce hook for performance optimization
 */
export function useDebounce<T extends (...args: any[]) => void>(
  callback: T,
  delay: number
): T {
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    (...args: Parameters<T>) => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      
      timeoutRef.current = setTimeout(() => {
        callback(...args);
      }, delay);
    },
    [callback, delay]
  ) as T;
}

/**
 * Throttle hook for performance optimization
 */
export function useThrottle<T extends (...args: any[]) => void>(
  callback: T,
  delay: number
): T {
  const lastCall = useRef<number>(0);
  const timeoutRef = useRef<NodeJS.Timeout>();

  return useCallback(
    (...args: Parameters<T>) => {
      const now = Date.now();
      
      if (now - lastCall.current >= delay) {
        lastCall.current = now;
        callback(...args);
      } else {
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        
        timeoutRef.current = setTimeout(() => {
          lastCall.current = Date.now();
          callback(...args);
        }, delay - (now - lastCall.current));
      }
    },
    [callback, delay]
  ) as T;
}

/**
 * Memoize expensive line parsing operations
 */
export function useMemoizedLines(content: string) {
  return useMemo(() => {
    const lines = content.split('\n');
    const parsedLines = lines.map((line, index) => ({
      content: line,
      index,
      level: Math.floor((line.match(/^ */)?.[0]?.length || 0) / 4),
      isEmpty: line.trim() === '',
    }));
    
    return { lines, parsedLines };
  }, [content]);
}

/**
 * Virtual scrolling utility for large documents
 */
export interface VirtualScrollItem {
  index: number;
  height: number;
  offset: number;
}

export function useVirtualScroll(
  itemCount: number,
  itemHeight: number,
  containerHeight: number,
  scrollOffset: number = 0
) {
  return useMemo(() => {
    const visibleStart = Math.max(0, Math.floor(scrollOffset / itemHeight) - 5);
    const visibleEnd = Math.min(
      itemCount,
      Math.ceil((scrollOffset + containerHeight) / itemHeight) + 5
    );
    
    const visibleItems: VirtualScrollItem[] = [];
    for (let i = visibleStart; i < visibleEnd; i++) {
      visibleItems.push({
        index: i,
        height: itemHeight,
        offset: i * itemHeight,
      });
    }
    
    return {
      visibleItems,
      totalHeight: itemCount * itemHeight,
      visibleStart,
      visibleEnd,
    };
  }, [itemCount, itemHeight, containerHeight, scrollOffset]);
}

/**
 * Optimize gesture recognition for better performance
 */
export class GestureOptimizer {
  private static readonly GESTURE_THROTTLE_MS = 16; // ~60fps
  private static readonly SELECTION_DEBOUNCE_MS = 100;
  
  static throttleGestureUpdate = (callback: Function) => {
    let lastCall = 0;
    let timeoutId: NodeJS.Timeout;
    
    return (...args: any[]) => {
      const now = Date.now();
      
      if (now - lastCall >= this.GESTURE_THROTTLE_MS) {
        lastCall = now;
        callback(...args);
      } else {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => {
          lastCall = Date.now();
          callback(...args);
        }, this.GESTURE_THROTTLE_MS);
      }
    };
  };
  
  static debounceSelection = (callback: Function) => {
    let timeoutId: NodeJS.Timeout;
    
    return (...args: any[]) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => {
        callback(...args);
      }, this.SELECTION_DEBOUNCE_MS);
    };
  };
}

/**
 * Memory management for large documents
 */
export class MemoryManager {
  private static readonly MAX_UNDO_HISTORY = 50;
  private static readonly CLEANUP_INTERVAL_MS = 30000; // 30 seconds
  
  static cleanupHistory<T>(history: T[], maxSize: number = this.MAX_UNDO_HISTORY): T[] {
    if (history.length <= maxSize) {
      return history;
    }
    
    return history.slice(-maxSize);
  }
  
  static schedulePeriodicCleanup(cleanupCallback: () => void) {
    return setInterval(cleanupCallback, this.CLEANUP_INTERVAL_MS);
  }
}

/**
 * Text processing optimizations
 */
export class TextProcessor {
  private static lineCache = new Map<string, any>();
  private static readonly CACHE_SIZE_LIMIT = 1000;
  
  static parseLinesCached(content: string) {
    const cacheKey = content.length < 10000 ? content : content.substring(0, 100) + content.length;
    
    if (this.lineCache.has(cacheKey)) {
      return this.lineCache.get(cacheKey);
    }
    
    const lines = content.split('\n');
    const result = lines.map((line, index) => ({
      content: line,
      index,
      level: Math.floor((line.match(/^ */)?.[0]?.length || 0) / 4),
      isEmpty: line.trim() === '',
    }));
    
    // Manage cache size
    if (this.lineCache.size >= this.CACHE_SIZE_LIMIT) {
      const firstKey = this.lineCache.keys().next().value;
      this.lineCache.delete(firstKey);
    }
    
    this.lineCache.set(cacheKey, result);
    return result;
  }
  
  static clearCache() {
    this.lineCache.clear();
  }
}