#!/usr/bin/env node
/**
 * WhatsApp PTT Service
 * Serviço para enviar áudios como PTT (Push-to-Talk) usando Baileys
 */

const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const { Boom } = require('@hapi/boom');
const express = require('express');
const multer = require('multer');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

// Configurações
const PORT = 3001;
const UPLOAD_DIR = path.join(__dirname, 'uploads');
const AUTH_DIR = path.join(__dirname, 'auth_baileys');

// Criar diretórios necessários
if (!fs.existsSync(UPLOAD_DIR)) {
    fs.mkdirSync(UPLOAD_DIR, { recursive: true });
}

// Configurar Express
const app = express();
app.use(cors());
app.use(express.json());

// Configurar Multer para upload de arquivos
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, UPLOAD_DIR);
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: { fileSize: 16 * 1024 * 1024 } // 16MB max
});

// Logger simples
const logger = {
    info: (msg, ...args) => console.log(`[INFO] ${msg}`, ...args),
    warn: (msg, ...args) => console.warn(`[WARN] ${msg}`, ...args),
    error: (msg, ...args) => console.error(`[ERROR] ${msg}`, ...args),
    success: (msg, ...args) => console.log(`[SUCCESS] ${msg}`, ...args)
};

// Estado do WhatsApp
let sock = null;
let qrCode = null;
let connectionState = {
    connected: false,
    qrCode: null,
    phoneNumber: null
};

/**
 * Conectar ao WhatsApp usando Baileys
 */
async function connectToWhatsApp() {
    try {
        const { state, saveCreds } = await useMultiFileAuthState(AUTH_DIR);
        const { version, isLatest } = await fetchLatestBaileysVersion();

        logger.info(`Usando Baileys v${version.join('.')}, é a última versão: ${isLatest}`);

        // Criar logger compatível com Baileys
        const baileysLogger = {
            level: 'silent',
            fatal: () => {},
            error: () => {},
            warn: () => {},
            info: () => {},
            debug: () => {},
            trace: () => {},
            child: function() { return this; }
        };

        sock = makeWASocket({
            version,
            auth: state,
            printQRInTerminal: false, // Não printar QR no terminal
            logger: baileysLogger,
            browser: ['WhatsApp PTT Bot', 'Chrome', '121.0.0'],
            getMessage: async (key) => {
                return { conversation: '' };
            }
        });

        // Salvar credenciais quando atualizadas
        sock.ev.on('creds.update', saveCreds);

        // Monitorar QR Code
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            // Atualizar QR Code
            if (qr) {
                qrCode = qr;
                connectionState.qrCode = qr;
                logger.info('📱 Novo QR Code gerado. Acesse /qr para visualizar.');
            }

            // Status da conexão
            if (connection === 'close') {
                const shouldReconnect = (lastDisconnect?.error instanceof Boom)
                    ? lastDisconnect.error.output.statusCode !== DisconnectReason.loggedOut
                    : true;

                logger.warn('❌ Conexão fechada. Reconectando...', { shouldReconnect });

                connectionState.connected = false;
                connectionState.phoneNumber = null;

                if (shouldReconnect) {
                    setTimeout(() => connectToWhatsApp(), 3000);
                }
            } else if (connection === 'open') {
                logger.info('✅ WhatsApp conectado com sucesso!');
                connectionState.connected = true;
                connectionState.qrCode = null;
                qrCode = null;

                // Obter número de telefone conectado
                try {
                    const user = sock.user;
                    if (user && user.id) {
                        connectionState.phoneNumber = user.id.split(':')[0];
                        logger.info(`📱 Número conectado: ${connectionState.phoneNumber}`);
                    }
                } catch (err) {
                    logger.error('Erro ao obter número do usuário:', err);
                }
            } else if (connection === 'connecting') {
                logger.info('🔄 Conectando ao WhatsApp...');
            }
        });

        // Monitorar mensagens recebidas (opcional)
        sock.ev.on('messages.upsert', async ({ messages }) => {
            // Você pode adicionar lógica aqui se quiser responder mensagens
        });

        return sock;

    } catch (error) {
        logger.error('❌ Erro ao conectar ao WhatsApp:', error);
        connectionState.connected = false;
        throw error;
    }
}

/**
 * Formatar número de telefone para JID do WhatsApp
 */
function formatPhoneToJID(phone) {
    // Remover caracteres especiais
    let cleanPhone = phone.replace(/[^0-9]/g, '');

    // Adicionar código do país se não tiver
    if (!cleanPhone.startsWith('55') && cleanPhone.length === 11) {
        cleanPhone = '55' + cleanPhone;
    }

    return cleanPhone + '@s.whatsapp.net';
}

/**
 * Converter áudio para formato OGG Opus
 */
async function convertToOgg(inputPath) {
    return new Promise((resolve, reject) => {
        const outputPath = inputPath.replace(/\.[^/.]+$/, '.ogg');
        const { exec } = require('child_process');

        // Converter para OGG Opus com configurações otimizadas para voz
        const command = `ffmpeg -i "${inputPath}" -c:a libopus -b:a 32k -vbr on -compression_level 10 -ar 48000 -ac 1 "${outputPath}" -y`;

        exec(command, (error, stdout, stderr) => {
            if (error) {
                logger.error('Erro ao converter áudio:', error);
                // Se falhar, retornar arquivo original
                resolve(inputPath);
            } else {
                logger.info('✅ Áudio convertido para OGG Opus');
                // Remover arquivo original
                try {
                    fs.unlinkSync(inputPath);
                } catch (e) {
                    logger.warn('Não foi possível remover arquivo original:', e);
                }
                resolve(outputPath);
            }
        });
    });
}

