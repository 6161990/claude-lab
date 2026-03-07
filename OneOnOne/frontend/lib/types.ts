// Git 분석 요약
export interface GitSummary {
  totalCommits: number
  totalFiles: number
  linesAdded: number
  linesDeleted: number
  commitsByDate: Record<string, number>
}

// Jira 이슈
export interface JiraIssue {
  key: string
  summary: string
  status: string
  statusCategory: string
  issueType: string
  project: string
  projectKey: string
  priority: string
  created: string
  updated: string
  resolutionDate: string | null
  labels: string[]
  url: string
}

// Confluence 페이지
export interface ConfluencePage {
  id: string
  title: string
  spaceKey: string
  spaceName: string
  lastUpdated: string
  lastUpdatedBy: string
  url: string
}

// Jira 회고 종합 응답
export interface RetrospectiveJiraResponse {
  quarter: string
  doneIssues: JiraIssue[]
  inProgressIssues: JiraIssue[]
  confluencePages: ConfluencePage[]
  totalDone: number
  totalInProgress: number
}

// POST /api/analyze 통합 응답
export interface AnalyzeResponse {
  userName: string
  quarter: string
  git: GitSummary
  jira: RetrospectiveJiraResponse | null
}
