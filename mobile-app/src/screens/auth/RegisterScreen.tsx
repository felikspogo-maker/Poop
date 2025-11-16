import React, { useState } from 'react';
import { View, StyleSheet, KeyboardAvoidingView, Platform, ScrollView, Alert } from 'react-native';
import { TextInput, Button, Text, Title } from 'react-native-paper';
import { useAuth } from '../../contexts/AuthContext';
import { spacing } from '../../utils/theme';

export const RegisterScreen = ({ navigation }: any) => {
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const { signUp } = useAuth();

  const handleRegister = async () => {
    if (!firstName || !lastName || !email || !phone || !password || !confirmPassword) {
      Alert.alert('Ошибка', 'Пожалуйста, заполните все поля');
      return;
    }

    if (password !== confirmPassword) {
      Alert.alert('Ошибка', 'Пароли не совпадают');
      return;
    }

    if (password.length < 6) {
      Alert.alert('Ошибка', 'Пароль должен содержать минимум 6 символов');
      return;
    }

    setLoading(true);
    try {
      await signUp({ email, password, firstName, lastName, phone });
    } catch (error: any) {
      Alert.alert(
        'Ошибка регистрации',
        error.response?.data?.message || 'Не удалось зарегистрироваться'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.content}>
          <Title style={styles.title}>Регистрация</Title>
          <Text style={styles.subtitle}>Создайте аккаунт для начала работы</Text>

          <TextInput
            label="Имя"
            value={firstName}
            onChangeText={setFirstName}
            mode="outlined"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Фамилия"
            value={lastName}
            onChangeText={setLastName}
            mode="outlined"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Email"
            value={email}
            onChangeText={setEmail}
            mode="outlined"
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Телефон"
            value={phone}
            onChangeText={setPhone}
            mode="outlined"
            keyboardType="phone-pad"
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Пароль"
            value={password}
            onChangeText={setPassword}
            mode="outlined"
            secureTextEntry={!showPassword}
            right={
              <TextInput.Icon
                icon={showPassword ? 'eye-off' : 'eye'}
                onPress={() => setShowPassword(!showPassword)}
              />
            }
            style={styles.input}
            disabled={loading}
          />

          <TextInput
            label="Подтвердите пароль"
            value={confirmPassword}
            onChangeText={setConfirmPassword}
            mode="outlined"
            secureTextEntry={!showPassword}
            style={styles.input}
            disabled={loading}
          />

          <Button
            mode="contained"
            onPress={handleRegister}
            loading={loading}
            disabled={loading}
            style={styles.button}
          >
            Зарегистрироваться
          </Button>

          <Button
            mode="text"
            onPress={() => navigation.navigate('Login')}
            disabled={loading}
            style={styles.loginButton}
          >
            Уже есть аккаунт? Войти
          </Button>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
  },
  content: {
    padding: spacing.lg,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    marginBottom: spacing.sm,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 16,
    color: '#64748b',
    marginBottom: spacing.xl,
    textAlign: 'center',
  },
  input: {
    marginBottom: spacing.md,
  },
  button: {
    marginTop: spacing.md,
    paddingVertical: spacing.sm,
  },
  loginButton: {
    marginTop: spacing.md,
  },
});
