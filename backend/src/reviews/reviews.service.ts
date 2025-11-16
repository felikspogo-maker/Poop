import {
  Injectable,
  NotFoundException,
  ConflictException,
  ForbiddenException,
} from '@nestjs/common';
import { PrismaService } from '../common/prisma/prisma.service';
import { CreateReviewDto } from './dto/create-review.dto';
import { UpdateReviewDto } from './dto/update-review.dto';

@Injectable()
export class ReviewsService {
  constructor(private prisma: PrismaService) {}

  /**
   * Create a new review for a consultant
   */
  async create(userId: string, createReviewDto: CreateReviewDto) {
    // Check if consultant exists
    const consultant = await this.prisma.consultant.findUnique({
      where: { id: createReviewDto.consultantId },
    });

    if (!consultant) {
      throw new NotFoundException('Consultant not found');
    }

    // Check if user has already reviewed this consultant
    const existingReview = await this.prisma.review.findUnique({
      where: {
        consultantId_userId: {
          consultantId: createReviewDto.consultantId,
          userId,
        },
      },
    });

    if (existingReview) {
      throw new ConflictException(
        'You have already reviewed this consultant. Use update instead.',
      );
    }

    // Create the review
    const review = await this.prisma.review.create({
      data: {
        userId,
        consultantId: createReviewDto.consultantId,
        rating: createReviewDto.rating,
        comment: createReviewDto.comment,
      },
      include: {
        user: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            avatar: true,
          },
        },
      },
    });

    // Update consultant's average rating and review count
    await this.updateConsultantRating(createReviewDto.consultantId);

    return review;
  }

  /**
   * Get all reviews for a consultant
   */
  async findByConsultant(consultantId: string) {
    return this.prisma.review.findMany({
      where: { consultantId },
      include: {
        user: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            avatar: true,
          },
        },
      },
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * Get reviews by user
   */
  async findByUser(userId: string) {
    return this.prisma.review.findMany({
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
      orderBy: { createdAt: 'desc' },
    });
  }

  /**
   * Update a review
   */
  async update(
    reviewId: string,
    userId: string,
    updateReviewDto: UpdateReviewDto,
  ) {
    const review = await this.prisma.review.findUnique({
      where: { id: reviewId },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    if (review.userId !== userId) {
      throw new ForbiddenException('You can only update your own reviews');
    }

    const updatedReview = await this.prisma.review.update({
      where: { id: reviewId },
      data: updateReviewDto,
      include: {
        user: {
          select: {
            id: true,
            firstName: true,
            lastName: true,
            avatar: true,
          },
        },
      },
    });

    // Update consultant's average rating
    await this.updateConsultantRating(review.consultantId);

    return updatedReview;
  }

  /**
   * Delete a review
   */
  async remove(reviewId: string, userId: string) {
    const review = await this.prisma.review.findUnique({
      where: { id: reviewId },
    });

    if (!review) {
      throw new NotFoundException('Review not found');
    }

    if (review.userId !== userId) {
      throw new ForbiddenException('You can only delete your own reviews');
    }

    await this.prisma.review.delete({
      where: { id: reviewId },
    });

    // Update consultant's average rating
    await this.updateConsultantRating(review.consultantId);

    return { success: true };
  }

  /**
   * Update consultant's average rating and review count
   */
  private async updateConsultantRating(consultantId: string) {
    const reviews = await this.prisma.review.findMany({
      where: { consultantId },
      select: { rating: true },
    });

    const totalReviews = reviews.length;
    const averageRating =
      totalReviews > 0
        ? reviews.reduce((sum, review) => sum + review.rating, 0) / totalReviews
        : 5.0;

    await this.prisma.consultant.update({
      where: { id: consultantId },
      data: {
        rating: Math.round(averageRating * 10) / 10, // Round to 1 decimal
        reviewsCount: totalReviews,
      },
    });
  }
}
