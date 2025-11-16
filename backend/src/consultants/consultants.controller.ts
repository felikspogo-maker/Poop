import { Controller, Get, Post, Patch, Body, Param, Query, UseGuards } from '@nestjs/common';
import { ApiTags, ApiOperation, ApiBearerAuth } from '@nestjs/swagger';
import { ConsultantsService } from './consultants.service';
import { JwtAuthGuard } from '../auth/guards/jwt-auth.guard';

@ApiTags('Consultants')
@Controller('consultants')
export class ConsultantsController {
  constructor(private readonly consultantsService: ConsultantsService) {}

  @Get()
  @ApiOperation({ summary: 'Get all consultants' })
  async findAll(@Query('specialization') specialization?: string) {
    return this.consultantsService.findAll(specialization);
  }

  @Get(':id')
  @ApiOperation({ summary: 'Get consultant by ID' })
  async findById(@Param('id') id: string) {
    return this.consultantsService.findById(id);
  }

  @Post()
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Create consultant profile' })
  async create(@Body() data: any) {
    return this.consultantsService.create(data.userId, data);
  }

  @Patch(':id')
  @UseGuards(JwtAuthGuard)
  @ApiBearerAuth()
  @ApiOperation({ summary: 'Update consultant profile' })
  async update(@Param('id') id: string, @Body() data: any) {
    return this.consultantsService.update(id, data);
  }
}
