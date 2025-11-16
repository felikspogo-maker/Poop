import React, { useEffect, useState, useRef } from 'react';
import { View, StyleSheet, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { TextInput, IconButton, Card, Paragraph } from 'react-native-paper';
import { messagesAPI } from '../../services/api';
import { useAuth } from '../../contexts/AuthContext';
import { spacing } from '../../utils/theme';
import io from 'socket.io-client';

export const ConversationScreen = ({ route }: any) => {
  const { id } = route.params;
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const flatListRef = useRef<FlatList>(null);
  const socketRef = useRef<any>(null);

  useEffect(() => {
    loadMessages();
    connectSocket();

    return () => {
      if (socketRef.current) {
        socketRef.current.disconnect();
      }
    };
  }, [id]);

  const connectSocket = () => {
    socketRef.current = io('http://localhost:3000');
    socketRef.current.emit('joinConversation', id);

    socketRef.current.on('newMessage', (message: any) => {
      setMessages((prev) => [...prev, message]);
    });
  };

  const loadMessages = async () => {
    setLoading(true);
    try {
      const response = await messagesAPI.getMessages(id);
      setMessages(response.data);
    } catch (error) {
      console.error('Error loading messages:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSend = async () => {
    if (!newMessage.trim()) return;

    const messageText = newMessage;
    setNewMessage('');

    try {
      await messagesAPI.sendMessage(id, messageText);
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const renderMessage = ({ item }: any) => {
    const isMyMessage = item.senderId === user?.id;

    return (
      <View
        style={[
          styles.messageContainer,
          isMyMessage ? styles.myMessageContainer : styles.otherMessageContainer,
        ]}
      >
        <Card style={[styles.message, isMyMessage ? styles.myMessage : styles.otherMessage]}>
          <Card.Content style={styles.messageContent}>
            <Paragraph style={isMyMessage ? styles.myMessageText : styles.otherMessageText}>
              {item.content}
            </Paragraph>
            <Paragraph style={styles.messageTime}>
              {new Date(item.createdAt).toLocaleTimeString('ru-RU', {
                hour: '2-digit',
                minute: '2-digit',
              })}
            </Paragraph>
          </Card.Content>
        </Card>
      </View>
    );
  };

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      keyboardVerticalOffset={90}
    >
      <FlatList
        ref={flatListRef}
        data={messages}
        renderItem={renderMessage}
        keyExtractor={(item) => item.id}
        contentContainerStyle={styles.messagesList}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
      />

      <View style={styles.inputContainer}>
        <TextInput
          mode="outlined"
          placeholder="Написать сообщение..."
          value={newMessage}
          onChangeText={setNewMessage}
          style={styles.input}
          right={
            <TextInput.Icon
              icon="send"
              onPress={handleSend}
              disabled={!newMessage.trim()}
            />
          }
        />
      </View>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8fafc',
  },
  messagesList: {
    padding: spacing.md,
  },
  messageContainer: {
    marginBottom: spacing.md,
    maxWidth: '80%',
  },
  myMessageContainer: {
    alignSelf: 'flex-end',
  },
  otherMessageContainer: {
    alignSelf: 'flex-start',
  },
  message: {
    elevation: 1,
  },
  myMessage: {
    backgroundColor: '#2563eb',
  },
  otherMessage: {
    backgroundColor: 'white',
  },
  messageContent: {
    padding: spacing.sm,
  },
  myMessageText: {
    color: 'white',
  },
  otherMessageText: {
    color: '#0f172a',
  },
  messageTime: {
    fontSize: 11,
    color: '#94a3b8',
    marginTop: spacing.xs,
  },
  inputContainer: {
    padding: spacing.md,
    backgroundColor: 'white',
    borderTopWidth: 1,
    borderTopColor: '#e2e8f0',
  },
  input: {
    backgroundColor: 'white',
  },
});
