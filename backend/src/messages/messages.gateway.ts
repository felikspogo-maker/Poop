import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
  OnGatewayConnection,
  OnGatewayDisconnect,
  UseGuards,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { MessagesService } from './messages.service';
import { WsJwtGuard } from '../auth/guards/ws-jwt.guard';
import { Logger } from '@nestjs/common';

@WebSocketGateway({
  cors: {
    origin: '*',
    credentials: true,
  },
})
@UseGuards(WsJwtGuard)
export class MessagesGateway
  implements OnGatewayConnection, OnGatewayDisconnect
{
  @WebSocketServer()
  server: Server;

  private logger = new Logger('MessagesGateway');

  constructor(private messagesService: MessagesService) {}

  async handleConnection(client: Socket) {
    try {
      const user = client.data.user;
      this.logger.log(`Client connected: ${client.id}, User: ${user?.sub}`);
    } catch (error) {
      this.logger.error('Connection error:', error.message);
      client.disconnect();
    }
  }

  handleDisconnect(client: Socket) {
    this.logger.log(`Client disconnected: ${client.id}`);
  }

  @SubscribeMessage('joinConversation')
  handleJoinConversation(
    @MessageBody() conversationId: string,
    @ConnectedSocket() client: Socket,
  ) {
    client.join(conversationId);
    const user = client.data.user;
    this.logger.log(
      `User ${user.sub} joined conversation ${conversationId}`,
    );
    return { event: 'joinedConversation', data: conversationId };
  }

  @SubscribeMessage('sendMessage')
  async handleSendMessage(
    @MessageBody()
    data: {
      conversationId: string;
      senderId: string;
      receiverId: string;
      content: string;
    },
    @ConnectedSocket() client: Socket,
  ) {
    const user = client.data.user;

    // Verify sender is the authenticated user
    if (data.senderId !== user.sub) {
      return {
        event: 'error',
        data: { message: 'Sender ID does not match authenticated user' },
      };
    }

    const message = await this.messagesService.sendMessage(data);

    // Broadcast to all clients in the conversation
    this.server.to(data.conversationId).emit('newMessage', message);

    return { event: 'messageSent', data: message };
  }

  @SubscribeMessage('typing')
  handleTyping(
    @MessageBody() data: { conversationId: string },
    @ConnectedSocket() client: Socket,
  ) {
    const user = client.data.user;
    client.to(data.conversationId).emit('userTyping', {
      conversationId: data.conversationId,
      userId: user.sub,
    });
  }
}
