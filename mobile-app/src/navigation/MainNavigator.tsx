import React from 'react';
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs';
import { createStackNavigator } from '@react-navigation/stack';
import Icon from 'react-native-vector-icons/MaterialCommunityIcons';

// Screens
import { HomeScreen } from '../screens/home/HomeScreen';
import { ConsultantsScreen } from '../screens/consultants/ConsultantsScreen';
import { ConsultantDetailScreen } from '../screens/consultants/ConsultantDetailScreen';
import { BookingScreen } from '../screens/booking/BookingScreen';
import { ConsultationsScreen } from '../screens/consultations/ConsultationsScreen';
import { ConsultationDetailScreen } from '../screens/consultations/ConsultationDetailScreen';
import { ChatScreen } from '../screens/chat/ChatScreen';
import { ConversationScreen } from '../screens/chat/ConversationScreen';
import { ProfileScreen } from '../screens/profile/ProfileScreen';
import { DocumentsScreen } from '../screens/documents/DocumentsScreen';

const Tab = createBottomTabNavigator();
const HomeStack = createStackNavigator();
const ConsultantsStack = createStackNavigator();
const ConsultationsStack = createStackNavigator();
const ChatStack = createStackNavigator();
const ProfileStack = createStackNavigator();

const HomeStackNavigator = () => (
  <HomeStack.Navigator>
    <HomeStack.Screen name="HomeMain" component={HomeScreen} options={{ title: 'Главная' }} />
  </HomeStack.Navigator>
);

const ConsultantsStackNavigator = () => (
  <ConsultantsStack.Navigator>
    <ConsultantsStack.Screen name="ConsultantsList" component={ConsultantsScreen} options={{ title: 'Консультанты' }} />
    <ConsultantsStack.Screen name="ConsultantDetail" component={ConsultantDetailScreen} options={{ title: 'Детали' }} />
    <ConsultantsStack.Screen name="Booking" component={BookingScreen} options={{ title: 'Бронирование' }} />
  </ConsultantsStack.Navigator>
);

const ConsultationsStackNavigator = () => (
  <ConsultationsStack.Navigator>
    <ConsultationsStack.Screen name="ConsultationsList" component={ConsultationsScreen} options={{ title: 'Консультации' }} />
    <ConsultationsStack.Screen name="ConsultationDetail" component={ConsultationDetailScreen} options={{ title: 'Детали' }} />
  </ConsultationsStack.Navigator>
);

const ChatStackNavigator = () => (
  <ChatStack.Navigator>
    <ChatStack.Screen name="ChatList" component={ChatScreen} options={{ title: 'Чат' }} />
    <ChatStack.Screen name="Conversation" component={ConversationScreen} options={{ title: 'Беседа' }} />
  </ChatStack.Navigator>
);

const ProfileStackNavigator = () => (
  <ProfileStack.Navigator>
    <ProfileStack.Screen name="ProfileMain" component={ProfileScreen} options={{ title: 'Профиль' }} />
    <ProfileStack.Screen name="Documents" component={DocumentsScreen} options={{ title: 'Документы' }} />
  </ProfileStack.Navigator>
);

export const MainNavigator = () => {
  return (
    <Tab.Navigator
      screenOptions={{
        headerShown: false,
        tabBarActiveTintColor: '#2563eb',
        tabBarInactiveTintColor: '#64748b',
      }}
    >
      <Tab.Screen
        name="Home"
        component={HomeStackNavigator}
        options={{
          tabBarLabel: 'Главная',
          tabBarIcon: ({ color, size }) => <Icon name="home" size={size} color={color} />,
        }}
      />
      <Tab.Screen
        name="Consultants"
        component={ConsultantsStackNavigator}
        options={{
          tabBarLabel: 'Консультанты',
          tabBarIcon: ({ color, size }) => <Icon name="account-group" size={size} color={color} />,
        }}
      />
      <Tab.Screen
        name="Consultations"
        component={ConsultationsStackNavigator}
        options={{
          tabBarLabel: 'Записи',
          tabBarIcon: ({ color, size }) => <Icon name="calendar-clock" size={size} color={color} />,
        }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatStackNavigator}
        options={{
          tabBarLabel: 'Чат',
          tabBarIcon: ({ color, size }) => <Icon name="message-text" size={size} color={color} />,
        }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStackNavigator}
        options={{
          tabBarLabel: 'Профиль',
          tabBarIcon: ({ color, size }) => <Icon name="account" size={size} color={color} />,
        }}
      />
    </Tab.Navigator>
  );
};
