"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { AnalyzeResponse, JiraIssue } from "@/lib/types"

// ============================================================
// 메인 컴포넌트
// ============================================================

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

  const { userName, quarter, git, jira } = data

  return (
    <main className="min-h-screen bg-background px-4 py-12">
      <div className="max-w-2xl mx-auto space-y-10">

        {/* 헤더 */}
        <div className="space-y-1">
          <Link
            href="/"
            className="text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            ← 다시 분석하기
          </Link>
          <h1 className="text-2xl font-bold mt-2">{quarter} 회고</h1>
          <p className="text-muted-foreground text-sm">{userName}</p>
        </div>

        {/* Git 통계 카드 */}
        <section className="space-y-3">
          <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
            Git 활동 요약
          </h2>
          <div className="grid grid-cols-2 gap-3">
            <StatCard label="총 커밋" value={git.totalCommits} unit="회" />
            <StatCard label="변경 파일" value={git.totalFiles} unit="개" />
            <StatCard label="추가 라인" value={git.linesAdded} unit="줄" accent="green" />
            <StatCard label="삭제 라인" value={git.linesDeleted} unit="줄" accent="red" />
          </div>
        </section>

        {/* 커밋 활동 차트 */}
        {Object.keys(git.commitsByDate).length > 0 && (
          <section className="space-y-3">
            <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
              날짜별 커밋 활동
            </h2>
            <ActivityChart data={git.commitsByDate} />
          </section>
        )}

        {/* Jira 섹션 */}
        {jira && (
          <>
            {/* 완료 이슈 */}
            <section className="space-y-3">
              <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                완료한 Jira 이슈{" "}
                <span className="text-foreground font-bold">{jira.totalDone}</span>개
              </h2>
              {jira.doneIssues.length > 0 ? (
                <IssueList issues={jira.doneIssues} />
              ) : (
                <EmptyState text="해당 분기에 완료된 이슈가 없습니다" />
              )}
            </section>

            {/* 진행 중 이슈 */}
            {jira.inProgressIssues.length > 0 && (
              <section className="space-y-3">
                <h2 className="text-sm font-semibold text-muted-foreground uppercase tracking-wide">
                  진행 중인 Jira 이슈{" "}
                  <span className="text-foreground font-bold">{jira.totalInProgress}</span>개
                </h2>
                <IssueList issues={jira.inProgressIssues} />
              </section>
            )}
          </>
        )}

      </div>
    </main>
  )
}

// ============================================================
// 서브 컴포넌트
// ============================================================

function StatCard({
  label,
  value,
  unit,
  accent,
}: {
  label: string
  value: number
  unit: string
  accent?: "green" | "red"
}) {
  const valueClass =
    accent === "green"
      ? "text-emerald-600 dark:text-emerald-400"
      : accent === "red"
        ? "text-rose-600 dark:text-rose-400"
        : "text-foreground"

  return (
    <div className="rounded-xl border bg-card p-5 space-y-1">
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className={`text-2xl font-bold ${valueClass}`}>
        {value.toLocaleString()}
        <span className="text-sm font-normal text-muted-foreground ml-1">{unit}</span>
      </p>
    </div>
  )
}

function ActivityChart({ data }: { data: Record<string, number> }) {
  const entries = Object.entries(data).sort(([a], [b]) => a.localeCompare(b))
  const max = Math.max(...entries.map(([, v]) => v), 1)

  return (
    <div className="rounded-xl border bg-card p-5 space-y-2.5">
      {entries.map(([date, count]) => (
        <div key={date} className="flex items-center gap-3 text-xs">
          <span className="text-muted-foreground w-20 shrink-0 tabular-nums">
            {date.slice(0, 10)}
          </span>
          <div className="flex-1 bg-muted rounded-full h-1.5 overflow-hidden">
            <div
              className="bg-primary h-full rounded-full"
              style={{ width: `${(count / max) * 100}%` }}
            />
          </div>
          <span className="w-6 text-right text-muted-foreground tabular-nums">{count}</span>
        </div>
      ))}
    </div>
  )
}

function IssueList({ issues }: { issues: JiraIssue[] }) {
  return (
    <ul className="rounded-xl border bg-card divide-y">
      {issues.map((issue) => (
        <li key={issue.key} className="px-5 py-3.5 flex items-start gap-3">
          <span className="text-xs text-muted-foreground font-mono shrink-0 mt-0.5 w-20">
            {issue.key}
          </span>
          <div className="flex-1 min-w-0 space-y-0.5">
            <a
              href={issue.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-sm font-medium hover:underline underline-offset-4 line-clamp-2"
            >
              {issue.summary}
            </a>
            <p className="text-xs text-muted-foreground">
              {issue.issueType} · {issue.project}
              {issue.priority !== "없음" && ` · ${issue.priority}`}
            </p>
          </div>
          <span
            className={[
              "shrink-0 text-xs px-2 py-0.5 rounded-full font-medium",
              issue.statusCategory === "done"
                ? "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400"
                : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400",
            ].join(" ")}
          >
            {issue.status}
          </span>
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
        <Link
          href="/"
          className="inline-block text-sm text-muted-foreground hover:text-foreground underline underline-offset-4"
        >
          처음으로 돌아가기
        </Link>
      </div>
    </main>
  )
}
