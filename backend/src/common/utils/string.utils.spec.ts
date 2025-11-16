import { StringUtils } from './string.utils';

describe('StringUtils', () => {
  describe('randomString', () => {
    it('should generate random string of specified length', () => {
      const length = 10;
      const result = StringUtils.randomString(length);

      expect(result).toHaveLength(length);
      expect(typeof result).toBe('string');
    });

    it('should generate different strings each time', () => {
      const str1 = StringUtils.randomString(10);
      const str2 = StringUtils.randomString(10);

      expect(str1).not.toBe(str2);
    });
  });

  describe('slugify', () => {
    it('should convert text to slug', () => {
      expect(StringUtils.slugify('Hello World')).toBe('hello-world');
      expect(StringUtils.slugify('Test String 123')).toBe('test-string-123');
    });

    it('should handle special characters', () => {
      expect(StringUtils.slugify('Test@#$String')).toBe('teststring');
    });

    it('should trim whitespace', () => {
      expect(StringUtils.slugify('  hello world  ')).toBe('hello-world');
    });
  });

  describe('truncate', () => {
    it('should truncate long text', () => {
      const text = 'This is a very long text that needs to be truncated';
      const result = StringUtils.truncate(text, 20);

      expect(result).toBe('This is a very lo...');
      expect(result).toHaveLength(20);
    });

    it('should not truncate short text', () => {
      const text = 'Short text';
      const result = StringUtils.truncate(text, 20);

      expect(result).toBe(text);
    });

    it('should use custom suffix', () => {
      const text = 'This is a long text';
      const result = StringUtils.truncate(text, 15, '---');

      expect(result).toBe('This is a l---');
    });
  });

  describe('capitalize', () => {
    it('should capitalize first letter', () => {
      expect(StringUtils.capitalize('hello')).toBe('Hello');
      expect(StringUtils.capitalize('WORLD')).toBe('World');
    });

    it('should handle empty string', () => {
      expect(StringUtils.capitalize('')).toBe('');
    });
  });

  describe('titleCase', () => {
    it('should convert to title case', () => {
      expect(StringUtils.titleCase('hello world')).toBe('Hello World');
      expect(StringUtils.titleCase('HELLO WORLD')).toBe('Hello World');
    });
  });

  describe('removeWhitespace', () => {
    it('should remove all whitespace', () => {
      expect(StringUtils.removeWhitespace('hello world')).toBe('helloworld');
      expect(StringUtils.removeWhitespace('  hello   world  ')).toBe('helloworld');
    });
  });

  describe('escapeHtml', () => {
    it('should escape HTML characters', () => {
      expect(StringUtils.escapeHtml('<script>alert("XSS")</script>')).toBe(
        '&lt;script&gt;alert(&quot;XSS&quot;)&#x2F;script&gt;'
      );
      expect(StringUtils.escapeHtml('Test & Test')).toBe('Test &amp; Test');
    });
  });

  describe('isEmail', () => {
    it('should validate email format', () => {
      expect(StringUtils.isEmail('test@example.com')).toBe(true);
      expect(StringUtils.isEmail('invalid.email')).toBe(false);
      expect(StringUtils.isEmail('test@')).toBe(false);
      expect(StringUtils.isEmail('@example.com')).toBe(false);
    });
  });

  describe('maskEmail', () => {
    it('should mask email address', () => {
      expect(StringUtils.maskEmail('test@example.com')).toBe('te***@example.com');
      expect(StringUtils.maskEmail('a@example.com')).toBe('a***@example.com');
    });
  });

  describe('maskPhone', () => {
    it('should mask phone number', () => {
      expect(StringUtils.maskPhone('+79001234567')).toBe('*******4567');
      expect(StringUtils.maskPhone('1234567890')).toBe('******7890');
    });

    it('should not mask short numbers', () => {
      expect(StringUtils.maskPhone('123')).toBe('123');
    });
  });
});
