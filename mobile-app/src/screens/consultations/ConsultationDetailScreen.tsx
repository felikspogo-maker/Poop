import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Title, Paragraph, Button, Card, Divider } from 'react-native-paper';
import { consultationsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const ConsultationDetailScreen = ({ route, navigation }: any) => {
  const { id } = route.params;
  const [consultation, setConsultation] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConsultation();
  }, [id]);

  const loadConsultation = async () => {
    try {
      const response = await consultationsAPI.getById(id);
      setConsultation(response.data);
    } catch (error) {
      console.error('Error loading consultation:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCancel = () => {
    Alert.alert(
      'Отменить консультацию',
      'Вы уверены, что хотите отменить эту консультацию?',
      [
        { text: 'Нет', style: 'cancel' },
        {
          text: 'Да, отменить',
          style: 'destructive',
          onPress: async () => {
            try {
              await consultationsAPI.cancel(id);
              Alert.alert('Успешно', 'Консультация отменена');
              navigation.goBack();
            } catch (error) {
              Alert.alert('Ошибка', 'Не удалось отменить консультацию');
            }
          },
        },
      ]
    );
  };

  if (loading || !consultation) {
    return <View style={styles.container} />;
  }

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.card}>
        <Card.Content>
          <Title>Консультант</Title>
          <Paragraph style={styles.consultantName}>{consultation.consultant?.name}</Paragraph>
          <Paragraph>{consultation.consultant?.specialization}</Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Дата и время</Title>
          <Paragraph style={styles.info}>
            {new Date(consultation.date).toLocaleDateString('ru-RU', {
              day: 'numeric',
              month: 'long',
              year: 'numeric',
              hour: '2-digit',
              minute: '2-digit',
            })}
          </Paragraph>
          <Divider style={styles.divider} />
          <Title>Длительность</Title>
          <Paragraph style={styles.info}>{consultation.duration} минут</Paragraph>
        </Card.Content>
      </Card>

      {consultation.description && (
        <Card style={styles.card}>
          <Card.Content>
            <Title>Описание</Title>
            <Paragraph style={styles.description}>{consultation.description}</Paragraph>
          </Card.Content>
        </Card>
      )}

      <Card style={styles.card}>
        <Card.Content>
          <Title>Статус</Title>
          <Paragraph style={styles.info}>
            {consultation.status === 'scheduled' ? 'Запланирована' :
             consultation.status === 'completed' ? 'Завершена' :
             consultation.status === 'cancelled' ? 'Отменена' : consultation.status}
          </Paragraph>
        </Card.Content>
      </Card>

      {consultation.status === 'scheduled' && (
        <Button
          mode="contained"
          onPress={handleCancel}
          style={styles.cancelButton}
          buttonColor="#dc2626"
        >
          Отменить консультацию
        </Button>
      )}
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  card: {
    margin: spacing.md,
  },
  consultantName: {
    fontSize: 20,
    fontWeight: 'bold',
    marginTop: spacing.sm,
  },
  info: {
    fontSize: 16,
    marginTop: spacing.sm,
  },
  description: {
    marginTop: spacing.sm,
    lineHeight: 22,
  },
  divider: {
    marginVertical: spacing.md,
  },
  cancelButton: {
    margin: spacing.md,
    paddingVertical: spacing.sm,
  },
});
