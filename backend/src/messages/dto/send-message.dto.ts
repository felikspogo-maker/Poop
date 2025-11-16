import {
  IsNotEmpty,
  IsString,
  IsArray,
  MinLength,
  MaxLength,
} from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class SendMessageDto {
  @ApiProperty({
    description: 'Conversation ID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @IsNotEmpty({ message: 'Conversation ID is required' })
  @IsString({ message: 'Conversation ID must be a string' })
  conversationId: string;

  @ApiProperty({
    description: 'Sender user ID',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @IsNotEmpty({ message: 'Sender ID is required' })
  @IsString({ message: 'Sender ID must be a string' })
  senderId: string;

  @ApiProperty({
    description: 'Receiver user ID',
    example: '550e8400-e29b-41d4-a716-446655440001',
  })
  @IsNotEmpty({ message: 'Receiver ID is required' })
  @IsString({ message: 'Receiver ID must be a string' })
  receiverId: string;

  @ApiProperty({
    description: 'Message content',
    example: 'Здравствуйте! Я хотел бы обсудить консультацию...',
  })
  @IsNotEmpty({ message: 'Content is required' })
  @IsString({ message: 'Content must be a string' })
  @MinLength(1, { message: 'Content cannot be empty' })
  @MaxLength(5000, { message: 'Content must not exceed 5000 characters' })
  content: string;
}

export class CreateConversationDto {
  @ApiProperty({
    description: 'Array of participant user IDs',
    example: [
      '550e8400-e29b-41d4-a716-446655440000',
      '550e8400-e29b-41d4-a716-446655440001',
    ],
  })
  @IsNotEmpty({ message: 'Participant IDs are required' })
  @IsArray({ message: 'Participant IDs must be an array' })
  @IsString({ each: true, message: 'Each participant ID must be a string' })
  participantIds: string[];
}
