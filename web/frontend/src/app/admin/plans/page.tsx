"use client"

import { useEffect, useState } from "react"
import { useRouter } from "next/navigation"
import ProtectedRoute from "@/components/auth/ProtectedRoute"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
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
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { plansApi } from "@/lib/api"
import type { Plan, PlanFeatures } from "@/types"
import { toast } from "sonner"

function AdminPlansContent() {
  const router = useRouter()
  const [plans, setPlans] = useState<Plan[]>([])
  const [deletedPlans, setDeletedPlans] = useState<Plan[]>([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [showDeleteModal, setShowDeleteModal] = useState(false)
  const [showDeletedSection, setShowDeletedSection] = useState(false)
  const [selectedPlan, setSelectedPlan] = useState<Plan | null>(null)
  const [deleteReason, setDeleteReason] = useState("")

  // Form state
  const [formData, setFormData] = useState({
    name: "",
    description: "",
    price_monthly: 0,
    price_yearly: 0,
    status: "active",
    is_visible: true,
    is_featured: false,
    features: {
      max_contacts: 100,
      max_messages_per_month: 500,
      max_devices: 1,
      has_variables: false,
      has_sequence: false,
      has_media: false,
      has_advanced_reports: false,
      has_api_access: false,
      has_multi_user: false,
      support_level: "email",
    } as PlanFeatures,
  })

  const fetchPlans = async () => {
    try {
      setLoading(true)
      const response = await plansApi.list(true, false) // include_invisible=true, only_deleted=false
      setPlans(response.data as Plan[])
    } catch (error: any) {
      toast.error("Erro ao carregar planos", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    } finally {
      setLoading(false)
    }
  }

  const fetchDeletedPlans = async () => {
    try {
      const response = await plansApi.listDeleted()
      setDeletedPlans(response.data as Plan[])
    } catch (error: any) {
      toast.error("Erro ao carregar planos deletados", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  useEffect(() => {
    fetchPlans()
  }, [])

  useEffect(() => {
    if (showDeletedSection) {
      fetchDeletedPlans()
    }
  }, [showDeletedSection])

  const resetForm = () => {
    setFormData({
      name: "",
      description: "",
      price_monthly: 0,
      price_yearly: 0,
      status: "active",
      is_visible: true,
      is_featured: false,
      features: {
        max_contacts: 100,
        max_messages_per_month: 500,
        max_devices: 1,
        has_variables: false,
        has_sequence: false,
        has_media: false,
        has_advanced_reports: false,
        has_api_access: false,
        has_multi_user: false,
        support_level: "email",
      },
    })
  }

  const handleCreate = async () => {
    try {
      await plansApi.create(formData)
      toast.success("Plano criado com sucesso!")
      setShowCreateModal(false)
      resetForm()
      fetchPlans()
    } catch (error: any) {
      toast.error("Erro ao criar plano", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const handleEdit = async () => {
    if (!selectedPlan) return

    try {
      await plansApi.update(selectedPlan.id, formData)
      toast.success("Plano atualizado com sucesso!")
      setShowEditModal(false)
      setSelectedPlan(null)
      resetForm()
      fetchPlans()
    } catch (error: any) {
      toast.error("Erro ao atualizar plano", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const handleDelete = async () => {
    if (!selectedPlan) return

    try {
      await plansApi.delete(selectedPlan.id, deleteReason)
      toast.success("Plano deletado com sucesso!")
      setShowDeleteModal(false)
      setSelectedPlan(null)
      setDeleteReason("")
      fetchPlans()
    } catch (error: any) {
      toast.error("Erro ao deletar plano", {
        description: error.response?.data?.detail || "Pode haver assinaturas ativas",
      })
    }
  }

  const handleToggleStatus = async (planId: string) => {
    try {
      await plansApi.toggleStatus(planId)
      toast.success("Status alterado com sucesso!")
      fetchPlans()
    } catch (error: any) {
      toast.error("Erro ao alterar status", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const handleRestore = async (planId: string) => {
    try {
      await plansApi.restore(planId)
      toast.success("Plano restaurado com sucesso!")
      fetchDeletedPlans()
      fetchPlans()
    } catch (error: any) {
      toast.error("Erro ao restaurar plano", {
        description: error.response?.data?.detail || "Tente novamente",
      })
    }
  }

  const openEditModal = (plan: Plan) => {
    setSelectedPlan(plan)
    setFormData({
      name: plan.name,
      description: plan.description,
      price_monthly: plan.price_monthly,
      price_yearly: plan.price_yearly,
      status: plan.status,
      is_visible: plan.is_visible,
      is_featured: plan.is_featured || false,
      features: plan.features,
    })
    setShowEditModal(true)
  }

  const openDeleteModal = (plan: Plan) => {
    setSelectedPlan(plan)
    setShowDeleteModal(true)
  }

  const formatPrice = (priceInCents: number) => {
    return (priceInCents / 100).toLocaleString("pt-BR", {
      style: "currency",
      currency: "BRL",
    })
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto"></div>
          <p className="mt-4 text-gray-600">Carregando planos...</p>
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
              <h1 className="text-2xl font-bold text-gray-900">Gerenciamento de Planos</h1>
              <p className="text-sm text-gray-600">Crie e gerencie os planos de assinatura</p>
            </div>
            <div className="flex gap-2">
              <Button variant="outline" onClick={() => router.push("/admin/dashboard")}>
                Voltar ao Dashboard
              </Button>
              <Button onClick={() => setShowCreateModal(true)}>
                + Criar Novo Plano
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Total de Planos</CardDescription>
              <CardTitle className="text-3xl">{plans.length}</CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Planos Ativos</CardDescription>
              <CardTitle className="text-3xl text-green-600">
                {plans.filter((p) => p.status === "active").length}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Planos Visíveis</CardDescription>
              <CardTitle className="text-3xl text-blue-600">
                {plans.filter((p) => p.is_visible).length}
              </CardTitle>
            </CardHeader>
          </Card>
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>Planos Deletados</CardDescription>
              <CardTitle className="text-3xl text-red-600">{deletedPlans.length}</CardTitle>
            </CardHeader>
          </Card>
        </div>

        {/* Plans Table */}
        <Card>
          <CardHeader>
            <CardTitle>Planos Cadastrados</CardTitle>
            <CardDescription>
              Gerencie os planos de assinatura do sistema
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Nome</TableHead>
                  <TableHead>Preço Mensal</TableHead>
                  <TableHead>Preço Anual</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Visível</TableHead>
                  <TableHead>Destaque</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {plans.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-gray-500 py-8">
                      Nenhum plano cadastrado. Crie seu primeiro plano!
                    </TableCell>
                  </TableRow>
                ) : (
                  plans.map((plan) => (
                    <TableRow key={plan.id}>
                      <TableCell className="font-medium">{plan.name}</TableCell>
                      <TableCell>{formatPrice(plan.price_monthly)}</TableCell>
                      <TableCell>{formatPrice(plan.price_yearly)}</TableCell>
                      <TableCell>
                        <Badge variant={plan.status === "active" ? "success" : "secondary"}>
                          {plan.status === "active" ? "Ativo" : "Inativo"}
                        </Badge>
                      </TableCell>
                      <TableCell>
                        {plan.is_visible ? (
                          <Badge variant="default">Sim</Badge>
                        ) : (
                          <Badge variant="outline">Não</Badge>
                        )}
                      </TableCell>
                      <TableCell>
                        {plan.is_featured ? (
                          <Badge variant="warning">⭐ Destaque</Badge>
                        ) : (
                          <span className="text-gray-400">-</span>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => openEditModal(plan)}
                          >
                            Editar
                          </Button>
                          <Button
                            size="sm"
                            variant={plan.status === "active" ? "secondary" : "default"}
                            onClick={() => handleToggleStatus(plan.id)}
                          >
                            {plan.status === "active" ? "Desativar" : "Ativar"}
                          </Button>
                          <Button
                            size="sm"
                            variant="destructive"
                            onClick={() => openDeleteModal(plan)}
                          >
                            Deletar
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </CardContent>
        </Card>

        {/* Deleted Plans Section */}
        <div className="mt-8">
          <Button
            variant="outline"
            onClick={() => setShowDeletedSection(!showDeletedSection)}
            className="mb-4"
          >
            {showDeletedSection ? "Ocultar" : "Ver"} Planos Deletados ({deletedPlans.length})
          </Button>

          {showDeletedSection && (
            <Card>
              <CardHeader>
                <CardTitle>Planos Deletados</CardTitle>
                <CardDescription>
                  Planos removidos do sistema (soft delete)
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nome</TableHead>
                      <TableHead>Deletado em</TableHead>
                      <TableHead>Motivo</TableHead>
                      <TableHead className="text-right">Ações</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {deletedPlans.length === 0 ? (
                      <TableRow>
                        <TableCell colSpan={4} className="text-center text-gray-500 py-8">
                          Nenhum plano deletado
                        </TableCell>
                      </TableRow>
                    ) : (
                      deletedPlans.map((plan) => (
                        <TableRow key={plan.id}>
                          <TableCell className="font-medium">{plan.name}</TableCell>
                          <TableCell>
                            {plan.deleted_at
                              ? new Date(plan.deleted_at).toLocaleString("pt-BR")
                              : "-"}
                          </TableCell>
                          <TableCell className="text-gray-600">
                            {plan.deleted_reason || "Sem motivo especificado"}
                          </TableCell>
                          <TableCell className="text-right">
                            <Button
                              size="sm"
                              variant="default"
                              onClick={() => handleRestore(plan.id)}
                            >
                              Restaurar
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))
                    )}
                  </TableBody>
                </Table>
              </CardContent>
            </Card>
          )}
        </div>
      </main>

      {/* Create Plan Modal */}
      <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Criar Novo Plano</DialogTitle>
            <DialogDescription>
              Preencha os dados do novo plano de assinatura
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            {/* Basic Info */}
            <div className="grid gap-2">
              <Label htmlFor="name">Nome do Plano *</Label>
              <Input
                id="name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                placeholder="Ex: Plano Básico"
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="description">Descrição *</Label>
              <Input
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                placeholder="Ex: Ideal para pequenas empresas"
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="price_monthly">Preço Mensal (centavos) *</Label>
                <Input
                  id="price_monthly"
                  type="number"
                  value={formData.price_monthly}
                  onChange={(e) =>
                    setFormData({ ...formData, price_monthly: parseInt(e.target.value) || 0 })
                  }
                  placeholder="Ex: 9900 (R$ 99,00)"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="price_yearly">Preço Anual (centavos) *</Label>
                <Input
                  id="price_yearly"
                  type="number"
                  value={formData.price_yearly}
                  onChange={(e) =>
                    setFormData({ ...formData, price_yearly: parseInt(e.target.value) || 0 })
                  }
                  placeholder="Ex: 99000 (R$ 990,00)"
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label htmlFor="status">Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => setFormData({ ...formData, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Ativo</SelectItem>
                    <SelectItem value="inactive">Inativo</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2 pt-8">
                <input
                  type="checkbox"
                  id="is_visible"
                  checked={formData.is_visible}
                  onChange={(e) =>
                    setFormData({ ...formData, is_visible: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="is_visible" className="cursor-pointer">
                  Visível
                </Label>
              </div>

              <div className="flex items-center space-x-2 pt-8">
                <input
                  type="checkbox"
                  id="is_featured"
                  checked={formData.is_featured}
                  onChange={(e) =>
                    setFormData({ ...formData, is_featured: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="is_featured" className="cursor-pointer">
                  Destaque
                </Label>
              </div>
            </div>

            {/* Features */}
            <div className="border-t pt-4 mt-2">
              <h3 className="font-semibold mb-4">Recursos do Plano</h3>

              <div className="grid grid-cols-2 gap-4">
                <div className="grid gap-2">
                  <Label>Máx. Contatos</Label>
                  <Input
                    type="number"
                    value={formData.features.max_contacts}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: {
                          ...formData.features,
                          max_contacts: parseInt(e.target.value) || 0,
                        },
                      })
                    }
                    placeholder="-1 para ilimitado"
                  />
                </div>

                <div className="grid gap-2">
                  <Label>Máx. Mensagens/Mês</Label>
                  <Input
                    type="number"
                    value={formData.features.max_messages_per_month}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: {
                          ...formData.features,
                          max_messages_per_month: parseInt(e.target.value) || 0,
                        },
                      })
                    }
                    placeholder="-1 para ilimitado"
                  />
                </div>

                <div className="grid gap-2">
                  <Label>Máx. Dispositivos</Label>
                  <Input
                    type="number"
                    value={formData.features.max_devices}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        features: {
                          ...formData.features,
                          max_devices: parseInt(e.target.value) || 0,
                        },
                      })
                    }
                  />
                </div>

                <div className="grid gap-2">
                  <Label>Nível de Suporte</Label>
                  <Select
                    value={formData.features.support_level}
                    onValueChange={(value) =>
                      setFormData({
                        ...formData,
                        features: { ...formData.features, support_level: value },
                      })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="email">Email</SelectItem>
                      <SelectItem value="chat">Chat</SelectItem>
                      <SelectItem value="priority">Prioritário</SelectItem>
                      <SelectItem value="dedicated">Dedicado</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              {/* Feature Checkboxes */}
              <div className="grid grid-cols-2 gap-4 mt-4">
                {[
                  { key: "has_variables", label: "Variáveis" },
                  { key: "has_sequence", label: "Sequências" },
                  { key: "has_media", label: "Mídia" },
                  { key: "has_advanced_reports", label: "Relatórios Avançados" },
                  { key: "has_api_access", label: "Acesso API" },
                  { key: "has_multi_user", label: "Multi-usuário" },
                ].map((feature) => (
                  <div key={feature.key} className="flex items-center space-x-2">
                    <input
                      type="checkbox"
                      id={feature.key}
                      checked={formData.features[feature.key as keyof PlanFeatures] as boolean}
                      onChange={(e) =>
                        setFormData({
                          ...formData,
                          features: {
                            ...formData.features,
                            [feature.key]: e.target.checked,
                          },
                        })
                      }
                      className="h-4 w-4"
                    />
                    <Label htmlFor={feature.key} className="cursor-pointer">
                      {feature.label}
                    </Label>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowCreateModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleCreate}>Criar Plano</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Edit Plan Modal */}
      <Dialog open={showEditModal} onOpenChange={setShowEditModal}>
        <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>Editar Plano</DialogTitle>
            <DialogDescription>
              Atualize os dados do plano {selectedPlan?.name}
            </DialogDescription>
          </DialogHeader>

          {/* Same form as Create Modal - reusing the structure */}
          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="edit_name">Nome do Plano *</Label>
              <Input
                id="edit_name"
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              />
            </div>

            <div className="grid gap-2">
              <Label htmlFor="edit_description">Descrição *</Label>
              <Input
                id="edit_description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              />
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="grid gap-2">
                <Label>Preço Mensal (centavos)</Label>
                <Input
                  type="number"
                  value={formData.price_monthly}
                  onChange={(e) =>
                    setFormData({ ...formData, price_monthly: parseInt(e.target.value) || 0 })
                  }
                />
              </div>

              <div className="grid gap-2">
                <Label>Preço Anual (centavos)</Label>
                <Input
                  type="number"
                  value={formData.price_yearly}
                  onChange={(e) =>
                    setFormData({ ...formData, price_yearly: parseInt(e.target.value) || 0 })
                  }
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4">
              <div className="grid gap-2">
                <Label>Status</Label>
                <Select
                  value={formData.status}
                  onValueChange={(value) => setFormData({ ...formData, status: value })}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="active">Ativo</SelectItem>
                    <SelectItem value="inactive">Inativo</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="flex items-center space-x-2 pt-8">
                <input
                  type="checkbox"
                  id="edit_visible"
                  checked={formData.is_visible}
                  onChange={(e) =>
                    setFormData({ ...formData, is_visible: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="edit_visible" className="cursor-pointer">
                  Visível
                </Label>
              </div>

              <div className="flex items-center space-x-2 pt-8">
                <input
                  type="checkbox"
                  id="edit_featured"
                  checked={formData.is_featured}
                  onChange={(e) =>
                    setFormData({ ...formData, is_featured: e.target.checked })
                  }
                  className="h-4 w-4"
                />
                <Label htmlFor="edit_featured" className="cursor-pointer">
                  Destaque
                </Label>
              </div>
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowEditModal(false)}>
              Cancelar
            </Button>
            <Button onClick={handleEdit}>Salvar Alterações</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Delete Confirmation Modal */}
      <Dialog open={showDeleteModal} onOpenChange={setShowDeleteModal}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Deletar Plano</DialogTitle>
            <DialogDescription>
              Tem certeza que deseja deletar o plano &quot;{selectedPlan?.name}&quot;?
              <br />
              Esta ação NÃO pode ser desfeita se houver assinaturas ativas.
            </DialogDescription>
          </DialogHeader>

          <div className="grid gap-4 py-4">
            <div className="grid gap-2">
              <Label htmlFor="delete_reason">Motivo da deleção (opcional)</Label>
              <Input
                id="delete_reason"
                value={deleteReason}
                onChange={(e) => setDeleteReason(e.target.value)}
                placeholder="Ex: Plano descontinuado"
              />
            </div>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteModal(false)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDelete}>
              Confirmar Deleção
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default function AdminPlansPage() {
  return (
    <ProtectedRoute requireAdmin={true}>
      <AdminPlansContent />
    </ProtectedRoute>
  )
}
