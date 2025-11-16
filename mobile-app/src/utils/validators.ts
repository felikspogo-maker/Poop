/**
 * Validation utility functions for mobile app
 */

/**
 * Validate email format
 */
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

/**
 * Validate phone number (Russian format)
 */
export const isValidPhone = (phone: string): boolean => {
  const cleaned = phone.replace(/\D/g, '');
  return cleaned.length === 10 || (cleaned.length === 11 && cleaned.startsWith('7'));
};

/**
 * Validate password
 */
export const isValidPassword = (password: string): boolean => {
  return password.length >= 6;
};

/**
 * Get password strength
 */
export const getPasswordStrength = (password: string): 'weak' | 'medium' | 'strong' => {
  let strength = 0;

  if (password.length >= 8) strength++;
  if (/[a-z]/.test(password)) strength++;
  if (/[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^a-zA-Z0-9]/.test(password)) strength++;

  if (strength < 2) return 'weak';
  if (strength < 4) return 'medium';
  return 'strong';
};

/**
 * Validate required field
 */
export const isRequired = (value: string): boolean => {
  return value.trim().length > 0;
};

/**
 * Validate minimum length
 */
export const hasMinLength = (value: string, minLength: number): boolean => {
  return value.length >= minLength;
};

/**
 * Validate maximum length
 */
export const hasMaxLength = (value: string, maxLength: number): boolean => {
  return value.length <= maxLength;
};

/**
 * Validate URL
 */
export const isValidUrl = (url: string): boolean => {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
};

/**
 * Validate date is in future
 */
export const isDateInFuture = (date: Date): boolean => {
  return date > new Date();
};

/**
 * Validate file size
 */
export const isValidFileSize = (sizeInBytes: number, maxSizeInMB: number): boolean => {
  const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
  return sizeInBytes <= maxSizeInBytes;
};

/**
 * Validate file type
 */
export const isValidFileType = (mimeType: string, allowedTypes: string[]): boolean => {
  return allowedTypes.includes(mimeType);
};

/**
 * Form validation errors
 */
export interface ValidationErrors {
  [key: string]: string;
}

/**
 * Validate login form
 */
export const validateLoginForm = (email: string, password: string): ValidationErrors => {
  const errors: ValidationErrors = {};

  if (!isRequired(email)) {
    errors.email = 'Email обязателен';
  } else if (!isValidEmail(email)) {
    errors.email = 'Некорректный email';
  }

  if (!isRequired(password)) {
    errors.password = 'Пароль обязателен';
  } else if (!isValidPassword(password)) {
    errors.password = 'Пароль должен быть минимум 6 символов';
  }

  return errors;
};

/**
 * Validate registration form
 */
export const validateRegisterForm = (data: {
  firstName: string;
  lastName: string;
  email: string;
  phone: string;
  password: string;
  confirmPassword: string;
}): ValidationErrors => {
  const errors: ValidationErrors = {};

  if (!isRequired(data.firstName)) {
    errors.firstName = 'Имя обязательно';
  }

  if (!isRequired(data.lastName)) {
    errors.lastName = 'Фамилия обязательна';
  }

  if (!isRequired(data.email)) {
    errors.email = 'Email обязателен';
  } else if (!isValidEmail(data.email)) {
    errors.email = 'Некорректный email';
  }

  if (!isRequired(data.phone)) {
    errors.phone = 'Телефон обязателен';
  } else if (!isValidPhone(data.phone)) {
    errors.phone = 'Некорректный номер телефона';
  }

  if (!isRequired(data.password)) {
    errors.password = 'Пароль обязателен';
  } else if (!isValidPassword(data.password)) {
    errors.password = 'Пароль должен быть минимум 6 символов';
  }

  if (data.password !== data.confirmPassword) {
    errors.confirmPassword = 'Пароли не совпадают';
  }

  return errors;
};

/**
 * Check if form has errors
 */
export const hasErrors = (errors: ValidationErrors): boolean => {
  return Object.keys(errors).length > 0;
};
