import streamlit as st
import string
import secrets
import re
from itertools import groupby

# =========================================================
# Funções de apoio para avaliação de senha
# =========================================================

def has_sequential_chars(password, min_seq_len=3):
    """Verifica se há sequências crescentes tipo 'abc', '123', 'qwe'."""
    if len(password) < min_seq_len:
        return False

    # Sequência alfabética simples
    for i in range(len(password) - min_seq_len + 1):
        chunk = password[i:i + min_seq_len]
        # Ex: 'abc' -> ord(b)-ord(a) == 1 e ord(c)-ord(b) == 1
        if all(ord(chunk[j+1]) - ord(chunk[j]) == 1 for j in range(len(chunk) - 1)):
            return True

    # Sequências numéricas simples
    digits = "0123456789"
    for i in range(len(password) - min_seq_len + 1):
        chunk = password[i:i + min_seq_len]
        if chunk in digits:
            return True

    # Sequências comuns de teclado (poderia expandir)
    common_seqs = ["qwerty", "asdfgh", "zxcvbn"]
    lower = password.lower()
    for seq in common_seqs:
        if seq in lower:
            return True

    return False


def has_repeated_patterns(password, min_repeat_len=2, min_repeats=2):
    """Detecta padrões repetidos, tipo 'aaaa', 'ababab', '1111'."""
    # Repetição de um único caractere, ex: 'aaaa'
    for char, group in groupby(password):
        if len(list(group)) >= min_repeat_len + 1:
            return True

    # Padrões pequenos repetidos, ex: 'abab', '1212'
    for size in range(1, min_repeat_len + 1):
        pattern = password[:size]
        if pattern * (len(password) // size) == password:
            return True

    return False

# =========================================================
# Funções de geração de senha / frase-senha
# =========================================================

def generate_password(length, include_uppercase, include_lowercase,
                      include_digits, include_symbols, exclude_ambiguous):
    """Gera uma senha forte com base nos critérios fornecidos, usando secrets."""

    # Conjuntos base locais (não alterar o módulo string)
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation

    ambiguous_chars = "lIO0"

    # Exclui caracteres ambíguos, se configurado
    if exclude_ambiguous:
        upper = "".join(c for c in upper if c not in ambiguous_chars)
        lower = "".join(c for c in lower if c not in ambiguous_chars)
        digits = "".join(c for c in digits if c not in ambiguous_chars)
        # poderíamos filtrar symbols aqui também se desejado

    # Monta conjunto total
    all_characters = ""
    if include_uppercase:
        all_characters += upper
    if include_lowercase:
        all_characters += lower
    if include_digits:
        all_characters += digits
    if include_symbols:
        all_characters += symbols

    if not all_characters:
        st.warning("Por favor, selecione pelo menos um tipo de caractere para incluir na senha.")
        return ""

    # Garante pelo menos um de cada tipo selecionado
    password_chars = []

    if include_uppercase and upper:
        password_chars.append(secrets.choice(upper))
    if include_lowercase and lower:
        password_chars.append(secrets.choice(lower))
    if include_digits and digits:
        password_chars.append(secrets.choice(digits))
    if include_symbols and symbols:
        password_chars.append(secrets.choice(symbols))

    # Se o número mínimo ultrapassar o tamanho total, ajusta
    if len(password_chars) > length:
        st.warning("O comprimento é muito curto para as opções selecionadas. Aumente o tamanho da senha.")
        return ""

    # Preenche o restante
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_characters))

    # Embaralha
    secrets.SystemRandom().shuffle(password_chars)
    return "".join(password_chars)


# Pequeno conjunto local de palavras para frases-senha
LOCAL_WORD_LIST = [
    "gato", "cachorro", "lua", "sol", "montanha", "rio", "floresta", "cafe",
    "chave", "livro", "neve", "vento", "fogo", "terra", "noite", "dia",
    "amigo", "sombra", "rocha", "oceano", "nuvem", "estrela", "ponte",
    "viagem", "trilho", "mapa", "porto", "metro", "trilha"
]

