"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ProtectedRoute from "@/components/auth/ProtectedRoute"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { authApi } from "@/lib/api"
import { toast } from "sonner"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface Session {
  id: string
  device_info: {
    browser?: string
    os?: string
    device?: string
    user_agent?: string
  }
  ip_address: string
  location?: {
    city?: string
    country?: string
  }
  created_at: string
  last_activity?: string
  is_active: boolean
  is_current?: boolean
}

function SessionsContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [sessions, setSessions] = useState<Session[]>([])
  const [showTerminateModal, setShowTerminateModal] = useState(false)
  const [showTerminateAllModal, setShowTerminateAllModal] = useState(false)
  const [selectedSession, setSelectedSession] = useState<Session | null>(null)
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null)

  const fetchSessions = async () => {
    try {
      setLoading(true)
      const response = await authApi.getSessions()
      const sessionsData = response.data.sessions

      // Identificar sessão atual (baseado no token atual)
      const currentToken = localStorage.getItem("access_token")

      setSessions(sessionsData)

      // A primeira sessão ativa geralmente é a atual
      const activeSessions = sessionsData.filter((s: Session) => s.is_active)
      if (activeSessions.length > 0) {
        setCurrentSessionId(activeSessions[0].id)
      }
    } catch (error: any) {
      toast.error("Erro ao carregar sessões", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchSessions()
  }, [])

  const handleTerminateSession = async () => {
    if (!selectedSession) return

    try {
      await authApi.terminateSession(selectedSession.id)
      toast.success("Sessão encerrada com sucesso")
      setShowTerminateModal(false)
      setSelectedSession(null)
      fetchSessions()
    } catch (error: any) {
      toast.error("Erro ao encerrar sessão", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const handleTerminateAllSessions = async () => {
    try {
      // Encerrar todas as sessões exceto a atual
      const otherSessions = sessions.filter(
        (s) => s.is_active && s.id !== currentSessionId
      )

      await Promise.all(
        otherSessions.map((session) => authApi.terminateSession(session.id))
      )

      toast.success(`${otherSessions.length} sessões encerradas com sucesso`)
      setShowTerminateAllModal(false)
      fetchSessions()
    } catch (error: any) {
      toast.error("Erro ao encerrar sessões", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })
    } catch {
      return dateString
    }
  }

  const getDeviceIcon = (deviceInfo: Session["device_info"]) => {
    const device = deviceInfo.device?.toLowerCase() || ""
    const os = deviceInfo.os?.toLowerCase() || ""

    if (device.includes("mobile") || os.includes("android") || os.includes("ios")) {
      return "📱"
    }
    if (os.includes("mac")) {
      return "🖥️"
    }
    if (os.includes("windows")) {
      return "💻"
    }
    if (os.includes("linux")) {
      return "🐧"
    }
    return "🌐"
  }

  const getBrowserName = (deviceInfo: Session["device_info"]) => {
    const browser = deviceInfo.browser || ""
    const userAgent = deviceInfo.user_agent?.toLowerCase() || ""

    if (browser) return browser

    if (userAgent.includes("chrome")) return "Chrome"
    if (userAgent.includes("firefox")) return "Firefox"
    if (userAgent.includes("safari")) return "Safari"
    if (userAgent.includes("edge")) return "Edge"
    if (userAgent.includes("opera")) return "Opera"
    return "Navegador desconhecido"
  }

  const getOSName = (deviceInfo: Session["device_info"]) => {
    const os = deviceInfo.os || ""
    const userAgent = deviceInfo.user_agent?.toLowerCase() || ""

    if (os) return os

    if (userAgent.includes("windows")) return "Windows"
    if (userAgent.includes("mac")) return "MacOS"
    if (userAgent.includes("linux")) return "Linux"
    if (userAgent.includes("android")) return "Android"
    if (userAgent.includes("ios")) return "iOS"
    return "Sistema desconhecido"
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando sessões...</p>
        </div>
      </div>
    )
  }

  const activeSessions = sessions.filter((s) => s.is_active)
  const inactiveSessions = sessions.filter((s) => !s.is_active)

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Sessões Ativas</h1>
              <p className="text-sm text-gray-600">
                Gerencie os dispositivos conectados à sua conta
              </p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => router.push("/profile")}>
                Voltar ao Perfil
              </Button>
              {activeSessions.length > 1 && (
                <Button
                  variant="destructive"
                  onClick={() => setShowTerminateAllModal(true)}
                >
                  Encerrar Todas
                </Button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Sessões Ativas</CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {activeSessions.length}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Sessões Encerradas</CardDescription>
              <CardTitle className="text-3xl text-gray-600">
                {inactiveSessions.length}
              </CardTitle>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total de Sessões</CardDescription>
              <CardTitle className="text-3xl">{sessions.length}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Active Sessions */}
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Sessões Ativas</CardTitle>
            <CardDescription>
              Dispositivos atualmente conectados à sua conta
            </CardDescription>
          </CardHeader>
          <CardContent>
            {activeSessions.length === 0 ? (
              <p className="text-sm text-gray-500 text-center py-8">
                Nenhuma sessão ativa
              </p>
            ) : (
              <div className="space-y-4">
                {activeSessions.map((session) => (
                  <div
                    key={session.id}
                    className="flex items-start gap-4 p-4 border rounded-lg hover:bg-gray-50"
                  >
                    {/* Icon */}
                    <div className="text-3xl">{getDeviceIcon(session.device_info)}</div>

                    {/* Info */}
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="font-semibold">
                          {getBrowserName(session.device_info)} · {getOSName(session.device_info)}
                        </h3>
                        {session.id === currentSessionId && (
                          <Badge variant="success">Sessão Atual</Badge>
                        )}
                      </div>

                      <div className="space-y-1 text-sm text-gray-600">
                        <p>
                          <span className="font-medium">IP:</span> {session.ip_address}
                        </p>
                        {session.location?.city && (
                          <p>
                            <span className="font-medium">Localização:</span>{" "}
                            {session.location.city}, {session.location.country}
                          </p>
                        )}
                        <p>
                          <span className="font-medium">Iniciada em:</span>{" "}
                          {formatDate(session.created_at)}
                        </p>
                        {session.last_activity && (
                          <p>
                            <span className="font-medium">Última atividade:</span>{" "}
                            {formatDate(session.last_activity)}
                          </p>
                        )}
                      </div>
                    </div>

                    {/* Actions */}
                    {session.id !== currentSessionId && (
                      <Button
                        size="sm"
                        variant="destructive"
                        onClick={() => {
                          setSelectedSession(session)
                          setShowTerminateModal(true)
                        }}
                      >
                        Encerrar
                      </Button>
                    )}
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Inactive Sessions */}
        {inactiveSessions.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Sessões Encerradas</CardTitle>
              <CardDescription>
                Histórico de sessões anteriores (últimas 10)
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {inactiveSessions.slice(0, 10).map((session) => (
                  <div
                    key={session.id}
                    className="flex items-start gap-4 p-4 border rounded-lg bg-gray-50 opacity-60"
                  >
                    <div className="text-3xl">{getDeviceIcon(session.device_info)}</div>

                    <div className="flex-1">
                      <h3 className="font-semibold mb-1">
                        {getBrowserName(session.device_info)} · {getOSName(session.device_info)}
                      </h3>

                      <div className="space-y-1 text-sm text-gray-600">
                        <p>
                          <span className="font-medium">IP:</span> {session.ip_address}
                        </p>
                        <p>
                          <span className="font-medium">Iniciada em:</span>{" "}
                          {formatDate(session.created_at)}
                        </p>
                      </div>
                    </div>

                    <Badge variant="outline">Encerrada</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Info Box */}
        <div className="mt-8 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="font-semibold text-blue-900 mb-2">ℹ️ Sobre as Sessões</h3>
          <div className="text-sm text-blue-800 space-y-1">
            <p>
              • Cada vez que você faz login, uma nova sessão é criada para o dispositivo
            </p>
            <p>• A sessão atual não pode ser encerrada manualmente</p>
            <p>
              • Encerrar uma sessão força o logout do dispositivo correspondente
            </p>
            <p>
              • Recomendamos encerrar sessões de dispositivos que você não reconhece
            </p>
          </div>
        </div>
      </main>

      {/* Terminate Single Session Modal */}
      <Dialog open={showTerminateModal} onOpenChange={setShowTerminateModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Encerrar Sessão</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja encerrar esta sessão?
            </DialogDescription>
          </DialogHeader>

          {selectedSession && (
            <div className="py-4">
              <div className="p-4 bg-gray-50 rounded-lg space-y-2 text-sm">
                <p>
                  <span className="font-medium">Dispositivo:</span>{" "}
                  {getBrowserName(selectedSession.device_info)} ·{" "}
                  {getOSName(selectedSession.device_info)}
                </p>
                <p>
                  <span className="font-medium">IP:</span> {selectedSession.ip_address}
                </p>
                <p>
                  <span className="font-medium">Criada em:</span>{" "}
                  {formatDate(selectedSession.created_at)}
                </p>
              </div>
              <p className="text-sm text-gray-600 mt-4">
                Este dispositivo será desconectado imediatamente.
              </p>
            </div>
          )}

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTerminateModal(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleTerminateSession}>
              Encerrar Sessão
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Terminate All Sessions Modal */}
      <Dialog open={showTerminateAllModal} onOpenChange={setShowTerminateAllModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Encerrar Todas as Sessões</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja encerrar todas as outras sessões?
            </DialogDescription>
          </DialogHeader>

          <div className="py-4">
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-800">
                ⚠️ Esta ação encerrará{" "}
                <strong>
                  {activeSessions.filter((s) => s.id !== currentSessionId).length} sessões
                </strong>{" "}
                ativas em outros dispositivos. Sua sessão atual não será afetada.
              </p>
            </div>
          </div>

          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => setShowTerminateAllModal(false)}
            >
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleTerminateAllSessions}>
              Encerrar Todas
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default function SessionsPage() {
  return (
    <ProtectedRoute>
      <SessionsContent />
    </ProtectedRoute>
  )
}
