import type { ReactNode } from 'react'
import { useEffect, useState } from 'react'
import { Link, useRouterState } from '@tanstack/react-router'
import { Moon, Sun } from 'lucide-react'

import { cn } from '@/lib/utils'
import { applyThemeClass, getPreferredTheme, getStoredTheme, setStoredTheme, type ThemeMode } from '@/lib/theme'

import { Button } from '@/components/ui/button'

type AppShellProps = {
  children: ReactNode
}

function NavItem({ to, label }: { to: string; label: string }) {
  const pathname = useRouterState({ select: (state) => state.location.pathname })
  const active = pathname === to

  return (
    <Link
      to={to}
      className={cn(
        'rounded-md px-3 py-2 text-sm font-medium transition',
        active
          ? 'bg-slate-900 text-white dark:bg-slate-50 dark:text-slate-900'
          : 'text-slate-700 hover:bg-slate-100 dark:text-slate-200 dark:hover:bg-slate-900/60',
      )}
    >
      {label}
    </Link>
  )
}

export function AppShell({ children }: AppShellProps) {
  const [theme, setTheme] = useState<ThemeMode>(() => getStoredTheme() ?? getPreferredTheme())

  useEffect(() => {
    applyThemeClass(theme)
  }, [theme])

  function toggleTheme() {
    const next: ThemeMode = theme === 'dark' ? 'light' : 'dark'
    setTheme(next)
    setStoredTheme(next)
  }

  return (
    <div className="min-h-screen text-slate-900 dark:text-slate-100">
      <header className="sticky top-0 z-10 border-b border-slate-200 bg-white/80 backdrop-blur dark:border-slate-800 dark:bg-slate-950/70">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-3 px-4 py-3">
          <div className="text-sm font-semibold tracking-wide text-slate-900 dark:text-slate-50">Renzu</div>
          <nav className="flex flex-1 items-center justify-end gap-2">
            <NavItem to="/" label="Workbench" />
            <NavItem to="/links" label="Web UIs" />
            <NavItem to="/readme" label="README" />
            <Button
              type="button"
              variant="ghost"
              size="icon"
              onClick={toggleTheme}
              aria-label="Toggle dark mode"
              title="Toggle dark mode"
            >
              {theme === 'dark' ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </Button>
          </nav>
        </div>
      </header>
      {children}
    </div>
  )
}
