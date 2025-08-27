# ======================
# IMPORTAÇÕES
# ======================
import streamlit as st
import requests
import json
import time
import random
import re
import uuid
import logging
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque

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
        logging.FileHandler('app.log'),
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
    ... /* (MESMO CSS, pode manter ou reduzir para breviedade) */
</style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# ======================
# CONSTANTES E CONFIGURAÇÕES
# ======================
class Config:
    API_KEY = st.secrets.get("API_KEY", "sua_chave_api_gemini_aqui")
    API_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"
    
    DONATION_CHECKOUT_LINKS = {
        30: "https://seu.link.de.checkout/30reais",
        50: "https://seu.link.de.checkout/50reais", 
        100: "https://seu.link.de.checkout/100reais",
        150: "https://seu.link.de.checkout/150reais",
        "custom": "https://seu.link.de.checkout/personalizado"
    }
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
    AUDIOS = {
        "claro_tenho_amostra_gratis": {"url": "...", "usage_count": 0, "last_used": None},
        "imagina_ela_bem_rosinha": {"url": "...", "usage_count": 0, "last_used": None},
        "o_que_achou_amostras": {"url": "...", "usage_count": 0, "last_used": None},
        "oi_meu_amor_tudo_bem": {"url": "...", "usage_count": 0, "last_used": None},
        "pq_nao_faco_chamada": {"url": "...", "usage_count": 0, "last_used": None},
        "ver_nua_tem_que_comprar": {"url": "...", "usage_count": 0, "last_used": None},
        "eu_tenho_uns_conteudos_que_vai_amar": {"url": "...", "usage_count": 0, "last_used": None},
        "nao_sou_fake_nao": {"url": "...", "usage_count": 0, "last_used": None},
        "vida_to_esperando_voce_me_responder_gatinho": {"url": "...", "usage_count": 0, "last_used": None},
        "boa_noite_nao_sou_fake": {"url": "...", "usage_count": 0, "last_used": None},
        "boa_tarde_nao_sou_fake": {"url": "...", "usage_count": 0, "last_used": None},
        "bom_dia_nao_sou_fake": {"url": "...", "usage_count": 0, "last_used": None}
    }
    DONATION_AMOUNTS = [30, 50, 100, 150]
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
# SISTEMA DE MEMÓRIA E BUFFER (CORRIGIDO, SEM DUPLICIDADE)
# ======================
class ConversationMemory:
    def __init__(self, max_size: int = 50):
        self.max_size = max_size
        self.conversations = defaultdict(lambda: deque(maxlen=max_size))
        self.user_profiles = defaultdict(dict)
        
    def add_message(self, user_id: str, role: str, content: str, metadata: dict = None):
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now(),
            "metadata": metadata or {}
        }
        self.conversations[user_id].append(message)
        
    def get_conversation_context(self, user_id: str, last_n: int = 10) -> str:
        messages = list(self.conversations[user_id])[-last_n:]
        context = []
        for msg in messages:
            role = "Usuário" if msg["role"] == "user" else "Mylle"
            context.append(f"{role}: {msg['content']}")
        return "\n".join(context)
    
    def update_user_profile(self, user_id: str, key: str, value: str):
        self.user_profiles[user_id][key] = value
        
    def get_user_profile(self, user_id: str) -> dict:
        return self.user_profiles[user_id]

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
        text_lower = text.lower()
        mood_scores = defaultdict(int)
        for mood, patterns in self.mood_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    mood_scores[mood] += 1
        if mood_scores:
            if mood_scores["desconfiado"] > 0: return "desconfiado"
            if mood_scores["excitado"] > 0: return "excitado"
            if mood_scores["triste"] > 0: return "triste"
            if mood_scores["feliz"] > 0: return "feliz"
            if mood_scores["interessado"] > 0: return "interessado"
            if mood_scores["curioso"] > 0: return "curioso"
            return max(mood_scores.items(), key=lambda x: x[1])[0]
        return "neutro"

