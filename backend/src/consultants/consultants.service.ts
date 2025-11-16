import { Injectable } from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';
import { CreateConsultantDto } from './dto/create-consultant.dto';
import { UpdateConsultantDto } from './dto/update-consultant.dto';

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

  async create(userId: string, data: CreateConsultantDto) {
    const { userId: _, ...createData } = data;
    return this.prisma.consultant.create({
      data: {
        userId,
        specialization: createData.specialization,
        bio: createData.bio,
        experience: createData.experience,
        hourlyRate: createData.rate,
        skills: createData.services || [],
        availability: createData.certifications
          ? { certifications: createData.certifications }
          : null,
      },
      include: {
        user: true,
      },
    });
  }

  async update(id: string, data: UpdateConsultantDto) {
    const updateData: any = {};

    if (data.specialization) updateData.specialization = data.specialization;
    if (data.bio) updateData.bio = data.bio;
    if (data.experience !== undefined) updateData.experience = data.experience;
    if (data.rate) updateData.hourlyRate = data.rate;
    if (data.services) updateData.skills = data.services;
    if (data.certifications) {
      updateData.availability = { certifications: data.certifications };
    }

    return this.prisma.consultant.update({
      where: { id },
      data: updateData,
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
