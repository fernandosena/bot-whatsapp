/**
 * TypeScript Types para o Frontend
 */

export interface User {
  _id: string
  email: string
  name: string
  phone?: string
  avatar?: string
  role: 'user' | 'admin' | 'super_admin'
  is_active: boolean
  email_verified: boolean
  current_plan_id?: string
  subscription_status: 'free' | 'active' | 'expired' | 'cancelled'
  created_at: string
  last_login?: string
}

export interface PlanFeatures {
  max_contacts: number // -1 = ilimitado
  max_messages_per_month: number // -1 = ilimitado
  max_devices: number
  has_variables: boolean
  has_sequence: boolean
  has_media: boolean
  has_advanced_reports: boolean
  has_api_access: boolean
  has_multi_user: boolean
  support_level: 'email' | 'email_chat' | 'priority_24x7'
}

export interface Plan {
  _id: string
  name: string
  slug: string
  description: string
  price_monthly: number // em centavos
  price_yearly?: number // em centavos
  features: PlanFeatures
  status: 'active' | 'inactive' | 'archived'
  is_visible: boolean
  is_featured: boolean
  trial_days: number
  setup_fee: number
  available_gateways: string[]
  created_at: string
  updated_at: string
}

export interface Session {
  _id: string
  user_id: string
  device_fingerprint: string
  ip_address: string
  user_agent: string
  is_active: boolean
  last_activity: string
  login_at: string
  is_desktop: boolean
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
  user: User
}

export interface ApiError {
  detail: string
}
