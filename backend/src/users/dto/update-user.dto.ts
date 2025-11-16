import { IsOptional, IsString, MinLength, MaxLength, Matches } from 'class-validator';
import { ApiPropertyOptional } from '@nestjs/swagger';

export class UpdateUserDto {
  @ApiPropertyOptional({
    description: 'First name of the user',
    example: 'Иван',
    minLength: 2,
    maxLength: 50,
  })
  @IsOptional()
  @IsString({ message: 'First name must be a string' })
  @MinLength(2, { message: 'First name must be at least 2 characters' })
  @MaxLength(50, { message: 'First name cannot exceed 50 characters' })
  firstName?: string;

  @ApiPropertyOptional({
    description: 'Last name of the user',
    example: 'Петров',
    minLength: 2,
    maxLength: 50,
  })
  @IsOptional()
  @IsString({ message: 'Last name must be a string' })
  @MinLength(2, { message: 'Last name must be at least 2 characters' })
  @MaxLength(50, { message: 'Last name cannot exceed 50 characters' })
  lastName?: string;

  @ApiPropertyOptional({
    description: 'Phone number in Russian format',
    example: '+79001234567',
  })
  @IsOptional()
  @IsString({ message: 'Phone must be a string' })
  @Matches(/^(\+7|8)?\d{10}$/, {
    message: 'Phone number must be in Russian format',
  })
  phone?: string;

  @ApiPropertyOptional({
    description: 'Avatar URL',
    example: 'https://example.com/avatar.jpg',
  })
  @IsOptional()
  @IsString({ message: 'Avatar must be a string' })
  avatar?: string;
}
