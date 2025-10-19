"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { toast } from "sonner"
import { paymentsApi } from "@/lib/api"
import {
  Loader2,
  CreditCard,
  Download,
  Eye,
  Filter,
  RefreshCw,
  TrendingUp,
  DollarSign,
  CheckCircle2,
  XCircle,
  Clock,
  ArrowLeft
} from "lucide-react"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface Payment {
  id: string
  amount: number
  currency: string
  status: string
  payment_method: string
  gateway: string
  created_at: string
  paid_at?: string
  plan_name?: string
}

export default function PaymentsHistoryPage() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [payments, setPayments] = useState<Payment[]>([])
  const [stats, setStats] = useState<any>(null)
  const [selectedPayment, setSelectedPayment] = useState<any>(null)
  const [showDetailsModal, setShowDetailsModal] = useState(false)

  // Filters
  const [statusFilter, setStatusFilter] = useState<string>("all")
  const [gatewayFilter, setGatewayFilter] = useState<string>("all")

  useEffect(() => {
    fetchData()
  }, [statusFilter, gatewayFilter])

  const fetchData = async () => {
    try {
      setLoading(true)

      // Buscar pagamentos com filtros
      const params: any = { limit: 50 }
      if (statusFilter !== "all") params.status = statusFilter
      if (gatewayFilter !== "all") params.gateway = gatewayFilter

      const [paymentsResponse, statsResponse] = await Promise.all([
        paymentsApi.getMyPayments(params),
        paymentsApi.getPaymentStats()
      ])

      setPayments(paymentsResponse.data.payments)
      setStats(statsResponse.data)
    } catch (error: any) {
      console.error("Erro ao buscar pagamentos:", error)
      toast.error(error.response?.data?.detail || "Erro ao carregar histórico")
    } finally {
      setLoading(false)
    }
  }

  const handleViewDetails = async (paymentId: string) => {
    try {
      const response = await paymentsApi.getPaymentDetails(paymentId)
      setSelectedPayment(response.data)
      setShowDetailsModal(true)
    } catch (error: any) {
      console.error("Erro ao buscar detalhes:", error)
      toast.error(error.response?.data?.detail || "Erro ao carregar detalhes")
    }
  }

  const getStatusBadge = (status: string) => {
    const statusConfig: Record<string, { variant: any; icon: any; label: string }> = {
      approved: {
        variant: "default",
        icon: <CheckCircle2 className="h-3 w-3" />,
        label: "Aprovado"
      },
      pending: {
        variant: "secondary",
        icon: <Clock className="h-3 w-3" />,
        label: "Pendente"
      },
      processing: {
        variant: "secondary",
        icon: <Loader2 className="h-3 w-3 animate-spin" />,
        label: "Processando"
      },
      rejected: {
        variant: "destructive",
        icon: <XCircle className="h-3 w-3" />,
        label: "Rejeitado"
      },
      cancelled: {
        variant: "outline",
        icon: <XCircle className="h-3 w-3" />,
        label: "Cancelado"
      },
      refunded: {
        variant: "outline",
        icon: <ArrowLeft className="h-3 w-3" />,
        label: "Reembolsado"
      }
    }

    const config = statusConfig[status] || statusConfig.pending

    return (
      <Badge variant={config.variant} className="flex items-center gap-1 w-fit">
        {config.icon}
        {config.label}
      </Badge>
    )
  }

  const getGatewayLabel = (gateway: string) => {
    const labels: Record<string, string> = {
      mercadopago: "Mercado Pago",
      stripe: "Stripe",
      paypal: "PayPal"
    }
    return labels[gateway] || gateway
  }

  const getMethodLabel = (method: string) => {
    const labels: Record<string, string> = {
      credit_card: "Cartão de Crédito",
      debit_card: "Cartão de Débito",
      pix: "PIX",
      boleto: "Boleto",
      paypal: "PayPal",
      apple_pay: "Apple Pay",
      google_pay: "Google Pay"
    }
    return labels[method] || method
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-blue-600" />
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Histórico de Pagamentos</h1>
          <p className="text-gray-600 mt-2">Visualize todos os seus pagamentos e transações</p>
        </div>

        {/* Stats Cards */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total de Pagamentos</p>
                    <p className="text-2xl font-bold mt-1">{stats.total_payments || 0}</p>
                  </div>
                  <CreditCard className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Aprovados</p>
                    <p className="text-2xl font-bold mt-1 text-green-600">
                      {stats.approved_payments || 0}
                    </p>
                  </div>
                  <CheckCircle2 className="h-8 w-8 text-green-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Pendentes</p>
                    <p className="text-2xl font-bold mt-1 text-yellow-600">
                      {stats.pending_payments || 0}
                    </p>
                  </div>
                  <Clock className="h-8 w-8 text-yellow-600" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="pt-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-gray-600">Total Gasto</p>
                    <p className="text-2xl font-bold mt-1 text-blue-600">
                      R$ {(stats.total_spent || 0).toFixed(2)}
                    </p>
                  </div>
                  <DollarSign className="h-8 w-8 text-blue-600" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Filters and Table */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Todos os Pagamentos</CardTitle>
                <CardDescription>Lista completa de transações</CardDescription>
              </div>
              <Button variant="outline" size="sm" onClick={fetchData}>
                <RefreshCw className="h-4 w-4 mr-2" />
                Atualizar
              </Button>
            </div>

            {/* Filters */}
            <div className="flex gap-4 mt-4">
              <div className="w-48">
                <Select value={statusFilter} onValueChange={setStatusFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Status" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os Status</SelectItem>
                    <SelectItem value="approved">Aprovado</SelectItem>
                    <SelectItem value="pending">Pendente</SelectItem>
                    <SelectItem value="processing">Processando</SelectItem>
                    <SelectItem value="rejected">Rejeitado</SelectItem>
                    <SelectItem value="cancelled">Cancelado</SelectItem>
                    <SelectItem value="refunded">Reembolsado</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="w-48">
                <Select value={gatewayFilter} onValueChange={setGatewayFilter}>
                  <SelectTrigger>
                    <SelectValue placeholder="Gateway" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="all">Todos os Gateways</SelectItem>
                    <SelectItem value="mercadopago">Mercado Pago</SelectItem>
                    <SelectItem value="stripe">Stripe</SelectItem>
                    <SelectItem value="paypal">PayPal</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
          </CardHeader>

          <CardContent>
            {payments.length === 0 ? (
              <div className="text-center py-12">
                <CreditCard className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Nenhum pagamento encontrado
                </h3>
                <p className="text-gray-600 mb-6">
                  Você ainda não realizou nenhum pagamento ou não há pagamentos com os filtros selecionados.
                </p>
                <Button onClick={() => router.push("/pricing")}>
                  Ver Planos Disponíveis
                </Button>
              </div>
            ) : (
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Data</TableHead>
                      <TableHead>Plano</TableHead>
                      <TableHead>Valor</TableHead>
                      <TableHead>Método</TableHead>
                      <TableHead>Gateway</TableHead>
                      <TableHead>Status</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {payments.map((payment) => (
                      <TableRow key={payment.id}>
                        <TableCell className="font-medium">
                          {format(new Date(payment.created_at), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                        </TableCell>
                        <TableCell>{payment.plan_name || "N/A"}</TableCell>
                        <TableCell className="font-semibold">
                          R$ {payment.amount.toFixed(2)}
                        </TableCell>
                        <TableCell>{getMethodLabel(payment.payment_method)}</TableCell>
                        <TableCell>{getGatewayLabel(payment.gateway)}</TableCell>
                        <TableCell>{getStatusBadge(payment.status)}</TableCell>
                        <TableCell className="text-right">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleViewDetails(payment.id)}
                          >
                            <Eye className="h-4 w-4 mr-2" />
                            Ver Detalhes
                          </Button>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Payment Details Modal */}
        <Dialog open={showDetailsModal} onOpenChange={setShowDetailsModal}>
          <DialogContent className="max-w-2xl">
            <DialogHeader>
              <DialogTitle>Detalhes do Pagamento</DialogTitle>
              <DialogDescription>
                Informações completas da transação
              </DialogDescription>
            </DialogHeader>

            {selectedPayment && (
              <div className="space-y-4">
                {/* Status */}
                <div className="flex items-center justify-between pb-4 border-b">
                  <span className="text-gray-600">Status</span>
                  {getStatusBadge(selectedPayment.payment.status)}
                </div>

                {/* Valor */}
                <div className="flex items-center justify-between pb-4 border-b">
                  <span className="text-gray-600">Valor</span>
                  <span className="text-2xl font-bold">
                    R$ {selectedPayment.payment.amount.toFixed(2)}
                  </span>
                </div>

                {/* Plano */}
                {selectedPayment.plan && (
                  <div className="pb-4 border-b">
                    <span className="text-gray-600 block mb-2">Plano</span>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="font-semibold">{selectedPayment.plan.name}</p>
                      <p className="text-sm text-gray-600">{selectedPayment.plan.description}</p>
                    </div>
                  </div>
                )}

                {/* Método e Gateway */}
                <div className="grid grid-cols-2 gap-4 pb-4 border-b">
                  <div>
                    <span className="text-gray-600 block mb-1">Método de Pagamento</span>
                    <p className="font-medium">{getMethodLabel(selectedPayment.payment.payment_method)}</p>
                  </div>
                  <div>
                    <span className="text-gray-600 block mb-1">Gateway</span>
                    <p className="font-medium">{getGatewayLabel(selectedPayment.payment.gateway)}</p>
                  </div>
                </div>

                {/* Datas */}
                <div className="grid grid-cols-2 gap-4 pb-4 border-b">
                  <div>
                    <span className="text-gray-600 block mb-1">Data de Criação</span>
                    <p className="font-medium">
                      {format(new Date(selectedPayment.payment.created_at), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                    </p>
                  </div>
                  {selectedPayment.payment.paid_at && (
                    <div>
                      <span className="text-gray-600 block mb-1">Data de Pagamento</span>
                      <p className="font-medium">
                        {format(new Date(selectedPayment.payment.paid_at), "dd/MM/yyyy HH:mm", { locale: ptBR })}
                      </p>
                    </div>
                  )}
                </div>

                {/* PIX QR Code */}
                {selectedPayment.payment.pix_qr_code && (
                  <div className="pb-4 border-b">
                    <span className="text-gray-600 block mb-2">PIX - Copiar código</span>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <code className="text-xs break-all">{selectedPayment.payment.pix_qr_code}</code>
                      <Button
                        variant="outline"
                        size="sm"
                        className="mt-2 w-full"
                        onClick={() => {
                          navigator.clipboard.writeText(selectedPayment.payment.pix_qr_code)
                          toast.success("Código PIX copiado!")
                        }}
                      >
                        Copiar Código PIX
                      </Button>
                    </div>
                  </div>
                )}

                {/* Boleto */}
                {selectedPayment.payment.boleto_url && (
                  <div className="pb-4 border-b">
                    <span className="text-gray-600 block mb-2">Boleto</span>
                    <Button
                      variant="outline"
                      className="w-full"
                      onClick={() => window.open(selectedPayment.payment.boleto_url, "_blank")}
                    >
                      <Download className="h-4 w-4 mr-2" />
                      Baixar Boleto
                    </Button>
                  </div>
                )}

                {/* Cartão */}
                {selectedPayment.payment.card_last_4_digits && (
                  <div className="pb-4 border-b">
                    <span className="text-gray-600 block mb-1">Cartão</span>
                    <p className="font-medium">
                      {selectedPayment.payment.card_brand} •••• {selectedPayment.payment.card_last_4_digits}
                    </p>
                  </div>
                )}

                {/* ID do Pagamento */}
                <div>
                  <span className="text-gray-600 block mb-1">ID da Transação</span>
                  <code className="text-xs bg-gray-100 px-2 py-1 rounded">{selectedPayment.payment.id}</code>
                </div>
              </div>
            )}
          </DialogContent>
        </Dialog>
      </div>
    </div>
  )
}
