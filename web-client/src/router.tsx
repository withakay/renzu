import { createRootRoute, createRoute, createRouter, Outlet } from '@tanstack/react-router'

import { AppShell } from '@/components/app-shell'
import { HomePage } from '@/routes/home'
import { LinksPage } from '@/routes/links'
import { ReadmePage } from '@/routes/readme'

const rootRoute = createRootRoute({
  component: () => (
    <AppShell>
      <Outlet />
    </AppShell>
  ),
})

const indexRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/',
  component: HomePage,
})

const linksRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/links',
  component: LinksPage,
})

const readmeRoute = createRoute({
  getParentRoute: () => rootRoute,
  path: '/readme',
  component: ReadmePage,
})

const routeTree = rootRoute.addChildren([indexRoute, linksRoute, readmeRoute])

export const router = createRouter({ routeTree })

declare module '@tanstack/react-router' {
  interface Register {
    router: typeof router
  }
}
