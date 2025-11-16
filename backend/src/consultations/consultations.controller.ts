import { Controller, Get, Post, Patch, Body, Param, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { ConsultationsService } from './consultations.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';
import { CurrentUser } from '../auth/decorators/current-user.decorator';
import { CreateConsultationDto } from './dto/create-consultation.dto';

@ApiTags('Consultations')
@Controller('consultations')
@UseGuards(JwtAuthGuard)
@ApiBearerAuth()
export class ConsultationsController {
  constructor(private readonly consultationsService: ConsultationsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all user consultations' })
  async findAll(@CurrentUser() user: any) {
    return this.consultationsService.findAll(user.id);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get consultation by ID' })
  async findById(@Param('id') id: string) {
    return this.consultationsService.findById(id);
  }

  @Post()
  @ApiOperation({ summary: 'Create new consultation' })
  async create(@CurrentUser() user: any, @Body() data: CreateConsultationDto) {
    return this.consultationsService.create(user.id, data);
  }

  @Patch(':id/cancel')
  @ApiOperation({ summary: 'Cancel consultation' })
  async cancel(@Param('id') id: string, @CurrentUser() user: any) {
    return this.consultationsService.cancel(id, user.id);
  }

  @Patch(':id/complete')
  @ApiOperation({ summary: 'Complete consultation' })
  async complete(@Param('id') id: string) {
    return this.consultationsService.complete(id);
  }
}
