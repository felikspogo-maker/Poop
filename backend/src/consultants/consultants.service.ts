import { Injectable } from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';

@Injectable()
export class ConsultantsService {
  constructor(private prisma: PrismaService) {}

  async findAll(specialization?: string) {
    return this.prisma.consultant.findMany({
      where: specialization ? { specialization } : {},
      include: {
        user: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            email: true,
            avatar: true,
          },
        },
      },
    });
  }

  async findById(id: string) {
    return this.prisma.consultant.findUnique({
      where: { id },
      include: {
        user: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            email: true,
            phone: true,
            avatar: true,
          },
        },
      },
    });
  }

  async create(userId: string, data: any) {
    return this.prisma.consultant.create({
      data: {
        userId,
        ...data,
      },
      include: {
        user: true,
      },
    });
  }

  async update(id: string, data: any) {
    return this.prisma.consultant.update({
      where: { id },
      data,
      include: {
        user: true,
      },
    });
  }

  /**
   * Get consultant availability - returns booked time slots
   */
  async getAvailability(consultantId: string, dateFilter?: string) {
    const startDate = dateFilter ? new Date(dateFilter) : new Date();

    // Get all future consultations for this consultant
    const consultations = await this.prisma.consultation.findMany({
      where: {
        consultantId,
        status: {
          in: ['SCHEDULED', 'CONFIRMED'],
        },
        date: {
          gte: startDate,
        },
      },
      select: {
        id: true,
        date: true,
        duration: true,
        status: true,
      },
      orderBy: {
        date: 'asc',
      },
    });

    // Transform to booked slots with start and end times
    const bookedSlots = consultations.map((consultation) => ({
      id: consultation.id,
      startTime: consultation.date,
      endTime: new Date(
        consultation.date.getTime() + consultation.duration * 60000,
      ),
      duration: consultation.duration,
      status: consultation.status,
    }));

    return {
      consultantId,
      bookedSlots,
      totalBooked: bookedSlots.length,
    };
  }
}
