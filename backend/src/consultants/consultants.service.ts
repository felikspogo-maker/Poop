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
}