// ==================== ROTAS DA API ====================

/**
 * GET / - Status do serviço
 */
app.get('/', (req, res) => {
    res.json({
        service: 'WhatsApp PTT Service',
        version: '1.0.0',
        status: 'running',
        endpoints: {
            status: 'GET /status',
            qr: 'GET /qr',
            sendPTT: 'POST /send-ptt',
            logout: 'POST /logout'
        }
    });
});

/**
 * GET /status - Status da conexão WhatsApp
 */
app.get('/status', (req, res) => {
    res.json({
        connected: connectionState.connected,
        phoneNumber: connectionState.phoneNumber,
        hasQR: !!connectionState.qrCode
    });
});

/**
 * GET /qr - Obter QR Code para login
 */
app.get('/qr', (req, res) => {
    if (!connectionState.qrCode) {
        return res.status(404).json({
            success: false,
            message: 'Nenhum QR Code disponível. WhatsApp pode já estar conectado ou aguardando conexão.'
        });
    }

    res.json({
        success: true,
        qrCode: connectionState.qrCode
    });
});

/**
 * POST /send-ptt - Enviar áudio como PTT
 *
 * Body (multipart/form-data):
 * - audio: arquivo de áudio (required)
 * - phone: número do WhatsApp (required)
 * - name: nome do contato (optional)
 */
app.post('/send-ptt', upload.single('audio'), async (req, res) => {
    try {
        // Verificar se está conectado
        if (!sock || !connectionState.connected) {
            return res.status(400).json({
                success: false,
                error: 'WhatsApp não está conectado. Faça login primeiro.'
            });
        }

        // Validar dados
        const { phone, name } = req.body;
        if (!phone) {
            return res.status(400).json({
                success: false,
                error: 'Número de telefone é obrigatório'
            });
        }

        if (!req.file) {
            return res.status(400).json({
                success: false,
                error: 'Arquivo de áudio é obrigatório'
            });
        }

        let audioPath = req.file.path;
        logger.info(`📤 Enviando PTT para ${phone} (${name || 'sem nome'})`);

        // Converter para OGG Opus
        audioPath = await convertToOgg(audioPath);

        // Ler arquivo de áudio
        const audioBuffer = fs.readFileSync(audioPath);

        // Formatar JID
        const jid = formatPhoneToJID(phone);

        // Enviar como PTT
        await sock.sendMessage(jid, {
            audio: audioBuffer,
            mimetype: 'audio/ogg; codecs=opus',
            ptt: true, // 🔥 Isto define como PTT!
            fileName: 'audio.ogg'
        });

        // Limpar arquivo temporário
        fs.unlinkSync(audioPath);

        logger.info(`✅ PTT enviado com sucesso para ${phone}`);

        res.json({
            success: true,
            phone: phone,
            empresa: name || '',
            timestamp: new Date().toISOString()
        });

    } catch (error) {
        logger.error('❌ Erro ao enviar PTT:', error);

        // Limpar arquivo se existir
        if (req.file && fs.existsSync(req.file.path)) {
            fs.unlinkSync(req.file.path);
        }

        res.status(500).json({
            success: false,
            error: error.message || 'Erro ao enviar áudio PTT'
        });
    }
});

/**
 * POST /logout - Desconectar do WhatsApp
 */
app.post('/logout', async (req, res) => {
    try {
        if (sock) {
            await sock.logout();
            sock = null;
            connectionState.connected = false;
            connectionState.phoneNumber = null;

            // Remover pasta de autenticação
            if (fs.existsSync(AUTH_DIR)) {
                fs.rmSync(AUTH_DIR, { recursive: true, force: true });
            }

            logger.info('👋 Logout realizado com sucesso');
        }

        res.json({
            success: true,
            message: 'Logout realizado com sucesso'
        });
    } catch (error) {
        logger.error('❌ Erro ao fazer logout:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// ==================== INICIALIZAÇÃO ====================

/**
 * Iniciar servidor
 */
async function start() {
    try {
        // Conectar ao WhatsApp
        logger.info('🚀 Iniciando WhatsApp PTT Service...');
        await connectToWhatsApp();

        // Iniciar servidor Express
        app.listen(PORT, '0.0.0.0', () => {
            logger.info(`✅ Servidor rodando na porta ${PORT}`);
            logger.info(`📍 Acesse: http://localhost:${PORT}`);
            logger.info(`📱 Status: http://localhost:${PORT}/status`);
            logger.info(`📱 QR Code: http://localhost:${PORT}/qr`);
            console.log('\n' + '='.repeat(60));
            console.log('🎤 WhatsApp PTT Service Iniciado!');
            console.log('='.repeat(60));
            console.log(`\n📍 URL: http://localhost:${PORT}`);
            console.log(`📊 Status: http://localhost:${PORT}/status\n`);
        });

    } catch (error) {
        logger.error('❌ Erro ao iniciar serviço:', error);
        process.exit(1);
    }
}

// Tratar sinais de interrupção
process.on('SIGINT', async () => {
    logger.info('\n👋 Encerrando serviço...');
    if (sock) {
        await sock.end();
    }
    process.exit(0);
});

process.on('SIGTERM', async () => {
    logger.info('\n👋 Encerrando serviço...');
    if (sock) {
        await sock.end();
    }
    process.exit(0);
});

// Iniciar
start();
