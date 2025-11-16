import React, { useState } from 'react';
import { View, StyleSheet, ScrollView, Alert } from 'react-native';
import { Title, Paragraph, Button, TextInput, Card } from 'react-native-paper';
import { Calendar } from 'react-native-calendars';
import { consultationsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const BookingScreen = ({ route, navigation }: any) => {
  const { consultantId, consultant } = route.params;
  const [selectedDate, setSelectedDate] = useState('');
  const [selectedTime, setSelectedTime] = useState('');
  const [duration, setDuration] = useState('60');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const timeSlots = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00'];

  const handleBooking = async () => {
    if (!selectedDate || !selectedTime) {
      Alert.alert('Ошибка', 'Пожалуйста, выберите дату и время');
      return;
    }

    setLoading(true);
    try {
      const dateTime = `${selectedDate}T${selectedTime}:00`;
      await consultationsAPI.create({
        consultantId,
        date: dateTime,
        duration: parseInt(duration),
        description,
      });

      Alert.alert('Успешно', 'Консультация забронирована!', [
        {
          text: 'OK',
          onPress: () => navigation.navigate('ConsultationsList'),
        },
      ]);
    } catch (error: any) {
      Alert.alert('Ошибка', error.response?.data?.message || 'Не удалось забронировать консультацию');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <Card style={styles.consultantCard}>
        <Card.Content>
          <Title>{consultant?.name}</Title>
          <Paragraph>{consultant?.specialization}</Paragraph>
          <Paragraph style={styles.price}>
            {consultant?.hourlyRate || '5000'} ₽/час
          </Paragraph>
        </Card.Content>
      </Card>

      <View style={styles.section}>
        <Title style={styles.sectionTitle}>Выберите дату</Title>
        <Calendar
          onDayPress={(day: any) => setSelectedDate(day.dateString)}
          markedDates={{
            [selectedDate]: { selected: true, selectedColor: '#2563eb' },
          }}
          minDate={new Date().toISOString().split('T')[0]}
          theme={{
            selectedDayBackgroundColor: '#2563eb',
            todayTextColor: '#2563eb',
            arrowColor: '#2563eb',
          }}
        />
      </View>

      {selectedDate && (
        <View style={styles.section}>
          <Title style={styles.sectionTitle}>Выберите время</Title>
          <View style={styles.timeSlots}>
            {timeSlots.map((time) => (
              <Button
                key={time}
                mode={selectedTime === time ? 'contained' : 'outlined'}
                onPress={() => setSelectedTime(time)}
                style={styles.timeSlot}
              >
                {time}
              </Button>
            ))}
          </View>
        </View>
      )}

      <View style={styles.section}>
        <Title style={styles.sectionTitle}>Длительность (минуты)</Title>
        <View style={styles.durationButtons}>
          {['30', '60', '90', '120'].map((dur) => (
            <Button
              key={dur}
              mode={duration === dur ? 'contained' : 'outlined'}
              onPress={() => setDuration(dur)}
              style={styles.durationButton}
            >
              {dur}
            </Button>
          ))}
        </View>
      </View>

      <View style={styles.section}>
        <Title style={styles.sectionTitle}>Описание (опционально)</Title>
        <TextInput
          mode="outlined"
          multiline
          numberOfLines={4}
          value={description}
          onChangeText={setDescription}
          placeholder="Опишите тему консультации"
        />
      </View>

      <Button
        mode="contained"
        onPress={handleBooking}
        loading={loading}
        disabled={loading || !selectedDate || !selectedTime}
        style={styles.bookButton}
      >
        Забронировать
      </Button>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  consultantCard: {
    margin: spacing.md,
  },
  price: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#2563eb',
    marginTop: spacing.sm,
  },
  section: {
    padding: spacing.md,
  },
  sectionTitle: {
    fontSize: 18,
    marginBottom: spacing.md,
  },
  timeSlots: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: spacing.sm,
  },
  timeSlot: {
    marginRight: spacing.sm,
    marginBottom: spacing.sm,
  },
  durationButtons: {
    flexDirection: 'row',
    gap: spacing.sm,
  },
  durationButton: {
    flex: 1,
  },
  bookButton: {
    margin: spacing.md,
    paddingVertical: spacing.sm,
  },
});