def generate_passphrase(num_words=4, separator="-", capitalize_first=True):
    """
    Gera uma frase-senha (passphrase) usando uma lista local de palavras.
    """
    words = [secrets.choice(LOCAL_WORD_LIST) for _ in range(num_words)]
    passphrase = separator.join(words)
    if capitalize_first:
        passphrase = passphrase.capitalize()
    return passphrase


# Exemplo para usar API externa (Api Ninjas) — OPCIONAL:
# Você poderia habilitar isso e armazenar a chave em st.secrets["API_NINJAS_KEY"]
"""
import requests

def get_random_word_from_api():
    api_key = st.secrets["API_NINJAS_KEY"]
    r = requests.get(
        "https://api.api-ninjas.com/v1/randomword",
        headers={"X-Api-Key": api_key},
        timeout=5
    )
    r.raise_for_status()
    return r.json()["word"]

def generate_passphrase_api(num_words=4, separator="-", capitalize_first=True):
    words = [get_random_word_from_api() for _ in range(num_words)]
    passphrase = separator.join(words)
    if capitalize_first:
        passphrase = passphrase.capitalize()
    return passphrase
"""


# =========================================================
# Avaliação de força da senha
# =========================================================

def assess_password_strength(password):
    """Avalia a força da senha e retorna nível, mensagem e score numérico (0-10)."""
    score = 0
    feedback = []

    length = len(password)

    # Comprimento
    if length < 8:
        feedback.append("A senha é muito curta. Tente pelo menos 8 caracteres.")
    elif 8 <= length < 12:
        score += 2
        feedback.append("Comprimento razoável.")
    elif 12 <= length < 16:
        score += 4
        feedback.append("Bom comprimento.")
    else:
        score += 5
        feedback.append("Excelente comprimento!")

    # Variedade de caracteres
    char_types = 0
    if any(c.isupper() for c in password):
        char_types += 1
    if any(c.islower() for c in password):
        char_types += 1
    if any(c.isdigit() for c in password):
        char_types += 1
    if any(c in string.punctuation for c in password):
        char_types += 1

    if char_types < 2:
        feedback.append("Use uma combinação maior de tipos de caracteres (maiúsculas, minúsculas, números, símbolos).")
    elif char_types == 2:
        score += 1
        feedback.append("Boa variedade de caracteres.")
    elif char_types == 3:
        score += 2
        feedback.append("Ótima variedade de caracteres!")
    elif char_types == 4:
        score += 3
        feedback.append("Excelente variedade de caracteres!")

    # Penalidades: sequências e repetições
    if has_sequential_chars(password):
        feedback.append("Evite sequências previsíveis como 'abc', '123' ou 'qwerty'.")
        score -= 2

    if has_repeated_patterns(password):
        feedback.append("Evite padrões ou caracteres repetidos em excesso.")
        score -= 1

    # Clampeia o score entre 0 e 10
    score = max(0, min(score, 10))

    # Avaliação final por faixa de score
    if score <= 3:
        level = "Fraca"
        prefix = "🔴 "
    elif score <= 6:
        level = "Média"
        prefix = "🟠 "
    elif score <= 8:
        level = "Forte"
        prefix = "🟢 "
    else:
        level = "Muito Forte"
        prefix = "✅ "

    return level, prefix + ", ".join(feedback), score


# =========================================================
# Configuração da Página Streamlit
# =========================================================

st.set_page_config(page_title="Gerador de Senhas Fortes", page_icon="🔒")

st.title("Gerador de Senhas Fortes 🔒")
st.markdown("Crie senhas seguras e únicas para todas as suas contas.")

# ---------------------------------------------------------
# Barra lateral – Escolha de modo e opções
# ---------------------------------------------------------
st.sidebar.header("Opções de Geração")

modo = st.sidebar.radio(
    "Tipo de geração",
    ["Senha tradicional", "Frase-senha (passphrase)"]
)

if modo == "Senha tradicional":
    password_length = st.sidebar.slider("Comprimento da Senha", min_value=8, max_value=64, value=16)

    st.sidebar.subheader("Incluir Caracteres:")
    include_uppercase = st.sidebar.checkbox("Letras Maiúsculas (A-Z)", value=True)
    include_lowercase = st.sidebar.checkbox("Letras Minúsculas (a-z)", value=True)
    include_digits = st.sidebar.checkbox("Números (0-9)", value=True)
    include_symbols = st.sidebar.checkbox("Símbolos (!@#$%)", value=True)

    st.sidebar.subheader("Opções Avançadas:")
    exclude_ambiguous = st.sidebar.checkbox("Excluir Caracteres Ambíguos (l, I, O, 0)", value=False)

