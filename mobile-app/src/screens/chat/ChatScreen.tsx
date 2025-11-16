import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl } from 'react-native';
import { Card, Title, Paragraph, Avatar, Badge } from 'react-native-paper';
import { messagesAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const ChatScreen = ({ navigation }: any) => {
  const [conversations, setConversations] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConversations();
  }, []);

  const loadConversations = async () => {
    setLoading(true);
    try {
      const response = await messagesAPI.getConversations();
      setConversations(response.data);
    } catch (error) {
      console.error('Error loading conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadConversations} />}
      >
        {conversations.length > 0 ? (
          conversations.map((conversation: any) => (
            <Card
              key={conversation.id}
              style={styles.card}
              onPress={() => navigation.navigate('Conversation', { id: conversation.id })}
            >
              <Card.Content>
                <View style={styles.conversationCard}>
                  <Avatar.Text size={48} label={conversation.otherUser?.name?.charAt(0) || 'U'} />
                  <View style={styles.conversationInfo}>
                    <View style={styles.header}>
                      <Title style={styles.name}>{conversation.otherUser?.name}</Title>
                      {conversation.unreadCount > 0 && (
                        <Badge style={styles.badge}>{conversation.unreadCount}</Badge>
                      )}
                    </View>
                    <Paragraph numberOfLines={1} style={styles.lastMessage}>
                      {conversation.lastMessage?.content || 'Нет сообщений'}
                    </Paragraph>
                    <Paragraph style={styles.time}>
                      {conversation.lastMessage?.createdAt
                        ? new Date(conversation.lastMessage.createdAt).toLocaleTimeString('ru-RU', {
                            hour: '2-digit',
                            minute: '2-digit',
                          })
                        : ''}
                    </Paragraph>
                  </View>
                </View>
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Paragraph style={styles.emptyText}>У вас пока нет сообщений</Paragraph>
            </Card.Content>
          </Card>
        )}
      </ScrollView>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  card: {
    marginHorizontal: spacing.md,
    marginVertical: spacing.sm,
  },
  conversationCard: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.md,
  },
  conversationInfo: {
    flex: 1,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  name: {
    fontSize: 16,
  },
  badge: {
    backgroundColor: '#2563eb',
  },
  lastMessage: {
    color: '#64748b',
    fontSize: 14,
  },
  time: {
    color: '#94a3b8',
    fontSize: 12,
    marginTop: spacing.xs,
  },
  emptyCard: {
    margin: spacing.xl,
  },
  emptyText: {
    textAlign: 'center',
    color: '#64748b',
  },
});
