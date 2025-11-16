import { Injectable, Logger, BadRequestException } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Stripe from 'stripe';
import { PrismaService } from '../common/prisma/prisma.service';

@Injectable()
export class PaymentsService {
  private stripe: Stripe;
  private webhookSecret: string;
  private logger = new Logger('PaymentsService');

  constructor(
    private prisma: PrismaService,
    private configService: ConfigService,
  ) {
    this.stripe = new Stripe(
      this.configService.get<string>('STRIPE_SECRET_KEY'),
      { apiVersion: '2024-11-20.acacia' },
    );
    this.webhookSecret = this.configService.get<string>(
      'STRIPE_WEBHOOK_SECRET',
      '',
    );
  }

  async createPaymentIntent(
    userId: string,
    amount: number,
    consultationId: string,
  ) {
    const paymentIntent = await this.stripe.paymentIntents.create({
      amount: amount * 100, // Convert to cents
      currency: 'rub',
      metadata: {
        userId,
        consultationId,
      },
    });

    await this.prisma.payment.create({
      data: {
        userId,
        consultationId,
        amount: amount * 100,
        currency: 'rub',
        status: 'PENDING',
        stripePaymentId: paymentIntent.id,
      },
    });

    return {
      clientSecret: paymentIntent.client_secret,
      paymentIntentId: paymentIntent.id,
    };
  }

  async confirmPayment(paymentIntentId: string) {
    const payment = await this.prisma.payment.findFirst({
      where: { stripePaymentId: paymentIntentId },
    });

    if (!payment) {
      throw new Error('Payment not found');
    }

    await this.prisma.payment.update({
      where: { id: payment.id },
      data: { status: 'COMPLETED' },
    });

    return { success: true };
  }

  async getPaymentHistory(userId: string) {
    return this.prisma.payment.findMany({
      where: { userId },
      include: {
        consultation: {
          include: {
            consultant: {
              include: {
                user: {
                  select: {
                    firstName: true,
                    lastName: true,
                  },
                },
              },
            },
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * Handle Stripe webhook events
   */
  async handleStripeWebhook(rawBody: Buffer, signature: string) {
    if (!this.webhookSecret) {
      this.logger.warn('Webhook secret not configured, skipping verification');
      return { received: true };
    }

    let event: Stripe.Event;

    try {
      // Verify webhook signature
      event = this.stripe.webhooks.constructEvent(
        rawBody,
        signature,
        this.webhookSecret,
      );
    } catch (error) {
      this.logger.error(`Webhook signature verification failed: ${error.message}`);
      throw new BadRequestException('Invalid signature');
    }

    this.logger.log(`Received webhook event: ${event.type}`);

    // Handle the event
    switch (event.type) {
      case 'payment_intent.succeeded':
        await this.handlePaymentSucceeded(event.data.object as Stripe.PaymentIntent);
        break;

      case 'payment_intent.payment_failed':
        await this.handlePaymentFailed(event.data.object as Stripe.PaymentIntent);
        break;

      case 'payment_intent.canceled':
        await this.handlePaymentCanceled(event.data.object as Stripe.PaymentIntent);
        break;

      default:
        this.logger.log(`Unhandled event type: ${event.type}`);
    }

    return { received: true };
  }

  private async handlePaymentSucceeded(paymentIntent: Stripe.PaymentIntent) {
    this.logger.log(`Payment succeeded: ${paymentIntent.id}`);

    const payment = await this.prisma.payment.findFirst({
      where: { stripePaymentId: paymentIntent.id },
    });

    if (!payment) {
      this.logger.error(`Payment not found for intent: ${paymentIntent.id}`);
      return;
    }

    // Update payment status
    await this.prisma.payment.update({
      where: { id: payment.id },
      data: { status: 'COMPLETED' },
    });

    // Update consultation status to CONFIRMED
    if (payment.consultationId) {
      await this.prisma.consultation.update({
        where: { id: payment.consultationId },
        data: { status: 'CONFIRMED' },
      });
    }

    this.logger.log(`Payment ${payment.id} marked as COMPLETED`);
  }

  private async handlePaymentFailed(paymentIntent: Stripe.PaymentIntent) {
    this.logger.log(`Payment failed: ${paymentIntent.id}`);

    const payment = await this.prisma.payment.findFirst({
      where: { stripePaymentId: paymentIntent.id },
    });

    if (!payment) {
      this.logger.error(`Payment not found for intent: ${paymentIntent.id}`);
      return;
    }

    // Update payment status
    await this.prisma.payment.update({
      where: { id: payment.id },
      data: { status: 'FAILED' },
    });

    // Cancel the consultation
    if (payment.consultationId) {
      await this.prisma.consultation.update({
        where: { id: payment.consultationId },
        data: { status: 'CANCELLED' },
      });
    }

    this.logger.log(`Payment ${payment.id} marked as FAILED`);
  }

  private async handlePaymentCanceled(paymentIntent: Stripe.PaymentIntent) {
    this.logger.log(`Payment canceled: ${paymentIntent.id}`);

    const payment = await this.prisma.payment.findFirst({
      where: { stripePaymentId: paymentIntent.id },
    });

    if (!payment) {
      this.logger.error(`Payment not found for intent: ${paymentIntent.id}`);
      return;
    }

    // Update payment status
    await this.prisma.payment.update({
      where: { id: payment.id },
      data: { status: 'CANCELLED' },
    });

    this.logger.log(`Payment ${payment.id} marked as CANCELLED`);
  }
}
