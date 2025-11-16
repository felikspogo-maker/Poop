import {
  IsNotEmpty,
  IsString,
  IsInt,
  Min,
  Max,
  IsOptional,
  IsArray,
  MaxLength,
  MinLength,
} from 'class-validator';
import { ApiProperty, ApiPropertyOptional } from '@nestjs/swagger';

export class CreateConsultantDto {
  @ApiProperty({
    description: 'User ID who will become a consultant',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @IsNotEmpty({ message: 'User ID is required' })
  @IsString({ message: 'User ID must be a string' })
  userId: string;

  @ApiProperty({
    description: 'Consultant specialization',
    example: 'Бизнес-стратегия',
  })
  @IsNotEmpty({ message: 'Specialization is required' })
  @IsString({ message: 'Specialization must be a string' })
  @MinLength(3, { message: 'Specialization must be at least 3 characters' })
  @MaxLength(100, { message: 'Specialization must not exceed 100 characters' })
  specialization: string;

  @ApiProperty({
    description: 'Consultant bio/description',
    example: 'Опытный консультант по бизнес-стратегии с 10+ летним опытом...',
  })
  @IsNotEmpty({ message: 'Bio is required' })
  @IsString({ message: 'Bio must be a string' })
  @MinLength(50, { message: 'Bio must be at least 50 characters' })
  @MaxLength(1000, { message: 'Bio must not exceed 1000 characters' })
  bio: string;

  @ApiProperty({
    description: 'Years of experience',
    example: 10,
    minimum: 0,
    maximum: 50,
  })
  @IsNotEmpty({ message: 'Experience is required' })
  @IsInt({ message: 'Experience must be an integer' })
  @Min(0, { message: 'Experience cannot be negative' })
  @Max(50, { message: 'Experience cannot exceed 50 years' })
  experience: number;

  @ApiProperty({
    description: 'Hourly rate in rubles',
    example: 5000,
    minimum: 500,
    maximum: 50000,
  })
  @IsNotEmpty({ message: 'Rate is required' })
  @IsInt({ message: 'Rate must be an integer' })
  @Min(500, { message: 'Rate must be at least 500 rubles' })
  @Max(50000, { message: 'Rate cannot exceed 50000 rubles' })
  rate: number;

  @ApiPropertyOptional({
    description: 'Array of services offered',
    example: ['Бизнес-анализ', 'Стратегическое планирование', 'Консалтинг'],
  })
  @IsOptional()
  @IsArray({ message: 'Services must be an array' })
  @IsString({ each: true, message: 'Each service must be a string' })
  services?: string[];

  @ApiPropertyOptional({
    description: 'Array of certifications',
    example: ['MBA', 'PMP', 'Six Sigma Black Belt'],
  })
  @IsOptional()
  @IsArray({ message: 'Certifications must be an array' })
  @IsString({ each: true, message: 'Each certification must be a string' })
  certifications?: string[];
}