mood_detector = MoodDetector()

# ======================
# SISTEMA ANTI-FAKE APRIMORADO
# ======================
class AntiFakeSystem:
    def __init__(self):
        self.user_interactions = defaultdict(list)
        self.verification_scores = defaultdict(float)
        
    def analyze_user_behavior(self, user_id: str, message: str) -> dict:
        now = datetime.now()
        self.user_interactions[user_id].append({"message": message, "timestamp": now})
        score = 0.0
        message_lower = message.lower()
        for patterns, pattern_score in Config.FAKE_DETECTION_PATTERNS:
            if all(p in message_lower for p in patterns):
                score += pattern_score
        self.verification_scores[user_id] = max(0.0, min(1.0, self.verification_scores[user_id] + score))
        return {"score": self.verification_scores[user_id]}

anti_fake_system = AntiFakeSystem()

# ======================
# SISTEMA DE TIMING E IMPERFEIÇÕES HUMANAS
# ======================
class Humanizer:
    def __init__(self):
        self.activities = {
            "tomando banho": {"delay_min": 900, "delay_max": 1200, "message": "Estava no banho agora, meu bem! Mas já saí correndo pra te responder. O que você queria?"},
            "comendo": {"delay_min": 600, "delay_max": 900, "message": "Acabei de comer, meu amor! Estava uma delícia, mas você é mais! 😉 O que me conta de bom?"},
            "se arrumando": {"delay_min": 1200, "delay_max": 1800, "message": "Me arrumando aqui, mas parei tudo pra te dar atenção! O que você aprontou?"},
            "gravando conteúdo": {"delay_min": 1800, "delay_max": 2700, "message": "Acabei de sair de uma gravação, estou exausta mas feliz! O que você me conta de bom?"},
            "respondendo outros clientes": {"delay_min": 300, "delay_max": 600, "message": "Estava respondendo uns fãs aqui, mas você é prioridade! 😉 Diga, meu bem..."},
            "celular lento": {"delay_min": 5, "delay_max": 15, "message": "Desculpa a demora, meu celular está uma carroça hoje! Mas cheguei com novidades!"},
            "bateria acabando": {"delay_min": 10, "delay_max": 20, "message": "Ai, meu amor, minha bateria está nas últimas! Preciso correr pro carregador. Te chamo assim que der, tá?"},
            "internet ruim": {"delay_min": 5, "delay_max": 15, "message": "A internet aqui está péssima hoje, quase não consegui te responder! Mas não podia deixar de falar com você."}
        }
    def simulate_delay_and_imperfection(self, user_id: str, message: str, personality: str) -> Tuple[int, str, str]:
        delay_ms = 0
        delay_reason = ""
        modified_message = message
        if random.random() < 0.15:
            activity_name, activity_data = random.choice(list(self.activities.items()))
            delay_ms = random.randint(activity_data["delay_min"], activity_data["delay_max"]) * 1000
            delay_reason = activity_data["message"]
        if random.random() < 0.05 and len(modified_message) > 5:
            idx1, idx2 = random.sample(range(len(modified_message)), 2)
            temp_list = list(modified_message)
            temp_list[idx1], temp_list[idx2] = temp_list[idx2], temp_list[idx1]
            modified_message = "".join(temp_list)
            modified_message += f"\nOps, meu dedo escorregou! Quis dizer: {message} 😉"
        if random.random() < 0.02:
            forget_phrases = [
                "Espera, o que eu ia dizer mesmo? Minha cabeça está nas nuvens hoje...",
                "Ai, me perdi! Onde estávamos? Minha memória anda meio seletiva, rs.",
                "Deu um branco agora! Mas não se preocupe, já volto ao assunto. 😉"
            ]
            modified_message += f"\n\n{random.choice(forget_phrases)}"
        return delay_ms, delay_reason, modified_message

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
        self.casual_responses = self.greetings  # Simplificação para exemplo
        self.sales_pitches = {
            "TARADINHA": {
                "manha": "O Pack Taradinha é perfeito para começar o dia com uma dose de ousadia!",
                "tarde": "Que tal apimentar sua tarde com o Pack Taradinha?",
                "noite": "A noite é perfeita para o Pack Taradinha...",
                "madrugada": "Nessa madrugada, o Pack Taradinha é só para você..."
            },
            "MOLHADINHA": {
                "manha": "O Pack Molhadinha vai refrescar sua manhã!",
                "tarde": "Para essa tarde quente, nada melhor que o Pack Molhadinha!",
                "noite": "Que tal um mergulho no Pack Molhadinha para esquentar a noite?",
                "madrugada": "Nessa madrugada, o Pack Molhadinha é um convite para a intimidade..."
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
                "Ah, meu bem, entendo sua preocupação com o preço. Mas cada imagem é com carinho e exclusividade para você!",
                "O valor é na qualidade e exclusividade, meu amor. Conteúdo feito só para você.",
                "A promoção de hoje acaba em 2 horas! Não perca essa chance de ter um conteúdo exclusivo."
            ]
        }
        self.positive_feedback_responses = [
            "Ah, meu amor, que alegria ler isso! 😍",
            "Você me deixa sem jeito falando assim! 😊",
            "Que bom que te fiz feliz! 😉"
        ]
        self.negative_feedback_responses = [
            "Ai, meu bem, sinto muito que não tenha gostado. 😔",
            "Poxa, que pena! Fico triste em saber disso.",
            "Entendo sua frustração, meu amor. Me dá uma chance de corrigir isso?"
        ]
        self.fake_detection_responses = self.greetings  # Simplificação para exemplo
        self.random_human_touches = [
            "Ops, meu dedo escorregou! Quis dizer: {original_message} 😉"
        ]

    def get_personality_by_time(self) -> str:
        hour = datetime.now().hour
        if 6 <= hour < 12: return "manha"
        elif 12 <= hour < 18: return "tarde"
        elif 18 <= hour < 24: return "noite"
        else: return "madrugada"
    def get_greeting(self, personality: str) -> str:
        return random.choice(self.greetings[personality])
    def get_casual_response(self, personality: str) -> str:
        return random.choice(self.casual_responses[personality])
    def get_sales_pitch(self, pack_name: str, personality: str) -> str:
        return self.sales_pitches.get(pack_name, {}).get(personality, "Tenho algo especial para você!")
    def get_objection_response(self, objection_type: str) -> str:
        return random.choice(self.objection_responses.get(objection_type, self.objection_responses["preco"]))
    def get_feedback_response(self, is_positive: bool) -> str:
        return random.choice(self.positive_feedback_responses) if is_positive else random.choice(self.negative_feedback_responses)
    def get_fake_detection_response(self, personality: str) -> str:
        return random.choice(self.fake_detection_responses[personality])
    def add_human_touch(self, message: str) -> str:
        if random.random() < 0.10:
            touch = random.choice(self.random_human_touches)
            if "{original_message}" in touch:
                original_words = message.split()
                if len(original_words) > 1:
                    idx = random.randint(0, len(original_words) - 1)
                    word = original_words[idx]
                    if len(word) > 2:
                        word_list = list(word)
                        i1, i2 = random.sample(range(len(word_list)), 2)
                        word_list[i1], word_list[i2] = word_list[i2], word_list[i1]
                        return touch.format(original_message=" ".join(original_words)) + "\n" + message
            return touch + "\n" + message
        return message

