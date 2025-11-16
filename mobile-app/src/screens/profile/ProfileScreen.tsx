import React from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { List, Avatar, Title, Paragraph, Button, Divider } from 'react-native-paper';
import { useAuth } from '../../contexts/AuthContext';
import { spacing } from '../../utils/theme';

export const ProfileScreen = ({ navigation }: any) => {
  const { user, signOut } = useAuth();

  const handleLogout = () => {
    Alert.alert('Выход', 'Вы уверены, что хотите выйти?', [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Выйти',
        style: 'destructive',
        onPress: async () => {
          await signOut();
        },
      },
    ]);
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Avatar.Text
          size={80}
          label={`${user?.firstName?.charAt(0)}${user?.lastName?.charAt(0)}`}
        />
        <Title style={styles.name}>
          {user?.firstName} {user?.lastName}
        </Title>
        <Paragraph style={styles.email}>{user?.email}</Paragraph>
      </View>

      <View style={styles.section}>
        <List.Section>
          <List.Subheader>Аккаунт</List.Subheader>
          <List.Item
            title="Личная информация"
            description="Имя, телефон, email"
            left={(props) => <List.Icon {...props} icon="account-circle" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Документы"
            description="Загруженные файлы и отчеты"
            left={(props) => <List.Icon {...props} icon="file-document" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => navigation.navigate('Documents')}
          />
          <Divider />
          <List.Item
            title="История платежей"
            description="Все транзакции"
            left={(props) => <List.Icon {...props} icon="credit-card" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </List.Section>

        <List.Section>
          <List.Subheader>Настройки</List.Subheader>
          <List.Item
            title="Уведомления"
            description="Управление уведомлениями"
            left={(props) => <List.Icon {...props} icon="bell" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Конфиденциальность"
            description="Безопасность и приватность"
            left={(props) => <List.Icon {...props} icon="shield-account" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="Язык"
            description="Русский"
            left={(props) => <List.Icon {...props} icon="translate" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </List.Section>

        <List.Section>
          <List.Subheader>Поддержка</List.Subheader>
          <List.Item
            title="Помощь"
            description="FAQ и поддержка"
            left={(props) => <List.Icon {...props} icon="help-circle" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
          <Divider />
          <List.Item
            title="О приложении"
            description="Версия 1.0.0"
            left={(props) => <List.Icon {...props} icon="information" />}
            right={(props) => <List.Icon {...props} icon="chevron-right" />}
            onPress={() => {}}
          />
        </List.Section>
      </View>

      <Button
        mode="outlined"
        onPress={handleLogout}
        style={styles.logoutButton}
        textColor="#dc2626"
      >
        Выйти из аккаунта
      </Button>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    alignItems: 'center',
    padding: spacing.xl,
    backgroundColor: 'white',
  },
  name: {
    fontSize: 24,
    fontWeight: 'bold',
    marginTop: spacing.md,
  },
  email: {
    color: '#64748b',
  },
  section: {
    marginTop: spacing.md,
    backgroundColor: 'white',
  },
  logoutButton: {
    margin: spacing.xl,
    borderColor: '#dc2626',
  },
});
