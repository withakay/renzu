import { Copy } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardTitle } from '@/components/ui/card'

type JsonPanelProps = {
  title: string
  description: string
  value: unknown
}

export function JsonPanel({ title, description, value }: JsonPanelProps) {
  const formatted = JSON.stringify(value ?? {}, null, 2)

  async function copyJson() {
    await navigator.clipboard.writeText(formatted)
  }

  return (
    <Card className="space-y-3">
      <div className="flex items-start justify-between gap-3">
        <div>
          <CardTitle>{title}</CardTitle>
          <CardDescription>{description}</CardDescription>
        </div>
        <Button type="button" variant="outline" className="gap-2" onClick={copyJson}>
          <Copy className="h-4 w-4" />
          Copy
        </Button>
      </div>
      <pre className="max-h-80 overflow-auto rounded-md bg-slate-950 p-3 text-xs text-slate-50">{formatted}</pre>
    </Card>
  )
}
