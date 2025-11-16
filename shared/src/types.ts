export enum UserRole {
  CLIENT = 'CLIENT',
  CONSULTANT = 'CONSULTANT',
  ADMIN = 'ADMIN',
}

export enum ConsultationStatus {
  SCHEDULED = 'SCHEDULED',
  COMPLETED = 'COMPLETED',
  CANCELLED = 'CANCELLED',
}

export enum PaymentStatus {
  PENDING = 'PENDING',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  REFUNDED = 'REFUNDED',
}

export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  phone: string;
  role: UserRole;
  avatar?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Consultant {
  id: string;
  userId: string;
  specialization: string;
  bio?: string;
  hourlyRate: number;
  rating: number;
  reviewsCount: number;
  skills: string[];
  availability?: any;
  user?: User;
  createdAt: Date;
  updatedAt: Date;
}

export interface Consultation {
  id: string;
  userId: string;
  consultantId: string;
  date: Date;
  duration: number;
  description?: string;
  status: ConsultationStatus;
  meetingLink?: string;
  notes?: string;
  consultant?: Consultant;
  user?: User;
  createdAt: Date;
  updatedAt: Date;
}

export interface Payment {
  id: string;
  userId: string;
  consultationId: string;
  amount: number;
  currency: string;
  status: PaymentStatus;
  stripePaymentId?: string;
  stripeCustomerId?: string;
  createdAt: Date;
  updatedAt: Date;
}

export interface Message {
  id: string;
  conversationId: string;
  senderId: string;
  receiverId: string;
  content: string;
  read: boolean;
  createdAt: Date;
}

export interface Conversation {
  id: string;
  participants: User[];
  messages: Message[];
  createdAt: Date;
  updatedAt: Date;
}

export interface Document {
  id: string;
  userId: string;
  name: string;
  type: string;
  size: number;
  url: string;
  path: string;
  createdAt: Date;
  updatedAt: Date;
}
