import { Vibration, Platform } from 'react-native';

export enum HapticType {
  Light = 'light',
  Medium = 'medium',
  Heavy = 'heavy',
  Success = 'success',
  Warning = 'warning',
  Error = 'error',
}

export class HapticFeedback {
  /**
   * Provide haptic feedback based on the type of interaction
   */
  static trigger(type: HapticType): void {
    if (Platform.OS === 'android') {
      // Android uses Vibration API with different durations
      switch (type) {
        case HapticType.Light:
          Vibration.vibrate(25);
          break;
        case HapticType.Medium:
          Vibration.vibrate(50);
          break;
        case HapticType.Heavy:
          Vibration.vibrate(100);
          break;
        case HapticType.Success:
          Vibration.vibrate([50, 50, 50]); // Three quick pulses
          break;
        case HapticType.Warning:
          Vibration.vibrate([100, 100]); // Two medium pulses
          break;
        case HapticType.Error:
          Vibration.vibrate([200, 100, 200]); // Long-short-long pattern
          break;
        default:
          Vibration.vibrate(50);
      }
    } else {
      // iOS would use more sophisticated haptic feedback
      // For now, fallback to simple vibration
      switch (type) {
        case HapticType.Light:
          Vibration.vibrate(25);
          break;
        case HapticType.Medium:
          Vibration.vibrate(50);
          break;
        case HapticType.Heavy:
          Vibration.vibrate(75);
          break;
        case HapticType.Success:
          Vibration.vibrate([30, 30, 30]);
          break;
        case HapticType.Warning:
          Vibration.vibrate([50, 50]);
          break;
        case HapticType.Error:
          Vibration.vibrate([100, 50, 100]);
          break;
        default:
          Vibration.vibrate(50);
      }
    }
  }

  /**
   * Specific haptic feedback for gesture interactions
   */
  static selectionStart(): void {
    this.trigger(HapticType.Medium);
  }

  static swipeIndent(): void {
    this.trigger(HapticType.Light);
  }

  static swipeOutdent(): void {
    this.trigger(HapticType.Light);
  }

  static fold(): void {
    this.trigger(HapticType.Light);
  }

  static unfold(): void {
    this.trigger(HapticType.Light);
  }

  static longPress(): void {
    this.trigger(HapticType.Heavy);
  }

  static doubleTap(): void {
    this.trigger(HapticType.Medium);
  }

  static success(): void {
    this.trigger(HapticType.Success);
  }

  static error(): void {
    this.trigger(HapticType.Error);
  }
}