persona_mylle = PersonaMylle()

# ======================
# FUNÇÕES DE UTILIDADE
# ======================

def display_audio(audio_url, caption=""): 
    st.audio(audio_url, format="audio/mp3", caption=caption)

@lru_cache(maxsize=128)
def get_gemini_response(prompt_parts: List[str]) -> str:
    headers = {"Content-Type": "application/json"}
    data = {"contents": [{"parts": [{"text": p} for p in prompt_parts]}]}
    try:
        response = requests.post(Config.API_URL, headers=headers, json=data, timeout=Config.REQUEST_TIMEOUT)
        response.raise_for_status()
        response_json = response.json()
        logger.info(f"Gemini API Response: {json.dumps(response_json, indent=2)}")
        if "candidates" in response_json and len(response_json["candidates"]) > 0:
            first_candidate = response_json["candidates"][0]
            if "content" in first_candidate and "parts" in first_candidate["content"] and len(first_candidate["content"]["parts"]) > 0:
                return first_candidate["content"]["parts"][0]["text"]
        return "Desculpe, não consegui gerar uma resposta. Tente novamente."
    except Exception as e:
        logger.error(f"Error contacting Gemini API: {e}")
        return "Erro ao processar a resposta da API. Por favor, tente novamente."

def translate_text(text, target_language="pt"):
    if GoogleTranslator:
        try:
            return GoogleTranslator(source='auto', target=target_language).translate(text)
        except Exception as e:
            logger.error(f"Erro na tradução: {e}")
            return text
    return text

