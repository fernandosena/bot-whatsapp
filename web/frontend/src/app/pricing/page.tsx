"use client"

import { useEffect, useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { plansApi } from "@/lib/api"
import { Plan } from "@/types"
import { toast } from "sonner"

export default function PricingPage() {
  const [plans, setPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [billingCycle, setBillingCycle] = useState<"monthly" | "yearly">("monthly")

  useEffect(() => {
    fetchPlans()
  }, [])

  const fetchPlans = async () => {
    try {
      // Buscar apenas planos ativos e visíveis
      const response = await plansApi.list(false, false)
      const allPlans = response.data as Plan[]

      // Filtrar apenas planos visíveis e ordenar por preço
      const visiblePlans = allPlans
        .filter(plan => plan.is_visible && plan.status === 'active')
        .sort((a, b) => a.price_monthly - b.price_monthly)

      setPlans(visiblePlans)
    } catch (error: any) {
      console.error("Erro ao buscar planos:", error)
      toast.error("Erro ao carregar planos")
    } finally {
      setLoading(false)
    }
  }

  const formatPrice = (priceInCents: number) => {
    return (priceInCents / 100).toLocaleString('pt-BR', {
      style: 'currency',
      currency: 'BRL',
    })
  }

  const getPrice = (plan: Plan) => {
    if (billingCycle === "yearly" && plan.price_yearly) {
      return formatPrice(plan.price_yearly)
    }
    return formatPrice(plan.price_monthly)
  }

  const getMonthlyPrice = (plan: Plan) => {
    if (billingCycle === "yearly" && plan.price_yearly) {
      const monthlyEquivalent = plan.price_yearly / 12
      return formatPrice(Math.round(monthlyEquivalent))
    }
    return formatPrice(plan.price_monthly)
  }

  const getSavings = (plan: Plan) => {
    if (!plan.price_yearly) return null
    const yearlyMonthly = plan.price_yearly / 12
    const savings = ((1 - yearlyMonthly / plan.price_monthly) * 100).toFixed(0)
    return `${savings}%`
  }

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent mx-auto mb-4"></div>
          <p className="text-muted-foreground">Carregando planos...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="flex min-h-screen flex-col">
      {/* Header */}
      <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="container flex h-16 items-center justify-between">
          <Link href="/" className="flex items-center gap-2">
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
          </Link>
          <nav className="flex items-center gap-4">
            <Link href="/" className="text-sm font-medium hover:text-primary">
              Início
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

      {/* Main Content */}
      <main className="flex-1">
        <section className="container py-20">
          {/* Header Section */}
          <div className="text-center space-y-4 mb-12">
            <h1 className="text-4xl font-bold tracking-tighter sm:text-5xl">
              Escolha o plano ideal para você
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Planos flexíveis para empresas de todos os tamanhos. Cancele quando quiser.
            </p>
          </div>

          {/* Billing Toggle */}
          <div className="flex justify-center mb-12">
            <div className="inline-flex items-center rounded-lg border p-1">
              <button
                onClick={() => setBillingCycle("monthly")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === "monthly"
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
              >
                Mensal
              </button>
              <button
                onClick={() => setBillingCycle("yearly")}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  billingCycle === "yearly"
                    ? "bg-primary text-primary-foreground"
                    : "hover:bg-muted"
                }`}
              >
                Anual
                {plans.some(p => p.price_yearly) && (
                  <Badge variant="success" className="ml-2">
                    Economize até 20%
                  </Badge>
                )}
              </button>
            </div>
          </div>

          {/* Plans Grid */}
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 max-w-7xl mx-auto">
            {plans.map((plan) => (
              <Card
                key={plan._id}
                className={`flex flex-col ${
                  plan.is_featured
                    ? "border-primary shadow-lg scale-105"
                    : ""
                }`}
              >
                <CardHeader>
                  <div className="flex items-center justify-between mb-2">
                    <CardTitle className="text-2xl">{plan.name}</CardTitle>
                    {plan.is_featured && (
                      <Badge variant="default">Mais Popular</Badge>
                    )}
                  </div>
                  <CardDescription>{plan.description}</CardDescription>
                </CardHeader>

                <CardContent className="flex-1 space-y-6">
                  {/* Price */}
                  <div>
                    <div className="flex items-baseline gap-1">
                      <span className="text-4xl font-bold">
                        {getMonthlyPrice(plan)}
                      </span>
                      <span className="text-muted-foreground">/mês</span>
                    </div>
                    {billingCycle === "yearly" && plan.price_yearly && (
                      <div className="mt-1">
                        <span className="text-sm text-muted-foreground">
                          {getPrice(plan)} cobrado anualmente
                        </span>
                        {getSavings(plan) && (
                          <Badge variant="success" className="ml-2">
                            Economize {getSavings(plan)}
                          </Badge>
                        )}
                      </div>
                    )}
                    {plan.trial_days > 0 && (
                      <p className="text-sm text-green-600 mt-2">
                        ✓ {plan.trial_days} dias de teste grátis
                      </p>
                    )}
                  </div>

                  {/* Features */}
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm">
                      <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>
                        {plan.features.max_contacts === -1
                          ? "Contatos ilimitados"
                          : `${plan.features.max_contacts.toLocaleString()} contatos`}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                      <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>
                        {plan.features.max_messages_per_month === -1
                          ? "Mensagens ilimitadas"
                          : `${plan.features.max_messages_per_month.toLocaleString()} mensagens/mês`}
                      </span>
                    </div>

                    <div className="flex items-center gap-2 text-sm">
                      <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>{plan.features.max_devices} dispositivo(s)</span>
                    </div>

                    {plan.features.has_variables && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Variáveis personalizadas</span>
                      </div>
                    )}

                    {plan.features.has_sequence && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Sequência de mensagens</span>
                      </div>
                    )}

                    {plan.features.has_media && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Envio de mídia</span>
                      </div>
                    )}

                    {plan.features.has_advanced_reports && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Relatórios avançados</span>
                      </div>
                    )}

                    {plan.features.has_api_access && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Acesso API</span>
                      </div>
                    )}

                    {plan.features.has_multi_user && (
                      <div className="flex items-center gap-2 text-sm">
                        <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                        </svg>
                        <span>Multi-usuário</span>
                      </div>
                    )}

                    <div className="flex items-center gap-2 text-sm">
                      <svg className="h-4 w-4 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span>
                        Suporte{" "}
                        {plan.features.support_level === "priority_24x7"
                          ? "prioritário 24/7"
                          : plan.features.support_level === "email_chat"
                          ? "email + chat"
                          : "por email"}
                      </span>
                    </div>
                  </div>
                </CardContent>

                <CardFooter>
                  <Link href="/auth/register" className="w-full">
                    <Button
                      className="w-full"
                      variant={plan.is_featured ? "default" : "outline"}
                      size="lg"
                    >
                      {plan.price_monthly === 0
                        ? "Começar Grátis"
                        : plan.trial_days > 0
                        ? "Iniciar Teste Grátis"
                        : "Assinar Agora"}
                    </Button>
                  </Link>
                </CardFooter>
              </Card>
            ))}
          </div>

          {/* FAQ or Additional Info */}
          <div className="mt-20 text-center">
            <h2 className="text-2xl font-bold mb-4">Dúvidas?</h2>
            <p className="text-muted-foreground mb-6">
              Entre em contato conosco para planos personalizados ou mais informações
            </p>
            <Button variant="outline" size="lg">
              Falar com Vendas
            </Button>
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
