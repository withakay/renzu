import { type ReactNode, useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { Activity, FileCode2, Search, Sparkles } from 'lucide-react'

import { JsonPanel } from '@/components/json-panel'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { renzuApi } from '@/lib/api'

function sectionTitle(icon: ReactNode, title: string, subtitle: string) {
  return (
    <div className="mb-3 flex items-start gap-3">
      <div className="rounded-md bg-sky-100 p-2 text-sky-700">{icon}</div>
      <div>
        <h2 className="text-lg font-semibold text-slate-900">{title}</h2>
        <p className="text-sm text-slate-600">{subtitle}</p>
      </div>
    </div>
  )
}

export function HomePage() {
  const [repoId, setRepoId] = useState('renzu')
  const [indexPath, setIndexPath] = useState('/workspace')
  const [globsInput, setGlobsInput] = useState('src/**/*.py\ntests/**/*.py')

  const [query, setQuery] = useState('mcp server registration')
  const [topK, setTopK] = useState(5)

  const [snippetPath, setSnippetPath] = useState('src/app/mcp/server.py')
  const [startLine, setStartLine] = useState(1)
  const [endLine, setEndLine] = useState(80)

  const [glassPath, setGlassPath] = useState('src/app/mcp/server.py')
  const [symbolId, setSymbolId] = useState('')

  const health = useQuery({ queryKey: ['healthz'], queryFn: renzuApi.healthz, refetchInterval: 15000 })
  const ready = useQuery({ queryKey: ['readyz'], queryFn: renzuApi.readyz, refetchInterval: 15000 })

  const indexMutation = useMutation({
    mutationFn: () =>
      renzuApi.index({
        repo_id: repoId,
        path: indexPath,
        globs: globsInput
          .split('\n')
          .map((item) => item.trim())
          .filter(Boolean),
      }),
  })

  const searchMutation = useMutation({
    mutationFn: () => renzuApi.search({ repo_id: repoId, query, top_k: topK }),
  })

  const snippetMutation = useMutation({
    mutationFn: () =>
      renzuApi.snippet({ repo_id: repoId, path: snippetPath, start_line: startLine, end_line: endLine, context_lines: 0 }),
  })

  const glassListMutation = useMutation({
    mutationFn: () => renzuApi.glassListSymbols({ repo_id: repoId, path: glassPath }),
    onSuccess: (payload) => {
      const first = Array.isArray(payload.data) ? payload.data[0] : undefined
      if (first && typeof first === 'object' && first !== null && 'symbol_id' in first) {
        setSymbolId(String((first as Record<string, unknown>).symbol_id ?? ''))
      }
    },
  })

  const glassDescribeMutation = useMutation({
    mutationFn: () => renzuApi.glassDescribe({ symbol_id: symbolId }),
  })

  const glassReferencesMutation = useMutation({
    mutationFn: () => renzuApi.glassReferences({ symbol_id: symbolId }),
  })

  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <header className="rounded-2xl border border-slate-200 bg-gradient-to-r from-white via-sky-50 to-cyan-50 p-6 shadow-sm">
        <div className="flex flex-wrap items-center gap-3">
          <Badge>Renzu Client</Badge>
          <Badge className="border-emerald-200 bg-emerald-50 text-emerald-700">TanStack + shadcn</Badge>
        </div>
        <h1 className="mt-3 text-3xl font-semibold text-slate-900">Search code without curl</h1>
        <p className="mt-2 max-w-3xl text-sm text-slate-600">
          Index repositories, run semantic search, fetch snippets, and explore symbol data from one static UI.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        <JsonPanel
          title="Health"
          description="Service liveness status"
          value={health.data ?? (health.error instanceof Error ? { error: health.error.message } : {})}
        />
        <JsonPanel
          title="Readiness"
          description="Dependency readiness status"
          value={ready.data ?? (ready.error instanceof Error ? { error: ready.error.message } : {})}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="space-y-3">
          {sectionTitle(<Activity className="h-5 w-5" />, 'Index Repository', 'POST /v1/index')}
          <Input value={repoId} onChange={(event) => setRepoId(event.target.value)} placeholder="repo id" />
          <Input value={indexPath} onChange={(event) => setIndexPath(event.target.value)} placeholder="path" />
          <Textarea value={globsInput} onChange={(event) => setGlobsInput(event.target.value)} />
          <Button onClick={() => indexMutation.mutate()} disabled={indexMutation.isPending}>
            {indexMutation.isPending ? 'Indexing...' : 'Run Index'}
          </Button>
        </Card>
        <JsonPanel
          title="Index Response"
          description="Chunk ingestion output"
          value={indexMutation.data ?? (indexMutation.error instanceof Error ? { error: indexMutation.error.message } : {})}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="space-y-3">
          {sectionTitle(<Search className="h-5 w-5" />, 'Semantic Search', 'POST /v1/search')}
          <Input value={repoId} onChange={(event) => setRepoId(event.target.value)} placeholder="repo id" />
          <Input value={query} onChange={(event) => setQuery(event.target.value)} placeholder="query" />
          <Input
            type="number"
            min={1}
            max={100}
            value={topK}
            onChange={(event) => setTopK(Number(event.target.value || 5))}
          />
          <Button onClick={() => searchMutation.mutate()} disabled={searchMutation.isPending}>
            {searchMutation.isPending ? 'Searching...' : 'Run Search'}
          </Button>
        </Card>
        <JsonPanel
          title="Search Response"
          description="Semantic matches"
          value={searchMutation.data ?? (searchMutation.error instanceof Error ? { error: searchMutation.error.message } : {})}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="space-y-3">
          {sectionTitle(<FileCode2 className="h-5 w-5" />, 'Snippet Fetch', 'POST /v1/snippet')}
          <Input value={repoId} onChange={(event) => setRepoId(event.target.value)} placeholder="repo id" />
          <Input value={snippetPath} onChange={(event) => setSnippetPath(event.target.value)} placeholder="path" />
          <div className="grid grid-cols-2 gap-3">
            <Input type="number" min={1} value={startLine} onChange={(event) => setStartLine(Number(event.target.value || 1))} />
            <Input type="number" min={1} value={endLine} onChange={(event) => setEndLine(Number(event.target.value || 1))} />
          </div>
          <Button onClick={() => snippetMutation.mutate()} disabled={snippetMutation.isPending}>
            {snippetMutation.isPending ? 'Loading...' : 'Fetch Snippet'}
          </Button>
        </Card>
        <JsonPanel
          title="Snippet Response"
          description="Repository excerpt"
          value={snippetMutation.data ?? (snippetMutation.error instanceof Error ? { error: snippetMutation.error.message } : {})}
        />
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <Card className="space-y-3">
          {sectionTitle(<Sparkles className="h-5 w-5" />, 'Glass: List Symbols', 'POST /v1/glass/list_symbols')}
          <Input value={repoId} onChange={(event) => setRepoId(event.target.value)} placeholder="repo id" />
          <Input value={glassPath} onChange={(event) => setGlassPath(event.target.value)} placeholder="path" />
          <Button onClick={() => glassListMutation.mutate()} disabled={glassListMutation.isPending}>
            {glassListMutation.isPending ? 'Listing...' : 'List Symbols'}
          </Button>

          <CardTitle className="pt-2">Glass: Describe / References</CardTitle>
          <CardDescription>Use a symbol id returned from list_symbols.</CardDescription>
          <Input value={symbolId} onChange={(event) => setSymbolId(event.target.value)} placeholder="symbol_id" />
          <div className="flex gap-2">
            <Button variant="outline" onClick={() => glassDescribeMutation.mutate()} disabled={glassDescribeMutation.isPending || !symbolId}>
              Describe
            </Button>
            <Button variant="outline" onClick={() => glassReferencesMutation.mutate()} disabled={glassReferencesMutation.isPending || !symbolId}>
              References
            </Button>
          </div>
        </Card>
        <div className="space-y-4">
          <JsonPanel
            title="Glass Symbols"
            description="Symbol list payload"
            value={glassListMutation.data ?? (glassListMutation.error instanceof Error ? { error: glassListMutation.error.message } : {})}
          />
          <JsonPanel
            title="Glass Symbol Detail"
            description="Describe and reference payloads"
            value={{
              describe: glassDescribeMutation.data ?? (glassDescribeMutation.error instanceof Error ? { error: glassDescribeMutation.error.message } : {}),
              references:
                glassReferencesMutation.data ??
                (glassReferencesMutation.error instanceof Error ? { error: glassReferencesMutation.error.message } : {}),
            }}
          />
        </div>
      </section>

      <footer className="rounded-xl border border-slate-200 bg-white p-4 text-xs text-slate-500">
        API base URL: <span className="font-mono">{import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'}</span>
        <span className="mx-2">•</span>
        Build with pnpm + Vite + TanStack + shadcn-style components.
      </footer>
    </main>
  )
}
