import { renderHook, act } from '@testing-library/react-hooks';
import { useDebounce, useThrottle, useMemoizedLines, TextProcessor, MemoryManager } from '../src/utils/performance';

// Mock timers for testing
jest.useFakeTimers();

describe('performance utilities', () => {
  describe('useDebounce', () => {
    it('should debounce function calls', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => useDebounce(mockFn, 100));
      
      // Call the debounced function multiple times
      act(() => {
        result.current('test1');
        result.current('test2');
        result.current('test3');
      });
      
      // Should not have been called yet
      expect(mockFn).not.toHaveBeenCalled();
      
      // Fast-forward time
      act(() => {
        jest.advanceTimersByTime(100);
      });
      
      // Should have been called once with the last argument
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenLastCalledWith('test3');
    });

    it('should reset timer on subsequent calls', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => useDebounce(mockFn, 100));
      
      act(() => {
        result.current('test1');
        jest.advanceTimersByTime(50);
        result.current('test2');
        jest.advanceTimersByTime(50);
      });
      
      // Should not have been called yet (timer was reset)
      expect(mockFn).not.toHaveBeenCalled();
      
      act(() => {
        jest.advanceTimersByTime(50);
      });
      
      // Now should be called
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenLastCalledWith('test2');
    });
  });

  describe('useThrottle', () => {
    it('should throttle function calls', () => {
      const mockFn = jest.fn();
      const { result } = renderHook(() => useThrottle(mockFn, 100));
      
      // First call should execute immediately
      act(() => {
        result.current('test1');
      });
      
      expect(mockFn).toHaveBeenCalledTimes(1);
      expect(mockFn).toHaveBeenLastCalledWith('test1');
      
      // Subsequent calls within throttle period should be delayed
      act(() => {
        result.current('test2');
        result.current('test3');
      });
      
      expect(mockFn).toHaveBeenCalledTimes(1);
      
      // After throttle period, last call should execute
      act(() => {
        jest.advanceTimersByTime(100);
      });
      
      expect(mockFn).toHaveBeenCalledTimes(2);
      expect(mockFn).toHaveBeenLastCalledWith('test3');
    });
  });

  describe('useMemoizedLines', () => {
    it('should memoize line parsing results', () => {
      const content = `Root item
    Child item
        Grandchild item`;
      
      const { result, rerender } = renderHook(
        ({ content }) => useMemoizedLines(content),
        { initialProps: { content } }
      );
      
      const firstResult = result.current;
      
      // Re-render with same content
      rerender({ content });
      
      // Should return same reference (memoized)
      expect(result.current).toBe(firstResult);
      
      // Re-render with different content
      const newContent = `Different content
    New child`;
      
      rerender({ content: newContent });
      
      // Should return new reference
      expect(result.current).not.toBe(firstResult);
      expect(result.current.lines).toEqual(['Different content', '    New child']);
    });

    it('should correctly parse line levels', () => {
      const content = `Root
    Level 1
        Level 2
            Level 3`;
      
      const { result } = renderHook(() => useMemoizedLines(content));
      
      const { parsedLines } = result.current;
      
      expect(parsedLines[0].level).toBe(0);
      expect(parsedLines[1].level).toBe(1);
      expect(parsedLines[2].level).toBe(2);
      expect(parsedLines[3].level).toBe(3);
    });
  });

  describe('TextProcessor', () => {
    beforeEach(() => {
      TextProcessor.clearCache();
    });

    it('should cache line parsing results', () => {
      const content = `Test content
    Child line`;
      
      const result1 = TextProcessor.parseLinesCached(content);
      const result2 = TextProcessor.parseLinesCached(content);
      
      // Should return same reference from cache
      expect(result2).toBe(result1);
    });

    it('should handle large content with partial caching', () => {
      const largeContent = 'x'.repeat(20000) + '\n    child';
      
      const result = TextProcessor.parseLinesCached(largeContent);
      
      expect(result).toBeDefined();
      expect(result.length).toBe(2);
    });

    it('should limit cache size', () => {
      // Fill cache beyond limit
      for (let i = 0; i < 1050; i++) {
        TextProcessor.parseLinesCached(`content ${i}`);
      }
      
      // Should not throw error and should work normally
      const result = TextProcessor.parseLinesCached('new content');
      expect(result).toBeDefined();
    });
  });

  describe('MemoryManager', () => {
    it('should cleanup history when exceeding max size', () => {
      const history = Array.from({ length: 60 }, (_, i) => `item-${i}`);
      
      const cleaned = MemoryManager.cleanupHistory(history, 50);
      
      expect(cleaned.length).toBe(50);
      expect(cleaned[0]).toBe('item-10'); // Should keep last 50 items
      expect(cleaned[49]).toBe('item-59');
    });

    it('should not modify history under max size', () => {
      const history = Array.from({ length: 30 }, (_, i) => `item-${i}`);
      
      const cleaned = MemoryManager.cleanupHistory(history, 50);
      
      expect(cleaned).toBe(history); // Should return same reference
      expect(cleaned.length).toBe(30);
    });

    it('should schedule periodic cleanup', () => {
      const mockCallback = jest.fn();
      
      const intervalId = MemoryManager.schedulePeriodicCleanup(mockCallback);
      
      // Fast-forward time
      act(() => {
        jest.advanceTimersByTime(30000);
      });
      
      expect(mockCallback).toHaveBeenCalledTimes(1);
      
      // Clean up
      clearInterval(intervalId);
    });
  });
});

// Restore real timers
afterAll(() => {
  jest.useRealTimers();
});