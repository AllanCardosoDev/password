import string
import secrets
from itertools import groupby

import streamlit as st

# =========================================================
# Configuração da Página
# =========================================================

st.set_page_config(
    page_title="Gerador de Senhas Fortes",
    page_icon="🔒",
    layout="centered"
)

# =========================================================
# Funções auxiliares
# =========================================================

def has_sequential_chars(password: str, min_seq_len: int = 3) -> bool:
    """Verifica se há sequências previsíveis como 'abc', '123', 'qwerty'."""
    if len(password) < min_seq_len:
        return False

    # Sequência alfabética simples
    for i in range(len(password) - min_seq_len + 1):
        chunk = password[i:i + min_seq_len]
        if all(ord(chunk[j + 1]) - ord(chunk[j]) == 1 for j in range(len(chunk) - 1)):
            return True

    # Sequências numéricas comuns
    digits = "0123456789"
    for i in range(len(password) - min_seq_len + 1):
        chunk = password[i:i + min_seq_len]
        if chunk in digits:
            return True

    # Sequências de teclado comuns
    common_seqs = ["qwerty", "asdfgh", "zxcvbn"]
    lower = password.lower()
    return any(seq in lower for seq in common_seqs)


def has_repeated_patterns(password: str, min_repeat_len: int = 2) -> bool:
    """Detecta padrões repetidos, como 'aaaa', 'ababab', '1111'."""
    if not password:
        return False

    # Repetição do mesmo caractere
    for _, group in groupby(password):
        if len(list(group)) >= min_repeat_len + 1:
            return True

    # Padrões pequenos repetidos (ex: 'abab', '1212')
    for size in range(1, min_repeat_len + 1):
        pattern = password[:size]
        if pattern and pattern * (len(password) // size) == password:
            return True

    return False


# =========================================================
# Geração de senha tradicional
# =========================================================

def generate_password(
    length: int,
    include_uppercase: bool,
    include_lowercase: bool,
    include_digits: bool,
    include_symbols: bool,
    exclude_ambiguous: bool,
) -> str:
    """Gera uma senha aleatória forte, usando secrets (cryptographically secure)."""

    # Conjuntos locais (não alterar o módulo string)
    upper = string.ascii_uppercase
    lower = string.ascii_lowercase
    digits = string.digits
    symbols = string.punctuation

    ambiguous_chars = "lIO0"

    if exclude_ambiguous:
        upper = "".join(c for c in upper if c not in ambiguous_chars)
        lower = "".join(c for c in lower if c not in ambiguous_chars)
        digits = "".join(c for c in digits if c not in ambiguous_chars)
        # Se quiser, poderia filtrar símbolos também

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
        st.warning("Selecione pelo menos um tipo de caractere para gerar a senha.")
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

    if len(password_chars) > length:
        st.warning(
            "O comprimento definido é muito curto para as opções selecionadas. "
            "Aumente o tamanho da senha."
        )
        return ""

    # Preenche o restante com caracteres aleatórios do conjunto total
    for _ in range(length - len(password_chars)):
        password_chars.append(secrets.choice(all_characters))

    # Embaralha a senha para não ficar previsível (ex.: sempre começando em maiúscula)
    secrets.SystemRandom().shuffle(password_chars)

    return "".join(password_chars)


# =========================================================
# Geração de frase-senha (passphrase)
# =========================================================

LOCAL_WORD_LIST = [
    "gato", "cachorro", "lua", "sol", "montanha", "rio", "floresta", "cafe",
    "chave", "livro", "neve", "vento", "fogo", "terra", "noite", "dia",
    "amigo", "sombra", "rocha", "oceano", "nuvem", "estrela", "ponte",
    "viagem", "trilho", "mapa", "porto", "metro", "trilha"
]


def generate_passphrase(
    num_words: int = 4,
    separator: str = "-",
    capitalize_first: bool = True,
) -> str:
    """Gera uma frase-senha usando uma lista local de palavras."""
    words = [secrets.choice(LOCAL_WORD_LIST) for _ in range(num_words)]
    passphrase = separator.join(words)
    if capitalize_first:
        passphrase = passphrase.capitalize()
    return passphrase


# -----------------------------------------------------------------
# Exemplo de uso de API externa (somente para referência futura):
#
# import requests
#
# def get_random_word_from_api() -> str:
#     api_key = st.secrets["API_NINJAS_KEY"]
#     response = requests.get(
#         "https://api.api-ninjas.com/v1/randomword",
#         headers={"X-Api-Key": api_key},
#         timeout=5,
#     )
#     response.raise_for_status()
#     return response.json()["word"]
#
# def generate_passphrase_api(
#     num_words: int = 4,
#     separator: str = "-",
#     capitalize_first: bool = True,
# ) -> str:
#     words = [get_random_word_from_api() for _ in range(num_words)]
#     passphrase = separator.join(words)
#     if capitalize_first:
#         passphrase = passphrase.capitalize()
#     return passphrase
# -----------------------------------------------------------------


# =========================================================
# Avaliação da força da senha
# =========================================================

def assess_password_strength(password: str):
    """
    Avalia a força da senha.

    Retorna:
        level (str): 'Fraca', 'Média', 'Forte', 'Muito Forte'
        feedback (str): mensagem descritiva
        score (int): pontuação de 0 a 10
    """
    score = 0
    feedback = []

    length = len(password)

    # Comprimento
    if length < 8:
        feedback.append("Senha muito curta. Use pelo menos 8 caracteres.")
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
        feedback.append(
            "Aumente a variedade: combine letras maiúsculas, minúsculas, números e símbolos."
        )
    elif char_types == 2:
        score += 1
        feedback.append("Boa variedade de tipos de caracteres.")
    elif char_types == 3:
        score += 2
        feedback.append("Ótima variedade de tipos de caracteres!")
    else:
        score += 3
        feedback.append("Excelente variedade de tipos de caracteres!")

    # Penalidades: sequências e repetições
    if has_sequential_chars(password):
        feedback.append("Evite sequências previsíveis como 'abc', '123' ou 'qwerty'.")
        score -= 2

    if has_repeated_patterns(password):
        feedback.append("Evite padrões ou caracteres repetidos em excesso.")
        score -= 1

    # Limita a pontuação entre 0 e 10
    score = max(0, min(score, 10))

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
# Interface Streamlit
# =========================================================

st.title("Gerador de Senhas Fortes 🔒")
st.markdown(
    "Gere senhas e frases‑senha seguras, personalizadas e avaliadas em tempo real."
)

st.sidebar.header("Configurações")

modo = st.sidebar.radio(
    "Tipo de geração",
    options=["Senha tradicional", "Frase-senha (passphrase)"],
)

if modo == "Senha tradicional":
    length = st.sidebar.slider("Comprimento da senha", 8, 64, 16)

    st.sidebar.subheader("Tipos de caracteres")
    include_uppercase = st.sidebar.checkbox("Letras maiúsculas (A-Z)", value=True)
    include_lowercase = st.sidebar.checkbox("Letras minúsculas (a-z)", value=True)
    include_digits = st.sidebar.checkbox("Números (0-9)", value=True)
    include_symbols = st.sidebar.checkbox("Símbolos (!@#$% etc.)", value=True)

    st.sidebar.subheader("Opções avançadas")
    exclude_ambiguous = st.sidebar.checkbox(
        "Excluir caracteres ambíguos (l, I, O, 0)",
        value=False,
    )

else:
    num_words = st.sidebar.slider("Quantidade de palavras", 3, 10, 4)
    separator = st.sidebar.text_input("Separador entre palavras", value="-")
    capitalize_first = st.sidebar.checkbox(
        "Capitalizar primeira letra da frase",
        value=True,
    )

# Botão de geração
if st.sidebar.button("Gerar", key="generate_btn"):
    if modo == "Senha tradicional":
        generated = generate_password(
            length=length,
            include_uppercase=include_uppercase,
            include_lowercase=include_lowercase,
            include_digits=include_digits,
            include_symbols=include_symbols,
            exclude_ambiguous=exclude_ambiguous,
        )
    else:
        generated = generate_passphrase(
            num_words=num_words,
            separator=separator,
            capitalize_first=capitalize_first,
        )

    if generated:
        st.session_state.current_password = generated
        history = st.session_state.get("password_history", [])
        history.insert(0, generated)
        st.session_state.password_history = history[:5]

# Resultado
st.subheader("Resultado gerado")

if st.session_state.get("current_password"):
    current = st.session_state.current_password
    st.code(current, language="text")

    if modo == "Senha tradicional":
        level, feedback, score = assess_password_strength(current)
        st.markdown(f"**Força da senha:** {level}")
        st.progress(score / 10)
        st.info(feedback)
    else:
        st.info(
            "Frases‑senha com várias palavras aleatórias costumam ser muito fortes, "
            "especialmente quando longas e com separadores pouco óbvios."
        )

    # Botão de copiar (JS simples)
    st.markdown(
        """
        <button onclick="navigator.clipboard.writeText(
                document.querySelector('code').innerText
            )"
            style="
                background-color: #FFC107;
                color: #1a1a1a;
                padding: 8px 18px;
                border-radius: 4px;
                border: none;
                cursor: pointer;
                font-weight: 600;
                margin-top: 8px;
            ">
            Copiar
        </button>
        """,
        unsafe_allow_html=True,
    )
    st.caption("Clique em “Copiar” para enviar a senha/frase-senha para a área de transferência.")

else:
    st.info("Configure as opções na barra lateral e clique em **Gerar**.")

# Histórico
st.subheader("Histórico recente")

history = st.session_state.get("password_history", [])
if history:
    for i, pwd in enumerate(history, start=1):
        st.text_input(
            f"Entrada {i}",
            value=pwd,
            type="password",
            disabled=True,
            key=f"hist_pwd_{i}",
        )
else:
    st.caption("Nenhuma senha ou frase‑senha gerada ainda.")

# Dicas
st.markdown("---")
st.subheader("Boas práticas de segurança")
st.markdown(
    """
- **Comprimento:** Prefira senhas com pelo menos 12–16 caracteres, ou frases‑senha com 4–6 palavras.
- **Variedade:** Misture letras maiúsculas, minúsculas, números e símbolos em senhas tradicionais.
- **Senhas únicas:** Nunca reutilize a mesma senha em serviços diferentes.
- **Informações pessoais:** Evite nomes, datas de aniversário e termos óbvios.
- **Gerenciador de senhas:** Use um gerenciador confiável para armazenar e organizar suas credenciais.
"""
)
