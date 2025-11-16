import { IsEmail, IsString, MinLength } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class RegisterDto {
  @ApiProperty({ example: 'user@example.com' })
  @IsEmail()
  email: string;

  @ApiProperty({ example: 'password123', minLength: 6 })
  @IsString()
  @MinLength(6)
  password: string;

  @ApiProperty({ example: 'Иван' })
  @IsString()
  firstName: string;

  @ApiProperty({ example: 'Иванов' })
  @IsString()
  lastName: string;

  @ApiProperty({ example: '+79001234567' })
  @IsString()
  phone: string;
}
