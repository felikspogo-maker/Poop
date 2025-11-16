import { Injectable, LoggerService as NestLoggerService, Scope } from '@nestjs/common';

@Injectable({ scope: Scope.TRANSIENT })
export class LoggerService implements NestLoggerService {
  private context?: string;

  setContext(context: string) {
    this.context = context;
  }

  log(message: any, context?: string) {
    const logContext = context || this.context || 'Application';
    console.log(`[${new Date().toISOString()}] [LOG] [${logContext}] ${message}`);
  }

  error(message: any, trace?: string, context?: string) {
    const logContext = context || this.context || 'Application';
    console.error(
      `[${new Date().toISOString()}] [ERROR] [${logContext}] ${message}${trace ? `\n${trace}` : ''}`
    );
  }

  warn(message: any, context?: string) {
    const logContext = context || this.context || 'Application';
    console.warn(`[${new Date().toISOString()}] [WARN] [${logContext}] ${message}`);
  }

  debug(message: any, context?: string) {
    if (process.env.NODE_ENV === 'development') {
      const logContext = context || this.context || 'Application';
      console.debug(`[${new Date().toISOString()}] [DEBUG] [${logContext}] ${message}`);
    }
  }

  verbose(message: any, context?: string) {
    if (process.env.NODE_ENV === 'development') {
      const logContext = context || this.context || 'Application';
      console.log(`[${new Date().toISOString()}] [VERBOSE] [${logContext}] ${message}`);
    }
  }
}
