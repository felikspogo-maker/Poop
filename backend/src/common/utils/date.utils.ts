/**
 * Date utility functions
 */

export class DateUtils {
  /**
   * Add days to a date
   */
  static addDays(date: Date, days: number): Date {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  }

  /**
   * Check if a date is in the past
   */
  static isPast(date: Date): boolean {
    return date < new Date();
  }

  /**
   * Check if a date is in the future
   */
  static isFuture(date: Date): boolean {
    return date > new Date();
  }

  /**
   * Check if a date is today
   */
  static isToday(date: Date): boolean {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  }

  /**
   * Get start of day
   */
  static startOfDay(date: Date): Date {
    const result = new Date(date);
    result.setHours(0, 0, 0, 0);
    return result;
  }

  /**
   * Get end of day
   */
  static endOfDay(date: Date): Date {
    const result = new Date(date);
    result.setHours(23, 59, 59, 999);
    return result;
  }

  /**
   * Format date to ISO string
   */
  static toISOString(date: Date): string {
    return date.toISOString();
  }

  /**
   * Parse ISO string to date
   */
  static fromISOString(iso: string): Date {
    return new Date(iso);
  }

  /**
   * Get difference in days between two dates
   */
  static differenceInDays(date1: Date, date2: Date): number {
    const diff = Math.abs(date1.getTime() - date2.getTime());
    return Math.floor(diff / (1000 * 60 * 60 * 24));
  }

  /**
   * Get difference in hours between two dates
   */
  static differenceInHours(date1: Date, date2: Date): number {
    const diff = Math.abs(date1.getTime() - date2.getTime());
    return Math.floor(diff / (1000 * 60 * 60));
  }
}
