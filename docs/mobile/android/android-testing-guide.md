# Android Device Testing Guide

## Prerequisites

### Development Environment
- Android Studio installed with SDK tools
- USB debugging enabled on Android device
- Device connected via USB or WiFi debugging
- Node.js and npm/yarn installed
- Expo CLI installed globally: `npm install -g @expo/cli`

### Device Requirements
- Android 6.0 (API level 23) or higher
- Minimum 2GB RAM for smooth performance
- 500MB free storage space
- Developer options enabled with USB debugging

## Pre-Testing Setup

### 1. Install Dependencies
```bash
cd [PROJECT_ROOT]/loglog-mobile
npm install
```

### 2. Run Tests
```bash
# Run unit tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test files
npm test TreeNode.test.ts
npm test parser.test.ts
npm test performance.test.ts
```

### 3. Build Development Version
```bash
# Start Expo development server
expo start

# Or start with specific options
expo start --android --clear
```

## Device Testing Protocol

### Phase 1: Basic Functionality (30 minutes)
- [ ] App launches without crashes
- [ ] Text input works correctly
- [ ] Real-time parsing displays properly
- [ ] Tree structure builds correctly
- [ ] Status bar updates appropriately

### Phase 2: Gesture System (45 minutes)
- [ ] Long-press enters selection mode
- [ ] Multiple line selection works
- [ ] Single tap toggles selection
- [ ] Double-tap folding/unfolding functions
- [ ] Swipe left/right for indent/outdent
- [ ] Haptic feedback on gestures
- [ ] Visual indicators during gestures

### Phase 3: File Operations (30 minutes)
- [ ] Create new file functionality
- [ ] Auto-save works correctly
- [ ] File loading from storage
- [ ] Recent files list updates
- [ ] File metadata tracking

### Phase 4: Export Features (30 minutes)
- [ ] Export menu opens correctly
- [ ] Loglog format export
- [ ] Markdown export with proper formatting
- [ ] HTML export with interactive features
- [ ] Native sharing integration
- [ ] File format validation

### Phase 5: Performance Testing (30 minutes)
- [ ] Large document handling (1000+ lines)
- [ ] Smooth scrolling performance
- [ ] Memory usage stability
- [ ] Gesture responsiveness under load
- [ ] Real-time parsing performance

### Phase 6: Edge Cases (30 minutes)
- [ ] Empty document handling
- [ ] Malformed input recovery
- [ ] Network interruption during save/export
- [ ] App backgrounding/foregrounding
- [ ] Memory pressure scenarios
- [ ] Rotation handling

## Performance Benchmarks

### Target Metrics
- App startup time: < 3 seconds
- Gesture response time: < 16ms (60fps)
- File save operation: < 500ms
- Export generation: < 2 seconds for 1000 lines
- Memory usage: < 200MB for large documents

### Measurement Tools
```bash
# Monitor performance with Flipper
npx react-native run-android --variant=debug

# Profile with Android Studio
# Tools > Layout Inspector
# View > Tool Windows > Profiler
```

## Known Issues and Workarounds

### Common Issues
1. **Gesture conflicts with system gestures**
   - Workaround: Adjust swipe thresholds in GestureEditor.tsx
   - Test with different sensitivity settings

2. **Virtual keyboard covering content**
   - Workaround: Implement KeyboardAvoidingView
   - Test with different input methods

3. **Memory pressure on large documents**
   - Workaround: Implement virtual scrolling
   - Monitor with performance utilities

### Debug Commands
```bash
# Clear Metro cache
npx react-native start --reset-cache

# Clean build
cd android && ./gradlew clean && cd ..

# Restart ADB
adb kill-server && adb start-server
```

## Test Data Sets

### Small Document (< 50 lines)
```
Project Planning
    Research Phase
        Market Analysis
        [ ] Competitor research
        Technical requirements
    Development Phase
        [ ] UI mockups
        [x] Architecture design
        Backend development
    Testing Phase
        Unit tests
        Integration tests
        [ ] User acceptance testing
```

### Medium Document (200-500 lines)
- Use generated content with nested structures
- Mix of todo items and regular content
- Multiple indentation levels (up to 6 deep)

### Large Document (1000+ lines)
- Stress test with auto-generated hierarchical content
- Performance monitoring required
- Memory usage tracking essential

## Reporting Issues

### Issue Template
```
**Device Information:**
- Model: [device model]
- Android Version: [version]
- RAM: [amount]
- Storage Available: [amount]

**Issue Description:**
[Detailed description of the issue]

**Steps to Reproduce:**
1. [Step 1]
2. [Step 2]
3. [Step 3]

**Expected Behavior:**
[What should have happened]

**Actual Behavior:**
[What actually happened]

**Screenshots/Videos:**
[Attach if applicable]

**Performance Impact:**
[Any performance degradation noticed]
```

### Priority Levels
- **P0 Critical:** App crashes, data loss
- **P1 High:** Core features broken
- **P2 Medium:** UI issues, minor functionality problems
- **P3 Low:** Cosmetic issues, enhancement requests

## Sign-off Criteria

### Must Pass
- [ ] No critical crashes during 2-hour continuous use
- [ ] All core gestures work reliably
- [ ] File operations complete successfully
- [ ] Export functions generate correct output
- [ ] Performance remains smooth with large documents

### Nice to Have
- [ ] Optimal performance on lower-end devices
- [ ] Perfect gesture recognition in all scenarios
- [ ] Sub-second export times for all formats
- [ ] Minimal battery usage during extended use

## Next Steps After Testing
1. Collect and analyze test results
2. File issues for any discovered problems
3. Prioritize fixes based on severity
4. Prepare for production build optimization
5. Plan app store submission process