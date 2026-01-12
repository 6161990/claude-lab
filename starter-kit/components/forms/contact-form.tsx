"use client"

import * as React from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { contactFormSchema, type ContactFormValues } from "@/lib/validations"

/**
 * 연락처 폼 컴포넌트
 * React Hook Form + Zod를 사용한 타입 안전한 폼 검증 예제
 */
export function ContactForm() {
  const [isSubmitting, setIsSubmitting] = React.useState(false)
  const [submitMessage, setSubmitMessage] = React.useState<string | null>(null)

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
    reset,
  } = useForm<ContactFormValues>({
    resolver: zodResolver(contactFormSchema),
  })

  const contactType = watch("contactType")

  /**
   * 폼 제출 핸들러
   * 실제 API 호출 대신 콘솔 로그 출력
   */
  const onSubmit = async (data: ContactFormValues) => {
    setIsSubmitting(true)
    setSubmitMessage(null)

    try {
      // 실제 API 호출 시뮬레이션 (2초 대기)
      await new Promise((resolve) => setTimeout(resolve, 2000))

      console.log("폼 제출 데이터:", data)

      setSubmitMessage("문의가 성공적으로 제출되었습니다!")
      reset()
    } catch (error) {
      setSubmitMessage("문의 제출 중 오류가 발생했습니다.")
      console.error(error)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      {/* 이름 필드 */}
      <div className="space-y-2">
        <Label htmlFor="name">이름 *</Label>
        <Input
          id="name"
          placeholder="홍길동"
          {...register("name")}
          disabled={isSubmitting}
        />
        {errors.name && (
          <p className="text-sm text-destructive">{errors.name.message}</p>
        )}
      </div>

      {/* 이메일 필드 */}
      <div className="space-y-2">
        <Label htmlFor="email">이메일 *</Label>
        <Input
          id="email"
          type="email"
          placeholder="example@email.com"
          {...register("email")}
          disabled={isSubmitting}
        />
        {errors.email && (
          <p className="text-sm text-destructive">{errors.email.message}</p>
        )}
      </div>

      {/* 문의 유형 필드 */}
      <div className="space-y-2">
        <Label htmlFor="contactType">문의 유형 *</Label>
        <Select
          value={contactType}
          onValueChange={(value) =>
            setValue("contactType", value as ContactFormValues["contactType"], {
              shouldValidate: true,
            })
          }
          disabled={isSubmitting}
        >
          <SelectTrigger id="contactType">
            <SelectValue placeholder="문의 유형을 선택하세요" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="일반 문의">일반 문의</SelectItem>
            <SelectItem value="기술 지원">기술 지원</SelectItem>
            <SelectItem value="제안">제안</SelectItem>
          </SelectContent>
        </Select>
        {errors.contactType && (
          <p className="text-sm text-destructive">
            {errors.contactType.message}
          </p>
        )}
      </div>

      {/* 메시지 필드 */}
      <div className="space-y-2">
        <Label htmlFor="message">메시지 *</Label>
        <Textarea
          id="message"
          placeholder="메시지를 입력하세요 (최소 10자)"
          rows={5}
          {...register("message")}
          disabled={isSubmitting}
        />
        {errors.message && (
          <p className="text-sm text-destructive">{errors.message.message}</p>
        )}
      </div>

      {/* 제출 메시지 */}
      {submitMessage && (
        <div
          className={`p-4 rounded-md ${
            submitMessage.includes("성공")
              ? "bg-green-50 dark:bg-green-950 text-green-800 dark:text-green-200"
              : "bg-red-50 dark:bg-red-950 text-red-800 dark:text-red-200"
          }`}
        >
          {submitMessage}
        </div>
      )}

      {/* 제출 버튼 */}
      <Button type="submit" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? "제출 중..." : "문의하기"}
      </Button>
    </form>
  )
}
