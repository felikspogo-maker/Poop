import { CanActivate, ExecutionContext, Injectable } from '@nestjs/common';
import { JwtService } from '@nestjs/jwt';
import { WsException } from '@nestjs/websockets';
import { Socket } from 'socket.io';

@Injectable()
export class WsJwtGuard implements CanActivate {
  constructor(private jwtService: JwtService) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    try {
      const client: Socket = context.switchToWs().getClient();
      const token = this.extractTokenFromHandshake(client);

      if (!token) {
        throw new WsException('No token provided');
      }

      const payload = await this.jwtService.verifyAsync(token, {
        secret: process.env.JWT_SECRET,
      });

      // Attach user data to socket for later use
      client.data.user = payload;

      return true;
    } catch (error) {
      throw new WsException('Invalid token');
    }
  }

  private extractTokenFromHandshake(client: Socket): string | null {
    // Try to get token from handshake auth
    if (client.handshake?.auth?.token) {
      return client.handshake.auth.token;
    }

    // Try to get token from query params
    if (client.handshake?.query?.token) {
      return client.handshake.query.token as string;
    }

    // Try to get token from headers (Authorization: Bearer <token>)
    const authHeader = client.handshake?.headers?.authorization;
    if (authHeader && authHeader.startsWith('Bearer ')) {
      return authHeader.substring(7);
    }

    return null;
  }
}
