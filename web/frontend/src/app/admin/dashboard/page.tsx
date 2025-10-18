"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ProtectedRoute from "@/components/auth/ProtectedRoute"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { dashboardApi } from "@/lib/api"
import { toast } from "sonner"
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface OverviewStats {
  total_users: number
  total_plans: number
  total_subscriptions: number
  active_subscriptions: number
  new_users_last_30_days: number
  total_revenue_monthly: number
  total_revenue_yearly: number
}

interface UserGrowthData {
  date: string
  count: number
}

interface SubscriptionByPlan {
  plan_id: string
  plan_name: string
  subscribers: number
  revenue_monthly: number
  revenue_yearly: number
}

interface RevenueTrendData {
  date: string
  revenue_monthly: number
  revenue_yearly: number
  subscriptions: number
}

interface Activity {
  id: string
  type: string
  action: string
  description: string
  timestamp: string
  user_id?: string
}

interface SubscriptionStatus {
  active: number
  pending: number
  canceled: number
  expired: number
  trial: number
}

interface TopUser {
  user_id: string
  name: string
  email: string
  plan: string
  monthly_value: number
  member_since: string
}

function AdminDashboardContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [overviewStats, setOverviewStats] = useState<OverviewStats | null>(null)
  const [usersGrowth, setUsersGrowth] = useState<UserGrowthData[]>([])
  const [subscriptionsByPlan, setSubscriptionsByPlan] = useState<SubscriptionByPlan[]>([])
  const [revenueTrend, setRevenueTrend] = useState<RevenueTrendData[]>([])
  const [recentActivities, setRecentActivities] = useState<Activity[]>([])
  const [subscriptionStatus, setSubscriptionStatus] = useState<SubscriptionStatus | null>(null)
  const [topUsers, setTopUsers] = useState<TopUser[]>([])

  const fetchAllData = async () => {
    try {
      setLoading(true)

      // Buscar todas as métricas em paralelo
      const [
        overviewRes,
        usersGrowthRes,
        subscriptionsByPlanRes,
        revenueTrendRes,
        activitiesRes,
        statusRes,
        topUsersRes,
      ] = await Promise.all([
        dashboardApi.getOverviewStats(),
        dashboardApi.getUsersGrowth(30),
        dashboardApi.getSubscriptionsByPlan(),
        dashboardApi.getRevenueTrend(30),
        dashboardApi.getRecentActivities(10),
        dashboardApi.getSubscriptionStatus(),
        dashboardApi.getTopUsers(5),
      ])

      setOverviewStats(overviewRes.data)
      setUsersGrowth(usersGrowthRes.data.data)
      setSubscriptionsByPlan(subscriptionsByPlanRes.data.data)
      setRevenueTrend(revenueTrendRes.data.data)
      setRecentActivities(activitiesRes.data.activities)
      setSubscriptionStatus(statusRes.data)
      setTopUsers(topUsersRes.data.users)
    } catch (error: any) {
      toast.error("Erro ao carregar dashboard", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchAllData()
  }, [])

  const formatPrice = (priceInCents: number) => {
    return (priceInCents / 100).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    })
  }

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), "dd/MM/yyyy", { locale: ptBR })
    } catch {
      return dateString
    }
  }

  const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#8884D8"]

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Dashboard Admin</h1>
              <p className="text-sm text-gray-600">Visão geral do sistema</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => router.push("/admin/plans")}>
                Gerenciar Planos
              </Button>
              <Button variant="outline" onClick={() => router.push("/dashboard")}>
                Dashboard Usuário
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overview Stats */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total de Usuários</CardDescription>
              <CardTitle className="text-3xl">{overviewStats?.total_users || 0}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-gray-600">
                +{overviewStats?.new_users_last_30_days || 0} nos últimos 30 dias
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Assinaturas Ativas</CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {overviewStats?.active_subscriptions || 0}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-gray-600">
                de {overviewStats?.total_subscriptions || 0} total
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Receita Mensal (MRR)</CardDescription>
              <CardTitle className="text-3xl text-blue-600">
                {formatPrice(overviewStats?.total_revenue_monthly || 0)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-gray-600">Receita recorrente</div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Receita Anual (ARR)</CardDescription>
              <CardTitle className="text-3xl text-purple-600">
                {formatPrice(overviewStats?.total_revenue_yearly || 0)}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-xs text-gray-600">Potencial anual</div>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Users Growth Chart */}
          <Card>
            <CardHeader>
              <CardTitle>Crescimento de Usuários</CardTitle>
              <CardDescription>Últimos 30 dias</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={usersGrowth}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date) => format(new Date(date), "dd/MM")}
                  />
                  <YAxis />
                  <Tooltip
                    labelFormatter={(date) => format(new Date(date), "dd/MM/yyyy")}
                  />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#8884d8"
                    name="Novos Usuários"
                    strokeWidth={2}
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Subscriptions by Plan */}
          <Card>
            <CardHeader>
              <CardTitle>Assinaturas por Plano</CardTitle>
              <CardDescription>Distribuição atual</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={subscriptionsByPlan}
                    dataKey="subscribers"
                    nameKey="plan_name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label
                  >
                    {subscriptionsByPlan.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                  <Legend />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Charts Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Revenue Trend */}
          <Card>
            <CardHeader>
              <CardTitle>Tendência de Receita</CardTitle>
              <CardDescription>Últimos 30 dias</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={revenueTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis
                    dataKey="date"
                    tickFormatter={(date) => format(new Date(date), "dd/MM")}
                  />
                  <YAxis tickFormatter={(value) => formatPrice(value)} />
                  <Tooltip
                    labelFormatter={(date) => format(new Date(date), "dd/MM/yyyy")}
                    formatter={(value: number) => formatPrice(value)}
                  />
                  <Legend />
                  <Bar dataKey="revenue_monthly" fill="#8884d8" name="Receita Mensal" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Subscription Status */}
          <Card>
            <CardHeader>
              <CardTitle>Status das Assinaturas</CardTitle>
              <CardDescription>Distribuição por status</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="success">Ativas</Badge>
                  </div>
                  <span className="text-2xl font-bold">
                    {subscriptionStatus?.active || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="warning">Trial</Badge>
                  </div>
                  <span className="text-2xl font-bold">
                    {subscriptionStatus?.trial || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="secondary">Pendentes</Badge>
                  </div>
                  <span className="text-2xl font-bold">
                    {subscriptionStatus?.pending || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="destructive">Canceladas</Badge>
                  </div>
                  <span className="text-2xl font-bold">
                    {subscriptionStatus?.canceled || 0}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Badge variant="outline">Expiradas</Badge>
                  </div>
                  <span className="text-2xl font-bold">
                    {subscriptionStatus?.expired || 0}
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Bottom Row */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Recent Activities */}
          <Card>
            <CardHeader>
              <CardTitle>Atividades Recentes</CardTitle>
              <CardDescription>Últimas 10 ações no sistema</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {recentActivities.length === 0 ? (
                  <p className="text-sm text-gray-500">Nenhuma atividade recente</p>
                ) : (
                  recentActivities.map((activity) => (
                    <div key={activity.id} className="flex items-start gap-3 pb-3 border-b last:border-0">
                      <div className="flex-1">
                        <p className="text-sm font-medium">{activity.description}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <Badge variant="outline" className="text-xs">
                            {activity.type}
                          </Badge>
                          <span className="text-xs text-gray-500">
                            {formatDate(activity.timestamp)}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>

          {/* Top Users */}
          <Card>
            <CardHeader>
              <CardTitle>Top Usuários</CardTitle>
              <CardDescription>Maiores valores de assinatura</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {topUsers.length === 0 ? (
                  <p className="text-sm text-gray-500">Nenhum usuário ainda</p>
                ) : (
                  topUsers.map((user, index) => (
                    <div key={user.user_id} className="flex items-center gap-3 pb-3 border-b last:border-0">
                      <div className="flex items-center justify-center w-8 h-8 rounded-full bg-blue-100 text-blue-600 font-bold">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{user.name}</p>
                        <p className="text-xs text-gray-500">{user.email}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-sm font-bold">{formatPrice(user.monthly_value)}</p>
                        <p className="text-xs text-gray-500">{user.plan}</p>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </CardContent>
          </Card>
        </div>
      </main>
    </div>
  )
}

export default function AdminDashboardPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
      <AdminDashboardContent />
    </ProtectedRoute>
  )
}
