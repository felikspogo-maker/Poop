import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView } from 'react-native';
import { Avatar, Title, Paragraph, Button, Card, Chip } from 'react-native-paper';
import { consultantsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const ConsultantDetailScreen = ({ route, navigation }: any) => {
  const { id } = route.params;
  const [consultant, setConsultant] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadConsultant();
  }, [id]);

  const loadConsultant = async () => {
    try {
      const response = await consultantsAPI.getById(id);
      setConsultant(response.data);
    } catch (error) {
      console.error('Error loading consultant:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading || !consultant) {
    return <View style={styles.container} />;
  }

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Avatar.Text size={80} label={consultant.name?.charAt(0) || 'C'} />
        <Title style={styles.name}>{consultant.name}</Title>
        <Paragraph style={styles.specialization}>{consultant.specialization}</Paragraph>
        <View style={styles.rating}>
          <Paragraph>⭐ {consultant.rating || '5.0'}</Paragraph>
          <Paragraph style={styles.reviews}>({consultant.reviewsCount || 0} отзывов)</Paragraph>
        </View>
      </View>

      <Card style={styles.card}>
        <Card.Content>
          <Title>О специалисте</Title>
          <Paragraph>{consultant.bio || 'Опытный консультант с многолетним опытом работы.'}</Paragraph>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Специализация</Title>
          <View style={styles.chips}>
            {(consultant.skills || ['Консалтинг', 'Стратегия', 'Аналитика']).map((skill: string) => (
              <Chip key={skill} style={styles.chip}>{skill}</Chip>
            ))}
          </View>
        </Card.Content>
      </Card>

      <Card style={styles.card}>
        <Card.Content>
          <Title>Стоимость</Title>
          <Paragraph style={styles.price}>{consultant.hourlyRate || '5000'} ₽/час</Paragraph>
        </Card.Content>
      </Card>

      <Button
        mode="contained"
        onPress={() => navigation.navigate('Booking', { consultantId: id, consultant })}
        style={styles.bookButton}
      >
        Записаться на консультацию
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
  specialization: {
    fontSize: 16,
    color: '#64748b',
  },
  rating: {
    flexDirection: 'row',
    alignItems: 'center',
    marginTop: spacing.sm,
    gap: spacing.xs,
  },
  reviews: {
    color: '#64748b',
  },
  card: {
    margin: spacing.md,
  },
  chips: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
    marginTop: spacing.sm,
  },
  chip: {
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
  },
  price: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#2563eb',
    marginTop: spacing.sm,
  },
  bookButton: {
    margin: spacing.md,
    paddingVertical: spacing.sm,
  },
});
