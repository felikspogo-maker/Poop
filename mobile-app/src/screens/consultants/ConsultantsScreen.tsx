import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Searchbar, Chip, Avatar } from 'react-native-paper';
import { consultantsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const ConsultantsScreen = ({ navigation }: any) => {
  const [consultants, setConsultants] = useState([]);
  const [filteredConsultants, setFilteredConsultants] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedSpecialization, setSelectedSpecialization] = useState<string | null>(null);

  const specializations = ['Финансы', 'Маркетинг', 'HR', 'IT', 'Стратегия', 'Юридические'];

  useEffect(() => {
    loadConsultants();
  }, []);

  useEffect(() => {
    filterConsultants();
  }, [searchQuery, selectedSpecialization, consultants]);

  const loadConsultants = async () => {
    setLoading(true);
    try {
      const response = await consultantsAPI.getAll();
      setConsultants(response.data);
      setFilteredConsultants(response.data);
    } catch (error) {
      console.error('Error loading consultants:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterConsultants = () => {
    let filtered = consultants;

    if (searchQuery) {
      filtered = filtered.filter((c: any) =>
        c.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        c.specialization.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }

    if (selectedSpecialization) {
      filtered = filtered.filter((c: any) => c.specialization === selectedSpecialization);
    }

    setFilteredConsultants(filtered);
  };

  return (
    <View style={styles.container}>
      <Searchbar
        placeholder="Поиск консультантов"
        onChangeText={setSearchQuery}
        value={searchQuery}
        style={styles.searchbar}
      />

      <ScrollView
        horizontal
        showsHorizontalScrollIndicator={false}
        style={styles.specializationsScroll}
      >
        <View style={styles.specializations}>
          <Chip
            selected={selectedSpecialization === null}
            onPress={() => setSelectedSpecialization(null)}
            style={styles.chip}
          >
            Все
          </Chip>
          {specializations.map((spec) => (
            <Chip
              key={spec}
              selected={selectedSpecialization === spec}
              onPress={() => setSelectedSpecialization(spec)}
              style={styles.chip}
            >
              {spec}
            </Chip>
          ))}
        </View>
      </ScrollView>

      <ScrollView
        style={styles.list}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadConsultants} />}
      >
        {filteredConsultants.map((consultant: any) => (
          <Card
            key={consultant.id}
            style={styles.card}
            onPress={() => navigation.navigate('ConsultantDetail', { id: consultant.id })}
          >
            <Card.Content>
              <View style={styles.consultantCard}>
                <Avatar.Text size={56} label={consultant.name?.charAt(0) || 'C'} />
                <View style={styles.consultantInfo}>
                  <Title>{consultant.name}</Title>
                  <Paragraph>{consultant.specialization}</Paragraph>
                  <Paragraph style={styles.rating}>
                    ⭐ {consultant.rating || '5.0'} ({consultant.reviewsCount || 0} отзывов)
                  </Paragraph>
                </View>
              </View>
            </Card.Content>
          </Card>
        ))}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  searchbar: {
    margin: spacing.md,
    elevation: 0,
  },
  specializationsScroll: {
    maxHeight: 60,
  },
  specializations: {
    flexDirection: 'row',
    paddingHorizontal: spacing.md,
    paddingBottom: spacing.md,
    gap: spacing.sm,
  },
  chip: {
    marginRight: spacing.sm,
  },
  list: {
    flex: 1,
    padding: spacing.md,
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
  rating: {
    color: '#64748b',
    fontSize: 14,
    marginTop: spacing.xs,
  },
});
