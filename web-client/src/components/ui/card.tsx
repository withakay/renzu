import type { HTMLAttributes } from 'react'

import { cn } from '@/lib/utils'

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        'rounded-xl border border-slate-200 bg-white/80 p-5 shadow-sm backdrop-blur-sm dark:border-slate-800 dark:bg-slate-950/50 dark:shadow-none',
        className,
      )}
      {...props}
    />
  )
}

export function CardTitle({ className, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return <h2 className={cn('text-base font-semibold text-slate-900 dark:text-slate-50', className)} {...props} />
}

export function CardDescription({ className, ...props }: HTMLAttributes<HTMLParagraphElement>) {
  return <p className={cn('text-sm text-slate-600 dark:text-slate-400', className)} {...props} />
}
