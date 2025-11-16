import { MD3LightTheme as DefaultTheme } from 'react-native-paper';

export const theme = {
  ...DefaultTheme,
  colors: {
    ...DefaultTheme.colors,
    primary: '#2563eb',
    secondary: '#7c3aed',
    error: '#dc2626',
    background: '#f8fafc',
    surface: '#ffffff',
    text: '#0f172a',
    onPrimary: '#ffffff',
    disabled: '#94a3b8',
    placeholder: '#64748b',
    backdrop: 'rgba(0, 0, 0, 0.5)',
  },
};

export const spacing = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
};

export const borderRadius = {
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  full: 9999,
};
