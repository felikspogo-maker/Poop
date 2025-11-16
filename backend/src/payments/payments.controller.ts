import { Controller, Post, Get, Body, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { PaymentsService } from './payments.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@ApiTags('Payments')
@Controller('payments')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class PaymentsController {
  constructor(private readonly paymentsService: PaymentsService) {}

  @Post('create-intent')
  @ApiOperation({ summary: 'Create payment intent' })
  async createPaymentIntent(
    @CurrentUser() user: any,
    @Body() data: { amount: number; consultationId: string },
  ) {
    return this.paymentsService.createPaymentIntent(
      user.id,
      data.amount,
      data.consultationId,
    );
  }

  @Post('confirm')
  @ApiOperation({ summary: 'Confirm payment' })
  async confirmPayment(@Body() data: { paymentIntentId: string }) {
    return this.paymentsService.confirmPayment(data.paymentIntentId);
  }

  @Get('history')
  @ApiOperation({ summary: 'Get payment history' })
  async getPaymentHistory(@CurrentUser() user: any) {
    return this.paymentsService.getPaymentHistory(user.id);
  }
}
