import { ResultsClient } from "./ResultsClient"

// Next.js App Router 서버 컴포넌트: params/searchParams를 클라이언트로 전달
export default async function ResultsPage({
  params,
  searchParams,
}: {
  params: Promise<{ id: string }>
  searchParams: Promise<{ quarter?: string; jiraEmail?: string }>
}) {
  const { id } = await params
  const { quarter, jiraEmail } = await searchParams

  return (
    <ResultsClient
      id={id}
      quarter={quarter ?? "Q1"}
      jiraEmail={jiraEmail}
    />
  )
}
