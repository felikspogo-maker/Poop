import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Button, Text, Avatar } from 'react-native-paper';
import { useAuth } from '../../contexts/AuthContext';
import { consultationsAPI, consultantsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const HomeScreen = ({ navigation }: any) => {
  const { user } = useAuth();
  const [upcomingConsultations, setUpcomingConsultations] = useState([]);
  const [featuredConsultants, setFeaturedConsultants] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [consultationsRes, consultantsRes] = await Promise.all([
        consultationsAPI.getAll(),
        consultantsAPI.getAll(),
      ]);
      setUpcomingConsultations(consultationsRes.data.slice(0, 3));
      setFeaturedConsultants(consultantsRes.data.slice(0, 3));
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView
      style={styles.container}
      refreshControl={<RefreshControl refreshing={loading} onRefresh={loadData} />}
    >
      <View style={styles.header}>
        <Title style={styles.greeting}>
          Привет, {user?.firstName}!
        </Title>
        <Paragraph style={styles.subtitle}>
          Добро пожаловать в Business Consulting
        </Paragraph>
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Быстрые действия</Text>
        </View>
        <View style={styles.quickActions}>
          <Card style={styles.actionCard} onPress={() => navigation.navigate('Consultants')}>
            <Card.Content style={styles.actionContent}>
              <Avatar.Icon size={48} icon="account-search" style={styles.actionIcon} />
              <Text style={styles.actionText}>Найти консультанта</Text>
            </Card.Content>
          </Card>
          <Card style={styles.actionCard} onPress={() => navigation.navigate('Consultations')}>
            <Card.Content style={styles.actionContent}>
              <Avatar.Icon size={48} icon="calendar" style={styles.actionIcon} />
              <Text style={styles.actionText}>Мои записи</Text>
            </Card.Content>
          </Card>
        </View>
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Предстоящие консультации</Text>
          <Button mode="text" onPress={() => navigation.navigate('Consultations')}>
            Все
          </Button>
        </View>
        {upcomingConsultations.length > 0 ? (
          upcomingConsultations.map((consultation: any) => (
            <Card key={consultation.id} style={styles.card}>
              <Card.Content>
                <Title>{consultation.consultant?.name}</Title>
                <Paragraph>
                  {new Date(consultation.date).toLocaleDateString('ru-RU', {
                    day: 'numeric',
                    month: 'long',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </Paragraph>
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.card}>
            <Card.Content>
              <Paragraph>У вас нет предстоящих консультаций</Paragraph>
            </Card.Content>
          </Card>
        )}
      </View>

      <View style={styles.section}>
        <View style={styles.sectionHeader}>
          <Text style={styles.sectionTitle}>Рекомендуемые консультанты</Text>
          <Button mode="text" onPress={() => navigation.navigate('Consultants')}>
            Все
          </Button>
        </View>
        {featuredConsultants.map((consultant: any) => (
          <Card
            key={consultant.id}
            style={styles.card}
            onPress={() =>
              navigation.navigate('Consultants', {
                screen: 'ConsultantDetail',
                params: { id: consultant.id },
              })
            }
          >
            <Card.Content>
              <View style={styles.consultantCard}>
                <Avatar.Text size={48} label={consultant.name?.charAt(0) || 'C'} />
                <View style={styles.consultantInfo}>
                  <Title>{consultant.name}</Title>
                  <Paragraph>{consultant.specialization}</Paragraph>
                </View>
              </View>
            </Card.Content>
          </Card>
        ))}
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  header: {
    padding: spacing.lg,
    backgroundColor: '#2563eb',
    paddingTop: spacing.xl,
  },
  greeting: {
    fontSize: 28,
    fontWeight: 'bold',
    color: 'white',
  },
  subtitle: {
    fontSize: 16,
    color: 'rgba(255, 255, 255, 0.9)',
  },
  section: {
    padding: spacing.lg,
  },
  sectionHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: spacing.md,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
  },
  quickActions: {
    flexDirection: 'row',
    gap: spacing.md,
  },
  actionCard: {
    flex: 1,
  },
  actionContent: {
    alignItems: 'center',
    padding: spacing.md,
  },
  actionIcon: {
    backgroundColor: '#2563eb',
    marginBottom: spacing.sm,
  },
  actionText: {
    fontSize: 14,
    textAlign: 'center',
  },
  card: {
    marginBottom: spacing.md,
  },
  consultantCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  consultantInfo: {
    flex: 1,
  },
});
