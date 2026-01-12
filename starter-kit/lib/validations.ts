import { z } from "zod"

/**
 * 연락처 폼 검증 스키마
 * React Hook Form + Zod를 사용한 타입 안전한 폼 검증
 */
export const contactFormSchema = z.object({
  name: z
    .string()
    .min(2, "이름은 최소 2자 이상이어야 합니다")
    .max(50, "이름은 최대 50자까지 입력 가능합니다"),

  email: z
    .string()
    .email("올바른 이메일 형식을 입력해주세요"),

  contactType: z.enum(["일반 문의", "기술 지원", "제안"], {
    message: "문의 유형을 선택해주세요",
  }),

  message: z
    .string()
    .min(10, "메시지는 최소 10자 이상이어야 합니다")
    .max(500, "메시지는 최대 500자까지 입력 가능합니다"),
})

/**
 * ContactFormSchema로부터 추론된 타입
 * 폼 데이터 타입 안전성 보장
 */
export type ContactFormValues = z.infer<typeof contactFormSchema>
