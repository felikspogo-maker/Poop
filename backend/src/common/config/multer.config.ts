import { diskStorage } from 'multer';
import { extname, join } from 'path';
import { existsSync, mkdirSync } from 'fs';
import { BadRequestException } from '@nestjs/common';

// Ensure uploads directory exists
const uploadPath = join(process.cwd(), 'uploads');
if (!existsSync(uploadPath)) {
  mkdirSync(uploadPath, { recursive: true });
}

// Allowed file types
const ALLOWED_MIME_TYPES = [
  // Documents
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'application/vnd.ms-powerpoint',
  'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  // Images
  'image/jpeg',
  'image/png',
  'image/gif',
  'image/webp',
  // Text
  'text/plain',
  'text/csv',
];

// File size limit: 10MB
const MAX_FILE_SIZE = 10 * 1024 * 1024;

export const multerConfig = {
  storage: diskStorage({
    destination: (req, file, cb) => {
      cb(null, uploadPath);
    },
    filename: (req, file, cb) => {
      // Generate unique filename
      const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
      const ext = extname(file.originalname);
      const filename = `${file.fieldname}-${uniqueSuffix}${ext}`;
      cb(null, filename);
    },
  }),
  fileFilter: (req, file, cb) => {
    // Check file type
    if (!ALLOWED_MIME_TYPES.includes(file.mimetype)) {
      return cb(
        new BadRequestException(
          `File type not allowed. Allowed types: PDF, Word, Excel, PowerPoint, Images (JPEG, PNG, GIF, WEBP), Text files`,
        ),
        false,
      );
    }
    cb(null, true);
  },
  limits: {
    fileSize: MAX_FILE_SIZE,
  },
};

// Separate config for avatar uploads (stricter)
export const avatarMulterConfig = {
  storage: diskStorage({
    destination: (req, file, cb) => {
      const avatarPath = join(uploadPath, 'avatars');
      if (!existsSync(avatarPath)) {
        mkdirSync(avatarPath, { recursive: true });
      }
      cb(null, avatarPath);
    },
    filename: (req, file, cb) => {
      const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1e9);
      const ext = extname(file.originalname);
      const filename = `avatar-${uniqueSuffix}${ext}`;
      cb(null, filename);
    },
  }),
  fileFilter: (req, file, cb) => {
    // Only allow images for avatars
    const allowedImageTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
    ];

    if (!allowedImageTypes.includes(file.mimetype)) {
      return cb(
        new BadRequestException(
          'Only image files are allowed for avatars (JPEG, PNG, GIF, WEBP)',
        ),
        false,
      );
    }
    cb(null, true);
  },
  limits: {
    fileSize: 5 * 1024 * 1024, // 5MB for avatars
  },
};
