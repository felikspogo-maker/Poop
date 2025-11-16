import { IsNotEmpty, IsString, IsInt, Min, Max } from 'class-validator';
import { ApiProperty } from '@nestjs/swagger';

export class CreatePaymentIntentDto {
  @ApiProperty({
    description: 'Payment amount in rubles',
    example: 5000,
    minimum: 100,
    maximum: 1000000,
  })
  @IsNotEmpty({ message: 'Amount is required' })
  @IsInt({ message: 'Amount must be an integer' })
  @Min(100, { message: 'Amount must be at least 100 rubles' })
  @Max(1000000, { message: 'Amount cannot exceed 1000000 rubles' })
  amount: number;

  @ApiProperty({
    description: 'Consultation ID for this payment',
    example: '550e8400-e29b-41d4-a716-446655440000',
  })
  @IsNotEmpty({ message: 'Consultation ID is required' })
  @IsString({ message: 'Consultation ID must be a string' })
  consultationId: string;
}

export class ConfirmPaymentDto {
  @ApiProperty({
    description: 'Stripe payment intent ID',
    example: 'pi_3K1...',
  })
  @IsNotEmpty({ message: 'Payment intent ID is required' })
  @IsString({ message: 'Payment intent ID must be a string' })
  paymentIntentId: string;
}
