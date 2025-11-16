import React, { useEffect, useState } from 'react';
import { View, StyleSheet, ScrollView, RefreshControl, Alert } from 'react-native';
import { Card, Title, Paragraph, IconButton, FAB } from 'react-native-paper';
import DocumentPicker from 'react-native-document-picker';
import { documentsAPI } from '../../services/api';
import { spacing } from '../../utils/theme';

export const DocumentsScreen = () => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDocuments();
  }, []);

  const loadDocuments = async () => {
    setLoading(true);
    try {
      const response = await documentsAPI.getAll();
      setDocuments(response.data);
    } catch (error) {
      console.error('Error loading documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = async () => {
    try {
      const result = await DocumentPicker.pick({
        type: [DocumentPicker.types.allFiles],
      });

      const formData = new FormData();
      formData.append('file', {
        uri: result[0].uri,
        type: result[0].type,
        name: result[0].name,
      } as any);

      await documentsAPI.upload(formData);
      Alert.alert('Успешно', 'Документ загружен');
      loadDocuments();
    } catch (error: any) {
      if (!DocumentPicker.isCancel(error)) {
        Alert.alert('Ошибка', 'Не удалось загрузить документ');
      }
    }
  };

  const handleDelete = (id: string, name: string) => {
    Alert.alert('Удалить документ', `Вы уверены, что хотите удалить "${name}"?`, [
      { text: 'Отмена', style: 'cancel' },
      {
        text: 'Удалить',
        style: 'destructive',
        onPress: async () => {
          try {
            await documentsAPI.delete(id);
            Alert.alert('Успешно', 'Документ удален');
            loadDocuments();
          } catch (error) {
            Alert.alert('Ошибка', 'Не удалось удалить документ');
          }
        },
      },
    ]);
  };

  const getFileIcon = (type: string) => {
    if (type?.includes('pdf')) return 'file-pdf-box';
    if (type?.includes('image')) return 'file-image';
    if (type?.includes('word') || type?.includes('document')) return 'file-word';
    if (type?.includes('excel') || type?.includes('spreadsheet')) return 'file-excel';
    return 'file-document';
  };

  return (
    <View style={styles.container}>
      <ScrollView
        refreshControl={<RefreshControl refreshing={loading} onRefresh={loadDocuments} />}
      >
        {documents.length > 0 ? (
          documents.map((doc: any) => (
            <Card key={doc.id} style={styles.card}>
              <Card.Content>
                <View style={styles.documentCard}>
                  <IconButton icon={getFileIcon(doc.type)} size={40} />
                  <View style={styles.documentInfo}>
                    <Title style={styles.documentName}>{doc.name}</Title>
                    <Paragraph style={styles.documentDate}>
                      {new Date(doc.createdAt).toLocaleDateString('ru-RU')}
                    </Paragraph>
                    <Paragraph style={styles.documentSize}>
                      {(doc.size / 1024).toFixed(2)} KB
                    </Paragraph>
                  </View>
                  <View style={styles.actions}>
                    <IconButton
                      icon="download"
                      onPress={() => {}}
                    />
                    <IconButton
                      icon="delete"
                      iconColor="#dc2626"
                      onPress={() => handleDelete(doc.id, doc.name)}
                    />
                  </View>
                </View>
              </Card.Content>
            </Card>
          ))
        ) : (
          <Card style={styles.emptyCard}>
            <Card.Content>
              <Paragraph style={styles.emptyText}>У вас пока нет документов</Paragraph>
            </Card.Content>
          </Card>
        )}
      </ScrollView>

      <FAB
        icon="upload"
        style={styles.fab}
        onPress={handleUpload}
      />
    </View>
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
  documentCard: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  documentInfo: {
    flex: 1,
  },
  documentName: {
    fontSize: 16,
  },
  documentDate: {
    fontSize: 14,
    color: '#64748b',
  },
  documentSize: {
    fontSize: 12,
    color: '#94a3b8',
  },
  actions: {
    flexDirection: 'row',
  },
  emptyCard: {
    margin: spacing.xl,
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
