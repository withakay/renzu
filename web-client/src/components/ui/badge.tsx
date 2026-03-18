import type { HTMLAttributes } from 'react'

import { cn } from '@/lib/utils'

export function Badge({ className, ...props }: HTMLAttributes<HTMLSpanElement>) {
  return (
    <span
      className={cn(
        'inline-flex items-center rounded-full border border-sky-200 bg-sky-50 px-2.5 py-1 text-xs font-medium text-sky-700 dark:border-sky-900/60 dark:bg-sky-950/30 dark:text-sky-200',
        className,
      )}
      {...props}
    />
  )
}
