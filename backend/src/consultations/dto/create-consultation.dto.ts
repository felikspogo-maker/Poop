import { IsNotEmpty, IsString, IsInt, Min, Max, IsDateString, IsOptional, MaxLength } from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateConsultationDto {
  @ApiProperty({
    description: 'ID of the consultant',
    example: 'uuid-consultant-id',
  })
  @IsNotEmpty({ message: 'Consultant ID is required' })
  @IsString({ message: 'Consultant ID must be a string' })
  consultantId: string;

  @ApiProperty({
    description: 'Date and time of the consultation',
    example: '2024-12-25T10:00:00.000Z',
  })
  @IsNotEmpty({ message: 'Date is required' })
  @IsDateString({}, { message: 'Date must be a valid ISO 8601 date string' })
  date: string;

  @ApiProperty({
    description: 'Duration of the consultation in minutes',
    example: 60,
    minimum: 30,
    maximum: 240,
  })
  @IsNotEmpty({ message: 'Duration is required' })
  @IsInt({ message: 'Duration must be an integer' })
  @Min(30, { message: 'Duration must be at least 30 minutes' })
  @Max(240, { message: 'Duration cannot exceed 240 minutes' })
  duration: number;

  @ApiPropertyOptional({
    description: 'Description or notes about the consultation',
    example: 'Discussion about financial planning for startup',
    maxLength: 500,
  })
  @IsOptional()
  @IsString({ message: 'Description must be a string' })
  @MaxLength(500, { message: 'Description cannot exceed 500 characters' })
  description?: string;
}
