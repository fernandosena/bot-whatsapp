"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "sonner"
import { paymentsApi } from "@/lib/api"
import {
  Loader2,
  CreditCard,
  Calendar,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ArrowUpCircle,
  ArrowDownCircle,
  Ban
} from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

export default function SubscriptionPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [subscription, setSubscription] = useState<any>(null)
  const [showCancelModal, setShowCancelModal] = useState(false)
  const [cancelReason, setCancelReason] = useState("")
  const [cancelling, setCancelling] = useState(false)

  useEffect(() => {
    fetchSubscription()
  }, [])

  const fetchSubscription = async () => {
    try {
      setLoading(true)
      const response = await paymentsApi.getMySubscription()
      setSubscription(response.data)
    } catch (error: any) {
      console.error("Erro ao buscar assinatura:", error)
      toast.error(error.response?.data?.detail || "Erro ao carregar assinatura")
    } finally {
      setLoading(false)
    }
  }

  const handleCancelSubscription = async () => {
    if (!cancelReason.trim()) {
      toast.error("Por favor, informe o motivo do cancelamento")
      return
    }

    try {
      setCancelling(true)

      // Cancelar no gateway (Stripe suporta)
      if (subscription.subscription.gateway === "stripe") {
        await paymentsApi.cancelStripeSubscription({
          reason: cancelReason,
          cancel_at_period_end: true
        })
      }

      toast.success("Assinatura cancelada com sucesso")
      setShowCancelModal(false)
      fetchSubscription()
    } catch (error: any) {
      console.error("Erro ao cancelar:", error)
      toast.error(error.response?.data?.detail || "Erro ao cancelar assinatura")
    } finally {
      setCancelling(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  // Sem assinatura
  if (!subscription?.has_subscription) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4">
        <div className="max-w-4xl mx-auto">
          <Card>
            <CardContent className="py-12 text-center">
              <AlertTriangle className="h-16 w-16 text-yellow-500 mx-auto mb-4" />
              <h2 className="text-2xl font-bold mb-2">Nenhuma Assinatura Ativa</h2>
              <p className="text-gray-600 mb-6">
                Você não possui uma assinatura ativa no momento.
              </p>
              <Button onClick={() => router.push("/pricing")}>
                Ver Planos Disponíveis
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  const { subscription: sub, plan, last_payment } = subscription

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Minha Assinatura</h1>
          <p className="text-gray-600 mt-2">Gerencie sua assinatura e pagamentos</p>
        </div>

        <div className="space-y-6">
          {/* Status da Assinatura */}
          <Card>
            <CardHeader>
              <div className="flex items-start justify-between">
                <div>
                  <CardTitle className="text-2xl">{plan.name}</CardTitle>
                  <CardDescription className="mt-2">{plan.description}</CardDescription>
                </div>
                <Badge
                  variant={sub.status === "active" ? "success" : "secondary"}
                  className="text-sm"
                >
                  {sub.status === "active" ? (
                    <>
                      <CheckCircle2 className="h-4 w-4 mr-1" />
                      Ativa
                    </>
                  ) : (
                    <>
                      <XCircle className="h-4 w-4 mr-1" />
                      Inativa
                    </>
                  )}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* Informações */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-600 mb-1">
                    <CreditCard className="h-4 w-4" />
                    <span className="text-sm">Valor Mensal</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">
                    R$ {plan.price_monthly.toFixed(2)}
                  </p>
                </div>

                <div className="bg-gray-50 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-gray-600 mb-1">
                    <Calendar className="h-4 w-4" />
                    <span className="text-sm">Próxima Cobrança</span>
                  </div>
                  <p className="text-2xl font-bold text-gray-900">
                    {sub.current_period_end
                      ? format(new Date(sub.current_period_end), "dd 'de' MMMM", { locale: ptBR })
                      : "N/A"}
                  </p>
                </div>
              </div>

              {/* Aviso de Cancelamento */}
              {sub.cancel_at_period_end && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="h-5 w-5 text-yellow-600 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-yellow-900">Assinatura será cancelada</h4>
                      <p className="text-sm text-yellow-800 mt-1">
                        Sua assinatura permanecerá ativa até{" "}
                        {sub.current_period_end && format(new Date(sub.current_period_end), "dd/MM/yyyy")} e não será renovada.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Recursos */}
              <div>
                <h3 className="font-semibold mb-3">Recursos inclusos:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  <div className="flex items-center gap-2 text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm">{plan.features?.max_contacts || 0} contatos</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm">{plan.features?.max_messages_per_month || 0} mensagens/mês</span>
                  </div>
                  <div className="flex items-center gap-2 text-gray-700">
                    <CheckCircle2 className="h-4 w-4 text-green-600" />
                    <span className="text-sm">{plan.features?.max_devices || 0} dispositivo(s)</span>
                  </div>
                  {plan.features?.gmaps_scraping && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Scraping Google Maps</span>
                    </div>
                  )}
                  {plan.features?.mass_messaging && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Envio em massa</span>
                    </div>
                  )}
                  {plan.features?.scheduling && (
                    <div className="flex items-center gap-2 text-gray-700">
                      <CheckCircle2 className="h-4 w-4 text-green-600" />
                      <span className="text-sm">Agendamento</span>
                    </div>
                  )}
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Último Pagamento */}
          {last_payment && (
            <Card>
              <CardHeader>
                <CardTitle>Último Pagamento</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Valor Pago</p>
                    <p className="text-2xl font-bold">R$ {last_payment.amount?.toFixed(2)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Data</p>
                    <p className="font-medium">
                      {last_payment.paid_at && format(new Date(last_payment.paid_at), "dd/MM/yyyy")}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm text-gray-600">Método</p>
                    <p className="font-medium capitalize">{last_payment.payment_method?.replace("_", " ")}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Ações */}
          <Card>
            <CardHeader>
              <CardTitle>Gerenciar Assinatura</CardTitle>
              <CardDescription>Altere ou cancele sua assinatura</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => router.push("/pricing")}
              >
                <ArrowUpCircle className="mr-2 h-4 w-4" />
                Fazer Upgrade do Plano
              </Button>

              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => router.push("/pricing")}
              >
                <ArrowDownCircle className="mr-2 h-4 w-4" />
                Fazer Downgrade do Plano
              </Button>

              {!sub.cancel_at_period_end && (
                <Button
                  variant="destructive"
                  className="w-full justify-start"
                  onClick={() => setShowCancelModal(true)}
                >
                  <Ban className="mr-2 h-4 w-4" />
                  Cancelar Assinatura
                </Button>
              )}

              <Button
                variant="outline"
                className="w-full justify-start"
                onClick={() => router.push("/payments")}
              >
                <CreditCard className="mr-2 h-4 w-4" />
                Ver Histórico de Pagamentos
              </Button>
            </CardContent>
          </Card>

          {/* Informações Adicionais */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-medium text-blue-900 mb-2">ℹ️ Informações Importantes</h4>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>• Sua assinatura renova automaticamente todo mês</li>
              <li>• Você pode cancelar a qualquer momento</li>
              <li>• Ao cancelar, você mantém acesso até o fim do período pago</li>
              <li>• Upgrades são aplicados imediatamente</li>
            </ul>
          </div>
        </div>

        {/* Modal de Cancelamento */}
        <Dialog open={showCancelModal} onOpenChange={setShowCancelModal}>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Cancelar Assinatura</DialogTitle>
              <DialogDescription>
                Tem certeza que deseja cancelar sua assinatura? Você continuará tendo acesso até o fim do período pago.
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div>
                <label className="text-sm font-medium mb-2 block">
                  Por que você está cancelando? (Opcional)
                </label>
                <Textarea
                  placeholder="Nos ajude a melhorar..."
                  value={cancelReason}
                  onChange={(e) => setCancelReason(e.target.value)}
                  rows={4}
                />
              </div>
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowCancelModal(false)}
                disabled={cancelling}
              >
                Voltar
              </Button>
              <Button
                variant="destructive"
                onClick={handleCancelSubscription}
                disabled={cancelling}
              >
                {cancelling ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Cancelando...
                  </>
                ) : (
                  "Confirmar Cancelamento"
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
