"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ProtectedRoute from "@/components/auth/ProtectedRoute"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Badge } from "@/components/ui/badge"
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from "@/components/ui/dialog"
import { profileApi, clearAuthTokens } from "@/lib/api"
import { toast } from "sonner"
import { format } from "date-fns"
import { ptBR } from "date-fns/locale"

interface UserProfile {
  id: string
  full_name: string
  email: string
  phone?: string
  company?: string
  bio?: string
  role: string
  email_verified: boolean
  created_at: string
  updated_at?: string
}

interface UserStats {
  account_created: string
  account_age_days: number
  email_verified: boolean
  current_plan: string
  subscription_status: string
  total_logins: number
  last_login?: string
}

function ProfileContent() {
  const router = useRouter()
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [stats, setStats] = useState<UserStats | null>(null)
  const [editMode, setEditMode] = useState(false)

  // Form states
  const [formData, setFormData] = useState({
    full_name: "",
    phone: "",
    company: "",
    bio: "",
  })

  // Change password modal
  const [showPasswordModal, setShowPasswordModal] = useState(false)
  const [passwordData, setPasswordData] = useState({
    current_password: "",
    new_password: "",
    confirm_password: "",
  })

  // Change email modal
  const [showEmailModal, setShowEmailModal] = useState(false)
  const [emailData, setEmailData] = useState({
    new_email: "",
    password: "",
  })

  // Delete account modal
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [deletePassword, setDeletePassword] = useState("")

  const fetchProfile = async () => {
    try {
      setLoading(true)
      const [profileRes, statsRes] = await Promise.all([
        profileApi.getMyProfile(),
        profileApi.getMyStats(),
      ])

      setProfile(profileRes.data)
      setStats(statsRes.data)

      // Preencher formulário com dados atuais
      setFormData({
        full_name: profileRes.data.full_name || "",
        phone: profileRes.data.phone || "",
        company: profileRes.data.company || "",
        bio: profileRes.data.bio || "",
      })
    } catch (error: any) {
      toast.error("Erro ao carregar perfil", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchProfile()
  }, [])

  const handleUpdateProfile = async () => {
    try {
      await profileApi.updateProfile(formData)
      toast.success("Perfil atualizado com sucesso!")
      setEditMode(false)
      fetchProfile()
    } catch (error: any) {
      toast.error("Erro ao atualizar perfil", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const handleChangePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      toast.error("As senhas não coincidem")
      return
    }

    if (passwordData.new_password.length < 6) {
      toast.error("A senha deve ter no mínimo 6 caracteres")
      return
    }

    try {
      await profileApi.changePassword({
        current_password: passwordData.current_password,
        new_password: passwordData.new_password,
      })
      toast.success("Senha alterada com sucesso!")
      setShowPasswordModal(false)
      setPasswordData({
        current_password: "",
        new_password: "",
        confirm_password: "",
      })
    } catch (error: any) {
      toast.error("Erro ao alterar senha", {
        description: error.response?.data?.detail || "Senha atual incorreta",
      })
    }
  }

  const handleChangeEmail = async () => {
    try {
      await profileApi.changeEmail({
        new_email: emailData.new_email,
        password: emailData.password,
      })
      toast.success("Email alterado com sucesso!")
      setShowEmailModal(false)
      setEmailData({ new_email: "", password: "" })
      fetchProfile()
    } catch (error: any) {
      toast.error("Erro ao alterar email", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const handleDeleteAccount = async () => {
    try {
      await profileApi.deleteAccount(deletePassword)
      toast.success("Conta deletada com sucesso")
      clearAuthTokens()
      router.push("/")
    } catch (error: any) {
      toast.error("Erro ao deletar conta", {
        description: error.response?.data?.detail || "Senha incorreta",
      })
    }
  }

  const formatDate = (dateString?: string) => {
    if (!dateString) return "-"
    try {
      return format(new Date(dateString), "dd/MM/yyyy 'às' HH:mm", { locale: ptBR })
    } catch {
      return dateString
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando perfil...</p>
        </div>
      </div>
    )
  }

  if (!profile) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <p className="text-gray-600">Erro ao carregar perfil</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white border-b">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Meu Perfil</h1>
              <p className="text-sm text-gray-600">Gerencie suas informações pessoais</p>
            </div>
            <Button variant="outline" onClick={() => router.push("/dashboard")}>
              Voltar ao Dashboard
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Stats */}
          <div className="space-y-6">
            {/* Account Info Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Informações da Conta</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-xs text-gray-500">Email</p>
                  <p className="text-sm font-medium">{profile.email}</p>
                  {profile.email_verified ? (
                    <Badge variant="success" className="mt-1">Verificado</Badge>
                  ) : (
                    <Badge variant="warning" className="mt-1">Não verificado</Badge>
                  )}
                </div>
                <div>
                  <p className="text-xs text-gray-500">Função</p>
                  <Badge variant={profile.role === "admin" ? "default" : "secondary"}>
                    {profile.role === "admin" ? "Administrador" : "Usuário"}
                  </Badge>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Membro desde</p>
                  <p className="text-sm">{formatDate(profile.created_at)}</p>
                </div>
                {stats && (
                  <>
                    <div>
                      <p className="text-xs text-gray-500">Plano Atual</p>
                      <p className="text-sm font-medium">{stats.current_plan}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Total de logins</p>
                      <p className="text-sm font-medium">{stats.total_logins}</p>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>

            {/* Actions Card */}
            <Card>
              <CardHeader>
                <CardTitle className="text-lg">Ações</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => setShowPasswordModal(true)}
                >
                  Alterar Senha
                </Button>
                <Button
                  variant="outline"
                  className="w-full justify-start"
                  onClick={() => setShowEmailModal(true)}
                >
                  Alterar Email
                </Button>
                <Button
                  variant="destructive"
                  className="w-full justify-start"
                  onClick={() => setShowDeleteModal(true)}
                >
                  Deletar Conta
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Right Column - Profile Form */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div>
                    <CardTitle>Dados Pessoais</CardTitle>
                    <CardDescription>
                      {editMode ? "Edite suas informações" : "Visualize suas informações"}
                    </CardDescription>
                  </div>
                  {!editMode ? (
                    <Button onClick={() => setEditMode(true)}>Editar</Button>
                  ) : (
                    <div className="flex gap-2">
                      <Button variant="outline" onClick={() => {
                        setEditMode(false)
                        setFormData({
                          full_name: profile.full_name || "",
                          phone: profile.phone || "",
                          company: profile.company || "",
                          bio: profile.bio || "",
                        })
                      }}>
                        Cancelar
                      </Button>
                      <Button onClick={handleUpdateProfile}>Salvar</Button>
                    </div>
                  )}
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  <div className="grid gap-2">
                    <Label htmlFor="full_name">Nome Completo</Label>
                    <Input
                      id="full_name"
                      value={formData.full_name}
                      onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
                      disabled={!editMode}
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="phone">Telefone</Label>
                    <Input
                      id="phone"
                      value={formData.phone}
                      onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                      disabled={!editMode}
                      placeholder="(00) 00000-0000"
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="company">Empresa</Label>
                    <Input
                      id="company"
                      value={formData.company}
                      onChange={(e) => setFormData({ ...formData, company: e.target.value })}
                      disabled={!editMode}
                      placeholder="Nome da sua empresa"
                    />
                  </div>

                  <div className="grid gap-2">
                    <Label htmlFor="bio">Bio</Label>
                    <textarea
                      id="bio"
                      value={formData.bio}
                      onChange={(e) => setFormData({ ...formData, bio: e.target.value })}
                      disabled={!editMode}
                      placeholder="Conte um pouco sobre você..."
                      className="min-h-[100px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50"
                    />
                  </div>

                  {profile.updated_at && (
                    <div className="pt-4 border-t">
                      <p className="text-xs text-gray-500">
                        Última atualização: {formatDate(profile.updated_at)}
                      </p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      {/* Change Password Modal */}
      <Dialog open={showPasswordModal} onOpenChange={setShowPasswordModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Alterar Senha</DialogTitle>
            <DialogDescription>
              Digite sua senha atual e escolha uma nova senha
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="current_password">Senha Atual</Label>
              <Input
                id="current_password"
                type="password"
                value={passwordData.current_password}
                onChange={(e) => setPasswordData({ ...passwordData, current_password: e.target.value })}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="new_password">Nova Senha</Label>
              <Input
                id="new_password"
                type="password"
                value={passwordData.new_password}
                onChange={(e) => setPasswordData({ ...passwordData, new_password: e.target.value })}
                placeholder="Mínimo 6 caracteres"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="confirm_password">Confirmar Nova Senha</Label>
              <Input
                id="confirm_password"
                type="password"
                value={passwordData.confirm_password}
                onChange={(e) => setPasswordData({ ...passwordData, confirm_password: e.target.value })}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowPasswordModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleChangePassword}>Alterar Senha</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Change Email Modal */}
      <Dialog open={showEmailModal} onOpenChange={setShowEmailModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Alterar Email</DialogTitle>
            <DialogDescription>
              Digite seu novo email e sua senha para confirmar
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="new_email">Novo Email</Label>
              <Input
                id="new_email"
                type="email"
                value={emailData.new_email}
                onChange={(e) => setEmailData({ ...emailData, new_email: e.target.value })}
                placeholder="novo@email.com"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="email_password">Senha Atual</Label>
              <Input
                id="email_password"
                type="password"
                value={emailData.password}
                onChange={(e) => setEmailData({ ...emailData, password: e.target.value })}
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEmailModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleChangeEmail}>Alterar Email</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Account Modal */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deletar Conta</DialogTitle>
            <DialogDescription>
              Esta ação não pode ser desfeita facilmente. Digite sua senha para confirmar.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="p-4 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-800">
                ⚠️ Sua conta será marcada para deleção. Seus dados serão preservados por 30 dias
                para recuperação, mas você perderá acesso imediatamente.
              </p>
            </div>

            <div className="grid gap-2">
              <Label htmlFor="delete_password">Senha</Label>
              <Input
                id="delete_password"
                type="password"
                value={deletePassword}
                onChange={(e) => setDeletePassword(e.target.value)}
                placeholder="Digite sua senha"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteAccount}>
              Confirmar Deleção
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default function ProfilePage() {
  return (
    <ProtectedRoute>
      <ProfileContent />
    </ProtectedRoute>
  )
}
