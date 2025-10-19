"use client"

import { useState, useEffect } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { toast } from "sonner"
import { plansApi, paymentsApi } from "@/lib/api"
import { Loader2, CreditCard, Smartphone, FileText, Wallet } from "lucide-react"

export default function CheckoutPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const planId = searchParams.get("plan_id")

  const [plan, setPlan] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [processing, setProcessing] = useState(false)
  const [selectedGateway, setSelectedGateway] = useState<"mercadopago" | "stripe" | "paypal" | null>(null)
  const [selectedMethod, setSelectedMethod] = useState<string | null>(null)

  // Buscar plano
  useEffect(() => {
    if (!planId) {
      toast.error("Plano não especificado")
      router.push("/pricing")
      return
    }

    fetchPlan()
  }, [planId])

  const fetchPlan = async () => {
    try {
      setLoading(true)
      const response = await plansApi.getById(planId!)
      setPlan(response.data)
    } catch (error: any) {
      console.error("Erro ao buscar plano:", error)
      toast.error(error.response?.data?.detail || "Erro ao carregar plano")
      router.push("/pricing")
    } finally {
      setLoading(false)
    }
  }

  // Processar pagamento
  const handlePayment = async () => {
    if (!selectedGateway || !selectedMethod) {
      toast.error("Selecione um método de pagamento")
      return
    }

    try {
      setProcessing(true)

      let response

      // Mercado Pago
      if (selectedGateway === "mercadopago") {
        response = await paymentsApi.createMercadoPagoPreference({
          plan_id: planId!,
          payment_method: selectedMethod,
          gateway: "mercadopago"
        })

        const { checkout_url, pix_qr_code } = response.data

        if (selectedMethod === "pix" && pix_qr_code) {
          // Mostrar QR Code PIX
          toast.success("QR Code PIX gerado!")
          // TODO: Abrir modal com QR Code
          window.open(checkout_url, "_blank")
        } else {
          // Redirecionar para checkout
          window.location.href = checkout_url
        }
      }

      // Stripe
      else if (selectedGateway === "stripe") {
        response = await paymentsApi.createStripeCheckout({
          plan_id: planId!,
          payment_method: selectedMethod,
          gateway: "stripe"
        })

        const { checkout_url } = response.data
        window.location.href = checkout_url
      }

      // PayPal
      else if (selectedGateway === "paypal") {
        response = await paymentsApi.createPayPalOrder({
          plan_id: planId!,
          payment_method: "paypal",
          gateway: "paypal"
        })

        const { checkout_url } = response.data
        window.location.href = checkout_url
      }

    } catch (error: any) {
      console.error("Erro ao processar pagamento:", error)
      toast.error(error.response?.data?.detail || "Erro ao processar pagamento")
      setProcessing(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  if (!plan) {
    return null
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Finalizar Assinatura</h1>
          <p className="text-gray-600 mt-2">Escolha a forma de pagamento</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Resumo do Plano */}
          <div className="lg:col-span-1">
            <Card>
              <CardHeader>
                <CardTitle>Resumo do Pedido</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <h3 className="font-semibold text-lg">{plan.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">{plan.description}</p>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-600">Plano Mensal</span>
                    <span className="font-semibold">
                      R$ {plan.price_monthly.toFixed(2)}
                    </span>
                  </div>
                  <div className="flex justify-between items-center text-sm text-gray-500">
                    <span>ou Plano Anual</span>
                    <span>R$ {plan.price_yearly.toFixed(2)}/ano</span>
                  </div>
                </div>

                <div className="border-t pt-4">
                  <h4 className="font-medium mb-2">Recursos inclusos:</h4>
                  <ul className="space-y-1 text-sm text-gray-600">
                    <li>✓ {plan.features?.max_contacts || 0} contatos</li>
                    <li>✓ {plan.features?.max_messages_per_month || 0} mensagens/mês</li>
                    <li>✓ {plan.features?.max_devices || 0} dispositivo(s)</li>
                    {plan.features?.gmaps_scraping && <li>✓ Scraping Google Maps</li>}
                    {plan.features?.mass_messaging && <li>✓ Envio em massa</li>}
                  </ul>
                </div>

                <div className="border-t pt-4">
                  <div className="flex justify-between items-center text-lg font-bold">
                    <span>Total</span>
                    <span className="text-blue-600">
                      R$ {plan.price_monthly.toFixed(2)}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Renovação automática mensal
                  </p>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Seleção de Pagamento */}
          <div className="lg:col-span-2 space-y-6">
            {/* Mercado Pago */}
            <Card className={selectedGateway === "mercadopago" ? "ring-2 ring-blue-600" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Mercado Pago</CardTitle>
                    <CardDescription>PIX, Boleto ou Cartão</CardDescription>
                  </div>
                  <Badge variant="secondary">🇧🇷 Brasil</Badge>
                </div>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
                  {/* PIX */}
                  <Button
                    variant={selectedGateway === "mercadopago" && selectedMethod === "pix" ? "default" : "outline"}
                    className="h-auto py-4"
                    onClick={() => {
                      setSelectedGateway("mercadopago")
                      setSelectedMethod("pix")
                    }}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <Smartphone className="h-6 w-6" />
                      <span>PIX</span>
                      <span className="text-xs">Aprovação instantânea</span>
                    </div>
                  </Button>

                  {/* Boleto */}
                  <Button
                    variant={selectedGateway === "mercadopago" && selectedMethod === "boleto" ? "default" : "outline"}
                    className="h-auto py-4"
                    onClick={() => {
                      setSelectedGateway("mercadopago")
                      setSelectedMethod("boleto")
                    }}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <FileText className="h-6 w-6" />
                      <span>Boleto</span>
                      <span className="text-xs">Até 3 dias úteis</span>
                    </div>
                  </Button>

                  {/* Cartão */}
                  <Button
                    variant={selectedGateway === "mercadopago" && selectedMethod === "credit_card" ? "default" : "outline"}
                    className="h-auto py-4"
                    onClick={() => {
                      setSelectedGateway("mercadopago")
                      setSelectedMethod("credit_card")
                    }}
                  >
                    <div className="flex flex-col items-center gap-2">
                      <CreditCard className="h-6 w-6" />
                      <span>Cartão</span>
                      <span className="text-xs">Até 12x sem juros</span>
                    </div>
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Stripe */}
            <Card className={selectedGateway === "stripe" ? "ring-2 ring-blue-600" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Cartão de Crédito Internacional</CardTitle>
                    <CardDescription>Visa, Mastercard, Apple Pay, Google Pay</CardDescription>
                  </div>
                  <Badge variant="secondary">🌎 Global</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Button
                  variant={selectedGateway === "stripe" ? "default" : "outline"}
                  className="w-full h-auto py-4"
                  onClick={() => {
                    setSelectedGateway("stripe")
                    setSelectedMethod("credit_card")
                  }}
                >
                  <div className="flex flex-col items-center gap-2">
                    <CreditCard className="h-6 w-6" />
                    <span>Pagar com Stripe</span>
                    <span className="text-xs">Pagamento seguro em USD</span>
                  </div>
                </Button>
              </CardContent>
            </Card>

            {/* PayPal */}
            <Card className={selectedGateway === "paypal" ? "ring-2 ring-blue-600" : ""}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>PayPal</CardTitle>
                    <CardDescription>Conta PayPal ou Cartão</CardDescription>
                  </div>
                  <Badge variant="secondary">🌎 Global</Badge>
                </div>
              </CardHeader>
              <CardContent>
                <Button
                  variant={selectedGateway === "paypal" ? "default" : "outline"}
                  className="w-full h-auto py-4"
                  onClick={() => {
                    setSelectedGateway("paypal")
                    setSelectedMethod("paypal")
                  }}
                >
                  <div className="flex flex-col items-center gap-2">
                    <Wallet className="h-6 w-6" />
                    <span>Pagar com PayPal</span>
                    <span className="text-xs">Proteção ao comprador</span>
                  </div>
                </Button>
              </CardContent>
            </Card>

            {/* Botão de Pagamento */}
            <div className="flex gap-4">
              <Button
                variant="outline"
                className="flex-1"
                onClick={() => router.push("/pricing")}
                disabled={processing}
              >
                Voltar
              </Button>
              <Button
                className="flex-1"
                onClick={handlePayment}
                disabled={!selectedGateway || !selectedMethod || processing}
              >
                {processing ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Processando...
                  </>
                ) : (
                  "Continuar para Pagamento"
                )}
              </Button>
            </div>

            {/* Informações de Segurança */}
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <h4 className="font-medium text-blue-900 mb-2">🔒 Pagamento Seguro</h4>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>✓ Transações criptografadas</li>
                <li>✓ Seus dados estão protegidos</li>
                <li>✓ Garantia de reembolso em 7 dias</li>
                <li>✓ Cancele a qualquer momento</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
