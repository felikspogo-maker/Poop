import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Chip, FAB } from 'react-native-paper';
import { consultationsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const ConsultationsScreen = ({ navigation }: any) => {
  const [consultations, setConsultations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConsultations();
  }, []);

  const loadConsultations = async () => {
    setLoading(true);
    try {
      const response = await consultationsAPI.getAll();
      setConsultations(response.data);
    } catch (error) {
      console.error('Error loading consultations:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'scheduled':
        return '#2563eb';
      case 'completed':
        return '#16a34a';
      case 'cancelled':
        return '#dc2626';
      default:
        return '#64748b';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'scheduled':
        return 'Запланирована';
      case 'completed':
        return 'Завершена';
      case 'cancelled':
        return 'Отменена';
      default:
        return status;
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        style={styles.list}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadConsultations} />}
      >
        {consultations.length > 0 ? (
          consultations.map((consultation: any) => (
            <Card
              key={consultation.id}
              style={styles.card}
              onPress={() => navigation.navigate('ConsultationDetail', { id: consultation.id })}
            >
              <Card.Content>
                <View style={styles.header}>
                  <Title style={styles.title}>{consultation.consultant?.name}</Title>
                  <Chip
                    style={[styles.statusChip, { backgroundColor: getStatusColor(consultation.status) }]}
                    textStyle={styles.statusText}
                  >
                    {getStatusText(consultation.status)}
                  </Chip>
                </View>
                <Paragraph style={styles.date}>
                  {new Date(consultation.date).toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Paragraph>
                <Paragraph style={styles.duration}>Длительность: {consultation.duration} мин</Paragraph>
                {consultation.description && (
                  <Paragraph style={styles.description} numberOfLines={2}>
                    {consultation.description}
                  </Paragraph>
                )}
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Paragraph style={styles.emptyText}>У вас пока нет консультаций</Paragraph>
            </Card.Content>
          </Card>
        )}
      </ScrollView>

      <FAB
        icon="plus"
        style={styles.fab}
        onPress={() => navigation.navigate('Consultants')}
      />
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  list: {
    flex: 1,
    padding: spacing.md,
  },
  card: {
    marginBottom: spacing.md,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: spacing.sm,
  },
  title: {
    flex: 1,
    fontSize: 18,
  },
  statusChip: {
    height: 28,
  },
  statusText: {
    color: 'white',
    fontSize: 12,
  },
  date: {
    color: '#64748b',
    marginBottom: spacing.xs,
  },
  duration: {
    color: '#64748b',
    fontSize: 14,
  },
  description: {
    marginTop: spacing.sm,
    fontStyle: 'italic',
  },
  emptyCard: {
    marginTop: spacing.xl,
  },
  emptyText: {
    textAlign: 'center',
    color: '#64748b',
  },
  fab: {
    position: 'absolute',
    margin: spacing.md,
    right: 0,
    bottom: 0,
    backgroundColor: '#2563eb',
  },
});
