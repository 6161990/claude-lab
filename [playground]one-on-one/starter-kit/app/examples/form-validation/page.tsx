import { Header } from "@/components/layout/header"
import { Footer } from "@/components/layout/footer"
import { ContactForm } from "@/components/forms/contact-form"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

/**
 * 폼 검증 예제 페이지
 * React Hook Form + Zod를 사용한 타입 안전한 폼 검증 데모
 */
export default function FormValidationPage() {
  return (
    <div className="flex flex-col min-h-screen">
      <Header />
      <main className="flex-1 container py-12 md:py-24">
        <div className="mx-auto max-w-2xl space-y-8">
          {/* 페이지 헤더 */}
          <div className="space-y-4 text-center">
            <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
              폼 검증 예제
            </h1>
            <p className="text-lg text-muted-foreground">
              React Hook Form과 Zod를 사용한 타입 안전한 폼 검증 예제입니다
            </p>
          </div>

          {/* 폼 카드 */}
          <Card>
            <CardHeader>
              <CardTitle>연락처 폼</CardTitle>
              <CardDescription>
                아래 폼을 작성하여 폼 검증 기능을 테스트해보세요.
                모든 필드는 실시간으로 검증됩니다.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <ContactForm />
            </CardContent>
          </Card>

          {/* 기술 스택 정보 */}
          <div className="rounded-lg border bg-card p-6">
            <h3 className="font-semibold mb-4">사용된 기술</h3>
            <ul className="space-y-2 text-sm text-muted-foreground">
              <li>
                • <strong>React Hook Form</strong>: 성능 최적화된 폼 관리 라이브러리
              </li>
              <li>
                • <strong>Zod</strong>: TypeScript 우선 스키마 검증 라이브러리
              </li>
              <li>
                • <strong>shadcn/ui</strong>: 접근성 높은 UI 컴포넌트
              </li>
            </ul>
          </div>
        </div>
      </main>
      <Footer />
    </div>
  )
}
