import streamlit as st
import random
import string

# --- Funções de Geração de Senha ---

def generate_password(length, include_uppercase, include_lowercase, include_digits, include_symbols, exclude_ambiguous):
    """Gera uma senha forte com base nos critérios fornecidos."""

    all_characters = ""

    if include_uppercase:
        all_characters += string.ascii_uppercase
    if include_lowercase:
        all_characters += string.ascii_lowercase
    if include_digits:
        all_characters += string.digits
    if include_symbols:
        all_characters += string.punctuation

    if not all_characters:
        st.warning("Por favor, selecione pelo menos um tipo de caractere para incluir na senha.")
        return ""

    # Excluir caracteres ambíguos se a opção estiver marcada
    if exclude_ambiguous:
        ambiguous_chars = "lIO0"  # L minúsculo, i maiúsculo, O maiúsculo, 0 número
        all_characters = "".join(c for c in all_characters if c not in ambiguous_chars)

        # Ajustar os conjuntos de caracteres para garantir que não tentemos escolher de um conjunto vazio
        if include_uppercase:
            string.ascii_uppercase = "".join(c for c in string.ascii_uppercase if c not in ambiguous_chars)
        if include_lowercase:
            string.ascii_lowercase = "".join(c for c in string.ascii_lowercase if c not in ambiguous_chars)
        if include_digits:
            string.digits = "".join(c for c in string.digits if c not in ambiguous_chars)
        # Símbolos raramente são ambíguos dessa forma, mas poderíamos adicionar se necessário

    if not all_characters: # Se após a exclusão não sobrar nada
        st.warning("Nenhum caractere disponível para gerar a senha com as opções selecionadas.")
        return ""

    password_chars = []

    # Garante que pelo menos um caractere de cada tipo selecionado esteja presente
    # Verifica se o conjunto de caracteres para cada tipo não está vazio após a exclusão de ambíguos
    if include_uppercase and string.ascii_uppercase:
        password_chars.append(random.choice(string.ascii_uppercase))
    if include_lowercase and string.ascii_lowercase:
        password_chars.append(random.choice(string.ascii_lowercase))
    if include_digits and string.digits:
        password_chars.append(random.choice(string.digits))
    if include_symbols and string.punctuation:
        password_chars.append(random.choice(string.punctuation))

    # Preenche o restante da senha
    for _ in range(length - len(password_chars)):
        password_chars.append(random.choice(all_characters))

    random.shuffle(password_chars)
    return "".join(password_chars)

def assess_password_strength(password, length, include_uppercase, include_lowercase, include_digits, include_symbols):
    """Avalia a força da senha e retorna um nível e uma mensagem."""
    score = 0
    feedback = []

    # Comprimento
    if length < 8:
        feedback.append("A senha é muito curta. Tente pelo menos 8 caracteres.")
    elif length >= 8 and length < 12:
        score += 1
        feedback.append("Comprimento razoável.")
    elif length >= 12 and length < 16:
        score += 2
        feedback.append("Bom comprimento.")
    else:
        score += 3
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

    # Avaliação final
    if score <= 2:
        return "Fraca", "🔴 " + ", ".join(feedback)
    elif score <= 4:
        return "Média", "🟠 " + ", ".join(feedback)
    elif score <= 6:
        return "Forte", "🟢 " + ", ".join(feedback)
    else:
        return "Muito Forte", "✅ " + ", ".join(feedback)

# --- Configuração da Página Streamlit ---

st.set_page_config(page_title="Gerador de Senhas Fortes", page_icon="🔒")

st.title("Gerador de Senhas Fortes 🔒")
st.markdown("Crie senhas seguras e únicas para todas as suas contas.")

# --- Barra Lateral para Opções ---
st.sidebar.header("Opções de Geração")

password_length = st.sidebar.slider("Comprimento da Senha", min_value=8, max_value=32, value=16)

st.sidebar.subheader("Incluir Caracteres:")
include_uppercase = st.sidebar.checkbox("Letras Maiúsculas (A-Z)", value=True)
include_lowercase = st.sidebar.checkbox("Letras Minúsculas (a-z)", value=True)
include_digits = st.sidebar.checkbox("Números (0-9)", value=True)
include_symbols = st.sidebar.checkbox("Símbolos (!@#$%)", value=True)

st.sidebar.subheader("Opções Avançadas:")
exclude_ambiguous = st.sidebar.checkbox("Excluir Caracteres Ambíguos (l, I, O, 0)", value=False)

# --- Botão Gerar Senha ---
if st.sidebar.button("Gerar Senha", key="generate_btn"):
    generated_pass = generate_password(
        password_length,
        include_uppercase,
        include_lowercase,
        include_digits,
        include_symbols,
        exclude_ambiguous
    )

    if generated_pass:
        st.session_state.current_password = generated_pass
        # Adiciona ao histórico
        if 'password_history' not in st.session_state:
            st.session_state.password_history = []
        st.session_state.password_history.insert(0, generated_pass) # Adiciona no início
        st.session_state.password_history = st.session_state.password_history[:5] # Mantém os últimos 5

# --- Exibição da Senha Gerada ---
st.subheader("Sua Senha Gerada:")

if 'current_password' in st.session_state and st.session_state.current_password:
    st.code(st.session_state.current_password, language="text")

    # Indicador de Força da Senha
    strength_level, strength_feedback = assess_password_strength(
        st.session_state.current_password,
        password_length,
        include_uppercase,
        include_lowercase,
        include_digits,
        include_symbols
    )
    st.markdown(f"**Força da Senha:** {strength_level}")
    st.info(strength_feedback)

    # Botão de Copiar (workaround)
    st.markdown(
        """
        <button onclick="navigator.clipboard.writeText(document.querySelector('code').innerText)" 
                style="background-color: #FFC107; color: #1a1a1a; padding: 10px 20px; border-radius: 5px; border: none; cursor: pointer; font-weight: bold;">
            Copiar Senha
        </button>
        """,
        unsafe_allow_html=True
    )
    st.caption("Clique no botão acima para copiar a senha para a área de transferência.")

else:
    st.info("Configure suas opções na barra lateral e clique em 'Gerar Senha'.")

# --- Histórico de Senhas ---
st.subheader("Histórico de Senhas Recentes")
if 'password_history' in st.session_state and st.session_state.password_history:
    for i, pwd in enumerate(st.session_state.password_history):
        st.text_input(f"Senha {i+1}", value=pwd, type="password", disabled=True, key=f"hist_pwd_{i}")
else:
    st.caption("Nenhuma senha gerada ainda.")

# --- Dicas de Segurança ---
st.markdown("---")
st.subheader("Dicas para Senhas Fortes:")
st.markdown("""
- **Comprimento:** Quanto mais longa, melhor. Tente pelo menos 12-16 caracteres.
- **Variedade:** Use uma mistura de letras maiúsculas e minúsculas, números e símbolos.
- **Exclusividade:** Nunca reutilize senhas em diferentes contas.
- **Evite Informações Pessoais:** Não use nomes, datas de aniversário ou palavras comuns.
- **Gerenciadores de Senha:** Considere usar um gerenciador de senhas para armazenar suas senhas de forma segura.
""")
