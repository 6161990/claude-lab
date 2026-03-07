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

// Jira + Confluence 회고 응답
export interface RetrospectiveJiraResponse {
  startDate: string
  endDate: string
  doneIssues: JiraIssue[]
  inProgressIssues: JiraIssue[]
  confluencePages: ConfluencePage[]
  totalDone: number
  totalInProgress: number
}

// POST /api/analyze 응답
export interface AnalyzeResponse {
  userName: string
  startDate: string
  endDate: string
  analysis: string | null       // Claude AI 분석 보고서
  jira: RetrospectiveJiraResponse | null
}
