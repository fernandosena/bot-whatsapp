// ====== CONTINUAÇÃO DO SCRIPT DE SEQUÊNCIA ======

// Inicializar Sortable (drag and drop)
function initSortable() {
    const el = document.getElementById('sequenceBuilder');
    Sortable.create(el, {
        animation: 150,
        handle: '.sequence-item',
        onEnd: function() {
            updateSequence();
        }
    });
}

// Adicionar item à sequência
function addMessageItem(type) {
    const item = {
        id: Date.now(),
        type: type,
        content: null,
        file: null,
        delay: type === 'delay' ? 5 : 0
    };

    sequence.push(item);
    renderSequence();
    updateStats();

    // Abrir modal de edição
    setTimeout(() => editItem(sequence.length - 1), 300);
}

// Renderizar sequência
function renderSequence() {
    const builder = document.getElementById('sequenceBuilder');

    if (sequence.length === 0) {
        builder.className = 'sequence-builder empty';
        builder.innerHTML = `
            <i class="fas fa-magic fa-3x mb-3 text-muted"></i>
            <h5 class="text-muted">Comece adicionando itens à sequência</h5>
            <p class="text-muted">Clique nos tipos de mensagem à esquerda</p>
        `;
        return;
    }

    builder.className = 'sequence-builder';
    builder.innerHTML = sequence.map((item, index) => `
        <div class="sequence-item" data-index="${index}">
            <div class="sequence-number">${index + 1}</div>
            <div class="sequence-item-header">
                <div class="sequence-item-type">
                    <span class="type-badge type-${item.type}">
                        ${getTypeIcon(item.type)} ${getTypeLabel(item.type)}
                    </span>
                </div>
                <div class="sequence-item-actions">
                    <button class="btn btn-sm btn-outline-primary" onclick="editItem(${index})">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="removeItem(${index})">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
            <div class="content-preview">
                ${getPreview(item)}
            </div>
        </div>
    `).join('');
}

// Obter ícone do tipo
function getTypeIcon(type) {
    const icons = {
        text: '<i class="fas fa-comment"></i>',
        image: '<i class="fas fa-image"></i>',
        audio: '<i class="fas fa-file-audio"></i>',
        ptt: '<i class="fas fa-microphone"></i>',
        video: '<i class="fas fa-video"></i>',
        document: '<i class="fas fa-file"></i>',
        contact: '<i class="fas fa-address-card"></i>',
        location: '<i class="fas fa-map-marker-alt"></i>',
        delay: '<i class="fas fa-clock"></i>'
    };
    return icons[type] || '<i class="fas fa-question"></i>';
}

// Obter label do tipo
function getTypeLabel(type) {
    const labels = {
        text: 'Texto',
        image: 'Imagem',
        audio: 'Áudio',
        ptt: 'PTT (Áudio de Voz)',
        video: 'Vídeo',
        document: 'Documento',
        contact: 'Contato',
        location: 'Localização',
        delay: 'Aguardar'
    };
    return labels[type] || type;
}

// Obter preview do conteúdo
function getPreview(item) {
    switch (item.type) {
        case 'text':
            return item.content ? `<p class="mb-0">${item.content.substring(0, 100)}${item.content.length > 100 ? '...' : ''}</p>` : '<em>Sem conteúdo</em>';

        case 'image':
            return item.file ? `<img src="${URL.createObjectURL(item.file)}" alt="Preview">` : '<em>Nenhuma imagem selecionada</em>';

        case 'audio':
        case 'ptt':
            return item.file ? `<audio controls><source src="${URL.createObjectURL(item.file)}"></audio>` : '<em>Nenhum áudio selecionado</em>';

        case 'video':
            return item.file ? `<video width="200" controls><source src="${URL.createObjectURL(item.file)}"></video>` : '<em>Nenhum vídeo selecionado</em>';

        case 'document':
            return item.file ? `<i class="fas fa-file-pdf fa-3x"></i><br>${item.file.name}` : '<em>Nenhum arquivo selecionado</em>';

        case 'contact':
            return item.content ? `
                <strong>${item.content.name}</strong><br>
                <small>${item.content.phone}</small>
            ` : '<em>Sem informações de contato</em>';

        case 'location':
            return item.content ? `
                <i class="fas fa-map-marker-alt"></i>
                Lat: ${item.content.latitude}, Long: ${item.content.longitude}
            ` : '<em>Sem localização</em>';

        case 'delay':
            return `<i class="fas fa-clock"></i> Aguardar ${item.delay} segundo(s)`;

        default:
            return '<em>Sem preview</em>';
    }
}

