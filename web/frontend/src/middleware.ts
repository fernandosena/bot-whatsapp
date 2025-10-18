import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// Rotas que requerem autenticação
const protectedRoutes = ['/dashboard', '/profile', '/settings']

// Rotas de admin
const adminRoutes = ['/admin']

// Rotas públicas (não requerem autenticação)
const publicRoutes = ['/', '/pricing', '/auth/login', '/auth/register']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl

  // Verificar se tem token no cookie ou localStorage será verificado no client-side
  // Aqui fazemos apenas redirecionamento básico

  // Se está tentando acessar rota protegida
  if (protectedRoutes.some(route => pathname.startsWith(route))) {
    // Verificação será feita no client-side component
    return NextResponse.next()
  }

  // Se está tentando acessar rota de admin
  if (adminRoutes.some(route => pathname.startsWith(route))) {
    // Verificação será feita no client-side component
    return NextResponse.next()
  }

  return NextResponse.next()
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!api|_next/static|_next/image|favicon.ico).*)',
  ],
}
