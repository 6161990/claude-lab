import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight, Github } from "lucide-react"

/**
 * 히어로 섹션 컴포넌트
 * 메인 타이틀, 서브타이틀, CTA 버튼 포함
 */
export function HeroSection() {
  return (
    <section className="container flex flex-col items-center justify-center gap-8 py-24 md:py-32">
      {/* 타이틀 */}
      <div className="flex flex-col items-center gap-4 text-center">
        <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
          모던 웹 개발을 위한
          <br />
          <span className="text-primary">스타터킷</span>
        </h1>
        <p className="max-w-[700px] text-lg text-muted-foreground sm:text-xl">
          Next.js 16 + React 19 + TypeScript + shadcn/ui로
          <br />
          빠르게 시작하세요
        </p>
      </div>

      {/* CTA 버튼 */}
      <div className="flex flex-col gap-4 sm:flex-row">
        <Button asChild size="lg" className="gap-2">
          <Link href="/examples/form-validation">
            시작하기
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
        <Button asChild variant="outline" size="lg" className="gap-2">
          <Link
            href="https://github.com"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Github className="h-4 w-4" />
            GitHub
          </Link>
        </Button>
      </div>

      {/* 배지 (선택 사항) */}
      <div className="flex flex-wrap items-center justify-center gap-4 text-sm text-muted-foreground">
        <span>✨ 최신 기술 스택</span>
        <span>🚀 빠른 개발 시작</span>
        <span>🎨 shadcn/ui 기본 제공</span>
      </div>
    </section>
  )
}