// Editar item
function editItem(index) {
    currentEditIndex = index;
    const item = sequence[index];
    const modal = new bootstrap.Modal(document.getElementById('editModal'));

    document.getElementById('editModalTitle').innerHTML = `
        ${getTypeIcon(item.type)} Editar ${getTypeLabel(item.type)}
    `;

    document.getElementById('editModalBody').innerHTML = getEditForm(item);
    modal.show();
}

// Obter formulário de edição
function getEditForm(item) {
    switch (item.type) {
        case 'text':
            return `
                <div class="mb-3">
                    <label class="form-label">Mensagem de Texto</label>
                    <textarea class="form-control" id="editContent" rows="5" placeholder="Digite sua mensagem...">${item.content || ''}</textarea>
                    <small class="text-muted">Use variáveis como {{nome}}, {{cidade}}, {{setor}}</small>
                </div>
                <div class="mb-3">
                    <label class="form-label">Preview com Variáveis</label>
                    <div class="alert alert-info">
                        <strong>Exemplo:</strong><br>
                        Olá {{nome}}! Somos da empresa XYZ de {{cidade}}.
                    </div>
                </div>
            `;

        case 'image':
            return `
                <div class="mb-3">
                    <label class="form-label">Selecionar Imagem</label>
                    <input type="file" class="form-control" id="editFile" accept="image/*">
                    ${item.file ? `<small class="text-success">✓ Arquivo: ${item.file.name}</small>` : ''}
                </div>
                <div class="mb-3">
                    <label class="form-label">Legenda (opcional)</label>
                    <textarea class="form-control" id="editContent" rows="3" placeholder="Adicione uma legenda...">${item.content || ''}</textarea>
                </div>
            `;

        case 'audio':
        case 'ptt':
            return `
                <div class="mb-3">
                    <label class="form-label">Selecionar Áudio</label>
                    <input type="file" class="form-control" id="editFile" accept="audio/*">
                    ${item.file ? `<small class="text-success">✓ Arquivo: ${item.file.name}</small>` : ''}
                </div>
                ${item.type === 'ptt' ? '<div class="alert alert-warning"><i class="fas fa-info-circle"></i> O áudio será enviado como mensagem de voz (PTT)</div>' : ''}
            `;

        case 'video':
            return `
                <div class="mb-3">
                    <label class="form-label">Selecionar Vídeo</label>
                    <input type="file" class="form-control" id="editFile" accept="video/*">
                    ${item.file ? `<small class="text-success">✓ Arquivo: ${item.file.name}</small>` : ''}
                </div>
                <div class="mb-3">
                    <label class="form-label">Legenda (opcional)</label>
                    <textarea class="form-control" id="editContent" rows="3" placeholder="Adicione uma legenda...">${item.content || ''}</textarea>
                </div>
            `;

        case 'document':
            return `
                <div class="mb-3">
                    <label class="form-label">Selecionar Arquivo</label>
                    <input type="file" class="form-control" id="editFile">
                    ${item.file ? `<small class="text-success">✓ Arquivo: ${item.file.name}</small>` : ''}
                </div>
            `;

        case 'contact':
            return `
                <div class="mb-3">
                    <label class="form-label">Nome do Contato</label>
                    <input type="text" class="form-control" id="editContactName" placeholder="João Silva" value="${item.content?.name || ''}">
                </div>
                <div class="mb-3">
                    <label class="form-label">Telefone</label>
                    <input type="tel" class="form-control" id="editContactPhone" placeholder="5511999999999" value="${item.content?.phone || ''}">
                </div>
            `;

        case 'location':
            return `
                <div class="mb-3">
                    <label class="form-label">Latitude</label>
                    <input type="number" step="any" class="form-control" id="editLatitude" placeholder="-23.5505" value="${item.content?.latitude || ''}">
                </div>
                <div class="mb-3">
                    <label class="form-label">Longitude</label>
                    <input type="number" step="any" class="form-control" id="editLongitude" placeholder="-46.6333" value="${item.content?.longitude || ''}">
                </div>
                <div class="alert alert-info">
                    <i class="fas fa-info-circle"></i> Você pode obter coordenadas no Google Maps
                </div>
            `;

        case 'delay':
            return `
                <div class="mb-3">
                    <label class="form-label">Tempo de Espera: <strong id="delayValueEdit">${item.delay}s</strong></label>
                    <input type="range" class="form-range" id="editDelay" min="1" max="60" value="${item.delay}" oninput="document.getElementById('delayValueEdit').textContent = this.value + 's'">
                    <small class="text-muted">Tempo que o sistema vai aguardar antes de enviar a próxima mensagem</small>
                </div>
            `;

        default:
            return '<p>Tipo não suportado</p>';
    }
}

