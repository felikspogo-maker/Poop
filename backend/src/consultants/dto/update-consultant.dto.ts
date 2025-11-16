import { PartialType } from '@nestjs/swagger';
import { CreateConsultantDto } from './create-consultant.dto';
import { OmitType } from '@nestjs/swagger';

export class UpdateConsultantDto extends PartialType(
  OmitType(CreateConsultantDto, ['userId'] as const),
) {}
