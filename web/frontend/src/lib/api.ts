/**
 * API Client para comunicação com o backend FastAPI
 */
import axios, { AxiosError } from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

// Criar instância do axios
export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Interceptor para adicionar token em todas as requisições
api.interceptors.request.use(
  (config) => {
    // Pega token do localStorage (client-side only)
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('access_token')
      if (token) {
        config.headers.Authorization = `Bearer ${token}`
      }
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Token expirado, tentar refresh
      if (typeof window !== 'undefined') {
        const refreshToken = localStorage.getItem('refresh_token')
        if (refreshToken) {
          try {
            const response = await axios.post(`${API_URL}/api/auth/refresh`, {
              refresh_token: refreshToken,
            })

            const { access_token, refresh_token: newRefreshToken } = response.data
            localStorage.setItem('access_token', access_token)
            localStorage.setItem('refresh_token', newRefreshToken)

            // Repetir requisição original com novo token
            if (error.config) {
              error.config.headers.Authorization = `Bearer ${access_token}`
              return axios.request(error.config)
            }
          } catch (refreshError) {
            // Refresh falhou, fazer logout
            localStorage.removeItem('access_token')
            localStorage.removeItem('refresh_token')
            localStorage.removeItem('user')
            window.location.href = '/auth/login'
          }
        } else {
          // Sem refresh token, redirecionar para login
          window.location.href = '/auth/login'
        }
      }
    }
    return Promise.reject(error)
  }
)

// Auth endpoints
export const authApi = {
  register: (data: { email: string; password: string; name: string; phone?: string }) =>
    api.post('/api/auth/register', data),

  login: (data: { email: string; password: string }) =>
    api.post('/api/auth/login', data),

  logout: () =>
    api.post('/api/auth/logout'),

  me: () =>
    api.get('/api/auth/me'),

  getSessions: () =>
    api.get('/api/auth/sessions'),

  terminateSession: (sessionId: string) =>
    api.delete(`/api/auth/sessions/${sessionId}`),
}

// Plans endpoints
export const plansApi = {
  list: (includeInactive = false, includeDeleted = false) =>
    api.get('/api/admin/plans/', {
      params: { include_inactive: includeInactive, include_deleted: includeDeleted },
    }),

  get: (planId: string) =>
    api.get(`/api/admin/plans/${planId}`),

  create: (data: any) =>
    api.post('/api/admin/plans/', data),

  update: (planId: string, data: any) =>
    api.put(`/api/admin/plans/${planId}`, data),

  delete: (planId: string, reason?: string) =>
    api.delete(`/api/admin/plans/${planId}`, {
      params: { reason },
    }),

  toggleStatus: (planId: string) =>
    api.post(`/api/admin/plans/${planId}/toggle-status`),

  listDeleted: () =>
    api.get('/api/admin/plans/deleted/list'),

  restore: (planId: string) =>
    api.post(`/api/admin/plans/deleted/${planId}/restore`),

  stats: () =>
    api.get('/api/admin/plans/stats/summary'),
}

// Profile endpoints
export const profileApi = {
  getMyProfile: () =>
    api.get('/api/profile/me'),

  updateProfile: (data: { full_name?: string; phone?: string; company?: string; bio?: string }) =>
    api.put('/api/profile/me', data),

  changePassword: (data: { current_password: string; new_password: string }) =>
    api.post('/api/profile/me/change-password', data),

  changeEmail: (data: { new_email: string; password: string }) =>
    api.post('/api/profile/me/change-email', data),

  deleteAccount: (password: string) =>
    api.delete('/api/profile/me', {
      params: { password },
    }),

  getMyStats: () =>
    api.get('/api/profile/me/stats'),
}

// Dashboard Admin endpoints
export const dashboardApi = {
  getOverviewStats: () =>
    api.get('/api/admin/dashboard/stats/overview'),

  getUsersGrowth: (days: number = 30) =>
    api.get('/api/admin/dashboard/stats/users-growth', {
      params: { days },
    }),

  getSubscriptionsByPlan: () =>
    api.get('/api/admin/dashboard/stats/subscriptions-by-plan'),

  getRevenueTrend: (days: number = 30) =>
    api.get('/api/admin/dashboard/stats/revenue-trend', {
      params: { days },
    }),

  getRecentActivities: (limit: number = 10) =>
    api.get('/api/admin/dashboard/stats/recent-activities', {
      params: { limit },
    }),

  getSubscriptionStatus: () =>
    api.get('/api/admin/dashboard/stats/subscription-status'),

  getTopUsers: (limit: number = 10) =>
    api.get('/api/admin/dashboard/stats/top-users', {
      params: { limit },
    }),
}

// ==================== Payments API ====================
export const paymentsApi = {
  // Mercado Pago
  createMercadoPagoPreference: (data: { plan_id: string; payment_method: string; gateway: string }) =>
    api.post('/api/payments/mercadopago/create-preference', data),

  getMercadoPagoStatus: (paymentId: string) =>
    api.get(`/api/payments/mercadopago/status/${paymentId}`),

  // Stripe
  createStripeCheckout: (data: { plan_id: string; payment_method: string; gateway: string }) =>
    api.post('/api/payments/stripe/create-checkout-session', data),

  createStripeSubscription: (data: {
    plan_id: string;
    payment_method: string;
    gateway: string;
    interval: string;
    card_token: string;
  }) =>
    api.post('/api/payments/stripe/create-subscription', data),

  cancelStripeSubscription: (data: { reason?: string; cancel_at_period_end: boolean }) =>
    api.post('/api/payments/stripe/cancel-subscription', data),

  getStripeStatus: (paymentId: string) =>
    api.get(`/api/payments/stripe/status/${paymentId}`),

  // PayPal
  createPayPalOrder: (data: { plan_id: string; payment_method: string; gateway: string }) =>
    api.post('/api/payments/paypal/create-order', data),

  capturePayPalOrder: (orderId: string) =>
    api.post(`/api/payments/paypal/capture-order/${orderId}`),

  getPayPalStatus: (paymentId: string) =>
    api.get(`/api/payments/paypal/status/${paymentId}`),

  // History and Subscription
  getMyPayments: (params?: { limit?: number; status?: string; gateway?: string }) =>
    api.get('/api/payments/my-payments', { params }),

  getMySubscription: () =>
    api.get('/api/payments/my-subscription'),

  getPaymentDetails: (paymentId: string) =>
    api.get(`/api/payments/payment/${paymentId}`),

  getPaymentStats: () =>
    api.get('/api/payments/stats'),
}

// Helper functions
export const setAuthTokens = (accessToken: string, refreshToken: string, user: any) => {
  if (typeof window !== 'undefined') {
    localStorage.setItem('access_token', accessToken)
    localStorage.setItem('refresh_token', refreshToken)
    localStorage.setItem('user', JSON.stringify(user))
  }
}

export const clearAuthTokens = () => {
  if (typeof window !== 'undefined') {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('user')
  }
}

export const getUser = () => {
  if (typeof window !== 'undefined') {
    const userStr = localStorage.getItem('user')
    return userStr ? JSON.parse(userStr) : null
  }
  return null
}

export const isAuthenticated = () => {
  if (typeof window !== 'undefined') {
    return !!localStorage.getItem('access_token')
  }
  return false
}