// Salvar item editado
function saveItem() {
    const item = sequence[currentEditIndex];

    switch (item.type) {
        case 'text':
            item.content = document.getElementById('editContent').value;
            break;

        case 'image':
        case 'audio':
        case 'ptt':
        case 'video':
        case 'document':
            const fileInput = document.getElementById('editFile');
            if (fileInput?.files[0]) {
                item.file = fileInput.files[0];
            }
            const contentInput = document.getElementById('editContent');
            if (contentInput) {
                item.content = contentInput.value;
            }
            break;

        case 'contact':
            item.content = {
                name: document.getElementById('editContactName').value,
                phone: document.getElementById('editContactPhone').value
            };
            break;

        case 'location':
            item.content = {
                latitude: document.getElementById('editLatitude').value,
                longitude: document.getElementById('editLongitude').value
            };
            break;

        case 'delay':
            item.delay = parseInt(document.getElementById('editDelay').value);
            break;
    }

    bootstrap.Modal.getInstance(document.getElementById('editModal')).hide();
    renderSequence();
    updateStats();
}

// Remover item
function removeItem(index) {
    if (confirm('Remover este item da sequência?')) {
        sequence.splice(index, 1);
        renderSequence();
        updateStats();
    }
}

// Limpar sequência
function clearSequence() {
    if (confirm('Limpar toda a sequência?')) {
        sequence = [];
        renderSequence();
        updateStats();
    }
}

// Atualizar sequência após drag
function updateSequence() {
    const items = document.querySelectorAll('.sequence-item');
    const newSequence = [];
    items.forEach(item => {
        const index = parseInt(item.getAttribute('data-index'));
        newSequence.push(sequence[index]);
    });
    sequence = newSequence;
    renderSequence();
}

// Atualizar estatísticas
function updateStats() {
    document.getElementById('sequenceCount').textContent = sequence.length;

    // Calcular tempo estimado
    let totalTime = 0;
    sequence.forEach(item => {
        if (item.type === 'delay') {
            totalTime += item.delay;
        } else {
            totalTime += 2; // Tempo médio de envio
        }
    });

    const contacts = selectedContacts.length || 0;
    const totalWithDelay = totalTime * contacts + (contacts * 5); // 5s de delay entre contatos

    document.getElementById('totalTime').textContent = formatTime(totalWithDelay);

    // Habilitar/desabilitar botão de envio
    const canSend = sequence.length > 0 && selectedContacts.length > 0;
    document.getElementById('sendBtn').disabled = !canSend;
}

