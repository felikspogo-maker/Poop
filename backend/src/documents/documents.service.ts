import { Injectable } from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class DocumentsService {
  constructor(private prisma: PrismaService) {}

  async findAll(userId: string) {
    return this.prisma.document.findMany({
      where: { userId },
      orderBy: { createdAt: 'desc' },
    });
  }

  async findById(id: string) {
    return this.prisma.document.findUnique({
      where: { id },
    });
  }

  async upload(userId: string, file: Express.Multer.File) {
    return this.prisma.document.create({
      data: {
        userId,
        name: file.originalname,
        type: file.mimetype,
        size: file.size,
        path: file.path,
        url: `/uploads/${file.filename}`,
      },
    });
  }

  async delete(id: string, userId: string) {
    const document = await this.prisma.document.findFirst({
      where: { id, userId },
    });

    if (document) {
      // Delete physical file
      try {
        fs.unlinkSync(document.path);
      } catch (error) {
        console.error('Error deleting file:', error);
      }

      // Delete database record
      await this.prisma.document.delete({
        where: { id },
      });
    }

    return { success: true };
  }

  async download(id: string) {
    const document = await this.prisma.document.findUnique({
      where: { id },
    });

    if (!document) {
      throw new Error('Document not found');
    }

    return {
      path: document.path,
      name: document.name,
      type: document.type,
    };
  }
}
