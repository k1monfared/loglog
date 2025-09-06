# Build and Deployment Instructions

## Development Setup

### Prerequisites
- Node.js 16.x or higher
- npm or yarn package manager
- Android Studio with SDK tools
- Expo CLI: `npm install -g @expo/cli`
- Git for version control

### Initial Setup
```bash
# Clone and navigate to project
cd /home/k1/Projects/loglog/loglog-mobile

# Install dependencies
npm install

# Verify installation
npm run typecheck
npm test
```

## Development Workflow

### Running Development Server
```bash
# Start Expo development server
npm start

# Or start directly for Android
npm run android

# Clear cache if needed
expo start --clear
```

### Quality Checks
```bash
# Run all tests
npm test

# Run tests with coverage report
npm run test:coverage

# Type checking
npm run typecheck

# Linting
npm run lint
npm run lint:fix
```

### Code Quality Standards
- Minimum 80% test coverage required
- All TypeScript errors must be resolved
- ESLint warnings should be addressed
- Performance benchmarks must be met

## Production Builds

### Android Production Build

#### Method 1: Expo Build Service (Recommended)
```bash
# Configure app signing
expo build:android --type=app-bundle

# Or APK format
expo build:android --type=apk
```

#### Method 2: Local Build (Advanced)
```bash
# Eject from Expo (if needed)
expo eject

# Build with Gradle
cd android
./gradlew assembleRelease
```

### iOS Production Build
```bash
# iOS App Store build
expo build:ios --type=archive

# Or development build
expo build:ios --type=simulator
```

## App Configuration

### app.json Configuration
```json
{
  "expo": {
    "name": "LogLog Mobile",
    "slug": "loglog-mobile",
    "version": "1.0.0",
    "orientation": "portrait",
    "icon": "./assets/icon.png",
    "splash": {
      "image": "./assets/splash.png",
      "resizeMode": "contain",
      "backgroundColor": "#ffffff"
    },
    "updates": {
      "fallbackToCacheTimeout": 0
    },
    "assetBundlePatterns": [
      "**/*"
    ],
    "ios": {
      "supportsTablet": true,
      "bundleIdentifier": "com.loglog.mobile"
    },
    "android": {
      "adaptiveIcon": {
        "foregroundImage": "./assets/adaptive-icon.png",
        "backgroundColor": "#FFFFFF"
      },
      "package": "com.loglog.mobile",
      "versionCode": 1,
      "permissions": [
        "WRITE_EXTERNAL_STORAGE",
        "READ_EXTERNAL_STORAGE"
      ]
    },
    "web": {
      "favicon": "./assets/favicon.png"
    }
  }
}
```

## Testing Before Deployment

### Pre-deployment Checklist
- [ ] All unit tests passing (`npm test`)
- [ ] TypeScript compilation successful (`npm run typecheck`)
- [ ] No linting errors (`npm run lint`)
- [ ] Android device testing completed
- [ ] Performance benchmarks met
- [ ] Export functionality validated
- [ ] File operations tested
- [ ] Gesture system working correctly

### Performance Validation
```bash
# Profile memory usage
expo start --android
# Use Android Studio Profiler to monitor

# Test with large documents (1000+ lines)
# Verify smooth scrolling and gesture responsiveness
# Check memory usage stays under 200MB
```

## App Store Submission

### Google Play Store

#### Step 1: Prepare Assets
- App icon (512x512 PNG)
- Feature graphic (1024x500 PNG)
- Screenshots for different screen sizes
- Store listing text and descriptions

#### Step 2: Build Signed APK/AAB
```bash
# Generate signing key (first time only)
keytool -genkey -v -keystore loglog-release-key.keystore -alias loglog-key -keyalg RSA -keysize 2048 -validity 10000

# Build signed bundle
expo build:android --type=app-bundle
```

#### Step 3: Google Play Console
1. Create new application
2. Upload APK/AAB file
3. Complete store listing
4. Set pricing and distribution
5. Submit for review

### Apple App Store

#### Step 1: Apple Developer Account
- Enroll in Apple Developer Program
- Generate certificates and profiles
- Configure App Store Connect

#### Step 2: Build and Upload
```bash
# Build iOS archive
expo build:ios --type=archive

# Upload to App Store Connect (automated)
# Or use Xcode to upload manually
```

#### Step 3: App Store Connect
1. Create new app record
2. Upload build file
3. Complete metadata
4. Submit for App Review

## Monitoring and Analytics

### Performance Monitoring
```javascript
// Add to App.tsx
import * as Analytics from 'expo-analytics';

// Track app launches
Analytics.track('app_launch');

// Track feature usage
Analytics.track('export_used', { format: 'markdown' });
```

### Error Tracking
```bash
# Install Sentry for error tracking
npm install @sentry/react-native

# Configure in App.tsx
import * as Sentry from '@sentry/react-native';
Sentry.init({ dsn: 'YOUR_DSN_HERE' });
```

## Version Management

### Semantic Versioning
- MAJOR: Breaking changes
- MINOR: New features
- PATCH: Bug fixes

### Release Process
```bash
# Update version in app.json and package.json
# Create git tag
git tag v1.0.0
git push --tags

# Build and deploy
npm run build:android
# Upload to stores
```

## Rollback Procedures

### Emergency Rollback
1. Revert to previous working commit
2. Rebuild and redeploy quickly
3. Update store listings if needed
4. Notify users through in-app messaging

### Gradual Rollback
1. Use Expo updates to push hotfix
2. Monitor crash rates and user feedback
3. Prepare next stable version

## Environment Variables

### Development
```bash
# .env.development
API_URL=http://localhost:3000
DEBUG_MODE=true
```

### Production
```bash
# .env.production  
API_URL=https://api.loglog.com
DEBUG_MODE=false
ANALYTICS_KEY=your_analytics_key
```

## Troubleshooting

### Common Build Issues

#### Metro bundler cache
```bash
npx react-native start --reset-cache
```

#### Android Gradle issues
```bash
cd android
./gradlew clean
cd ..
expo start --clear
```

#### iOS CocoaPods issues
```bash
cd ios
pod deintegrate
pod install
cd ..
```

### Performance Issues
- Check memory usage with profiling tools
- Optimize large document rendering
- Review gesture handler performance
- Validate export generation times

## Support and Maintenance

### Update Schedule
- Security patches: Immediate
- Bug fixes: Weekly releases
- Feature updates: Monthly releases
- Major versions: Quarterly

### User Support
- In-app feedback mechanism
- GitHub issues for bug reports
- Documentation updates
- Community support forum

## Backup and Recovery

### Code Backup
- Git repository with multiple remotes
- Regular automated backups
- Version control best practices

### Data Recovery
- AsyncStorage data export/import
- Cloud backup integration (future)
- User data migration tools