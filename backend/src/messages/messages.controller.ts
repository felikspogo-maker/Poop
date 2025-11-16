import { Controller, Get, Post, Body, Param, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { MessagesService } from './messages.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@ApiTags('Messages')
@Controller('messages')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class MessagesController {
  constructor(private readonly messagesService: MessagesService) {}

  @Get('conversations')
  @ApiOperation({ summary: 'Get all conversations' })
  async getConversations(@CurrentUser() user: any) {
    return this.messagesService.getConversations(user.id);
  }

  @Get(':conversationId')
  @ApiOperation({ summary: 'Get messages in conversation' })
  async getMessages(@Param('conversationId') conversationId: string) {
    return this.messagesService.getMessages(conversationId);
  }

  @Post()
  @ApiOperation({ summary: 'Send message' })
  async sendMessage(
    @CurrentUser() user: any,
    @Body() data: { conversationId: string; receiverId: string; content: string },
  ) {
    return this.messagesService.sendMessage({
      conversationId: data.conversationId,
      senderId: user.id,
      receiverId: data.receiverId,
      content: data.content,
    });
  }

  @Post('conversations')
  @ApiOperation({ summary: 'Create conversation' })
  async createConversation(
    @CurrentUser() user: any,
    @Body() data: { participantId: string },
  ) {
    return this.messagesService.createConversation([user.id, data.participantId]);
  }
}
