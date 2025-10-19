"use client"

import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { XCircle, RefreshCw, ArrowLeft, HelpCircle } from "lucide-react"

export default function CheckoutFailedPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const reason = searchParams.get("reason") || "Não foi possível processar seu pagamento"

  const commonIssues = [
    {
      title: "Dados do cartão incorretos",
      description: "Verifique o número, validade e CVV do cartão"
    },
    {
      title: "Saldo insuficiente",
      description: "Certifique-se de ter saldo disponível"
    },
    {
      title: "Cartão bloqueado",
      description: "Entre em contato com seu banco"
    },
    {
      title: "Limite excedido",
      description: "Verifique o limite do seu cartão"
    }
  ]

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-gray-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4">
            <div className="relative">
              <div className="bg-red-500 rounded-full p-3">
                <XCircle className="h-16 w-16 text-white" />
              </div>
            </div>
          </div>
          <CardTitle className="text-3xl font-bold text-red-600 mb-2">
            Pagamento Não Aprovado
          </CardTitle>
          <p className="text-gray-600 text-lg">
            {reason}
          </p>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Motivo do Erro */}
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <h3 className="font-semibold text-red-900 mb-2">⚠️ O que aconteceu?</h3>
            <p className="text-red-800 text-sm">
              Seu pagamento foi recusado pela operadora do cartão ou pelo gateway de pagamento.
              Isso pode acontecer por diversos motivos.
            </p>
          </div>

          {/* Problemas Comuns */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Problemas Comuns</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {commonIssues.map((issue, index) => (
                <div
                  key={index}
                  className="bg-gray-50 border rounded-lg p-4"
                >
                  <h4 className="font-medium text-gray-900 mb-1 flex items-start gap-2">
                    <HelpCircle className="h-4 w-4 mt-0.5 flex-shrink-0 text-gray-400" />
                    {issue.title}
                  </h4>
                  <p className="text-sm text-gray-600 ml-6">{issue.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* O que fazer agora */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-3">💡 O que você pode fazer</h3>
            <ul className="space-y-2 text-blue-800 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">1.</span>
                <span>Verifique os dados do cartão e tente novamente</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">2.</span>
                <span>Tente usar outro cartão ou método de pagamento</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">3.</span>
                <span>Entre em contato com seu banco para liberar a transação</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">4.</span>
                <span>Use PIX ou Boleto para pagamento instantâneo (Mercado Pago)</span>
              </li>
            </ul>
          </div>

          {/* Informações Adicionais */}
          <div className="bg-gray-50 rounded-lg p-4 text-sm text-gray-600">
            <p>
              <strong>Importante:</strong> Nenhum valor foi cobrado. Você pode tentar novamente sem preocupações.
            </p>
          </div>

          {/* Botões de Ação */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => router.push("/pricing")}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Ver Planos
            </Button>
            <Button
              className="flex-1"
              onClick={() => router.back()}
            >
              <RefreshCw className="mr-2 h-4 w-4" />
              Tentar Novamente
            </Button>
          </div>

          {/* Métodos Alternativos */}
          <div className="border-t pt-6">
            <h3 className="font-semibold mb-3">Métodos de Pagamento Alternativos</h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">📱</div>
                <h4 className="font-medium text-sm">PIX</h4>
                <p className="text-xs text-gray-600 mt-1">Aprovação instantânea</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">📄</div>
                <h4 className="font-medium text-sm">Boleto</h4>
                <p className="text-xs text-gray-600 mt-1">Até 3 dias úteis</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-4 text-center">
                <div className="text-2xl mb-2">💳</div>
                <h4 className="font-medium text-sm">PayPal</h4>
                <p className="text-xs text-gray-600 mt-1">Proteção ao comprador</p>
              </div>
            </div>
          </div>

          {/* Suporte */}
          <div className="text-center pt-4 border-t">
            <p className="text-sm text-gray-600 mb-2">
              Ainda com problemas para efetuar o pagamento?
            </p>
            <Button variant="link" onClick={() => router.push("/support")}>
              Fale com nosso suporte
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
