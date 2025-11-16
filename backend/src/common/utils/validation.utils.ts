/**
 * Validation utility functions
 */

export class ValidationUtils {
  /**
   * Validate email format
   */
  static isValidEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  }

  /**
   * Validate phone number (Russian format)
   */
  static isValidPhone(phone: string): boolean {
    const phoneRegex = /^(\+7|8)?\s?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{2}[\s.-]?\d{2}$/;
    return phoneRegex.test(phone);
  }

  /**
   * Validate password strength
   */
  static isStrongPassword(password: string): {
    isValid: boolean;
    errors: string[];
  } {
    const errors: string[] = [];

    if (password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Password must contain at least one uppercase letter');
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Password must contain at least one lowercase letter');
    }

    if (!/[0-9]/.test(password)) {
      errors.push('Password must contain at least one number');
    }

    return {
      isValid: errors.length === 0,
      errors,
    };
  }

  /**
   * Validate URL
   */
  static isValidUrl(url: string): boolean {
    try {
      new URL(url);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Validate UUID
   */
  static isValidUuid(uuid: string): boolean {
    const uuidRegex = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
    return uuidRegex.test(uuid);
  }

  /**
   * Sanitize string (remove dangerous characters)
   */
  static sanitizeString(input: string): string {
    return input.replace(/[<>]/g, '');
  }

  /**
   * Validate file size
   */
  static isValidFileSize(sizeInBytes: number, maxSizeInMB: number): boolean {
    const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
    return sizeInBytes <= maxSizeInBytes;
  }

  /**
   * Validate file type
   */
  static isValidFileType(mimeType: string, allowedTypes: string[]): boolean {
    return allowedTypes.includes(mimeType);
  }

  /**
   * Validate date is in future
   */
  static isDateInFuture(date: Date): boolean {
    return date > new Date();
  }

  /**
   * Validate date range
   */
  static isValidDateRange(startDate: Date, endDate: Date): boolean {
    return startDate < endDate;
  }
}
