import { Copy } from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Card, CardDescription, CardTitle } from '@/components/ui/card'
import {
  CodeBlock,
  CodeBlockBody,
  CodeBlockContent,
  CodeBlockCopyButton,
  CodeBlockFilename,
  CodeBlockHeader,
  CodeBlockItem,
} from '@/components/kibo-ui/code-block'

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
          Copy JSON
        </Button>
      </div>
      <CodeBlock
        data={[{ language: 'json', filename: `${title.toLowerCase().replaceAll(' ', '-')}.json`, code: formatted }]}
        defaultValue="json"
      >
        <CodeBlockHeader className="items-center justify-between">
          <CodeBlockFilename value="json">{`${title.toLowerCase().replaceAll(' ', '-')}.json`}</CodeBlockFilename>
          <CodeBlockCopyButton />
        </CodeBlockHeader>
        <CodeBlockBody>
          {(item) => (
            <CodeBlockItem key={item.language} value={item.language} className="max-h-80 overflow-auto">
              <CodeBlockContent language="json">{item.code}</CodeBlockContent>
            </CodeBlockItem>
          )}
        </CodeBlockBody>
      </CodeBlock>
    </Card>
  )
}
