import { Test, TestingModule } from '@nestjs/testing';
import { JwtService } from '@nestjs/jwt';
import { UnauthorizedException, ConflictException } from '@nestjs/common';
import { AuthService } from './auth.service';
import { UsersService } from '../users/users.service';
import * as bcrypt from 'bcrypt';

jest.mock('bcrypt');

describe('AuthService', () => {
  let service: AuthService;
  let usersService: UsersService;
  let jwtService: JwtService;

  const mockUser = {
    id: '1',
    email: 'test@example.com',
    password: 'hashedPassword',
    firstName: 'Test',
    lastName: 'User',
    phone: '+79001234567',
    role: 'CLIENT' as const,
    avatar: null,
    createdAt: new Date(),
    updatedAt: new Date(),
  };

  const mockUsersService = {
    findByEmail: jest.fn(),
    findById: jest.fn(),
    create: jest.fn(),
  };

  const mockJwtService = {
    sign: jest.fn(),
  };

  beforeEach(async () => {
    const module: TestingModule = await Test.createTestingModule({
      providers: [
        AuthService,
        {
          provide: UsersService,
          useValue: mockUsersService,
        },
        {
          provide: JwtService,
          useValue: mockJwtService,
        },
      ],
    }).compile();

    service = module.get<AuthService>(AuthService);
    usersService = module.get<UsersService>(UsersService);
    jwtService = module.get<JwtService>(JwtService);

    jest.clearAllMocks();
  });

  it('should be defined', () => {
    expect(service).toBeDefined();
  });

  describe('validateUser', () => {
    it('should validate user with correct credentials', async () => {
      mockUsersService.findByEmail.mockResolvedValue(mockUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);

      const result = await service.validateUser('test@example.com', 'password');

      expect(result).toEqual({
        id: mockUser.id,
        email: mockUser.email,
        firstName: mockUser.firstName,
        lastName: mockUser.lastName,
        phone: mockUser.phone,
        role: mockUser.role,
        avatar: mockUser.avatar,
        createdAt: mockUser.createdAt,
        updatedAt: mockUser.updatedAt,
      });
      expect(mockUsersService.findByEmail).toHaveBeenCalledWith('test@example.com');
    });

    it('should throw UnauthorizedException for invalid email', async () => {
      mockUsersService.findByEmail.mockResolvedValue(null);

      await expect(service.validateUser('wrong@example.com', 'password')).rejects.toThrow(
        UnauthorizedException
      );
    });

    it('should throw UnauthorizedException for invalid password', async () => {
      mockUsersService.findByEmail.mockResolvedValue(mockUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(false);

      await expect(service.validateUser('test@example.com', 'wrongpassword')).rejects.toThrow(
        UnauthorizedException
      );
    });
  });

  describe('login', () => {
    it('should return access token and user', async () => {
      const { password, ...userWithoutPassword } = mockUser;

      mockUsersService.findByEmail.mockResolvedValue(mockUser);
      (bcrypt.compare as jest.Mock).mockResolvedValue(true);
      mockJwtService.sign.mockReturnValue('mock-jwt-token');

      const result = await service.login({
        email: 'test@example.com',
        password: 'password',
      });

      expect(result).toEqual({
        access_token: 'mock-jwt-token',
        user: userWithoutPassword,
      });
      expect(mockJwtService.sign).toHaveBeenCalledWith({
        sub: mockUser.id,
        email: mockUser.email,
        role: mockUser.role,
      });
    });
  });

  describe('register', () => {
    it('should create a new user and return access token', async () => {
      const registerDto = {
        email: 'new@example.com',
        password: 'password',
        firstName: 'New',
        lastName: 'User',
        phone: '+79009999999',
      };

      mockUsersService.findByEmail.mockResolvedValue(null);
      (bcrypt.hash as jest.Mock).mockResolvedValue('hashedPassword');
      mockUsersService.create.mockResolvedValue({
        ...mockUser,
        email: registerDto.email,
      });
      mockJwtService.sign.mockReturnValue('mock-jwt-token');

      const result = await service.register(registerDto);

      expect(result).toHaveProperty('access_token');
      expect(result).toHaveProperty('user');
      expect(mockUsersService.create).toHaveBeenCalledWith({
        ...registerDto,
        password: 'hashedPassword',
      });
    });

    it('should throw ConflictException if email already exists', async () => {
      const registerDto = {
        email: 'test@example.com',
        password: 'password',
        firstName: 'Test',
        lastName: 'User',
        phone: '+79001234567',
      };

      mockUsersService.findByEmail.mockResolvedValue(mockUser);

      await expect(service.register(registerDto)).rejects.toThrow(ConflictException);
    });
  });

  describe('getProfile', () => {
    it('should return user profile', async () => {
      mockUsersService.findById.mockResolvedValue(mockUser);

      const result = await service.getProfile(mockUser.id);

      expect(result).toEqual(mockUser);
      expect(mockUsersService.findById).toHaveBeenCalledWith(mockUser.id);
    });
  });
});