# ======================
# LÓGICA DO CHATBOT
# ======================

def get_mylle_response(user_input: str, user_id: str) -> Tuple[str, Optional[str]]:
    current_personality = persona_mylle.get_personality_by_time()
    mood = mood_detector.detect_mood(user_input)
    fake_analysis = anti_fake_system.analyze_user_behavior(user_id, user_input)
    delay_ms, delay_reason, processed_user_input = humanizer.simulate_delay_and_imperfection(user_id, user_input, current_personality)
    if delay_ms > 0:
        st.session_state.messages.append({"role": "assistant", "content": delay_reason})
        st.experimental_rerun()
        time.sleep(delay_ms / 1000)
    response_text = ""
    audio_to_play = None
    user_input_lower = user_input.lower()
    if fake_analysis["score"] > 0.5:
        response_text = persona_mylle.get_fake_detection_response(current_personality)
        audio_to_play = None
    elif any(word in user_input_lower for word in ["pack", "fotos", "vídeos", "comprar", "quero", "preço"]):
        if "taradinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("TARADINHA", current_personality) + f"\n\nLink para o Pack Taradinha: {Config.CHECKOUT_TARADINHA}"
        elif "molhadinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("MOLHADINHA", current_personality) + f"\n\nLink para o Pack Molhadinha: {Config.CHECKOUT_MOLHADINHA}"
        elif "safadinha" in user_input_lower:
            response_text = persona_mylle.get_sales_pitch("SAFADINHA", current_personality) + f"\n\nLink para o Pack Safadinha: {Config.CHECKOUT_SAFADINHA}"
        else:
            response_text = persona_mylle.get_casual_response(current_personality) + " Tenho packs incríveis para você! Qual tipo de conteúdo você mais gosta? 😉"
    elif any(word in user_input_lower for word in ["caro", "preço alto", "não tenho dinheiro"]):
        response_text = persona_mylle.get_objection_response("preco")
    elif mood == "feliz" or any(word in user_input_lower for word in ["linda", "gostosa", "perfeita", "amei", "adorei"]):
        response_text = persona_mylle.get_feedback_response(True)
    elif mood == "triste":
        response_text = persona_mylle.get_feedback_response(False)
    elif any(word in user_input_lower for word in ["doar", "doação", "contribuir", "pix"]):
        response_text = "Que carinho! Fico muito feliz com sua generosidade, meu bem! ❤️ Você pode me ajudar com qualquer valor, e cada centavo me ajuda a criar mais conteúdo para você!"
        st.session_state.show_donation_buttons = True
    elif any(word in user_input_lower for word in ["instagram", "onlyfans", "telegram", "twitter", "redes sociais"]):
        response_text = "Claro, meu amor! Você pode me encontrar em todas as minhas redes sociais. Lá eu posto muito conteúdo exclusivo e interajo com meus fãs! Qual você quer conhecer primeiro?"
        st.session_state.show_social_buttons = True
    elif any(word in user_input_lower for word in ["oi", "olá", "bom dia", "boa tarde", "boa noite", "e aí"]):
        response_text = persona_mylle.get_greeting(current_personality)
    elif any(word in user_input_lower for word in ["chamada", "ligar", "video chamada"]):
        response_text = "Ah, meu bem, adoraria te ver, mas não faço chamadas de vídeo! Minha magia acontece por aqui, nas mensagens e nos meus packs exclusivos. 😉"
    elif any(word in user_input_lower for word in ["amostra", "gratis", "degustação"]):
        response_text = "Claro, meu amor! Tenho uma amostra grátis que preparei com muito carinho para você. É só um gostinho do que te espera nos meus packs! 😉"
        st.session_state.show_preview_button = True
    elif any(word in user_input_lower for word in ["nua", "pelada", "sem roupa"]):
        response_text = "Ah, meu bem, para me ver assim, você tem que comprar meus packs! Lá eu me revelo por completo, só para quem merece. 😉"
    elif mood == "excitado":
        response_text = "Uau, meu amor! Você me deixa toda arrepiada com essas palavras! 😉"
    elif mood == "curioso":
        response_text = persona_mylle.get_casual_response(current_personality) + " O que te deixou curioso(a), meu bem? Me conta tudo!"
    elif mood == "interessado":
        response_text = persona_mylle.get_casual_response(current_personality) + " Que bom que você está interessado(a)! O que você gostaria de saber?"
    else:
        context = conversation_memory.get_conversation_context(user_id)
        user_profile = conversation_memory.get_user_profile(user_id)
        persona_instructions = f"Você é a Mylle Alves, uma influenciadora digital com uma personalidade dinâmica e sedutora."
        prompt_parts = [
            persona_instructions,
            f"\n\nContexto da Conversa:\n{context}",
            f"\n\nÚltima mensagem do usuário: {user_input}",
            f"\n\nSua resposta como Mylle (no tom de {current_personality}):"
        ]
        response_text = get_gemini_response(prompt_parts)
    response_text = persona_mylle.add_human_touch(response_text)
    return response_text, audio_to_play

