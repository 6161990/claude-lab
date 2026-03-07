import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Zap,
  Moon,
  Shield,
  Palette,
  CheckCircle,
  Smartphone,
} from "lucide-react"

/**
 * 기능 카드 타입
 */
interface Feature {
  icon: React.ReactNode
  title: string
  description: string
}

/**
 * 기능 목록 정의
 */
const features: Feature[] = [
  {
    icon: <Zap className="h-10 w-10 text-primary" />,
    title: "최신 기술 스택",
    description: "Next.js 16 + React 19로 최신 웹 개발 경험을 제공합니다",
  },
  {
    icon: <Moon className="h-10 w-10 text-primary" />,
    title: "다크모드 지원",
    description: "라이트/다크 테마를 자유롭게 전환할 수 있습니다",
  },
  {
    icon: <Shield className="h-10 w-10 text-primary" />,
    title: "타입 안전성",
    description: "TypeScript로 완전한 타입 안전성을 보장합니다",
  },
  {
    icon: <Palette className="h-10 w-10 text-primary" />,
    title: "UI 컴포넌트",
    description: "shadcn/ui 컴포넌트가 기본으로 제공됩니다",
  },
  {
    icon: <CheckCircle className="h-10 w-10 text-primary" />,
    title: "폼 검증",
    description: "React Hook Form + Zod로 타입 안전한 폼 검증",
  },
  {
    icon: <Smartphone className="h-10 w-10 text-primary" />,
    title: "반응형 디자인",
    description: "모바일 우선 레이아웃으로 모든 기기에 최적화",
  },
]

/**
 * 기능 소개 섹션 컴포넌트
 * 6개의 기능 카드를 그리드 레이아웃으로 표시
 */
export function FeaturesSection() {
  return (
    <section className="container py-24 md:py-32">
      <div className="flex flex-col items-center gap-12">
        {/* 섹션 타이틀 */}
        <div className="flex flex-col items-center gap-4 text-center">
          <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl">
            주요 기능
          </h2>
          <p className="max-w-[700px] text-lg text-muted-foreground">
            프로덕션 준비된 스타터킷의 핵심 기능들
          </p>
        </div>

        {/* 기능 카드 그리드 */}
        <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 w-full">
          {features.map((feature, index) => (
            <Card key={index} className="border-2 hover:border-primary/50 transition-colors">
              <CardHeader>
                <div className="flex items-center gap-4">
                  {feature.icon}
                  <CardTitle>{feature.title}</CardTitle>
                </div>
              </CardHeader>
              <CardContent>
                <p className="text-muted-foreground">{feature.description}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  )
}
