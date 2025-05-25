import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

// 認証が必要なパス
const protectedPaths = ['/dashboard']

// 認証済みユーザーがアクセスすべきでないパス
const authPaths = ['/login', '/register']

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl
  
  // アクセストークンの存在確認
  const accessToken = request.cookies.get('access_token')
  
  // 保護されたパスへのアクセス
  if (protectedPaths.some(path => pathname.startsWith(path))) {
    if (!accessToken) {
      const url = new URL('/login', request.url)
      url.searchParams.set('from', pathname)
      return NextResponse.redirect(url)
    }
  }
  
  // 認証済みユーザーがログイン・登録ページにアクセスした場合
  if (authPaths.some(path => pathname.startsWith(path))) {
    if (accessToken) {
      return NextResponse.redirect(new URL('/dashboard', request.url))
    }
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