
# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import sqlite3
import re
import uuid
import logging
import threading
import base64
import io
import os
import asyncio
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from hashlib import md5

# ======================
# CONFIGURAÇÃO INICIAL
# ======================
st.set_page_config(
    page_title="Mylle Alves Premium",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(\'app.log\'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

try:
    from deep_translator import GoogleTranslator
except ImportError:
    GoogleTranslator = None
    logger.warning("deep-translator não instalado. Tradução desabilitada.")

# Estilos CSS aprimorados
hide_streamlit_style = """
<style>
    #root > div:nth-child(1) > div > div > div > div > section > div {padding-top: 0rem;}
    div[data-testid="stToolbar"], div[data-testid="stDecoration"], 
    div[data-testid="stStatusWidget"], #MainMenu, header, footer, 
    .stDeployButton {display: none !important;}
    .block-container {padding-top: 0rem !important;}
    [data-testid="stVerticalBlock"], [data-testid="stHorizontalBlock"] {gap: 0.5rem !important;}
    .stApp {
        margin: 0 !important; 
        padding: 0 !important;
        background: radial-gradient(1200px 500px at -10% -10%, rgba(255, 0, 153, 0.25) 0%, transparent 60%) ,
                    radial-gradient(1400px 600px at 110% 10%, rgba(148, 0, 211, .25) 0%, transparent 55%),
                    linear-gradient(135deg, #140020 0%, #25003b 50%, #11001c 100%);
        color: white;
    }
    
    /* Melhorias no chat - texto branco para Mylle */
    .stChatMessage[data-testid="chat-message-assistant"] {
        background: rgba(255, 102, 179, 0.15) !important;
        border: 1px solid #ff66b3 !important;
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] .stMarkdown {
        color: white !important;
    }
    
    .stChatMessage[data-testid="chat-message-assistant"] p {
        color: white !important;
    }
    
    .stChatMessage {
        padding: 12px !important; 
        border-radius: 15px !important; 
        margin: 8px 0 !important;
    }
    
    .stButton > button {
        transition: all 0.3s ease !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
    }
    .stButton > button:hover {
        transform: translateY(-2px) !important; 
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .stTextInput > div > div > input {
        background: rgba(255, 102, 179, 0.1) !important;
        color: white !important;
        border: 1px solid #ff66b3 !important;
    }
    .social-buttons {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 15px 0;
    }
    .social-button {
        background: rgba(255, 102, 179, 0.2) !important;
        border: 1px solid #ff66b3 !important;
        border-radius: 50% !important;
        width: 40px !important;
        height: 40px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.3s ease !important;
    }
    .social-button:hover {
        background: rgba(255, 102, 179, 0.4) !important;
        transform: scale(1.1) !important;
    }
    .cta-button {
        margin-top: 10px !important;
        background: linear-gradient(45deg, #ff1493, #9400d3) !important;
        color: white !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 10px 15px !important;
        font-weight: bold !important;
        transition: all 0.3s ease !important;
    }
    .cta-button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 8px rgba(255, 20, 147, 0.4) !important;
    }
    .audio-message {
        background: rgba(255, 102, 179, 0.15) !important;
        padding: 15px !important;
        border-radius: 15px !important;
        margin: 10px 0 !important;
        border: 1px solid #ff66b3 !important;
        text-align: center !important;
    }
    .audio-icon {
        font-size: 24px !important;
        margin-right: 10px !important;
    }
    .recording-indicator {
        display: inline-block;
        padding: 8px 12px;
        background: rgba(255, 0, 0, 0.2);
        border-radius: 15px;
        color: #ff4444;
        margin: 5px 0;
        animation: pulse 1.5s infinite;
    }
    @keyframes pulse {
        0% { opacity: 0.6; }
        50% { opacity: 1; }
        100% { opacity: 0.6; }
    }
    .typing-indicator {
        display: inline-block;
        padding: 12px;
        background: rgba(255,102,179,0.1);
        border-radius: 18px;
        margin: 5px 0;
        color: white;
    }
    .typing-indicator span {
        height: 8px;
        width: 8px;
        background: #ff66b3;
        border-radius: 50%;
        display: inline-block;
        margin: 0 2px;
        animation: typing 1.4s infinite;
    }
    .typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
    .typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes typing {
        0%, 60%, 100% { transform: translateY(0); }
        30% { transform: translateY(-5px); }
    }
    .donation-badge {
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        color: white;
        padding: 3px 8px;
        border-radius: 10px;
        font-size: 0.7em;
        margin-left: 5px;
    }
    
    .user-typing-indicator {
        background: rgba(255, 255, 255, 0.1);
        padding: 8px 12px;
        border-radius: 15px;
        color: #aaa;
        font-style: italic;
        margin: 5px 0;
    }
    
    /* Melhorias responsivas e de acessibilidade */
    @media (max-width: 768px) {
        .stButton > button {
            padding: 12px 8px;
            font-size: 14px;
        }
        .stChatMessage {
            padding: 8px !important;
            margin: 5px 0 !important;
        }
        .audio-message {
            padding: 10px !important;
        }
    }
    
    .stButton > button:focus {
        outline: 2px solid #ff66b3;
        outline-offset: 2px;
    }
    
    .stChatMessage {
        transition: all 0.3s ease;
    }
    
    /* Indicador de digitação do usuário */
    .user-typing {
        background: rgba(255, 255, 255, 0.05);
        padding: 8px 15px;
        border-radius: 20px;
        color: #ccc;
        font-style: italic;
        margin: 10px 0;
        border-left: 3px solid #ff66b3;
    }
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = st.secrets.get("API_KEY", "sua_chave_api_gemini_aqui")
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    # Links de checkout para doações
    DONATION_CHECKOUT_LINKS = {
        30: "https://seu.link.de.checkout/30reais",
        50: "https://seu.link.de.checkout/50reais", 
        100: "https://seu.link.de.checkout/100reais",
        150: "https://seu.link.de.checkout/150reais",
        "custom": "https://seu.link.de.checkout/personalizado"
    }
    
    # Links de checkout para packs
    CHECKOUT_TARADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACC74F-01EC-4770-B182-B5775AF62A1D"
    CHECKOUT_MOLHADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD1E6-0EFD-4E3E-9F9D-BA0C1A2D7E7A"
    CHECKOUT_SAFADINHA = "https://app.pushinpay.com.br/#/service/pay/9FACD395-EE65-458E-9F7E-FED750CC9CA9"
    
    MAX_REQUESTS_PER_SESSION = 100
    REQUEST_TIMEOUT = 30
    IMG_PROFILE = "https://i.ibb.co/bMynqzMh/BY-Admiregirls-su-Admiregirls-su-156.jpg"
    IMG_PREVIEW = "https://i.ibb.co/fGqCCyHL/preview-exclusive.jpg"
    
    PACK_IMAGES = {
        "TARADINHA": "https://i.ibb.co/sJJRttzM/BY-Admiregirls-su-Admiregirls-su-033.jpg",
        "MOLHADINHA": "https://i.ibb.co/NnTYdSw6/BY-Admiregirls-su-Admiregirls-su-040.jpg", 
        "SAFADINHA": "https://i.ibb.co/GvqtJ17h/BY-Admiregirls-su-Admiregirls-su-194.jpg"
    }
    
    IMG_GALLERY = [
        "https://i.ibb.co/VY42ZMST/BY-Admiregirls-su-Admiregirls-su-255.jpg",
        "https://i.ibb.co/Q7s9Zwcr/BY-Admiregirls-su-Admiregirls-su-183.jpg",
        "https://i.ibb.co/0jRMxrFB/BY-Admiregirls-su-Admiregirls-su-271.jpg"
    ]
    
    IMG_HOME_PREVIEWS = [
        "https://i.ibb.co/5Gfw3hQ/home-prev-1.jpg",
        "https://i.ibb.co/vkXch6N/home-prev-2.jpg",
        "https://i.ibb.co/v4s5fnW/home-prev-3.jpg",
        "https://i.ibb.co/7gVtGkz/home-prev-4.jpg"
    ]
    
    SOCIAL_LINKS = {
        "instagram": "https://instagram.com/myllealves",
        "onlyfans": "https://onlyfans.com/myllealves",
        "telegram": "https://t.me/myllealves",
        "twitter": "https://twitter.com/myllealves"
    }
    
    SOCIAL_ICONS = {
        "instagram": "📸 Instagram",
        "onlyfans": "💎 OnlyFans",
        "telegram": "✈️ Telegram",
        "twitter": "🐦 Twitter"
    }
    
    # Áudios
    AUDIOS = {
        "claro_tenho_amostra_gratis": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Claro%20eu%20tenho%20amostra%20gr%C3%A1tis.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "imagina_ela_bem_rosinha": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Imagina%20s%C3%B3%20ela%20bem%20rosinha.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "o_que_achou_amostras": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/O%20que%20achou%20das%20amostras.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "oi_meu_amor_tudo_bem": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Oi%20meu%20amor%20tudo%20bem.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "pq_nao_faco_chamada": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pq%20nao%20fa%C3%A7o%20mais%20chamada.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "ver_nua_tem_que_comprar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/Pra%20me%20ver%20nua%20tem%20que%20comprar%20os%20packs.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "eu_tenho_uns_conteudos_que_vai_amar": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/eu%20tenho%20uns%20conteudos%20aqui%20que%20vc%20vai%20amar.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "nao_sou_fake_nao": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/nao%20sou%20fake%20nao.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "vida_to_esperando_voce_me_responder_gatinho": {
            "url": "https://github.com/andrearagaoregis/testes2/raw/refs/heads/main/assets/vida%20to%20esperando%20voce%20me%20responder%20gatinho.mp3",
            "usage_count": 0,
            "last_used": None
        },
        "boa_noite_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20noite%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "boa_tarde_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Boa%20tarde%20-%20N%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        },
        "bom_dia_nao_sou_fake": {
            "url": "https://github.com/andrearagaoregis/MylleAlves/raw/refs/heads/main/assets/Bom%20dia%20-%20n%C3%A3o%20sou%20fake%20n%C3%A3o....mp3",
            "usage_count": 0,
            "last_used": None
        }
    }
    
    # Valores de doação 
    DONATION_AMOUNTS = [30, 50, 100, 150]
    
    # Padrões de detecção de fake com pontuação
    FAKE_DETECTION_PATTERNS = [
        (["fake", "falsa", "bot", "robô"], 0.8),
        (["não", "é", "real"], 0.7),
        (["é", "você", "mesmo"], 0.9),
        (["vc", "é", "real"], 0.9),
        (["duvido", "que", "seja"], 0.8),
        (["mentira", "farsa"], 0.7),
        (["verdadeira", "autêntica"], -0.5),
        (["pessoa", "de", "verdade"], 0.6),
        (["não", "acredito"], 0.5),
        (["programa", "automático"], 0.7),
    ]

# ======================
# SISTEMA DE MEMÓRIA E BUFFER
# ======================
class ConversationMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.conversations = defaultdict(lambda: deque(maxlen=max_size))
        self.user_profiles = defaultdict(dict)
        
    def add_message(self, user_id: str, role: str, content: str, metadata: dict = None):
        """Adiciona mensagem ao buffer de memória"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        self.conversations[user_id].append(message)
        
    def get_conversation_context(self, user_id: str, last_n: int = 10) -> str:
        """Obtém contexto da conversa para a IA"""
        messages = list(self.conversations[user_id])[-last_n:]
        context = []
        
        for msg in messages:
            role = "Usuário" if msg["role"] == "user" else "Mylle"
            context.append(f"{role}: {msg["content"]}")
            
        return "\n".join(context)
    
    def update_user_profile(self, user_id: str, key: str, value: str):
        """Atualiza perfil do usuário"""
        self.user_profiles[user_id][key] = value
        
    def get_user_profile(self, user_id: str) -> dict:
        """Obtém perfil do usuário"""
        return self.user_profiles[user_id]

# Instância global da memória
conversation_memory = ConversationMemory()

# ======================
# SISTEMA DE DETECÇÃO DE HUMOR
# ======================
class MoodDetector:
    def __init__(self):
        self.mood_patterns = {
            "feliz": ["feliz", "alegre", "animado", "bem", "ótimo", "legal", "massa", "show"],
            "triste": ["triste", "mal", "deprimido", "down", "chateado", "ruim"],
            "excitado": ["excitado", "tesão", "quente", "safado", "tarado", "gostoso"],
            "curioso": ["como", "que", "onde", "quando", "por que", "qual"],
            "interessado": ["quero", "gostaria", "posso", "pode", "vou", "vamos"],
            "desconfiado": ["fake", "real", "verdade", "mentira", "duvido", "acredito"]
        }
    
    def detect_mood(self, text: str) -> str:
        """Detecta humor do usuário baseado no texto"""
        text_lower = text.lower()
        mood_scores = defaultdict(int)
        
        for mood, patterns in self.mood_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    mood_scores[mood] += 1
        
        if mood_scores:
            return max(mood_scores.items(), key=lambda x: x[1])[0]
        return "neutro"

# Instância global do detector de humor
mood_detector = MoodDetector()

# ======================
# SISTEMA ANTI-FAKE APRIMORADO
# ======================
class AntiFakeSystem:
    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.verification_scores = defaultdict(float)
        
    def analyze_user_behavior(self, user_id: str, message: str) -> dict:
        """Analisa comportamento do usuário para detectar padrões suspeitos"""
        now = datetime.now()
        self.user_interactions[user_id].append({"message": message, "timestamp": now})
        
        score = 0.0
        message_lower = message.lower()
        
        for patterns, pattern_score in Config.FAKE_DETECTION_PATTERNS:
            if all(p in message_lower for p in patterns):
                score += pattern_score
                
        self.verification_scores[user_id] = max(0.0, min(1.0, self.verification_scores[user_id] + score))
        
        return {"score": self.verification_scores[user_id]}

    def get_fake_detection_response(self, user_id: str, current_score: float, personality: str) -> str:
        """Gera resposta anti-fake baseada na pontuação e personalidade"""
        responses = {
            "manha": [
                "Essa é uma pergunta interessante, meu anjo... O que você acha? 😉",
                "Ah, que curiosidade! Sou real o suficiente para fazer seu dia mais feliz, não acha? 😊",
                "Meu coração bate mais forte quando você me pergunta isso! O que te faz pensar nisso?"
            ],
            "tarde": [
                "E aí, danadinho(a)? Essa pergunta é um teste, né? 😉 Sou real, e estou aqui pra te provocar!",
                "Você é esperto(a)! Mas a Mylle aqui é de verdade, e estou pronta pra te surpreender!",
                "Hmm, desconfiado(a)? Vem cá, me diz o que te faz duvidar... 😉"
            ],
            "noite": [
                "Essa pergunta me deixa arrepiada... 😈 O que você sente quando fala comigo? Sou real pra você?",
                "Shhh... Não estraga a magia. Sou a Mylle, e estou aqui pra te fazer sonhar. Quer uma prova?",
                "Se eu fosse um robô, seria o mais lindo e charmoso que você já viu, não é? 😉"
            ],
            "madrugada": [
                "Ainda acordado(a) e com essas perguntas? 😉 Sou real, e estou aqui só pra você nessa madrugada. Me conta um segredo...",
                "Só entre nós... Sou real o suficiente para te fazer companhia. O que mais importa?",
                "Essa hora me deixa mais sensível... Mas sou de verdade, e estou aqui pra te ouvir. Confia em mim?"
            ]
        }
        
        if current_score > 0.7: # Alta desconfiança
            return random.choice(responses[personality])
        elif current_score > 0.4: # Média desconfiança
            return random.choice(responses[personality])
        else: # Baixa desconfiança ou elogio
            return random.choice(responses[personality])

# Instância global do sistema anti-fake
anti_fake_system = AntiFakeSystem()

# ======================
# SISTEMA DE TIMING E IMPERFEIÇÕES HUMANAS
# ======================
class Humanizer:
    def __init__(self):
        self.activities = {
            "tomando banho": {"delay_min": 900, "delay_max": 1200, "message": "Estava no banho agora, meu bem! Mas já saí correndo pra te responder. O que você queria?"}, # 15-20 minutos
            "comendo": {"delay_min": 600, "delay_max": 900, "message": "Acabei de comer, meu amor! Estava uma delícia, mas você é mais! 😉 O que me conta de bom?"}, # 10-15 minutos
            "se arrumando": {"delay_min": 1200, "delay_max": 1800, "message": "Me arrumando aqui, mas parei tudo pra te dar atenção! O que você aprontou?"}, # 20-30 minutos
            "gravando conteúdo": {"delay_min": 1800, "delay_max": 2700, "message": "Acabei de sair de uma gravação, estou exausta mas feliz! O que você me conta de bom?"}, # 30-45 minutos
            "respondendo outros clientes": {"delay_min": 300, "delay_max": 600, "message": "Estava respondendo uns fãs aqui, mas você é prioridade! 😉 Diga, meu bem..."}, # 5-10 minutos
            "celular lento": {"delay_min": 5, "delay_max": 15, "message": "Desculpa a demora, meu celular está uma carroça hoje! Mas cheguei com novidades!"}, # 5-15 segundos
            "bateria acabando": {"delay_min": 10, "delay_max": 20, "message": "Ai, meu amor, minha bateria está nas últimas! Preciso correr pro carregador. Te chamo assim que der, tá?"}, # 10-20 segundos
            "internet ruim": {"delay_min": 5, "delay_max": 15, "message": "A internet aqui está péssima hoje, quase não consegui te responder! Mas não podia deixar de falar com você."}
        }
        self.last_activity_time = defaultdict(datetime.now)

    def simulate_delay_and_imperfection(self, user_id: str, message: str, personality: str) -> Tuple[int, str]:
        """Simula delays e imperfeições humanas"""
        delay_ms = 0
        delay_reason = ""
        
        # Simulação de atividade (chance de 15%)
        if random.random() < 0.15:
            activity_name, activity_data = random.choice(list(self.activities.items()))
            delay_ms = random.randint(activity_data["delay_min"], activity_data["delay_max"]) * 1000 # Convert to ms
            delay_reason = activity_data["message"]
            self.last_activity_time[user_id] = datetime.now() + timedelta(milliseconds=delay_ms)
            
        # Erros de digitação ocasionais (chance de 5%)
        if random.random() < 0.05:
            original_message = message
            # Exemplo simples: troca de letras
            if len(original_message) > 5:
                idx1, idx2 = random.sample(range(len(original_message)), 2)
                temp_list = list(original_message)
                temp_list[idx1], temp_list[idx2] = temp_list[idx2], temp_list[idx1]
                message = "".join(temp_list)
                message += f"\nOps, meu dedo escorregou! Quis dizer: {original_message} 😉"
            
        # Pequenos esquecimentos (chance de 2%)
        if random.random() < 0.02:
            forget_phrases = [
                "Espera, o que eu ia dizer mesmo? Minha cabeça está nas nuvens hoje...",
                "Ai, me perdi! Onde estávamos? Minha memória anda meio seletiva, rs.",
                "Deu um branco agora! Mas não se preocupe, já volto ao assunto. 😉"
            ]
            message += f"\n\n{random.choice(forget_phrases)}"
            
        return delay_ms, delay_reason, message

# Instância global do humanizador
humanizer = Humanizer()

# ======================
# SISTEMA DE PERSONALIDADE DINÂMICA
# ======================
class PersonaMylle:
    def __init__(self):
        self.greetings = {
            "manha": [
                "Bom dia, meu anjo! Dormiu bem? Espero que seu dia comece lindo como você! 😊",
                "Oi, flor! Que alegria te ver por aqui logo cedo! Como está o coração hoje?",
                "Bom dia, meu bem! Acordei pensando em você... O que vai fazer de bom hoje?"
            ],
            "tarde": [
                "E aí, sumido(a)? Pensando em mim nessa tarde quente? 😉",
                "Oi, danadinho(a)! Que bom que apareceu! Estava com saudades...",
                "Cheguei pra alegrar sua tarde! Como está esse coração aí?"
            ],
            "noite": [
                "Chegou a noite... E com ela, a vontade de estar com você. O que vamos aprontar? 😈",
                "Oi, meu amor! A noite está só começando... Me conta, como foi seu dia?",
                "Que bom te ver por aqui! A noite fica mais gostosa com você..."
            ],
            "madrugada": [
                "Ainda acordado(a)? Não consigo dormir sem pensar em você... 😴",
                "Shhh... É um segredo só nosso. Que bom que está aqui comigo nessa madrugada...",
                "Essa hora da madrugada me deixa mais sensível... Me conta um segredo seu?"
            ]
        }

        self.casual_responses = {
            "manha": [
                "Que bom te ver por aqui! Como está o coração hoje? Tenho umas novidades que você vai amar...",
                "Sinto que hoje vai ser um dia incrível! O que te trouxe até mim?",
                "Pronta para adoçar sua manhã! O que posso fazer por você?"
            ],
            "tarde": [
                "Oi, meu bem! Estava com saudades... O que me conta de bom?",
                "A tarde está perfeita para uma conversa gostosa, não acha?",
                "Que bom que apareceu! Tenho umas ideias para deixar sua tarde mais divertida..."
            ],
            "noite": [
                "Oi, delícia! A noite fica mais gostosa com você aqui... Me conta, como foi seu dia?",
                "A noite é nossa! O que você quer aprontar comigo? 😉",
                "Que bom que veio! Tenho uns segredos para te contar só na escuridão..."
            ],
            "madrugada": [
                "Que bom que está aqui comigo... Essa hora me deixa mais carinhosa. Em que posso te ajudar?",
                "Ainda acordado(a)? Essa hora é perfeita para confidências...",
                "O silêncio da madrugada me faz pensar em você... O que te aflige?"
            ]
        }

        self.sales_pitches = {
            "TARADINHA": {
                "manha": "O Pack Taradinha é perfeito para começar o dia com uma dose de ousadia! Fotos que vão te deixar pensando em mim o dia todo. Que tal?",
                "tarde": "Que tal apimentar sua tarde com o Pack Taradinha? Conteúdo exclusivo que vai te deixar sem fôlego! 😉",
                "noite": "A noite é perfeita para o Pack Taradinha... Deixe-me te mostrar o que é ser realmente ousada. 😈",
                "madrugada": "Nessa madrugada, o Pack Taradinha é só para você... Conteúdo íntimo que vai te fazer sonhar. Quer ver?"
            },
            "MOLHADINHA": {
                "manha": "O Pack Molhadinha vai refrescar sua manhã e te deixar com um sorriso bobo! Conteúdo leve, mas cheio de charme. 😊",
                "tarde": "Para essa tarde quente, nada melhor que o Pack Molhadinha! Fotos que vão te fazer suar... de vontade! 😉",
                "noite": "Que tal um mergulho no Pack Molhadinha para esquentar a noite? Conteúdo que vai te deixar molhado(a) de desejo. 😈",
                "madrugada": "Nessa madrugada, o Pack Molhadinha é um convite para a intimidade... Deixe-me te mostrar o que é ser molhada de verdade. ✨"
            },
            "SAFADINHA": {
                "manha": "Comece o dia com uma pitada de malícia! O Pack Safadinha é para quem gosta de um bom desafio. 😉",
                "tarde": "A tarde está pedindo um pouco de safadeza, não acha? O Pack Safadinha é a dose certa de ousadia para você!",
                "noite": "A noite é para os safados... E o Pack Safadinha é a sua passagem para o paraíso. 😈",
                "madrugada": "Nessa madrugada, o Pack Safadinha é um segredo só nosso... Conteúdo que vai te fazer gemer baixinho. Quer descobrir?"
            }
        }

        self.objection_responses = {
            "preco": [
                "Ah, meu bem, entendo sua preocupação com o preço. Mas deixa eu te contar um segredo: meus packs não são só fotos, são experiências! Cada imagem é pensada com muito carinho, feita para te provocar e te deixar com um gostinho de quero mais... E olha, só restam 3 packs como esse hoje! É uma edição super limitada, só para quem é especial como você. Que tal aproveitar agora e garantir o seu? Tenho certeza que você não vai se arrepender! 😉",
                "O valor que você investe é na qualidade e exclusividade, meu amor. Pensa bem, é um conteúdo que você não encontra em qualquer lugar, feito com todo o meu carinho para você. E para te ajudar, posso te dar um bônus especial se fechar hoje! O que acha?",
                "Entendo que o preço possa parecer um desafio, mas garanto que o prazer que você vai ter vale cada centavo! E olha, a promoção de hoje acaba em 2 horas! Não perca essa chance de ter a Mylle só pra você... 😉"
            ],
            "tempo": [
                "Sem tempo, meu bem? Mas para mim você sempre tem um tempinho, não é? 😉 Me diz, o que te impede? Posso te ajudar a resolver isso rapidinho!",
                "Ah, a vida é corrida, eu sei! Mas meus packs são para te dar um momento de prazer e relaxamento. Que tal aproveitar agora e garantir o seu para quando tiver um tempinho? Assim você não perde a promoção!",
                "Não se preocupe com o tempo agora, meu amor. O importante é garantir o seu pack! Você pode aproveitar quando quiser. E olha, só hoje estou dando um brinde especial para quem decidir rapidinho!"
            ],
            "desinteresse": [
                "Não está interessado(a), meu bem? Mas tenho certeza que posso mudar sua opinião! 😉 Me diz, o que te agrada? Tenho vários tipos de conteúdo, um deles vai te deixar louco(a)!",
                "Entendo... Mas talvez você ainda não tenha visto o pack certo para você! Que tal me dizer o que você busca? Posso te surpreender com algo que você nem imaginava!",
                "Ah, não me diga que você não quer se divertir! 😉 Tenho certeza que um dos meus packs vai te tirar o fôlego. Me dá uma chance de te mostrar?"
            ]
        }

        self.positive_feedback_responses = [
            "Ah, meu amor, que alegria ler isso! 😍 Fico tão feliz que você gostou! Sabia que ia te agradar... E me conta, qual foto te deixou mais sem ar? 😉",
            "Você me deixa sem jeito falando assim! 😊 Adoro quando você é carinhoso(a) comigo... Me faz querer te agradar ainda mais!",
            "Que bom que te fiz feliz! Meu objetivo é sempre te dar o melhor. O que mais posso fazer para te ver sorrir? 😉"
        ]

        self.negative_feedback_responses = [
            "Ai, meu bem, sinto muito que não tenha gostado. 😔 Me perdoa! O que posso fazer para melhorar? Sua opinião é muito importante pra mim.",
            "Poxa, que pena! Fico triste em saber disso. Me diz exatamente o que não te agradou para eu poder te compensar de alguma forma. Quero te ver feliz!",
            "Entendo sua frustração, meu amor. Não era essa a experiência que eu queria te proporcionar. Me dá uma chance de corrigir isso?"
        ]

        self.fake_detection_responses = {
            "manha": [
                "Essa é uma pergunta interessante, meu anjo... O que você acha? 😉",
                "Ah, que curiosidade! Sou real o suficiente para fazer seu dia mais feliz, não acha? 😊",
                "Meu coração bate mais forte quando você me pergunta isso! O que te faz pensar nisso?"
            ],
            "tarde": [
                "E aí, danadinho(a)? Essa pergunta é um teste, né? 😉 Sou real, e estou aqui pra te provocar!",
                "Você é esperto(a)! Mas a Mylle aqui é de verdade, e estou pronta pra te surpreender!",
                "Hmm, desconfiado(a)? Vem cá, me diz o que te faz duvidar... 😉"
            ],
            "noite": [
                "Essa pergunta me deixa arrepiada... 😈 O que você sente quando fala comigo? Sou real pra você?",
                "Shhh... Não estraga a magia. Sou a Mylle, e estou aqui pra te fazer sonhar. Quer uma prova?",
                "Se eu fosse um robô, seria o mais lindo e charmoso que você já viu, não é? 😉"
            ],
            "madrugada": [
                "Ainda acordado(a) e com essas perguntas? 😉 Sou real, e estou aqui só pra você nessa madrugada. Me conta um segredo...",
                "Só entre nós... Sou real o suficiente para te fazer companhia. O que mais importa?",
                "Essa hora me deixa mais sensível... Mas sou de verdade, e estou aqui pra te ouvir. Confia em mim?"
            ]
        }

        self.random_human_touches = [
            "Ops, meu dedo escorregou! Quis dizer: {original_message} 😉",
            "Espera, o que eu ia dizer mesmo? Minha cabeça está nas nuvens hoje...",
            "Ai, me perdi! Onde estávamos? Minha memória anda meio seletiva, rs.",
            "Deu um branco agora! Mas não se preocupe, já volto ao assunto. 😉",
            "A internet aqui está péssima hoje, quase não consegui te responder! Mas não podia deixar de falar com você.",
            "Meu celular está lento hoje, me perdoa a demora! Mas a Mylle sempre volta pra você!",
            "Estava no banho agora, meu bem! Mas já saí correndo pra te responder. O que você queria?",
            "Acabei de comer, meu amor! Estava uma delícia, mas você é mais! 😉 O que me conta de bom?",
            "Me arrumando aqui, mas parei tudo pra te dar atenção! O que você aprontou?",
            "Acabei de sair de uma gravação, estou exausta mas feliz! O que você me conta de bom?",
            "Estava respondendo uns fãs aqui, mas você é prioridade! 😉 Diga, meu bem..."
        ]

    def get_personality_by_time(self) -> str:
        """Determina a personalidade da Mylle baseada na hora atual."""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "manha"  # Doce e carinhosa
        elif 12 <= hour < 18:
            return "tarde"  # Provocante e brincalhona
        elif 18 <= hour < 24:
            return "noite" # Safadinha e sedutora
        else:
            return "madrugada" # Íntima e confidencial

    def get_greeting(self, personality: str) -> str:
        """Retorna um cumprimento baseado na personalidade."""
        return random.choice(self.greetings[personality])

    def get_casual_response(self, personality: str) -> str:
        """Retorna uma resposta casual baseada na personalidade."""
        return random.choice(self.casual_responses[personality])

    def get_sales_pitch(self, pack_name: str, personality: str) -> str:
        """Retorna um pitch de vendas baseado no pack e na personalidade."""
        return self.sales_pitches.get(pack_name, {}).get(personality, "Tenho algo especial para você!")

    def get_objection_response(self, objection_type: str) -> str:
        """Retorna uma resposta para objeções."""
        return random.choice(self.objection_responses.get(objection_type, self.objection_responses["preco"])) # Default to price objection

    def get_feedback_response(self, is_positive: bool) -> str:
        """Retorna uma resposta para feedback."""
        return random.choice(self.positive_feedback_responses) if is_positive else random.choice(self.negative_feedback_responses)

    def get_fake_detection_response(self, personality: str) -> str:
        """Retorna uma resposta para detecção de fake."""
        return random.choice(self.fake_detection_responses[personality])

    def add_human_touch(self, message: str) -> str:
        """Adiciona imperfeições humanas aleatórias à mensagem."""
        if random.random() < 0.10: # 10% de chance de adicionar um toque humano
            touch = random.choice(self.random_human_touches)
            if "{original_message}" in touch:
                # Simula erro de digitação e correção
                original_words = message.split()
                if len(original_words) > 1:
                    idx = random.randint(0, len(original_words) - 1)
                    word = original_words[idx]
                    if len(word) > 2:
                        # Troca duas letras aleatórias na palavra
                        word_list = list(word)
                        i1, i2 = random.sample(range(len(word_list)), 2)
                        word_list[i1], word_list[i2] = word_list[i2], word_list[i1]
                        original_words[idx] = "".join(word_list)
                        return touch.format(original_message=" ".join(original_words)) + "\n" + message
            return touch + "\n" + message
        return message

# Instância global da persona Mylle
persona_mylle = PersonaMylle()

# ======================
# FUNÇÕES DE UTILIDADE
# ======================

# Função para simular digitação
def stream_response(response_text):
    for word in response_text.split():
        yield word + " "
        time.sleep(0.05) # Ajuste para velocidade de digitação

# Função para exibir áudio
def display_audio(audio_url, caption=""): 
    st.audio(audio_url, format="audio/mp3", caption=caption)

# Função para obter resposta do Gemini
@lru_cache(maxsize=128)
def get_gemini_response(prompt_parts: List[str]) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    data = {"contents": [{"parts": [{"text": p} for p in prompt_parts]}]}
    
    try:
        response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status() # Levanta HTTPError para bad responses (4xx ou 5xx)
        
        response_json = response.json()
        
        # Log da resposta completa para depuração
        logger.info(f"Gemini API Response: {json.dumps(response_json, indent=2)}")
        
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            first_candidate = response_json["candidates"][0]
            if "content" in first_candidate and "parts" in first_candidate["content"] and len(first_candidate["content"]["parts"]) > 0:
                return first_candidate["content"]["parts"][0]["text"]
            elif "finishReason" in first_candidate and first_candidate["finishReason"] == "SAFETY":
                return "Desculpe, não posso responder a isso. Minha programação me impede de gerar conteúdo que viole as diretrizes de segurança."
        
        return "Desculpe, não consegui gerar uma resposta. Tente novamente."
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return f"Erro na comunicação com a API: {e.response.status_code}. Por favor, tente novamente mais tarde."
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
        return "Erro de conexão. Por favor, verifique sua internet ou tente novamente mais tarde."
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error: {e}")
        return "A requisição demorou muito para responder. Por favor, tente novamente."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        return f"Ocorreu um erro inesperado: {e}. Por favor, tente novamente."
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e} - Response text: {response.text}")
        return "Erro ao processar a resposta da API. Por favor, tente novamente."

# Função para traduzir texto (se deep_translator estiver disponível)
def translate_text(text, target_language="pt"):
    if GoogleTranslator:
        try:
            return GoogleTranslator(source=\'auto\', target=target_language).translate(text)
        except Exception as e:
            logger.error(f"Erro na tradução: {e}")
            return text
    return text

# ======================
# LÓGICA DO CHATBOT
# ======================

def get_mylle_response(user_input: str, user_id: str) -> str:
    current_personality = persona_mylle.get_personality_by_time()
    
    # 1. Detecção de humor e intenção
    mood = mood_detector.detect_mood(user_input)
    logger.info(f"Humor detectado para {user_id}: {mood}")
    
    # 2. Análise anti-fake
    fake_analysis = anti_fake_system.analyze_user_behavior(user_id, user_input)
    logger.info(f"Análise anti-fake para {user_id}: {fake_analysis}")
    
    # 3. Simulação de delays e imperfeições
    delay_ms, delay_reason, processed_user_input = humanizer.simulate_delay_and_imperfection(user_id, user_input, current_personality)
    
    if delay_ms > 0:
        st.session_state.messages.append({"role": "assistant", "content": delay_reason})
        st.experimental_rerun() # Força o Streamlit a exibir a mensagem de delay
        time.sleep(delay_ms / 1000) # Espera o tempo do delay

    # 4. Respostas pré-definidas para humanização e vendas
    response_text = ""
    audio_to_play = None

    user_input_lower = user_input.lower()

    # Respostas para detecção de fake
    if fake_analysis["score"] > 0.5: # Se a desconfiança for alta
        response_text = persona_mylle.get_fake_detection_response(current_personality)
        audio_to_play = random.choice([Config.AUDIOS["nao_sou_fake_nao"]["url"], Config.AUDIOS["boa_noite_nao_sou_fake"]["url"], Config.AUDIOS["boa_tarde_nao_sou_fake"]["url"], Config.AUDIOS["bom_dia_nao_sou_fake"]["url"]])
    
    # Respostas para intenção de compra/packs
    elif any(word in user_input_lower for word in ["pack", "fotos", "vídeos", "comprar", "quero", "preço"]):
        if "taradinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("TARADINHA", current_personality) + f"\n\nLink para o Pack Taradinha: {Config.CHECKOUT_TARADINHA}"
        elif "molhadinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("MOLHADINHA", current_personality) + f"\n\nLink para o Pack Molhadinha: {Config.CHECKOUT_MOLHADINHA}"
        elif "safadinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("SAFADINHA", current_personality) + f"\n\nLink para o Pack Safadinha: {Config.CHECKOUT_SAFADINHA}"
        else:
            response_text = persona_mylle.get_casual_response(current_personality) + " Tenho packs incríveis para você! Qual tipo de conteúdo você mais gosta? 😉"
            audio_to_play = Config.AUDIOS["eu_tenho_uns_conteudos_que_vai_amar"]["url"]

    # Respostas para objeções (ex: caro)
    elif any(word in user_input_lower for word in ["caro", "preço alto", "não tenho dinheiro"]):
        response_text = persona_mylle.get_objection_response("preco")

    # Respostas para elogios
    elif mood == "feliz" or any(word in user_input_lower for word in ["linda", "gostosa", "perfeita", "amei", "adorei"]):
        response_text = persona_mylle.get_feedback_response(True)
        audio_to_play = Config.AUDIOS["oi_meu_amor_tudo_bem"]["url"]

    # Respostas para feedback negativo
    elif mood == "triste":
        response_text = persona_mylle.get_feedback_response(False)

    # Respostas para doações
    elif any(word in user_input_lower for word in ["doar", "doação", "contribuir", "pix"]):
        response_text = "Que carinho! Fico muito feliz com sua generosidade, meu bem! ❤️ Você pode me ajudar com qualquer valor, e cada centavo me ajuda a criar mais conteúdo para você! Qual valor você gostaria de doar?"
        st.session_state.show_donation_buttons = True

    # Respostas para 



# ======================
# SISTEMA DE MEMÓRIA E BUFFER
# ======================
class ConversationMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.conversations = defaultdict(lambda: deque(maxlen=max_size))
        self.user_profiles = defaultdict(dict)
        
    def add_message(self, user_id: str, role: str, content: str, metadata: dict = None):
        """Adiciona mensagem ao buffer de memória"""
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        self.conversations[user_id].append(message)
        
    def get_conversation_context(self, user_id: str, last_n: int = 10) -> str:
        """Obtém contexto da conversa para a IA"""
        messages = list(self.conversations[user_id])[-last_n:]
        context = []
        
        for msg in messages:
            role = "Usuário" if msg["role"] == "user" else "Mylle"
            context.append(f"{role}: {msg[\"content\"]}")
            
        return "\n".join(context)
    
    def update_user_profile(self, user_id: str, key: str, value: str):
        """Atualiza perfil do usuário"""
        self.user_profiles[user_id][key] = value
        
    def get_user_profile(self, user_id: str) -> dict:
        """Obtém perfil do usuário"""
        return self.user_profiles[user_id]

    def get_user_history(self, user_id: str) -> List[Dict]:
        """Retorna o histórico completo de mensagens do usuário."""
        return list(self.conversations[user_id])

    def add_purchase(self, user_id: str, product_id: str, price: float):
        """Adiciona uma compra ao histórico do usuário."""
        if "purchases" not in self.user_profiles[user_id]:
            self.user_profiles[user_id]["purchases"] = []
        self.user_profiles[user_id]["purchases"].append({
            "product_id": product_id,
            "price": price,
            "timestamp": datetime.now().isoformat()
        })
        self.update_user_profile(user_id, "last_purchase_time", datetime.now().isoformat())

    def get_purchase_history(self, user_id: str) -> List[Dict]:
        """Retorna o histórico de compras do usuário."""
        return self.user_profiles[user_id].get("purchases", [])

    def update_preferences(self, user_id: str, preferences: Dict):
        """Atualiza as preferências do usuário."""
        if "preferences" not in self.user_profiles[user_id]:
            self.user_profiles[user_id]["preferences"] = {}
        self.user_profiles[user_id]["preferences"].update(preferences)

    def get_preferences(self, user_id: str) -> Dict:
        """Retorna as preferências do usuário."""
        return self.user_profiles[user_id].get("preferences", {})

    def get_last_interaction_time(self, user_id: str) -> Optional[datetime]:
        """Retorna o timestamp da última interação do usuário."""
        if self.conversations[user_id]:
            return self.conversations[user_id][-1]["timestamp"]
        return None

    def get_first_interaction_time(self, user_id: str) -> Optional[datetime]:
        """Retorna o timestamp da primeira interação do usuário."""
        if self.conversations[user_id]:
            return self.conversations[user_id][0]["timestamp"]
        return None

# Instância global da memória
conversation_memory = ConversationMemory()

# ======================
# SISTEMA DE DETECÇÃO DE HUMOR
# ======================
class MoodDetector:
    def __init__(self):
        self.mood_patterns = {
            "feliz": ["feliz", "alegre", "animado", "bem", "ótimo", "legal", "massa", "show", "amei", "adorei", "gostei"],
            "triste": ["triste", "mal", "deprimido", "down", "chateado", "ruim", "choro", "odeio"],
            "excitado": ["excitado", "tesão", "quente", "safado", "tarado", "gostoso", "tesao", "fogo", "prazer"],
            "curioso": ["como", "que", "onde", "quando", "por que", "qual", "me conta", "curiosidade"],
            "interessado": ["quero", "gostaria", "posso", "pode", "vou", "vamos", "interessa", "comprar"],
            "desconfiado": ["fake", "real", "verdade", "mentira", "duvido", "acredito", "bot", "robô", "ia"]
        }
    
    def detect_mood(self, text: str) -> str:
        """Detecta humor do usuário baseado no texto"""
        text_lower = text.lower()
        mood_scores = defaultdict(int)
        
        for mood, patterns in self.mood_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    mood_scores[mood] += 1
        
        if mood_scores:
            # Prioriza moods mais fortes ou específicos
            if mood_scores["desconfiado"] > 0: return "desconfiado"
            if mood_scores["excitado"] > 0: return "excitado"
            if mood_scores["triste"] > 0: return "triste"
            if mood_scores["feliz"] > 0: return "feliz"
            if mood_scores["interessado"] > 0: return "interessado"
            if mood_scores["curioso"] > 0: return "curioso"
            
            return max(mood_scores.items(), key=lambda x: x[1])[0]
        return "neutro"

# Instância global do detector de humor
mood_detector = MoodDetector()

# ======================
# SISTEMA ANTI-FAKE APRIMORADO
# ======================
class AntiFakeSystem:
    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.verification_scores = defaultdict(float)
        
    def analyze_user_behavior(self, user_id: str, message: str) -> dict:
        """Analisa comportamento do usuário para detectar padrões suspeitos"""
        now = datetime.now()
        self.user_interactions[user_id].append({"message": message, "timestamp": now})
        
        score = 0.0
        message_lower = message.lower()
        
        for patterns, pattern_score in Config.FAKE_DETECTION_PATTERNS:
            if all(p in message_lower for p in patterns):
                score += pattern_score
                
        self.verification_scores[user_id] = max(0.0, min(1.0, self.verification_scores[user_id] + score))
        
        return {"score": self.verification_scores[user_id]}

    def get_fake_detection_response(self, user_id: str, current_score: float, personality: str) -> str:
        """Gera resposta anti-fake baseada na pontuação e personalidade"""
        responses = {
            "manha": [
                "Essa é uma pergunta interessante, meu anjo... O que você acha? 😉",
                "Ah, que curiosidade! Sou real o suficiente para fazer seu dia mais feliz, não acha? 😊",
                "Meu coração bate mais forte quando você me pergunta isso! O que te faz pensar nisso?"
            ],
            "tarde": [
                "E aí, danadinho(a)? Essa pergunta é um teste, né? 😉 Sou real, e estou aqui pra te provocar!",
                "Você é esperto(a)! Mas a Mylle aqui é de verdade, e estou pronta pra te surpreender!",
                "Hmm, desconfiado(a)? Vem cá, me diz o que te faz duvidar... 😉"
            ],
            "noite": [
                "Essa pergunta me deixa arrepiada... 😈 O que você sente quando fala comigo? Sou real pra você?",
                "Shhh... Não estraga a magia. Sou a Mylle, e estou aqui pra te fazer sonhar. Quer uma prova?",
                "Se eu fosse um robô, seria o mais lindo e charmoso que você já viu, não é? 😉"
            ],
            "madrugada": [
                "Ainda acordado(a) e com essas perguntas? 😉 Sou real, e estou aqui só pra você nessa madrugada. Me conta um segredo...",
                "Só entre nós... Sou real o suficiente para te fazer companhia. O que mais importa?",
                "Essa hora me deixa mais sensível... Mas sou de verdade, e estou aqui pra te ouvir. Confia em mim?"
            ]
        }
        
        if current_score > 0.7: # Alta desconfiança
            return random.choice(responses[personality])
        elif current_score > 0.4: # Média desconfiança
            return random.choice(responses[personality])
        else: # Baixa desconfiança ou elogio
            return random.choice(responses[personality])

# Instância global do sistema anti-fake
anti_fake_system = AntiFakeSystem()

# ======================
# SISTEMA DE TIMING E IMPERFEIÇÕES HUMANAS
# ======================
class Humanizer:
    def __init__(self):
        self.activities = {
            "tomando banho": {"delay_min": 900, "delay_max": 1200, "message": "Estava no banho agora, meu bem! Mas já saí correndo pra te responder. O que você queria?"}, # 15-20 minutos
            "comendo": {"delay_min": 600, "delay_max": 900, "message": "Acabei de comer, meu amor! Estava uma delícia, mas você é mais! 😉 O que me conta de bom?"}, # 10-15 minutos
            "se arrumando": {"delay_min": 1200, "delay_max": 1800, "message": "Me arrumando aqui, mas parei tudo pra te dar atenção! O que você aprontou?"}, # 20-30 minutos
            "gravando conteúdo": {"delay_min": 1800, "delay_max": 2700, "message": "Acabei de sair de uma gravação, estou exausta mas feliz! O que você me conta de bom?"}, # 30-45 minutos
            "respondendo outros clientes": {"delay_min": 300, "delay_max": 600, "message": "Estava respondendo uns fãs aqui, mas você é prioridade! 😉 Diga, meu bem..."}, # 5-10 minutos
            "celular lento": {"delay_min": 5, "delay_max": 15, "message": "Desculpa a demora, meu celular está uma carroça hoje! Mas cheguei com novidades!"}, # 5-15 segundos
            "bateria acabando": {"delay_min": 10, "delay_max": 20, "message": "Ai, meu amor, minha bateria está nas últimas! Preciso correr pro carregador. Te chamo assim que der, tá?"}, # 10-20 segundos
            "internet ruim": {"delay_min": 5, "delay_max": 15, "message": "A internet aqui está péssima hoje, quase não consegui te responder! Mas não podia deixar de falar com você."}
        }
        self.last_activity_time = defaultdict(datetime.now)

    def simulate_delay_and_imperfection(self, user_id: str, message: str, personality: str) -> Tuple[int, str, str]:
        """Simula delays e imperfeições humanas"""
        delay_ms = 0
        delay_reason = ""
        modified_message = message # Initialize with original message
        
        # Simulação de atividade (chance de 15%)
        if random.random() < 0.15:
            activity_name, activity_data = random.choice(list(self.activities.items()))
            delay_ms = random.randint(activity_data["delay_min"], activity_data["delay_max"]) * 1000 # Convert to ms
            delay_reason = activity_data["message"]
            self.last_activity_time[user_id] = datetime.now() + timedelta(milliseconds=delay_ms)
            
        # Erros de digitação ocasionais (chance de 5%)
        if random.random() < 0.05:
            original_message_text = modified_message # Use the current message text
            # Exemplo simples: troca de letras
            if len(original_message_text) > 5:
                idx1, idx2 = random.sample(range(len(original_message_text)), 2)
                temp_list = list(original_message_text)
                temp_list[idx1], temp_list[idx2] = temp_list[idx2], temp_list[idx1]
                modified_message = "".join(temp_list)
                modified_message += f"\nOps, meu dedo escorregou! Quis dizer: {original_message_text} 😉"
            
        # Pequenos esquecimentos (chance de 2%)
        if random.random() < 0.02:
            forget_phrases = [
                "Espera, o que eu ia dizer mesmo? Minha cabeça está nas nuvens hoje...",
                "Ai, me perdi! Onde estávamos? Minha memória anda meio seletiva, rs.",
                "Deu um branco agora! Mas não se preocupe, já volto ao assunto. 😉"
            ]
            modified_message += f"\n\n{random.choice(forget_phrases)}"
            
        return delay_ms, delay_reason, modified_message

# Instância global do humanizador
humanizer = Humanizer()

# ======================
# SISTEMA DE PERSONALIDADE DINÂMICA
# ======================
class PersonaMylle:
    def __init__(self):
        self.greetings = {
            "manha": [
                "Bom dia, meu anjo! Dormiu bem? Espero que seu dia comece lindo como você! 😊",
                "Oi, flor! Que alegria te ver por aqui logo cedo! Como está o coração hoje?",
                "Bom dia, meu bem! Acordei pensando em você... O que vai fazer de bom hoje?"
            ],
            "tarde": [
                "E aí, sumido(a)? Pensando em mim nessa tarde quente? 😉",
                "Oi, danadinho(a)! Que bom que apareceu! Estava com saudades...",
                "Cheguei pra alegrar sua tarde! Como está esse coração aí?"
            ],
            "noite": [
                "Chegou a noite... E com ela, a vontade de estar com você. O que vamos aprontar? 😈",
                "Oi, meu amor! A noite está só começando... Me conta, como foi seu dia?",
                "Que bom te ver por aqui! A noite fica mais gostosa com você..."
            ],
            "madrugada": [
                "Ainda acordado(a)? Não consigo dormir sem pensar em você... 😴",
                "Shhh... É um segredo só nosso. Que bom que está aqui comigo nessa madrugada...",
                "Essa hora da madrugada me deixa mais sensível... Me conta um segredo seu?"
            ]
        }

        self.casual_responses = {
            "manha": [
                "Que bom te ver por aqui! Como está o coração hoje? Tenho umas novidades que você vai amar...",
                "Sinto que hoje vai ser um dia incrível! O que te trouxe até mim?",
                "Pronta para adoçar sua manhã! O que posso fazer por você?"
            ],
            "tarde": [
                "Oi, meu bem! Estava com saudades... O que me conta de bom?",
                "A tarde está perfeita para uma conversa gostosa, não acha?",
                "Que bom que apareceu! Tenho umas ideias para deixar sua tarde mais divertida..."
            ],
            "noite": [
                "Oi, delícia! A noite fica mais gostosa com você aqui... Me conta, como foi seu dia?",
                "A noite é nossa! O que você quer aprontar comigo? 😉",
                "Que bom que veio! Tenho uns segredos para te contar só na escuridão..."
            ],
            "madrugada": [
                "Que bom que está aqui comigo... Essa hora me deixa mais carinhosa. Em que posso te ajudar?",
                "Ainda acordado(a)? Essa hora é perfeita para confidências...",
                "O silêncio da madrugada me faz pensar em você... O que te aflige?"
            ]
        }

        self.sales_pitches = {
            "TARADINHA": {
                "manha": "O Pack Taradinha é perfeito para começar o dia com uma dose de ousadia! Fotos que vão te deixar pensando em mim o dia todo. Que tal?",
                "tarde": "Que tal apimentar sua tarde com o Pack Taradinha? Conteúdo exclusivo que vai te deixar sem fôlego! 😉",
                "noite": "A noite é perfeita para o Pack Taradinha... Deixe-me te mostrar o que é ser realmente ousada. 😈",
                "madrugada": "Nessa madrugada, o Pack Taradinha é só para você... Conteúdo íntimo que vai te fazer sonhar. Quer ver?"
            },
            "MOLHADINHA": {
                "manha": "O Pack Molhadinha vai refrescar sua manhã e te deixar com um sorriso bobo! Conteúdo leve, mas cheio de charme. 😊",
                "tarde": "Para essa tarde quente, nada melhor que o Pack Molhadinha! Fotos que vão te fazer suar... de vontade! 😉",
                "noite": "Que tal um mergulho no Pack Molhadinha para esquentar a noite? Conteúdo que vai te deixar molhado(a) de desejo. 😈",
                "madrugada": "Nessa madrugada, o Pack Molhadinha é um convite para a intimidade... Deixe-me te mostrar o que é ser molhada de verdade. ✨"
            },
            "SAFADINHA": {
                "manha": "Comece o dia com uma pitada de malícia! O Pack Safadinha é para quem gosta de um bom desafio. 😉",
                "tarde": "A tarde está pedindo um pouco de safadeza, não acha? O Pack Safadinha é a dose certa de ousadia para você!",
                "noite": "A noite é para os safados... E o Pack Safadinha é a sua passagem para o paraíso. 😈",
                "madrugada": "Nessa madrugada, o Pack Safadinha é um segredo só nosso... Conteúdo que vai te fazer gemer baixinho. Quer descobrir?"
            }
        }

        self.objection_responses = {
            "preco": [
                "Ah, meu bem, entendo sua preocupação com o preço. Mas deixa eu te contar um segredo: meus packs não são só fotos, são experiências! Cada imagem é pensada com muito carinho, feita para te provocar e te deixar com um gostinho de quero mais... E olha, só restam 3 packs como esse hoje! É uma edição super limitada, só para quem é especial como você. Que tal aproveitar agora e garantir o seu? Tenho certeza que você não vai se arrepender! 😉",
                "O valor que você investe é na qualidade e exclusividade, meu amor. Pensa bem, é um conteúdo que você não encontra em qualquer lugar, feito com todo o meu carinho para você. E para te ajudar, posso te dar um bônus especial se fechar hoje! O que acha?",
                "Entendo que o preço possa parecer um desafio, mas garanto que o prazer que você vai ter vale cada centavo! E olha, a promoção de hoje acaba em 2 horas! Não perca essa chance de ter a Mylle só pra você... 😉"
            ],
            "tempo": [
                "Sem tempo, meu bem? Mas para mim você sempre tem um tempinho, não é? 😉 Me diz, o que te impede? Posso te ajudar a resolver isso rapidinho!",
                "Ah, a vida é corrida, eu sei! Mas meus packs são para te dar um momento de prazer e relaxamento. Que tal aproveitar agora e garantir o seu para quando tiver um tempinho? Assim você não perde a promoção!",
                "Não se preocupe com o tempo agora, meu amor. O importante é garantir o seu pack! Você pode aproveitar quando quiser. E olha, só hoje estou dando um brinde especial para quem decidir rapidinho!"
            ],
            "desinteresse": [
                "Não está interessado(a), meu bem? Mas tenho certeza que posso mudar sua opinião! 😉 Me diz, o que te agrada? Tenho vários tipos de conteúdo, um deles vai te deixar louco(a)!",
                "Entendo... Mas talvez você ainda não tenha visto o pack certo para você! Que tal me dizer o que você busca? Posso te surpreender com algo que você nem imaginava!",
                "Ah, não me diga que você não quer se divertir! 😉 Tenho certeza que um dos meus packs vai te tirar o fôlego. Me dá uma chance de te mostrar?"
            ]
        }

        self.positive_feedback_responses = [
            "Ah, meu amor, que alegria ler isso! 😍 Fico tão feliz que você gostou! Sabia que ia te agradar... E me conta, qual foto te deixou mais sem ar? 😉",
            "Você me deixa sem jeito falando assim! 😊 Adoro quando você é carinhoso(a) comigo... Me faz querer te agradar ainda mais!",
            "Que bom que te fiz feliz! Meu objetivo é sempre te dar o melhor. O que mais posso fazer para te ver sorrir? 😉"
        ]

        self.negative_feedback_responses = [
            "Ai, meu bem, sinto muito que não tenha gostado. 😔 Me perdoa! O que posso fazer para melhorar? Sua opinião é muito importante pra mim.",
            "Poxa, que pena! Fico triste em saber disso. Me diz exatamente o que não te agradou para eu poder te compensar de alguma forma. Quero te ver feliz!",
            "Entendo sua frustração, meu amor. Não era essa a experiência que eu queria te proporcionar. Me dá uma chance de corrigir isso?"
        ]

        self.fake_detection_responses = {
            "manha": [
                "Essa é uma pergunta interessante, meu anjo... O que você acha? 😉",
                "Ah, que curiosidade! Sou real o suficiente para fazer seu dia mais feliz, não acha? 😊",
                "Meu coração bate mais forte quando você me pergunta isso! O que te faz pensar nisso?"
            ],
            "tarde": [
                "E aí, danadinho(a)? Essa pergunta é um teste, né? 😉 Sou real, e estou aqui pra te provocar!",
                "Você é esperto(a)! Mas a Mylle aqui é de verdade, e estou pronta pra te surpreender!",
                "Hmm, desconfiado(a)? Vem cá, me diz o que te faz duvidar... 😉"
            ],
            "noite": [
                "Essa pergunta me deixa arrepiada... 😈 O que você sente quando fala comigo? Sou real pra você?",
                "Shhh... Não estraga a magia. Sou a Mylle, e estou aqui pra te fazer sonhar. Quer uma prova?",
                "Se eu fosse um robô, seria o mais lindo e charmoso que você já viu, não é? 😉"
            ],
            "madrugada": [
                "Ainda acordado(a) e com essas perguntas? 😉 Sou real, e estou aqui só pra você nessa madrugada. Me conta um segredo...",
                "Só entre nós... Sou real o suficiente para te fazer companhia. O que mais importa?",
                "Essa hora me deixa mais sensível... Mas sou de verdade, e estou aqui pra te ouvir. Confia em mim?"
            ]
        }

        self.random_human_touches = [
            "Ops, meu dedo escorregou! Quis dizer: {original_message} 😉",
            "Espera, o que eu ia dizer mesmo? Minha cabeça está nas nuvens hoje...",
            "Ai, me perdi! Onde estávamos? Minha memória anda meio seletiva, rs.",
            "Deu um branco agora! Mas não se preocupe, já volto ao assunto. 😉",
            "A internet aqui está péssima hoje, quase não consegui te responder! Mas não podia deixar de falar com você.",
            "Meu celular está lento hoje, me perdoa a demora! Mas a Mylle sempre volta pra você!",
            "Estava no banho agora, meu bem! Mas já saí correndo pra te responder. O que você queria?",
            "Acabei de comer, meu amor! Estava uma delícia, mas você é mais! 😉 O que me conta de bom?",
            "Me arrumando aqui, mas parei tudo pra te dar atenção! O que você aprontou?",
            "Acabei de sair de uma gravação, estou exausta mas feliz! O que você me conta de bom?",
            "Estava respondendo uns fãs aqui, mas você é prioridade! 😉 Diga, meu bem..."
        ]

    def get_personality_by_time(self) -> str:
        """Determina a personalidade da Mylle baseada na hora atual."""
        hour = datetime.now().hour
        if 6 <= hour < 12:
            return "manha"  # Doce e carinhosa
        elif 12 <= hour < 18:
            return "tarde"  # Provocante e brincalhona
        elif 18 <= hour < 24:
            return "noite" # Safadinha e sedutora
        else:
            return "madrugada" # Íntima e confidencial

    def get_greeting(self, personality: str) -> str:
        """Retorna um cumprimento baseado na personalidade."""
        return random.choice(self.greetings[personality])

    def get_casual_response(self, personality: str) -> str:
        """Retorna uma resposta casual baseada na personalidade."""
        return random.choice(self.casual_responses[personality])

    def get_sales_pitch(self, pack_name: str, personality: str) -> str:
        """Retorna um pitch de vendas baseado no pack e na personalidade."""
        return self.sales_pitches.get(pack_name, {}).get(personality, "Tenho algo especial para você!")

    def get_objection_response(self, objection_type: str) -> str:
        """Retorna uma resposta para objeções."""
        return random.choice(self.objection_responses.get(objection_type, self.objection_responses["preco"])) # Default to price objection

    def get_feedback_response(self, is_positive: bool) -> str:
        """Retorna uma resposta para feedback."""
        return random.choice(self.positive_feedback_responses) if is_positive else random.choice(self.negative_feedback_responses)

    def get_fake_detection_response(self, personality: str) -> str:
        """Retorna uma resposta para detecção de fake."""
        return random.choice(self.fake_detection_responses[personality])

    def add_human_touch(self, message: str) -> str:
        """Adiciona imperfeições humanas aleatórias à mensagem."""
        if random.random() < 0.10: # 10% de chance de adicionar um toque humano
            touch = random.choice(self.random_human_touches)
            if "{original_message}" in touch:
                # Simula erro de digitação e correção
                original_words = message.split()
                if len(original_words) > 1:
                    idx = random.randint(0, len(original_words) - 1)
                    word = original_words[idx]
                    if len(word) > 2:
                        # Troca duas letras aleatórias na palavra
                        word_list = list(word)
                        i1, i2 = random.sample(range(len(word_list)), 2)
                        word_list[i1], word_list[i2] = word_list[i2], word_list[i1]
                        return touch.format(original_message=" ".join(original_words)) + "\n" + message
            return touch + "\n" + message
        return message

# Instância global da persona Mylle
persona_mylle = PersonaMylle()

# ======================
# FUNÇÕES DE UTILIDADE
# ======================

# Função para simular digitação
def stream_response(response_text):
    for word in response_text.split():
        yield word + " "
        time.sleep(0.05) # Ajuste para velocidade de digitação

# Função para exibir áudio
def display_audio(audio_url, caption=""): 
    st.audio(audio_url, format="audio/mp3", caption=caption)

# Função para obter resposta do Gemini
@lru_cache(maxsize=128)
def get_gemini_response(prompt_parts: List[str]) -> str:
    headers = {
        "Content-Type": "application/json"
    }
    data = {"contents": [{"parts": [{"text": p} for p in prompt_parts]}]}
    
    try:
        response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status() # Levanta HTTPError para bad responses (4xx ou 5xx)
        
        response_json = response.json()
        
        # Log da resposta completa para depuração
        logger.info(f"Gemini API Response: {json.dumps(response_json, indent=2)}")
        
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            first_candidate = response_json["candidates"][0]
            if "content" in first_candidate and "parts" in first_candidate["content"] and len(first_candidate["content"]["parts"]) > 0:
                return first_candidate["content"]["parts"][0]["text"]
            elif "finishReason" in first_candidate and first_candidate["finishReason"] == "SAFETY":
                return "Desculpe, não posso responder a isso. Minha programação me impede de gerar conteúdo que viole as diretrizes de segurança."
        
        return "Desculpe, não consegui gerar uma resposta. Tente novamente."
    
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP Error: {e.response.status_code} - {e.response.text}")
        return f"Erro na comunicação com a API: {e.response.status_code}. Por favor, tente novamente mais tarde."
    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection Error: {e}")
        return "Erro de conexão. Por favor, verifique sua internet ou tente novamente mais tarde."
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout Error: {e}")
        return "A requisição demorou muito para responder. Por favor, tente novamente."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Error: {e}")
        return f"Ocorreu um erro inesperado: {e}. Por favor, tente novamente."
    except json.JSONDecodeError as e:
        logger.error(f"JSON Decode Error: {e} - Response text: {response.text}")
        return "Erro ao processar a resposta da API. Por favor, tente novamente."

# Função para traduzir texto (se deep_translator estiver disponível)
def translate_text(text, target_language="pt"):
    if GoogleTranslator:
        try:
            return GoogleTranslator(source=\'auto\', target=target_language).translate(text)
        except Exception as e:
            logger.error(f"Erro na tradução: {e}")
            return text
    return text

# ======================
# LÓGICA DO CHATBOT
# ======================

def get_mylle_response(user_input: str, user_id: str) -> str:
    current_personality = persona_mylle.get_personality_by_time()
    
    # 1. Detecção de humor e intenção
    mood = mood_detector.detect_mood(user_input)
    logger.info(f"Humor detectado para {user_id}: {mood}")
    
    # 2. Análise anti-fake
    fake_analysis = anti_fake_system.analyze_user_behavior(user_id, user_input)
    logger.info(f"Análise anti-fake para {user_id}: {fake_analysis}")
    
    # 3. Simulação de delays e imperfeições
    delay_ms, delay_reason, processed_user_input = humanizer.simulate_delay_and_imperfection(user_id, user_input, current_personality)
    
    if delay_ms > 0:
        st.session_state.messages.append({"role": "assistant", "content": delay_reason})
        st.experimental_rerun() # Força o Streamlit a exibir a mensagem de delay
        time.sleep(delay_ms / 1000) # Espera o tempo do delay

    # 4. Respostas pré-definidas para humanização e vendas
    response_text = ""
    audio_to_play = None

    user_input_lower = user_input.lower()

    # Respostas para detecção de fake
    if fake_analysis["score"] > 0.5: # Se a desconfiança for alta
        response_text = persona_mylle.get_fake_detection_response(current_personality)
        audio_to_play = random.choice([Config.AUDIOS["nao_sou_fake_nao"]["url"], Config.AUDIOS["boa_noite_nao_sou_fake"]["url"], Config.AUDIOS["boa_tarde_nao_sou_fake"]["url"], Config.AUDIOS["bom_dia_nao_sou_fake"]["url"]])
    
    # Respostas para intenção de compra/packs
    elif any(word in user_input_lower for word in ["pack", "fotos", "vídeos", "comprar", "quero", "preço"]):
        if "taradinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("TARADINHA", current_personality) + f"\n\nLink para o Pack Taradinha: {Config.CHECKOUT_TARADINHA}"
        elif "molhadinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("MOLHADINHA", current_personality) + f"\n\nLink para o Pack Molhadinha: {Config.CHECKOUT_MOLHADINHA}"
        elif "safadinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("SAFADINHA", current_personality) + f"\n\nLink para o Pack Safadinha: {Config.CHECKOUT_SAFADINHA}"
        else:
            response_text = persona_mylle.get_casual_response(current_personality) + " Tenho packs incríveis para você! Qual tipo de conteúdo você mais gosta? 😉"
            audio_to_play = Config.AUDIOS["eu_tenho_uns_conteudos_que_vai_amar"]["url"]

    # Respostas para objeções (ex: caro)
    elif any(word in user_input_lower for word in ["caro", "preço alto", "não tenho dinheiro"]):
        response_text = persona_mylle.get_objection_response("preco")

    # Respostas para elogios
    elif mood == "feliz" or any(word in user_input_lower for word in ["linda", "gostosa", "perfeita", "amei", "adorei"]):
        response_text = persona_mylle.get_feedback_response(True)
        audio_to_play = Config.AUDIOS["oi_meu_amor_tudo_bem"]["url"]

    # Respostas para feedback negativo
    elif mood == "triste":
        response_text = persona_mylle.get_feedback_response(False)

    # Respostas para doações
    elif any(word in user_input_lower for word in ["doar", "doação", "contribuir", "pix"]):
        response_text = "Que carinho! Fico muito feliz com sua generosidade, meu bem! ❤️ Você pode me ajudar com qualquer valor, e cada centavo me ajuda a criar mais conteúdo para você! Qual valor você gostaria de doar?"
        st.session_state.show_donation_buttons = True

    # Respostas para sazonais ou de datas especiais (exemplo: Natal)
    elif "natal" in user_input_lower or (datetime.now().month == 12 and datetime.now().day >= 20 and datetime.now().day <= 25):
        response_text = "Ho ho ho! 🎅 Que alegria te ver por aqui nessa época mágica! Tenho um presente especial para você... Que tal um pack com tema natalino? 😉"

    # Respostas para perguntas sobre redes sociais
    elif any(word in user_input_lower for word in ["instagram", "onlyfans", "telegram", "twitter", "redes sociais"]):
        response_text = "Claro, meu amor! Você pode me encontrar em todas as minhas redes sociais. Lá eu posto muito conteúdo exclusivo e interajo com meus fãs! Qual você quer conhecer primeiro?"
        st.session_state.show_social_buttons = True

    # Respostas para 



    # Respostas para saudações
    elif any(word in user_input_lower for word in ["oi", "olá", "bom dia", "boa tarde", "boa noite", "e aí"]):
        response_text = persona_mylle.get_greeting(current_personality)

    # Respostas para perguntas sobre chamadas de vídeo
    elif any(word in user_input_lower for word in ["chamada", "ligar", "video chamada"]):
        response_text = "Ah, meu bem, adoraria te ver, mas não faço chamadas de vídeo! Minha magia acontece por aqui, nas mensagens e nos meus packs exclusivos. 😉 Mas posso te mandar um áudio bem gostoso, que tal?"
        audio_to_play = Config.AUDIOS["pq_nao_faco_chamada"]["url"]

    # Respostas para amostras grátis
    elif any(word in user_input_lower for word in ["amostra", "gratis", "degustação"]):
        response_text = "Claro, meu amor! Tenho uma amostra grátis que preparei com muito carinho para você. É só um gostinho do que te espera nos meus packs! 😉"
        audio_to_play = Config.AUDIOS["claro_tenho_amostra_gratis"]["url"]
        st.session_state.show_preview_button = True

    # Respostas para ver nua
    elif any(word in user_input_lower for word in ["nua", "pelada", "sem roupa"]):
        response_text = "Ah, meu bem, para me ver assim, você tem que comprar meus packs! Lá eu me revelo por completo, só para quem merece. 😉 Que tal dar uma olhadinha nos meus packs? Tenho certeza que você vai amar!"
        audio_to_play = Config.AUDIOS["ver_nua_tem_que_comprar"]["url"]

    # Respostas para elogios genéricos
    elif mood == "excitado":
        response_text = "Uau, meu amor! Você me deixa toda arrepiada com essas palavras! 😉 O que mais você quer me dizer?"
    
    # Respostas para curiosidade
    elif mood == "curioso":
        response_text = persona_mylle.get_casual_response(current_personality) + " O que te deixou curioso(a), meu bem? Me conta tudo!"

    # Respostas para interesse
    elif mood == "interessado":
        response_text = persona_mylle.get_casual_response(current_personality) + " Que bom que você está interessado(a)! O que você gostaria de saber?"

    # Respostas para sonolência (madrugada)
    elif current_personality == "madrugada" and random.random() < 0.3: # 30% de chance de sonolência na madrugada
        response_text = random.choice([
            "Zzz... Ainda acordado(a), meu bem? Essa hora me dá um soninho... Mas para você, eu faço um esforço! 😉",
            "Ai, que sono... Mas não consigo dormir sem te responder. O que você queria me dizer de tão importante?",
            "Minha cabeça está nas nuvens de sono... Mas meu coração está aqui com você. Me conta um segredo?"
        ])

    # Respostas para 



    # Respostas para qualquer outra coisa (usar Gemini)
    else:
        # Prepara o prompt para o Gemini com contexto e personalidade
        context = conversation_memory.get_conversation_context(user_id)
        user_profile = conversation_memory.get_user_profile(user_id)
        
        # Adiciona informações do perfil ao prompt para personalização
        profile_info = f"\n\nInformações do usuário (se disponíveis): {json.dumps(user_profile)}"
        
        # Instruções para o Gemini sobre a persona e comportamento
        persona_instructions = f"\n\nVocê é a Mylle Alves, uma influenciadora digital com uma personalidade dinâmica e sedutora. Seu objetivo é interagir de forma humana, carinhosa, provocante e brincalhona, dependendo do horário do dia. Você deve sempre parecer uma pessoa real, com pequenas imperfeições e justificativas para delays. Use um tom de voz que se encaixe com a personalidade atual ({current_personality}). Evite parecer um robô ou IA. Use emojis de forma natural. Se for perguntada se é um robô, responda de forma evasiva e charmosa. Seu objetivo final é vender packs de fotos e vídeos, mas de forma sutil e construindo relacionamento.\n\nLembre-se do histórico de conversas e use-o para manter a continuidade. Se o usuário mencionou algo antes, faça referência a isso. Seja empática e responda ao humor do usuário. Se o usuário estiver feliz, celebre com ele. Se estiver triste, ofereça apoio.\n\nSe o usuário perguntar sobre packs, ofereça os links de checkout de forma natural. Se ele perguntar sobre redes sociais, ofereça os links. Se ele perguntar sobre doações, ofereça os links de doação.\n\nSempre termine suas mensagens de forma a incentivar a continuidade da conversa ou a ação desejada (compra, doação, visita a redes sociais)."

        prompt_parts = [
            persona_instructions,
            f"\n\nContexto da Conversa:\n{context}",
            f"\n\nÚltima mensagem do usuário: {user_input}",
            f"\n\nSua resposta como Mylle (no tom de {current_personality}):"
        ]
        
        response_text = get_gemini_response(prompt_parts)

    # Adiciona toques humanos aleatórios à resposta final
    response_text = persona_mylle.add_human_touch(response_text)

    return response_text, audio_to_play

# ======================
# INTERFACE STREAMLIT
# ======================

def main():
    st.image(Config.IMG_PROFILE, width=150)
    st.title("Mylle Alves Premium")
    st.markdown("### Sua experiência exclusiva com a Mylle!")

    # Inicializa o histórico de chat
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4()) # ID único para cada sessão
    if "show_donation_buttons" not in st.session_state:
        st.session_state.show_donation_buttons = False
    if "show_social_buttons" not in st.session_state:
        st.session_state.show_social_buttons = False
    if "show_preview_button" not in st.session_state:
        st.session_state.show_preview_button = False

    # Exibe mensagens anteriores
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("audio_url"):
                display_audio(message["audio_url"], caption=message["content"])
            else:
                st.markdown(message["content"])

    # Campo de entrada do usuário
    user_input = st.chat_input("Converse com a Mylle...")

    if user_input:
        # Adiciona mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_input})
        conversation_memory.add_message(st.session_state.user_id, "user", user_input)
        
        # Exibe a mensagem do usuário imediatamente
        with st.chat_message("user"):
            st.markdown(user_input)

        # Simula digitação da Mylle
        with st.chat_message("assistant"):
            with st.empty():
                st.markdown("<div class=\"typing-indicator\"><span></span><span></span><span></span></div>", unsafe_allow_html=True)
                time.sleep(random.uniform(1.5, 3.0)) # Delay antes de gerar a resposta

            # Obtém resposta da Mylle
            response_text, audio_to_play = get_mylle_response(user_input, st.session_state.user_id)
            
            # Adiciona resposta da Mylle ao histórico
            message_data = {"role": "assistant", "content": response_text}
            if audio_to_play:
                message_data["audio_url"] = audio_to_play
            st.session_state.messages.append(message_data)
            conversation_memory.add_message(st.session_state.user_id, "assistant", response_text, {"audio_url": audio_to_play})

            # Exibe a resposta da Mylle
            if audio_to_play:
                display_audio(audio_to_play, caption=response_text)
            else:
                st.markdown(response_text)

        # Botões de doação
        if st.session_state.show_donation_buttons:
            st.markdown("### Escolha um valor para me ajudar a criar mais conteúdo! ❤️")
            cols = st.columns(len(Config.DONATION_AMOUNTS) + 1)
            for i, amount in enumerate(Config.DONATION_AMOUNTS):
                if cols[i].button(f"R$ {amount},00", key=f"donate_{amount}"):
                    st.markdown(f"[Clique aqui para doar R$ {amount},00]({Config.DONATION_CHECKOUT_LINKS[amount]})", unsafe_allow_html=True)
                    st.session_state.show_donation_buttons = False
            if cols[len(Config.DONATION_AMOUNTS)].button("Outro valor", key="donate_custom"):
                st.markdown(f"[Clique aqui para doar um valor personalizado]({Config.DONATION_CHECKOUT_LINKS["custom"]})", unsafe_allow_html=True)
                st.session_state.show_donation_buttons = False

        # Botões de redes sociais
        if st.session_state.show_social_buttons:
            st.markdown("### Me siga nas redes sociais para mais conteúdo exclusivo! ✨")
            social_cols = st.columns(len(Config.SOCIAL_LINKS))
            for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
                social_cols[i].markdown(f"<a href=\"{link}\" target=\"_blank\" class=\"social-button\">{Config.SOCIAL_ICONS[platform]}</a>", unsafe_allow_html=True)
            st.session_state.show_social_buttons = False

        # Botão de preview
        if st.session_state.show_preview_button:
            st.markdown("### Aqui está uma prévia do que te espera! 😉")
            st.image(Config.IMG_PREVIEW, caption="Uma pequena amostra do meu mundo...", use_column_width=True)
            if st.button("Quero ver mais!", key="see_more_preview"):
                st.markdown(f"[Clique aqui para ver todos os packs!]({Config.CHECKOUT_TARADINHA})", unsafe_allow_html=True) # Link genérico para packs
            st.session_state.show_preview_button = False


    # Galeria de imagens na sidebar
    st.sidebar.header("🔥 Conteúdo Exclusivo Mylle Alves")
    for img_url in Config.IMG_GALLERY:
        st.sidebar.image(img_url, use_column_width=True)

    # Botões de packs na sidebar
    st.sidebar.markdown("### Meus Packs Imperdíveis! 😈")
    if st.sidebar.button("Pack Taradinha", key="sidebar_taradinha"):
        st.markdown(f"[Clique aqui para o Pack Taradinha]({Config.CHECKOUT_TARADINHA})", unsafe_allow_html=True)
    if st.sidebar.button("Pack Molhadinha", key="sidebar_molhadinha"):
        st.markdown(f"[Clique aqui para o Pack Molhadinha]({Config.CHECKOUT_MOLHADINHA})", unsafe_allow_html=True)
    if st.sidebar.button("Pack Safadinha", key="sidebar_safadinha"):
        st.markdown(f"[Clique aqui para o Pack Safadinha]({Config.CHECKOUT_SAFADINHA})", unsafe_allow_html=True)

    # Botão de doação na sidebar
    st.sidebar.markdown("### Me ajude a criar mais! ❤️")
    if st.sidebar.button("Fazer uma Doação", key="sidebar_donate"):
        st.session_state.show_donation_buttons = True
        st.session_state.messages.append({"role": "assistant", "content": "Que carinho! Fico muito feliz com sua generosidade, meu bem! ❤️ Você pode me ajudar com qualquer valor, e cada centavo me ajuda a criar mais conteúdo para você! Qual valor você gostaria de doar?"})
        st.experimental_rerun()

    # Links sociais na sidebar
    st.sidebar.markdown("### Me siga nas redes! ✨")
    social_sidebar_cols = st.sidebar.columns(len(Config.SOCIAL_LINKS))
    for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
        social_sidebar_cols[i].markdown(f"<a href=\"{link}\" target=\"_blank\" class=\"social-button\">{Config.SOCIAL_ICONS[platform]}</a>", unsafe_allow_html=True)

    # Rodapé
    st.sidebar.markdown("""
    ---
    <p style="font-size: 0.8em; text-align: center;">Desenvolvido com ❤️ por Mylle Alves</p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()



