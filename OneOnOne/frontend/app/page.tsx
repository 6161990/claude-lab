"use client"

import { useState, useRef, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AnalyzeResponse } from "@/lib/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"

export default function Home() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [files, setFiles] = useState<File[]>([])
  const [gitEmail, setGitEmail] = useState("")
  const [quarter, setQuarter] = useState("Q1")
  const [jiraEmail, setJiraEmail] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const addFiles = (incoming: FileList | File[]) => {
    const zips = Array.from(incoming).filter((f) => f.name.endsWith(".zip"))
    if (zips.length === 0) return
    setFiles((prev) => [...prev, ...zips])
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    addFiles(e.dataTransfer.files)
  }, [])

  const handleSubmit = async () => {
    if (!files.length || !gitEmail.trim()) return
    setIsLoading(true)
    setError("")

    try {
      const formData = new FormData()
      files.forEach((f) => formData.append("repositories", f))
      formData.append("userName", gitEmail.trim())
      formData.append("quarter", quarter)
      if (jiraEmail.trim()) formData.append("jiraEmail", jiraEmail.trim())

      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      })

      if (!res.ok) {
        const msg = await res.text().catch(() => "")
        throw new Error(`서버 오류 (${res.status})${msg ? `: ${msg}` : ""}`)
      }

      const data: AnalyzeResponse = await res.json()

      // 결과를 sessionStorage에 저장 후 results 페이지로 이동
      sessionStorage.setItem("analysisResult", JSON.stringify(data))
      router.push("/results")
    } catch (e) {
      setError(e instanceof Error ? e.message : "알 수 없는 오류가 발생했습니다")
    } finally {
      setIsLoading(false)
    }
  }

  const canSubmit = files.length > 0 && gitEmail.trim().length > 0 && !isLoading

  return (
    <main className="min-h-screen flex items-center justify-center bg-background px-4">
      <div className="w-full max-w-md space-y-8">

        {/* 타이틀 */}
        <div className="text-center space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">OneOnOne 회고</h1>
          <p className="text-muted-foreground text-sm">
            Git 저장소를 업로드하여 분기 회고를 생성하세요
          </p>
        </div>

        {/* ZIP 파일 업로드 영역 */}
        <div
          onClick={() => fileInputRef.current?.click()}
          onDragOver={(e) => { e.preventDefault(); setIsDragging(true) }}
          onDragLeave={() => setIsDragging(false)}
          onDrop={handleDrop}
          className={[
            "border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-colors select-none",
            isDragging
              ? "border-primary bg-primary/5"
              : "border-muted-foreground/30 hover:border-primary/50 hover:bg-muted/30",
          ].join(" ")}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".zip"
            multiple
            className="hidden"
            onChange={(e) => e.target.files && addFiles(e.target.files)}
          />
          <div className="space-y-2 pointer-events-none">
            <div className="text-4xl">📁</div>
            <p className="font-medium text-sm">ZIP 파일을 드래그하거나 클릭하여 업로드</p>
            <p className="text-xs text-muted-foreground">여러 저장소 동시 업로드 가능</p>
          </div>
        </div>

        {/* 선택된 파일 목록 */}
        {files.length > 0 && (
          <ul className="space-y-1.5">
            {files.map((f, i) => (
              <li
                key={i}
                className="flex items-center justify-between text-sm bg-muted rounded-lg px-3 py-2"
              >
                <span className="truncate text-muted-foreground text-xs">📄 {f.name}</span>
                <button
                  onClick={() => setFiles((prev) => prev.filter((_, idx) => idx !== i))}
                  className="ml-2 text-muted-foreground hover:text-destructive shrink-0 text-xs"
                >
                  ✕
                </button>
              </li>
            ))}
          </ul>
        )}

        {/* 입력 폼 */}
        <div className="space-y-4">
          {/* Git 이메일 */}
          <div className="space-y-1.5">
            <Label htmlFor="gitEmail">Git 이메일 또는 이름</Label>
            <Input
              id="gitEmail"
              type="text"
              placeholder="author@example.com"
              value={gitEmail}
              onChange={(e) => setGitEmail(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && canSubmit && handleSubmit()}
            />
          </div>

          {/* 분기 선택 */}
          <div className="space-y-1.5">
            <Label>분기</Label>
            <div className="grid grid-cols-4 gap-2">
              {(["Q1", "Q2", "Q3", "Q4"] as const).map((q) => (
                <button
                  key={q}
                  onClick={() => setQuarter(q)}
                  className={[
                    "py-2 rounded-lg text-sm font-medium border transition-colors",
                    quarter === q
                      ? "bg-primary text-primary-foreground border-primary"
                      : "border-muted-foreground/30 hover:border-primary/50",
                  ].join(" ")}
                >
                  {q}
                </button>
              ))}
            </div>
          </div>

          {/* Jira 이메일 (선택) */}
          <div className="space-y-1.5">
            <Label htmlFor="jiraEmail">
              Jira 이메일{" "}
              <span className="text-muted-foreground font-normal text-xs">
                (선택 — 입력 시 Jira 티켓 포함)
              </span>
            </Label>
            <Input
              id="jiraEmail"
              type="email"
              placeholder="jira@company.com"
              value={jiraEmail}
              onChange={(e) => setJiraEmail(e.target.value)}
            />
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <p className="text-sm text-destructive text-center rounded-lg bg-destructive/10 px-4 py-2">
            {error}
          </p>
        )}

        {/* 제출 버튼 */}
        <Button
          onClick={handleSubmit}
          disabled={!canSubmit}
          className="w-full"
          size="lg"
        >
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block h-4 w-4 rounded-full border-2 border-current border-r-transparent animate-spin" />
              분석 중...
            </span>
          ) : (
            "분석 시작 →"
          )}
        </Button>
      </div>
    </main>
  )
}
