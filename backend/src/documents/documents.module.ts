import { Module } from '@nestjs/common';
import { MulterModule } from '@nestjs/platform-express';
import { DocumentsService } from './documents.service';
import { DocumentsController } from './documents.controller';
import { multerConfig } from '../common/config/multer.config';

@Module({
  imports: [MulterModule.register(multerConfig)],
  controllers: [DocumentsController],
  providers: [DocumentsService],
  exports: [DocumentsService],
})
export class DocumentsModule {}
