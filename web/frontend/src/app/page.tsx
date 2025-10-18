import Link from "next/link"
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="h-6 w-6 text-primary"
            >
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
            <span className="font-bold text-xl">WhatsApp Business</span>
          </div>
          <nav className="flex items-center gap-4">
            <Link href="/pricing" className="text-sm font-medium hover:text-primary">
              Preços
            </Link>
            <Link href="/auth/login">
              <Button variant="ghost">Entrar</Button>
            </Link>
            <Link href="/auth/register">
              <Button>Começar Grátis</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="container grid place-items-center gap-10 py-20 md:py-32">
          <div className="text-center space-y-6 max-w-3xl">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl md:text-6xl lg:text-7xl">
              Automatize seu WhatsApp Business
            </h1>
            <p className="mx-auto max-w-[700px] text-gray-500 md:text-xl dark:text-gray-400">
              Envie mensagens em massa, gerencie contatos e campanhas de forma profissional.
              Sistema completo com planos flexíveis para seu negócio.
            </p>
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center">
              <Link href="/auth/register">
                <Button size="lg" className="w-full sm:w-auto">
                  Começar Gratuitamente
                </Button>
              </Link>
              <Link href="/pricing">
                <Button size="lg" variant="outline" className="w-full sm:w-auto">
                  Ver Preços
                </Button>
              </Link>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="container py-20 bg-muted/50">
          <div className="text-center space-y-4 mb-12">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
              Recursos Poderosos
            </h2>
            <p className="text-gray-500 dark:text-gray-400">
              Tudo que você precisa para gerenciar seu WhatsApp Business
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            <div className="flex flex-col gap-2 p-6 bg-background rounded-lg border">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-primary"
              >
                <path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2" />
                <circle cx="9" cy="7" r="4" />
                <path d="M22 21v-2a4 4 0 0 0-3-3.87" />
                <path d="M16 3.13a4 4 0 0 1 0 7.75" />
              </svg>
              <h3 className="text-xl font-bold">Gerenciamento de Contatos</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Importe e organize seus contatos do Google Maps ou CSV
              </p>
            </div>

            <div className="flex flex-col gap-2 p-6 bg-background rounded-lg border">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-primary"
              >
                <path d="m22 2-7 20-4-9-9-4Z" />
                <path d="M22 2 11 13" />
              </svg>
              <h3 className="text-xl font-bold">Envio em Massa</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Envie mensagens personalizadas para milhares de contatos
              </p>
            </div>

            <div className="flex flex-col gap-2 p-6 bg-background rounded-lg border">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-primary"
              >
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                <line x1="16" x2="16" y1="2" y2="6" />
                <line x1="8" x2="8" y1="2" y2="6" />
                <line x1="3" x2="21" y1="10" y2="10" />
              </svg>
              <h3 className="text-xl font-bold">Campanhas Agendadas</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Agende suas campanhas para o melhor momento
              </p>
            </div>

            <div className="flex flex-col gap-2 p-6 bg-background rounded-lg border">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-primary"
              >
                <path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z" />
                <polyline points="14 2 14 8 20 8" />
              </svg>
              <h3 className="text-xl font-bold">Variáveis Personalizadas</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Use {"{nome}"}, {"{empresa}"} e outras variáveis nas mensagens
              </p>
            </div>

            <div className="flex flex-col gap-2 p-6 bg-background rounded-lg border">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-primary"
              >
                <line x1="12" x2="12" y1="20" y2="10" />
                <line x1="18" x2="18" y1="20" y2="4" />
                <line x1="6" x2="6" y1="20" y2="16" />
              </svg>
              <h3 className="text-xl font-bold">Relatórios Avançados</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Acompanhe métricas e resultados em tempo real
              </p>
            </div>

            <div className="flex flex-col gap-2 p-6 bg-background rounded-lg border">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
                className="h-10 w-10 text-primary"
              >
                <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
                <path d="M7 11V7a5 5 0 0 1 10 0v4" />
              </svg>
              <h3 className="text-xl font-bold">100% Seguro</h3>
              <p className="text-gray-500 dark:text-gray-400">
                Seus dados protegidos com criptografia de ponta
              </p>
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="container py-20">
          <div className="flex flex-col items-center gap-6 text-center">
            <h2 className="text-3xl font-bold tracking-tighter sm:text-4xl">
              Pronto para começar?
            </h2>
            <p className="max-w-[600px] text-gray-500 md:text-xl dark:text-gray-400">
              Comece gratuitamente hoje e veja como é fácil automatizar seu WhatsApp Business.
            </p>
            <Link href="/auth/register">
              <Button size="lg">
                Criar Conta Grátis
              </Button>
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t py-6 md:py-0">
        <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
          <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
            © 2025 WhatsApp Business SaaS. Todos os direitos reservados.
          </p>
        </div>
      </footer>
    </div>
  )
}
