import {
  WebSocketGateway,
  WebSocketServer,
  SubscribeMessage,
  MessageBody,
  ConnectedSocket,
} from '@nestjs/websockets';
import { Server, Socket } from 'socket.io';
import { MessagesService } from './messages.service';

@WebSocketGateway({
  cors: {
    origin: '*',
  },
})
export class MessagesGateway {
  @WebSocketServer()
  server: Server;

  constructor(private messagesService: MessagesService) {}

  @SubscribeMessage('joinConversation')
  handleJoinConversation(
    @MessageBody() conversationId: string,
    @ConnectedSocket() client: Socket,
  ) {
    client.join(conversationId);
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
    const message = await this.messagesService.sendMessage(data);

    // Broadcast to all clients in the conversation
    this.server.to(data.conversationId).emit('newMessage', message);

    return { event: 'messageSent', data: message };
  }

  @SubscribeMessage('typing')
  handleTyping(
    @MessageBody() data: { conversationId: string; userId: string },
    @ConnectedSocket() client: Socket,
  ) {
    client.to(data.conversationId).emit('userTyping', data);
  }
}
