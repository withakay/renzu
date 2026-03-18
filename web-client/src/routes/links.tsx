import { ExternalLink } from 'lucide-react'

import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardTitle } from '@/components/ui/card'

type UiLink = {
  name: string
  url: string
  description: string
  kind: string
}

const links: UiLink[] = [
  {
    name: 'Renzu Workbench',
    url: 'http://localhost:8080',
    description: 'TanStack client for index/search/snippet/glass workflows.',
    kind: 'Primary UI',
  },
  {
    name: 'Renzu API Docs',
    url: 'http://localhost:8000/docs',
    description: 'Interactive FastAPI Swagger docs for all REST endpoints.',
    kind: 'Developer UI',
  },
  {
    name: 'Renzu API ReDoc',
    url: 'http://localhost:8000/redoc',
    description: 'Alternative OpenAPI documentation view.',
    kind: 'Developer UI',
  },
  {
    name: 'Qdrant Dashboard',
    url: 'http://localhost:6333/dashboard',
    description: 'Inspect collections, points, and vectors in Qdrant.',
    kind: 'Infra UI',
  },
  {
    name: 'Qdrant REST Root',
    url: 'http://localhost:6333',
    description: 'Raw Qdrant endpoint for API-level diagnostics.',
    kind: 'Infra API',
  },
]

export function LinksPage() {
  return (
    <main className="mx-auto max-w-6xl space-y-6 px-4 py-8">
      <header className="rounded-2xl border border-slate-200 bg-gradient-to-r from-white via-cyan-50 to-sky-50 p-6 shadow-sm">
        <h1 className="text-3xl font-semibold text-slate-900">Web UIs</h1>
        <p className="mt-2 text-sm text-slate-600">
          Quick links for the Renzu app, API docs, and infrastructure interfaces.
        </p>
      </header>

      <section className="grid gap-4 md:grid-cols-2">
        {links.map((link) => (
          <Card key={link.name} className="space-y-3">
            <div className="flex items-start justify-between gap-3">
              <div>
                <CardTitle>{link.name}</CardTitle>
                <CardDescription>{link.description}</CardDescription>
              </div>
              <Badge>{link.kind}</Badge>
            </div>
            <div className="flex items-center justify-between gap-3 rounded-md border border-slate-200 bg-slate-50 p-3">
              <code className="overflow-hidden text-ellipsis whitespace-nowrap text-xs text-slate-700">{link.url}</code>
              <Button
                variant="outline"
                className="gap-2"
                onClick={() => window.open(link.url, '_blank', 'noopener,noreferrer')}
              >
                Open
                <ExternalLink className="h-4 w-4" />
              </Button>
            </div>
          </Card>
        ))}
      </section>
    </main>
  )
}
