import axios from 'axios';
import { API_URL } from '../../config';

export interface Review {
  id: string;
  consultantId: string;
  userId: string;
  rating: number;
  comment?: string;
  createdAt: string;
  updatedAt: string;
  user?: {
    id: string;
    firstName: string;
    lastName: string;
    avatar?: string;
  };
}

export interface CreateReviewData {
  consultantId: string;
  rating: number;
  comment?: string;
}

export interface UpdateReviewData {
  rating?: number;
  comment?: string;
}

export const reviewsAPI = {
  // Get all reviews for a consultant
  getByConsultant: async (consultantId: string): Promise<Review[]> => {
    const response = await axios.get(`${API_URL}/reviews/consultant/${consultantId}`);
    return response.data;
  },

  // Get all reviews written by current user
  getMyReviews: async (token: string): Promise<Review[]> => {
    const response = await axios.get(`${API_URL}/reviews/my-reviews`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  // Create a new review
  create: async (token: string, data: CreateReviewData): Promise<Review> => {
    const response = await axios.post(`${API_URL}/reviews`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  // Update a review
  update: async (
    token: string,
    reviewId: string,
    data: UpdateReviewData,
  ): Promise<Review> => {
    const response = await axios.patch(`${API_URL}/reviews/${reviewId}`, data, {
      headers: { Authorization: `Bearer ${token}` },
    });
    return response.data;
  },

  // Delete a review
  delete: async (token: string, reviewId: string): Promise<void> => {
    await axios.delete(`${API_URL}/reviews/${reviewId}`, {
      headers: { Authorization: `Bearer ${token}` },
    });
  },
};
