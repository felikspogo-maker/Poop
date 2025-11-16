import {
  Injectable,
  BadRequestException,
  NotFoundException,
  ConflictException,
} from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';
import { CreateConsultationDto } from './dto/create-consultation.dto';

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

  async create(userId: string, data: CreateConsultationDto) {
    const consultationDate = new Date(data.date);

    // 1. Validate that date is in the future
    if (consultationDate <= new Date()) {
      throw new BadRequestException(
        'Consultation date must be in the future',
      );
    }

    // 2. Check if consultant exists
    const consultant = await this.prisma.consultant.findUnique({
      where: { id: data.consultantId },
    });

    if (!consultant) {
      throw new NotFoundException('Consultant not found');
    }

    // 3. Check for time conflicts
    const hasConflict = await this.checkTimeConflict(
      data.consultantId,
      consultationDate,
      data.duration,
    );

    if (hasConflict) {
      throw new ConflictException(
        'This time slot is not available. Please choose another time.',
      );
    }

    // 4. Create consultation
    return this.prisma.consultation.create({
      data: {
        userId,
        consultantId: data.consultantId,
        date: consultationDate,
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

  /**
   * Check if there are any time conflicts with existing consultations
   */
  private async checkTimeConflict(
    consultantId: string,
    requestedDate: Date,
    duration: number,
  ): Promise<boolean> {
    const requestedEndTime = new Date(
      requestedDate.getTime() + duration * 60000,
    );

    // Find all scheduled consultations for this consultant
    const existingConsultations = await this.prisma.consultation.findMany({
      where: {
        consultantId,
        status: 'SCHEDULED',
        date: {
          gte: new Date(), // Only future consultations
        },
      },
      select: {
        date: true,
        duration: true,
      },
    });

    // Check for overlaps
    for (const consultation of existingConsultations) {
      const existingStart = new Date(consultation.date);
      const existingEnd = new Date(
        existingStart.getTime() + consultation.duration * 60000,
      );

      // Check if time ranges overlap
      const hasOverlap =
        (requestedDate >= existingStart && requestedDate < existingEnd) ||
        (requestedEndTime > existingStart && requestedEndTime <= existingEnd) ||
        (requestedDate <= existingStart && requestedEndTime >= existingEnd);

      if (hasOverlap) {
        return true;
      }
    }

    return false;
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
