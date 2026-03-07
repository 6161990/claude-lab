"use client"

import { useState, useRef, useCallback } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { AnalyzeResponse } from "@/lib/types"

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8080"
const MAX_ZIP_SIZE_MB = 500
const MAX_ZIP_COUNT = 3

function formatBytes(bytes: number) {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function getDefaultDates() {
  const today = new Date()
  const year = today.getFullYear()
  const q = Math.floor(today.getMonth() / 3)
  const starts = ["-01-01", "-04-01", "-07-01", "-10-01"]
  const ends   = ["-03-31", "-06-30", "-09-30", "-12-31"]
  return { startDate: `${year}${starts[q]}`, endDate: `${year}${ends[q]}` }
}

export default function Home() {
  const router = useRouter()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const { startDate: defaultStart, endDate: defaultEnd } = getDefaultDates()

  const [files, setFiles] = useState<File[]>([])
  const [gitEmail, setGitEmail] = useState("")
  const [startDate, setStartDate] = useState(defaultStart)
  const [endDate, setEndDate] = useState(defaultEnd)
  const [jiraEmail, setJiraEmail] = useState("")
  const [customPrompt, setCustomPrompt] = useState("")
  const [isDragging, setIsDragging] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")

  const validateAndAddFiles = (incoming: FileList | File[]) => {
    const zips = Array.from(incoming).filter((f) => f.name.endsWith(".zip"))
    if (zips.length === 0) {
      setError("ZIP 파일만 업로드할 수 있습니다.")
      return
    }

    const oversized = zips.find((f) => f.size > MAX_ZIP_SIZE_MB * 1024 * 1024)
    if (oversized) {
      setError(
        `'${oversized.name}' (${formatBytes(oversized.size)})이 ${MAX_ZIP_SIZE_MB}MB를 초과합니다.\n` +
        `GitHub 저장소 1개를 ZIP으로 다운로드한 파일을 업로드해주세요.`
      )
      return
    }

    setFiles((prev) => {
      const next = [...prev, ...zips]
      if (next.length > MAX_ZIP_COUNT) {
        setError(`ZIP 파일은 최대 ${MAX_ZIP_COUNT}개까지 업로드할 수 있습니다.`)
        return prev
      }
      setError("")
      return next
    })
  }

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragging(false)
    validateAndAddFiles(e.dataTransfer.files)
  }, [])

  const handleSubmit = async () => {
    if (!files.length || !gitEmail.trim() || !startDate || !endDate) return
    setIsLoading(true)
    setError("")

    try {
      const formData = new FormData()
      files.forEach((f) => formData.append("repositories", f))
      formData.append("userName", gitEmail.trim())
      formData.append("startDate", startDate)
      formData.append("endDate", endDate)
      if (jiraEmail.trim()) formData.append("jiraEmail", jiraEmail.trim())
      if (customPrompt.trim()) formData.append("customPrompt", customPrompt.trim())

      const res = await fetch(`${API_URL}/api/analyze`, {
        method: "POST",
        body: formData,
      })

      const json = await res.json()

      if (!res.ok) {
        throw new Error(json?.error || `서버 오류 (${res.status})`)
      }

      const data: AnalyzeResponse = json
      sessionStorage.setItem("analysisResult", JSON.stringify(data))
      router.push("/results")
    } catch (e) {
      setError(e instanceof Error ? e.message : "알 수 없는 오류가 발생했습니다")
    } finally {
      setIsLoading(false)
    }
  }

  const canSubmit = files.length > 0 && gitEmail.trim().length > 0 && !!startDate && !!endDate && !isLoading

  return (
    <main className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md space-y-8">

        {/* 타이틀 */}
        <div className="text-center space-y-1">
          <h1 className="text-3xl font-bold tracking-tight">OneOnOne 회고</h1>
          <p className="text-muted-foreground text-sm">
            GitHub 저장소를 업로드하면 AI가 코드를 분석하고 회고 보고서를 작성합니다
          </p>
        </div>

        {/* ZIP 업로드 영역 */}
        <div className="space-y-2">
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
              onChange={(e) => e.target.files && validateAndAddFiles(e.target.files)}
            />
            <div className="space-y-2 pointer-events-none">
              <div className="text-4xl">📁</div>
              <p className="font-medium text-sm">ZIP 파일을 드래그하거나 클릭하여 업로드</p>
              <p className="text-xs text-muted-foreground">
                GitHub 저장소 1개 = ZIP 1개 · 최대 {MAX_ZIP_MB}MB · 최대 {MAX_ZIP_COUNT}개
              </p>
            </div>
          </div>

          {/* 업로드 안내 */}
          <div className="rounded-lg bg-muted/50 px-4 py-3 text-xs text-muted-foreground space-y-1">
            <p className="font-medium text-foreground/70">ZIP 파일 준비 방법</p>
            <p>터미널에서 아래 명령어를 실행하세요 (저장소 폴더 기준):</p>
            <code className="block bg-muted px-2 py-1 rounded font-mono text-xs">
              zip -r repo.zip . --exclude "*/node_modules/*" "*/build/*" "*/.next/*"
            </code>
            <p className="text-muted-foreground/70">
              ⚠️ GitHub의 "Download ZIP"은 커밋 이력이 없어 분석 불가.
              반드시 로컬 저장소를 직접 압축하세요.
            </p>
          </div>
        </div>

        {/* 선택된 파일 목록 */}
        {files.length > 0 && (
          <ul className="space-y-1.5">
            {files.map((f, i) => (
              <li key={i} className="flex items-center justify-between text-sm bg-muted rounded-lg px-3 py-2">
                <div className="flex items-center gap-2 min-w-0">
                  <span className="text-xs">📄</span>
                  <span className="truncate text-muted-foreground text-xs">{f.name}</span>
                  <span className="text-xs text-muted-foreground/60 shrink-0">{formatBytes(f.size)}</span>
                </div>
                <button
                  onClick={() => { setFiles((prev) => prev.filter((_, idx) => idx !== i)); setError("") }}
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
          <div className="space-y-1.5">
            <Label htmlFor="gitEmail">Git 이메일 또는 이름</Label>
            <Input
              id="gitEmail"
              type="text"
              placeholder="author 또는 홍길동"
              value={gitEmail}
              onChange={(e) => setGitEmail(e.target.value)}
            />
            <p className="text-xs text-muted-foreground">git log에 표시되는 이름 또는 이메일</p>
          </div>

          <div className="space-y-1.5">
            <Label>분석 기간</Label>
            <div className="grid grid-cols-2 gap-2">
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">시작일</p>
                <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </div>
              <div className="space-y-1">
                <p className="text-xs text-muted-foreground">종료일</p>
                <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
              </div>
            </div>
          </div>

          <div className="space-y-1.5">
            <Label htmlFor="jiraEmail">
              Jira 이메일{" "}
              <span className="text-muted-foreground font-normal text-xs">
                (선택 — 입력 시 Jira 이슈 + Confluence 페이지 포함)
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

          <div className="space-y-1.5">
            <Label htmlFor="customPrompt">
              추가 분석 요청{" "}
              <span className="text-muted-foreground font-normal text-xs">(선택)</span>
            </Label>
            <textarea
              id="customPrompt"
              className="w-full rounded-md border border-input bg-background px-3 py-2 text-sm resize-none min-h-[80px]"
              placeholder="예: 1:1 미팅 관점에서 성장 포인트를 중심으로 분석해주세요"
              value={customPrompt}
              onChange={(e) => setCustomPrompt(e.target.value)}
            />
          </div>
        </div>

        {/* 에러 메시지 */}
        {error && (
          <p className="text-sm text-destructive text-center rounded-lg bg-destructive/10 px-4 py-2 whitespace-pre-line">
            {error}
          </p>
        )}

        <Button onClick={handleSubmit} disabled={!canSubmit} className="w-full" size="lg">
          {isLoading ? (
            <span className="flex items-center gap-2">
              <span className="inline-block h-4 w-4 rounded-full border-2 border-current border-r-transparent animate-spin" />
              분석 중... (코드량에 따라 수분 소요될 수 있습니다)
            </span>
          ) : (
            "분석 시작 →"
          )}
        </Button>
      </div>
    </main>
  )
}

const MAX_ZIP_MB = MAX_ZIP_SIZE_MB
