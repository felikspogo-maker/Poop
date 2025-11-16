import { Injectable } from '@nestjs/common';
import { ConfigService } from '@nestjs/config';
import Stripe from 'stripe';
import { PrismaService } from '../common/prisma/prisma.service';

@Injectable()
export class PaymentsService {
  private stripe: Stripe;

  constructor(
    private prisma: PrismaService,
    private configService: ConfigService,
  ) {
    this.stripe = new Stripe(
      this.configService.get<string>('STRIPE_SECRET_KEY'),
      { apiVersion: '2024-11-20.acacia' },
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
}
