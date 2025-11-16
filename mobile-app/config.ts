// Environment configuration for mobile app

export const config = {
  // API Configuration
  api: {
    baseUrl: __DEV__
      ? 'http://localhost:3000/api' // Development
      : 'https://your-production-api.com/api', // Production
    timeout: 10000,
  },

  // WebSocket Configuration
  socket: {
    url: __DEV__ ? 'http://localhost:3000' : 'https://your-production-api.com',
  },

  // Stripe Configuration
  stripe: {
    publishableKey: __DEV__
      ? 'pk_test_your_stripe_test_key'
      : 'pk_live_your_stripe_live_key',
  },

  // App Configuration
  app: {
    name: 'Business Consulting',
    version: '1.0.0',
  },

  // Storage Keys
  storage: {
    accessToken: 'access_token',
    user: 'user',
  },

  // Pagination
  pagination: {
    defaultPageSize: 20,
  },

  // File Upload
  upload: {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedTypes: [
      'image/jpeg',
      'image/png',
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ],
  },
};
