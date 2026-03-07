"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AnalyzeResponse, JiraIssue, ConfluencePage } from "@/lib/types"

export default function ResultsPage() {
  const [data, setData] = useState<AnalyzeResponse | null>(null)
  const [error, setError] = useState("")

  useEffect(() => {
    try {
      const raw = sessionStorage.getItem("analysisResult")
      if (!raw) throw new Error("분석 결과가 없습니다. 먼저 분석을 실행해주세요.")
      setData(JSON.parse(raw))
    } catch (e) {
      setError(e instanceof Error ? e.message : "데이터를 불러오는 중 오류가 발생했습니다")
    }
  }, [])

  if (error) return <ErrorScreen message={error} />
  if (!data) return <LoadingScreen />

  const { userName, startDate, endDate, analysis, jira } = data

  return (
    <main className="min-h-screen bg-background px-4 py-12">
      <div className="max-w-2xl mx-auto space-y-10">

        {/* 헤더 */}
        <div className="space-y-1">
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            ← 다시 분석하기
          </Link>
          <h1 className="text-2xl font-bold mt-2">회고 보고서</h1>
          <p className="text-muted-foreground text-sm">
            {userName} · {startDate} ~ {endDate}
          </p>
        </div>

        {/* Claude AI 분석 */}
        {analysis ? (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide flex items-center gap-2">
              AI 전문가 분석
              <span className="text-xs font-normal normal-case px-2 py-0.5 rounded-full bg-primary/10 text-primary">
                Claude
              </span>
            </h2>
            <AnalysisRenderer text={analysis} />
          </section>
        ) : (
          <section className="rounded-xl border bg-muted/40 px-5 py-8 text-center text-sm text-muted-foreground">
            ANTHROPIC_API_KEY를 설정하면 AI 분석 보고서가 생성됩니다
          </section>
        )}

        {/* Jira 섹션 */}
        {jira && (
          <>
            <section className="space-y-3">
              <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                완료한 Jira 이슈 <span className="text-foreground font-bold">{jira.totalDone}</span>개
              </h2>
              {jira.doneIssues.length > 0
                ? <IssueList issues={jira.doneIssues} />
                : <EmptyState text="해당 기간에 완료된 이슈가 없습니다" />}
            </section>

            {jira.inProgressIssues.length > 0 && (
              <section className="space-y-3">
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  진행 중인 Jira 이슈 <span className="text-foreground font-bold">{jira.totalInProgress}</span>개
                </h2>
                <IssueList issues={jira.inProgressIssues} />
              </section>
            )}

            {jira.confluencePages.length > 0 && (
              <section className="space-y-3">
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  Confluence 기여 페이지 <span className="text-foreground font-bold">{jira.confluencePages.length}</span>개
                </h2>
                <ConfluenceList pages={jira.confluencePages} />
              </section>
            )}
          </>
        )}

      </div>
    </main>
  )
}

// ============================================================
// 마크다운 렌더러 (의존성 없이 간단 파싱)
// ============================================================

function AnalysisRenderer({ text }: { text: string }) {
  const lines = text.split("\n")

  return (
    <div className="rounded-xl border bg-card p-6 space-y-1">
      {lines.map((line, i) => {
        if (line.startsWith("# ")) {
          return <h2 key={i} className="text-lg font-bold mt-5 mb-2 first:mt-0">{line.slice(2)}</h2>
        }
        if (line.startsWith("## ")) {
          return <h3 key={i} className="text-base font-semibold mt-4 mb-1">{line.slice(3)}</h3>
        }
        if (line.startsWith("### ")) {
          return <h4 key={i} className="text-sm font-semibold mt-3 mb-1">{line.slice(4)}</h4>
        }
        if (line.startsWith("- ") || line.startsWith("• ")) {
          return (
            <p key={i} className="text-sm text-foreground/90 pl-3 before:content-['·'] before:mr-2 before:text-muted-foreground">
              {line.slice(2)}
            </p>
          )
        }
        if (/^\d+\.\s/.test(line)) {
          return <p key={i} className="text-sm text-foreground/90 pl-3">{line}</p>
        }
        if (line.startsWith("**") && line.endsWith("**")) {
          return <p key={i} className="text-sm font-semibold mt-3">{line.slice(2, -2)}</p>
        }
        if (line.trim() === "" || line.trim() === "---") {
          return <div key={i} className="h-3" />
        }
        // 인라인 볼드 처리
        const parts = line.split(/\*\*(.*?)\*\*/g)
        return (
          <p key={i} className="text-sm text-foreground/90 leading-relaxed">
            {parts.map((part, j) =>
              j % 2 === 1 ? <strong key={j}>{part}</strong> : part
            )}
          </p>
        )
      })}
    </div>
  )
}

// ============================================================
// 서브 컴포넌트
// ============================================================

function IssueList({ issues }: { issues: JiraIssue[] }) {
  return (
    <ul className="rounded-xl border bg-card divide-y">
      {issues.map((issue) => (
        <li key={issue.key} className="px-5 py-3.5 flex items-start gap-3">
          <span className="text-xs text-muted-foreground font-mono shrink-0 mt-0.5 w-20">{issue.key}</span>
          <div className="flex-1 min-w-0 space-y-0.5">
            <a href={issue.url} target="_blank" rel="noopener noreferrer"
              className="text-sm font-medium hover:underline underline-offset-4 line-clamp-2">
              {issue.summary}
            </a>
            <p className="text-xs text-muted-foreground">
              {issue.issueType} · {issue.project}
              {issue.priority !== "없음" && ` · ${issue.priority}`}
            </p>
          </div>
          <span className={[
            "shrink-0 text-xs px-2 py-0.5 rounded-full font-medium",
            issue.statusCategory === "done"
              ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
              : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
          ].join(" ")}>
            {issue.status}
          </span>
        </li>
      ))}
    </ul>
  )
}

function ConfluenceList({ pages }: { pages: ConfluencePage[] }) {
  return (
    <ul className="rounded-xl border bg-card divide-y">
      {pages.map((page) => (
        <li key={page.id} className="px-5 py-3.5">
          <a href={page.url} target="_blank" rel="noopener noreferrer"
            className="text-sm font-medium hover:underline underline-offset-4 line-clamp-2">
            {page.title}
          </a>
          <p className="text-xs text-muted-foreground mt-0.5">
            {page.spaceName} · 최종 수정 {page.lastUpdated.slice(0, 10)} · {page.lastUpdatedBy}
          </p>
        </li>
      ))}
    </ul>
  )
}

function EmptyState({ text }: { text: string }) {
  return (
    <div className="rounded-xl border bg-card px-5 py-8 text-center text-sm text-muted-foreground">
      {text}
    </div>
  )
}

function LoadingScreen() {
  return (
    <main className="min-h-screen flex items-center justify-center">
      <div className="text-center space-y-3">
        <div className="inline-block h-6 w-6 rounded-full border-2 border-primary border-r-transparent animate-spin" />
        <p className="text-sm text-muted-foreground">결과를 불러오는 중...</p>
      </div>
    </main>
  )
}

function ErrorScreen({ message }: { message: string }) {
  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <div className="text-center space-y-4 max-w-sm">
        <p className="text-sm text-destructive">{message}</p>
        <Link href="/" className="inline-block text-sm text-muted-foreground hover:text-foreground underline underline-offset-4">
          처음으로 돌아가기
        </Link>
      </div>
    </main>
  )
}
