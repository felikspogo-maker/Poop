import {
  IsNotEmpty,
  IsString,
  IsInt,
  Min,
  Max,
  IsOptional,
  MaxLength,
} from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateReviewDto {
  @ApiProperty({
    description: 'Consultant ID to review',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @IsNotEmpty({ message: 'Consultant ID is required' })
  @IsString({ message: 'Consultant ID must be a string' })
  consultantId: string;

  @ApiProperty({
    description: 'Rating from 1 to 5 stars',
    example: 5,
    minimum: 1,
    maximum: 5,
  })
  @IsNotEmpty({ message: 'Rating is required' })
  @IsInt({ message: 'Rating must be an integer' })
  @Min(1, { message: 'Rating must be at least 1' })
  @Max(5, { message: 'Rating cannot exceed 5' })
  rating: number;

  @ApiPropertyOptional({
    description: 'Review comment',
    example: 'Отличный консультант! Очень помог с бизнес-стратегией.',
  })
  @IsOptional()
  @IsString({ message: 'Comment must be a string' })
  @MaxLength(1000, { message: 'Comment must not exceed 1000 characters' })
  comment?: string;
}
