import Link from "next/link"
import { Button } from "@/components/ui/button"
import { ArrowRight } from "lucide-react"

/**
 * CTA (Call To Action) 섹션 컴포넌트
 * 사용자 행동을 유도하는 마지막 섹션
 */
export function CTASection() {
  return (
    <section className="container py-24 md:py-32">
      <div className="flex flex-col items-center gap-8 rounded-lg bg-muted p-12 text-center">
        {/* 타이틀 */}
        <div className="flex flex-col gap-4">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            지금 바로 시작하세요
          </h2>
          <p className="max-w-[600px] text-lg text-muted-foreground">
            모든 설정이 완료된 스타터킷으로 빠르게 개발을 시작하세요
          </p>
        </div>

        {/* CTA 버튼 */}
        <Button asChild size="lg" className="gap-2">
          <Link href="/examples/form-validation">
            예제 보기
            <ArrowRight className="h-4 w-4" />
          </Link>
        </Button>
      </div>
    </section>
  )
}
