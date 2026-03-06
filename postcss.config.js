import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

const PUBLIC_PATHS = ['/', '/login', '/register', '/forgot-password', '/reset-password',
                      '/verify-email', '/for-owners', '/for-vets', '/hub', '/find-vet'];

const PROTECTED_PATHS = ['/dashboard', '/pets', '/messages', '/appointments',
                         '/account', '/notifications', '/admin'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  const isProtected = PROTECTED_PATHS.some((p) => pathname.startsWith(p));
  const accessToken = request.cookies.get('access_token')?.value;

  if (isProtected && !accessToken) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    url.searchParams.set('from', pathname);
    return NextResponse.redirect(url);
  }

  // Redirect logged-in users away from auth pages
  if ((pathname === '/login' || pathname === '/register') && accessToken) {
    const url = request.nextUrl.clone();
    url.pathname = '/dashboard';
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico|.*\\..*).*)'],
};
