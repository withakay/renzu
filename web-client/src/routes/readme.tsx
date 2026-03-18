import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { ExternalLink, Github } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardTitle } from '@/components/ui/card'

const githubRepoUrl = (import.meta.env.VITE_GITHUB_REPO_URL as string | undefined) ?? 'https://github.com/withakay/renzu'

function rawReadmeUrl(repoUrl: string): string {
  if (repoUrl.includes('github.com/')) {
    return repoUrl.replace('github.com/', 'raw.githubusercontent.com/') + '/main/README.md'
  }
  return repoUrl
}

export function ReadmePage() {
  const readmeUrl = useMemo(() => rawReadmeUrl(githubRepoUrl), [])

  const readmeQuery = useQuery({
    queryKey: ['github-readme', readmeUrl],
    queryFn: async () => {
      const response = await fetch(readmeUrl)
      if (!response.ok) {
        throw new Error(`Failed to fetch README (${response.status})`)
      }
      return response.text()
    },
  })

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <header className="rounded-2xl border border-slate-200 bg-gradient-to-r from-white via-slate-50 to-cyan-50 p-6 shadow-sm">
        <h1 className="text-3xl font-semibold text-slate-900">README + Repository</h1>
        <p className="mt-2 text-sm text-slate-600">Reference documentation and repository links for Renzu.</p>
      </header>

      <Card className="space-y-4">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <CardTitle>GitHub Repository</CardTitle>
            <CardDescription>Open the source repository and README directly.</CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              className="gap-2"
              onClick={() => window.open(githubRepoUrl, '_blank', 'noopener,noreferrer')}
            >
              <Github className="h-4 w-4" />
              Repository
            </Button>
            <Button className="gap-2" onClick={() => window.open(readmeUrl, '_blank', 'noopener,noreferrer')}>
              README Raw
              <ExternalLink className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </Card>

      <Card className="space-y-3">
        <CardTitle>README Preview</CardTitle>
        <CardDescription>Fetched from the GitHub `main` branch.</CardDescription>
        {readmeQuery.isPending ? <p className="text-sm text-slate-600">Loading README...</p> : null}
        {readmeQuery.error instanceof Error ? (
          <p className="text-sm text-rose-600">Unable to load README: {readmeQuery.error.message}</p>
        ) : null}
        {readmeQuery.data ? (
          <pre className="max-h-[60vh] overflow-auto rounded-md bg-slate-950 p-4 text-xs leading-relaxed text-slate-100">
            {readmeQuery.data}
          </pre>
        ) : null}
      </Card>
    </main>
  )
}
