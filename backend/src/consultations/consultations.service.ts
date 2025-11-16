import { Injectable } from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';

@Injectable()
export class ConsultationsService {
  constructor(private prisma: PrismaService) {}

  async findAll(userId: string) {
    return this.prisma.consultation.findMany({
      where: { userId },
      include: {
        consultant: {
          include: {
            user: {
              select: {
                firstName: true,
                lastName: true,
                avatar: true,
              },
            },
          },
        },
      },
      orderBy: { date: 'asc' },
    });
  }

  async findById(id: string) {
    return this.prisma.consultation.findUnique({
      where: { id },
      include: {
        consultant: {
          include: {
            user: true,
          },
        },
        user: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            email: true,
            phone: true,
          },
        },
      },
    });
  }

  async create(userId: string, data: {
    consultantId: string;
    date: string;
    duration: number;
    description?: string;
  }) {
    return this.prisma.consultation.create({
      data: {
        userId,
        consultantId: data.consultantId,
        date: new Date(data.date),
        duration: data.duration,
        description: data.description,
        status: 'SCHEDULED',
      },
      include: {
        consultant: {
          include: {
            user: true,
          },
        },
      },
    });
  }

  async cancel(id: string, userId: string) {
    return this.prisma.consultation.updateMany({
      where: {
        id,
        userId,
      },
      data: {
        status: 'CANCELLED',
      },
    });
  }

  async complete(id: string) {
    return this.prisma.consultation.update({
      where: { id },
      data: { status: 'COMPLETED' },
    });
  }
}