// Formatar tempo
function formatTime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${minutes}min ${secs}s`;
}

// Copiar variável
function copyVariable(variable) {
    navigator.clipboard.writeText(variable);

    // Feedback visual
    const toast = document.createElement('div');
    toast.className = 'alert alert-success position-fixed top-0 start-50 translate-middle-x mt-3';
    toast.innerHTML = `<i class="fas fa-check"></i> ${variable} copiado!`;
    toast.style.zIndex = '9999';
    document.body.appendChild(toast);

    setTimeout(() => toast.remove(), 2000);
}

// Atualizar valor do delay
function updateDelayValue(value) {
    document.getElementById('contactDelayValue').textContent = value + 's';
}

// Preview da sequência
function previewSequence() {
    if (sequence.length === 0) {
        alert('Adicione itens à sequência primeiro!');
        return;
    }

    let preview = 'PREVIEW DA SEQUÊNCIA:\n\n';
    sequence.forEach((item, index) => {
        preview += `${index + 1}. ${getTypeLabel(item.type)}\n`;
        if (item.type === 'text' && item.content) {
            preview += `   "${item.content.substring(0, 50)}..."\n`;
        } else if (item.type === 'delay') {
            preview += `   Aguardar ${item.delay}s\n`;
        } else if (item.file) {
            preview += `   Arquivo: ${item.file.name}\n`;
        }
        preview += '\n';
    });

    alert(preview);
}

// Selecionar contatos
async function selectContacts() {
    try {
        const setor = document.getElementById('filterSetor').value;
        const cidade = document.getElementById('filterCidade').value;

        const params = new URLSearchParams({ setor, cidade, has_whatsapp: 'true' });
        const response = await fetch(`/api/audio/empresas-disponiveis?${params}`);
        const data = await response.json();

        const modal = new bootstrap.Modal(document.getElementById('contactsModal'));
        const modalBody = document.getElementById('contactsModalBody');

        modalBody.innerHTML = `
            <div class="mb-3">
                <button class="btn btn-sm btn-primary" onclick="selectAllContacts()">
                    <i class="fas fa-check-double"></i> Selecionar Todos
                </button>
                <button class="btn btn-sm btn-secondary" onclick="deselectAllContacts()">
                    <i class="fas fa-times"></i> Desmarcar Todos
                </button>
                <span class="ms-3">Total: ${data.empresas.length} contatos</span>
            </div>
            <div style="max-height: 400px; overflow-y: auto;">
                ${data.empresas.map(emp => `
                    <div class="form-check mb-2">
                        <input class="form-check-input contact-checkbox" type="checkbox" value="${emp.id}" id="contact${emp.id}">
                        <label class="form-check-label" for="contact${emp.id}">
                            <strong>${emp.nome}</strong> - ${emp.cidade}
                            <br><small class="text-muted">${emp.whatsapp}</small>
                        </label>
                    </div>
                `).join('')}
            </div>
        `;

        modal.show();

        // Aplicar seleções existentes
        selectedContacts.forEach(id => {
            const checkbox = document.getElementById(`contact${id}`);
            if (checkbox) checkbox.checked = true;
        });

        // Event listener para checkboxes
        document.querySelectorAll('.contact-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', updateSelectedContacts);
        });

    } catch (error) {
        console.error('Erro ao carregar contatos:', error);
        alert('Erro ao carregar contatos');
    }
}

// Atualizar contatos selecionados
function updateSelectedContacts() {
    selectedContacts = Array.from(document.querySelectorAll('.contact-checkbox:checked'))
        .map(cb => parseInt(cb.value));

    document.getElementById('contactCount').textContent = selectedContacts.length;
    updateStats();
}

// Selecionar todos os contatos
function selectAllContacts() {
    document.querySelectorAll('.contact-checkbox').forEach(cb => cb.checked = true);
    updateSelectedContacts();
}

// Desmarcar todos os contatos
function deselectAllContacts() {
    document.querySelectorAll('.contact-checkbox').forEach(cb => cb.checked = false);
    updateSelectedContacts();
}

// Enviar sequência
async function sendSequence() {
    if (sequence.length === 0) {
        alert('Adicione mensagens à sequência!');
        return;
    }

    if (selectedContacts.length === 0) {
        alert('Selecione pelo menos um contato!');
        return;
    }

    if (!confirm(`Enviar sequência de ${sequence.length} mensagens para ${selectedContacts.length} contato(s)?`)) {
        return;
    }

    // Preparar dados
    const formData = new FormData();
    formData.append('campaign_name', document.getElementById('campaignName').value || 'Campanha Sequência');
    formData.append('contact_delay', document.getElementById('contactDelay').value);
    formData.append('selected_contacts', JSON.stringify(selectedContacts));

    // Adicionar sequência
    sequence.forEach((item, index) => {
        formData.append(`sequence[${index}][type]`, item.type);

        if (item.file) {
            formData.append(`sequence[${index}][file]`, item.file);
        }

        if (item.content) {
            formData.append(`sequence[${index}][content]`, typeof item.content === 'object' ? JSON.stringify(item.content) : item.content);
        }

        if (item.type === 'delay') {
            formData.append(`sequence[${index}][delay]`, item.delay);
        }
    });

    try {
        const btn = document.getElementById('sendBtn');
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';

        document.getElementById('progressCard').style.display = 'block';

        const response = await fetch('/api/whatsapp/send-sequence', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();

        if (result.success) {
            // WebSocket vai lidar com o progresso
            listenToProgress(result.campaign_id);
        } else {
            alert('Erro: ' + result.message);
            btn.disabled = false;
            btn.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Sequência';
        }

    } catch (error) {
        console.error('Erro ao enviar:', error);
        alert('Erro ao enviar sequência');
    }
}

// Ouvir progresso via WebSocket
function listenToProgress(campaignId) {
    socket.on('sequence_progress', (data) => {
        updateProgress(data);
    });

    socket.on('sequence_complete', (data) => {
        alert(`Sequência concluída!\n${data.success} enviados com sucesso\n${data.failed} falhas`);
        document.getElementById('sendBtn').disabled = false;
        document.getElementById('sendBtn').innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Sequência';
    });

    socket.on('sequence_error', (data) => {
        alert('Erro: ' + data.message);
        document.getElementById('sendBtn').disabled = false;
        document.getElementById('sendBtn').innerHTML = '<i class="fas fa-paper-plane"></i> Enviar Sequência';
    });
}

// Atualizar progresso visual
function updateProgress(data) {
    const percent = (data.current / data.total) * 100;
    document.getElementById('progressBar').style.width = percent + '%';
    document.getElementById('progressText').textContent = `${data.current}/${data.total}`;

    const log = document.getElementById('progressLog');
    const entry = document.createElement('div');
    entry.className = `progress-item progress-${data.success ? 'success' : 'error'}`;
    entry.innerHTML = `
        <i class="fas fa-${data.success ? 'check-circle' : 'times-circle'}"></i>
        <strong>${data.contact}</strong> - ${data.message || data.error}
    `;
    log.prepend(entry);
}
