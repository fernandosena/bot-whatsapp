"use client"

import { useEffect, useState } from "react"
import { useRouter, useSearchParams } from "next/navigation"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { CheckCircle2, Loader2, ArrowRight } from "lucide-react"
import confetti from "canvas-confetti"

export default function CheckoutSuccessPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Efeito de confetti
    confetti({
      particleCount: 100,
      spread: 70,
      origin: { y: 0.6 }
    })

    // Simular verificação de pagamento
    setTimeout(() => {
      setLoading(false)
    }, 2000)
  }, [])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <Card className="w-full max-w-md">
          <CardContent className="pt-6 text-center">
            <Loader2 className="h-12 w-12 animate-spin text-blue-600 mx-auto mb-4" />
            <h2 className="text-xl font-semibold mb-2">Verificando pagamento...</h2>
            <p className="text-gray-600">Aguarde enquanto confirmamos seu pagamento</p>
          </CardContent>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-blue-50 flex items-center justify-center p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto mb-4">
            <div className="relative">
              <div className="absolute inset-0 bg-green-100 rounded-full animate-ping opacity-75"></div>
              <div className="relative bg-green-500 rounded-full p-3">
                <CheckCircle2 className="h-16 w-16 text-white" />
              </div>
            </div>
          </div>
          <CardTitle className="text-3xl font-bold text-green-600 mb-2">
            Pagamento Aprovado! 🎉
          </CardTitle>
          <p className="text-gray-600 text-lg">
            Sua assinatura foi ativada com sucesso
          </p>
        </CardHeader>

        <CardContent className="space-y-6">
          {/* Informações do Pagamento */}
          <div className="bg-gray-50 rounded-lg p-6 space-y-4">
            <h3 className="font-semibold text-lg mb-4">Detalhes da Assinatura</h3>

            <div className="space-y-3">
              <div className="flex justify-between items-center pb-3 border-b">
                <span className="text-gray-600">Status</span>
                <span className="flex items-center gap-2 text-green-600 font-medium">
                  <div className="h-2 w-2 bg-green-600 rounded-full animate-pulse"></div>
                  Ativo
                </span>
              </div>

              <div className="flex justify-between items-center pb-3 border-b">
                <span className="text-gray-600">Próxima cobrança</span>
                <span className="font-medium">
                  {new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString('pt-BR')}
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-gray-600">Forma de pagamento</span>
                <span className="font-medium">
                  {searchParams.get("method") || "Cartão de Crédito"}
                </span>
              </div>
            </div>
          </div>

          {/* O que fazer agora */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="font-semibold text-blue-900 mb-3">🚀 Próximos Passos</h3>
            <ul className="space-y-2 text-blue-800">
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">1.</span>
                <span>Acesse seu dashboard para configurar sua conta</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">2.</span>
                <span>Conecte seu WhatsApp Business</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-blue-600 font-bold mt-0.5">3.</span>
                <span>Importe seus contatos e comece a enviar mensagens</span>
              </li>
            </ul>
          </div>

          {/* Email de Confirmação */}
          <div className="text-center text-sm text-gray-600">
            <p>
              📧 Um email de confirmação foi enviado para você com todos os detalhes da sua assinatura.
            </p>
          </div>

          {/* Botões de Ação */}
          <div className="flex flex-col sm:flex-row gap-3 pt-4">
            <Button
              variant="outline"
              className="flex-1"
              onClick={() => router.push("/profile")}
            >
              Ver Perfil
            </Button>
            <Button
              className="flex-1"
              onClick={() => router.push("/dashboard")}
            >
              Ir para Dashboard
              <ArrowRight className="ml-2 h-4 w-4" />
            </Button>
          </div>

          {/* Suporte */}
          <div className="text-center pt-4 border-t">
            <p className="text-sm text-gray-600">
              Precisa de ajuda?{" "}
              <a href="/support" className="text-blue-600 hover:underline font-medium">
                Entre em contato com o suporte
              </a>
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
