"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"

/**
 * 네비게이션 메뉴 항목 타입
 */
interface NavItem {
  label: string
  href: string
}

/**
 * 메뉴 항목 정의
 */
const navItems: NavItem[] = [
  { label: "홈", href: "/" },
  { label: "예제", href: "/examples/form-validation" },
]

/**
 * 데스크톱 네비게이션 컴포넌트
 * 활성 링크 하이라이트 기능 포함
 */
export function Navigation() {
  const pathname = usePathname()

  return (
    <nav className="hidden md:flex items-center gap-6">
      {navItems.map((item) => {
        const isActive = pathname === item.href
        return (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "text-sm font-medium transition-colors hover:text-primary",
              isActive
                ? "text-foreground"
                : "text-muted-foreground"
            )}
          >
            {item.label}
          </Link>
        )
      })}
    </nav>
  )
}

/**
 * 네비게이션 메뉴 항목 데이터 export (모바일 메뉴에서 재사용)
 */
export { navItems }
