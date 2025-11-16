import {
  Controller,
  Post,
  Get,
  Body,
  UseGuards,
  Headers,
  RawBodyRequest,
  Req,
  BadRequestException,
} from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { Request } from 'express';
import { PaymentsService } from './payments.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';
import {
  CreatePaymentIntentDto,
  ConfirmPaymentDto,
} from './dto/create-payment.dto';

@ApiTags('Payments')
@Controller('payments')
export class PaymentsController {
  constructor(private readonly paymentsService: PaymentsService) {}

  @Post('create-intent')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Create payment intent' })
  async createPaymentIntent(
    @CurrentUser() user: any,
    @Body() data: CreatePaymentIntentDto,
  ) {
    return this.paymentsService.createPaymentIntent(
      user.id,
      data.amount,
      data.consultationId,
    );
  }

  @Post('confirm')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Confirm payment' })
  async confirmPayment(@Body() data: ConfirmPaymentDto) {
    return this.paymentsService.confirmPayment(data.paymentIntentId);
  }

  @Get('history')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Get payment history' })
  async getPaymentHistory(@CurrentUser() user: any) {
    return this.paymentsService.getPaymentHistory(user.id);
  }

  @Post('webhook')
  @ApiOperation({ summary: 'Stripe webhook endpoint' })
  async handleWebhook(
    @Headers('stripe-signature') signature: string,
    @Req() request: RawBodyRequest<Request>,
  ) {
    if (!signature) {
      throw new BadRequestException('Missing stripe-signature header');
    }

    return this.paymentsService.handleStripeWebhook(
      request.rawBody,
      signature,
    );
  }
}