else:
    # Configurações para frase-senha
    num_words = st.sidebar.slider("Quantidade de palavras", min_value=3, max_value=10, value=4)
    separator = st.sidebar.text_input("Separador entre palavras", value="-")
    capitalize_first = st.sidebar.checkbox("Capitalizar primeira letra", value=True)
    # Poderia adicionar opção para usar API externa aqui

# ---------------------------------------------------------
# Botão Gerar
# ---------------------------------------------------------
if st.sidebar.button("Gerar", key="generate_btn"):
    if modo == "Senha tradicional":
        generated_pass = generate_password(
            password_length,
            include_uppercase,
            include_lowercase,
            include_digits,
            include_symbols,
            exclude_ambiguous
        )
    else:
        generated_pass = generate_passphrase(
            num_words=num_words,
            separator=separator,
            capitalize_first=capitalize_first
        )
        # Ou, se quiser usar API:
        # generated_pass = generate_passphrase_api(
        #     num_words=num_words,
        #     separator=separator,
        #     capitalize_first=capitalize_first
        # )

    if generated_pass:
        st.session_state.current_password = generated_pass
        # Histórico
        if "password_history" not in st.session_state:
            st.session_state.password_history = []
        st.session_state.password_history.insert(0, generated_pass)
        st.session_state.password_history = st.session_state.password_history[:5]

# ---------------------------------------------------------
# Exibição da senha / frase-senha
# ---------------------------------------------------------
st.subheader("Resultado gerado:")

if "current_password" in st.session_state and st.session_state.current_password:
    st.code(st.session_state.current_password, language="text")

    # Avalia força apenas se for senha "tradicional"
    if modo == "Senha tradicional":
        strength_level, strength_feedback, score = assess_password_strength(
            st.session_state.current_password
        )
        st.markdown(f"**Força da Senha:** {strength_level}")

        # Barra de força (0-10 -> 0-100%)
        st.progress(score / 10)

        st.info(strength_feedback)
    else:
        st.info(
            "Frases-senha longas com palavras aleatórias tendem a ser bem fortes, "
            "principalmente se você usar várias palavras e um separador não óbvio."
        )

    # Botão de copiar via HTML/JS
    st.markdown(
        """
        <button onclick="navigator.clipboard.writeText(document.querySelector('code').innerText)"
                style="background-color: #FFC107; color: #1a1a1a; padding: 10px 20px;
                       border-radius: 5px; border: none; cursor: pointer; font-weight: bold;">
            Copiar
        </button>
        """,
        unsafe_allow_html=True
    )
    st.caption("Clique em 'Copiar' para enviar para a área de transferência.")

else:
    st.info("Escolha as opções na barra lateral e clique em 'Gerar'.")

# ---------------------------------------------------------
# Histórico de senhas / frases-senha
# ---------------------------------------------------------
st.subheader("Histórico recente")
if "password_history" in st.session_state and st.session_state.password_history:
    for i, pwd in enumerate(st.session_state.password_history):
        st.text_input(f"Entrada {i+1}", value=pwd, type="password", disabled=True, key=f"hist_pwd_{i}")
else:
    st.caption("Nenhuma senha ou frase-senha gerada ainda.")

# ---------------------------------------------------------
# Dicas de segurança
# ---------------------------------------------------------
st.markdown("---")
st.subheader("Dicas para senhas fortes:")
st.markdown(
    """
- **Comprimento:** Quanto mais longa, melhor. Tente pelo menos 12–16 caracteres, ou 4–6 palavras em uma frase‑senha.
- **Variedade:** Use mistura de maiúsculas, minúsculas, números e símbolos em senhas tradicionais.
- **Exclusividade:** Nunca reutilize senhas em diferentes contas.
- **Evite informações pessoais:** Não use nomes, datas de aniversário ou palavras muito óbvias.
- **Gerenciadores de senha:** Considere usar um gerenciador confiável para armazenar tudo com segurança.
"""
)