# ======================
# INTERFACE STREAMLIT
# ======================

def main():
    st.image(Config.IMG_PROFILE, width=150)
    st.title("Mylle Alves Premium")
    st.markdown("### Sua experiência exclusiva com a Mylle!")
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())
    if "show_donation_buttons" not in st.session_state:
        st.session_state.show_donation_buttons = False
    if "show_social_buttons" not in st.session_state:
        st.session_state.show_social_buttons = False
    if "show_preview_button" not in st.session_state:
        st.session_state.show_preview_button = False
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if message["role"] == "assistant" and message.get("audio_url"):
                display_audio(message["audio_url"], caption=message["content"])
            else:
                st.markdown(message["content"])
    user_input = st.chat_input("Converse com a Mylle...")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        conversation_memory.add_message(st.session_state.user_id, "user", user_input)
        with st.chat_message("user"):
            st.markdown(user_input)
        with st.chat_message("assistant"):
            with st.empty():
                st.markdown("<div class=\"typing-indicator\"><span></span><span></span><span></span></div>", unsafe_allow_html=True)
                time.sleep(random.uniform(1.5, 3.0))
            response_text, audio_to_play = get_mylle_response(user_input, st.session_state.user_id)
            message_data = {"role": "assistant", "content": response_text}
            if audio_to_play:
                message_data["audio_url"] = audio_to_play
            st.session_state.messages.append(message_data)
            conversation_memory.add_message(st.session_state.user_id, "assistant", response_text, {"audio_url": audio_to_play})
            if audio_to_play:
                display_audio(audio_to_play, caption=response_text)
            else:
                st.markdown(response_text)
        if st.session_state.show_donation_buttons:
            st.markdown("### Escolha um valor para me ajudar a criar mais conteúdo! ❤️")
            cols = st.columns(len(Config.DONATION_AMOUNTS) + 1)
            for i, amount in enumerate(Config.DONATION_AMOUNTS):
                if cols[i].button(f"R$ {amount},00", key=f"donate_{amount}"):
                    st.markdown(f"[Clique aqui para doar R$ {amount},00]({Config.DONATION_CHECKOUT_LINKS[amount]})", unsafe_allow_html=True)
                    st.session_state.show_donation_buttons = False
            if cols[len(Config.DONATION_AMOUNTS)].button("Outro valor", key="donate_custom"):
                st.markdown(f"[Clique aqui para doar um valor personalizado]({Config.DONATION_CHECKOUT_LINKS['custom']})", unsafe_allow_html=True)
                st.session_state.show_donation_buttons = False
        if st.session_state.show_social_buttons:
            st.markdown("### Me siga nas redes sociais para mais conteúdo exclusivo! ✨")
            social_cols = st.columns(len(Config.SOCIAL_LINKS))
            for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
                social_cols[i].markdown(f"<a href=\"{link}\" target=\"_blank\" class=\"social-button\">{Config.SOCIAL_ICONS[platform]}</a>", unsafe_allow_html=True)
            st.session_state.show_social_buttons = False
        if st.session_state.show_preview_button:
            st.markdown("### Aqui está uma prévia do que te espera! 😉")
            st.image(Config.IMG_PREVIEW, caption="Uma pequena amostra do meu mundo...", use_column_width=True)
            if st.button("Quero ver mais!", key="see_more_preview"):
                st.markdown(f"[Clique aqui para ver todos os packs!]({Config.CHECKOUT_TARADINHA})", unsafe_allow_html=True)
            st.session_state.show_preview_button = False
    st.sidebar.header("🔥 Conteúdo Exclusivo Mylle Alves")
    for img_url in Config.IMG_GALLERY:
        st.sidebar.image(img_url, use_column_width=True)
    st.sidebar.markdown("### Meus Packs Imperdíveis! 😈")
    if st.sidebar.button("Pack Taradinha", key="sidebar_taradinha"):
        st.markdown(f"[Clique aqui para o Pack Taradinha]({Config.CHECKOUT_TARADINHA})", unsafe_allow_html=True)
    if st.sidebar.button("Pack Molhadinha", key="sidebar_molhadinha"):
        st.markdown(f"[Clique aqui para o Pack Molhadinha]({Config.CHECKOUT_MOLHADINHA})", unsafe_allow_html=True)
    if st.sidebar.button("Pack Safadinha", key="sidebar_safadinha"):
        st.markdown(f"[Clique aqui para o Pack Safadinha]({Config.CHECKOUT_SAFADINHA})", unsafe_allow_html=True)
    st.sidebar.markdown("### Me ajude a criar mais! ❤️")
    if st.sidebar.button("Fazer uma Doação", key="sidebar_donate"):
        st.session_state.show_donation_buttons = True
        st.session_state.messages.append({"role": "assistant", "content": "Que carinho! Fico muito feliz com sua generosidade, meu bem! ❤️"})
        st.experimental_rerun()
    st.sidebar.markdown("### Me siga nas redes! ✨")
    social_sidebar_cols = st.sidebar.columns(len(Config.SOCIAL_LINKS))
    for i, (platform, link) in enumerate(Config.SOCIAL_LINKS.items()):
        social_sidebar_cols[i].markdown(f"<a href=\"{link}\" target=\"_blank\" class=\"social-button\">{Config.SOCIAL_ICONS[platform]}</a>", unsafe_allow_html=True)
    st.sidebar.markdown("""
    ---
    <p style="font-size: 0.8em; text-align: center;">Desenvolvido com ❤️ por Mylle Alves</p>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
