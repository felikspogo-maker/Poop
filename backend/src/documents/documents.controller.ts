import {
  Controller,
  Get,
  Post,
  Delete,
  Param,
  UseGuards,
  UseInterceptors,
  UploadedFile,
  Res,
} from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { ApiTags, ApiOperation, ApiBearerAuth, ApiConsumes } from '@nestjs/swagger';
import { Response } from 'express';
import { DocumentsService } from './documents.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';

@ApiTags('Documents')
@Controller('documents')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class DocumentsController {
  constructor(private readonly documentsService: DocumentsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all user documents' })
  async findAll(@CurrentUser() user: any) {
    return this.documentsService.findAll(user.id);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get document by ID' })
  async findById(@Param('id') id: string) {
    return this.documentsService.findById(id);
  }

  @Post('upload')
  @ApiOperation({ summary: 'Upload document' })
  @ApiConsumes('multipart/form-data')
  @UseInterceptors(FileInterceptor('file'))
  async upload(
    @CurrentUser() user: any,
    @UploadedFile() file: Express.Multer.File,
  ) {
    return this.documentsService.upload(user.id, file);
  }

  @Get(':id/download')
  @ApiOperation({ summary: 'Download document' })
  async download(@Param('id') id: string, @Res() res: Response) {
    const document = await this.documentsService.download(id);
    res.download(document.path, document.name);
  }

  @Delete(':id')
  @ApiOperation({ summary: 'Delete document' })
  async delete(@Param('id') id: string, @CurrentUser() user: any) {
    return this.documentsService.delete(id, user.id);
  }
}
