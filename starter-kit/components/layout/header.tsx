"use client"

import Link from "next/link"
import { Navigation } from "./navigation"
import { MobileMenu } from "./mobile-menu"
import { ThemeToggle } from "./theme-toggle"

/**
 * 사이트 헤더 컴포넌트
 * 로고, 네비게이션, 다크모드 토글, 모바일 메뉴 포함
 */
export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container flex h-16 items-center justify-between px-4 md:px-8">
        {/* 왼쪽: 로고 + 모바일 메뉴 */}
        <div className="flex items-center gap-2">
          <MobileMenu />
          <Link href="/" className="flex items-center space-x-2">
            <span className="font-bold text-xl">Starter Kit</span>
          </Link>
        </div>

        {/* 중앙: 데스크톱 네비게이션 */}
        <Navigation />

        {/* 오른쪽: 다크모드 토글 */}
        <div className="flex items-center">
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
