import { Injectable } from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';

@Injectable()
export class MessagesService {
  constructor(private prisma: PrismaService) {}

  async getConversations(userId: string) {
    const conversations = await this.prisma.conversation.findMany({
      where: {
        participants: {
          some: { id: userId },
        },
      },
      include: {
        participants: {
          where: {
            id: { not: userId },
          },
          select: {
            id: true,
            firstName: true,
            lastName: true,
            avatar: true,
          },
        },
        messages: {
          orderBy: { createdAt: 'desc' },
          take: 1,
        },
      },
    });

    return conversations.map((conv) => ({
      id: conv.id,
      otherUser: conv.participants[0],
      lastMessage: conv.messages[0],
      unreadCount: 0, // TODO: Calculate unread count
    }));
  }

  async getMessages(conversationId: string) {
    return this.prisma.message.findMany({
      where: { conversationId },
      orderBy: { createdAt: 'asc' },
      include: {
        sender: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            avatar: true,
          },
        },
      },
    });
  }

  async sendMessage(data: {
    conversationId: string;
    senderId: string;
    receiverId: string;
    content: string;
  }) {
    return this.prisma.message.create({
      data: {
        conversationId: data.conversationId,
        senderId: data.senderId,
        receiverId: data.receiverId,
        content: data.content,
      },
      include: {
        sender: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            avatar: true,
          },
        },
      },
    });
  }

  async createConversation(participantIds: string[]) {
    return this.prisma.conversation.create({
      data: {
        participants: {
          connect: participantIds.map((id) => ({ id })),
        },
      },
      include: {
        participants: true,
      },
    });
  }
}
