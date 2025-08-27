# Mylle Alves Premium - Agente de IA Humanizado

Bem-vindo ao repositório do Mylle Alves Premium, um agente de IA desenvolvido para interagir de forma ultra-humanizada, vendendo packs de fotos e vídeos no WhatsApp. Este projeto utiliza Streamlit para a interface de chat e o modelo Gemini para as interações da IA, incorporando uma persona dinâmica, sistema de memória avançado, simulação de imperfeições humanas e um funil de vendas psicológico.

## 🚀 Funcionalidades Principais

- **Personalidade Dinâmica:** A Mylle adapta seu tom e comportamento de acordo com o horário do dia (Manhã, Tarde, Noite, Madrugada).
- **Sistema de Memória Avançado:** Lembra de interações passadas, preferências do usuário e histórico de compras para uma conversa mais contextualizada.
- **Imperfeições Humanas Simuladas:** Inclui pequenos delays, erros de digitação ocasionais e justificativas para pausas, tornando a interação mais realista.
- **Funil de Vendas Psicológico:** Utiliza gatilhos de escassez, urgência e prova social para otimizar as vendas de packs.
- **Sistema Anti-Detecção:** Respostas evasivas e convincentes para perguntas sobre a natureza da IA, mantendo a ilusão de uma pessoa real.
- **Integração com Áudios:** Reprodução de áudios pré-gravados para humanizar ainda mais a comunicação.

## 🛠️ Configuração do Ambiente Local

Siga os passos abaixo para configurar e executar o aplicativo Mylle Alves Premium em seu ambiente local.

### 1. Pré-requisitos

Certifique-se de ter o Python 3.8 ou superior instalado em sua máquina.

### 2. Clonar o Repositório

Primeiro, clone este repositório para o seu ambiente local:

```bash
git clone <URL_DO_SEU_REPOSITORIO>
cd mylle-alves-premium
```

### 3. Criar e Ativar um Ambiente Virtual

É altamente recomendável usar um ambiente virtual para gerenciar as dependências do projeto. Isso evita conflitos com outras instalações Python.

```bash
python -m venv venv
```

**No Windows:**

```bash
.\venv\Scripts\activate
```

**No macOS/Linux:**

```bash
source venv/bin/activate
```

### 4. Instalar as Dependências

Com o ambiente virtual ativado, instale as bibliotecas necessárias usando o `requirements.txt` fornecido:

```bash
pip install -r requirements.txt
```

### 5. Configurar a Chave da API do Gemini

O aplicativo utiliza a API do Google Gemini para gerar as respostas da IA. Você precisará obter uma chave de API e configurá-la.

1. Acesse o [Google AI Studio](https://aistudio.google.com/)
2. Crie um novo projeto ou selecione um existente.
3. Vá para a seção "Get API key" e crie uma nova chave.
4. No diretório raiz do seu projeto (`mylle-alves-premium`), crie um arquivo chamado `.streamlit/secrets.toml`.
5. Adicione sua chave de API a este arquivo no seguinte formato:

```toml
API_KEY = "sua_chave_api_gemini_aqui"
```

Substitua `"sua_chave_api_gemini_aqui"` pela chave que você obteve no Google AI Studio.

### 6. Executar o Aplicativo Streamlit

Com todas as dependências instaladas e a chave da API configurada, você pode iniciar o aplicativo Streamlit:

```bash
streamlit run mylle_alves_app_humanized.py
```

Isso abrirá o aplicativo em seu navegador padrão. Se não abrir automaticamente, copie e cole o URL fornecido no terminal (geralmente `http://localhost:8501`).

## ☁️ Deploy no Streamlit Cloud

Para disponibilizar seu agente Mylle Alves Premium online, você pode implantá-lo gratuitamente no Streamlit Cloud. Siga estes passos:

### 1. Crie um Repositório no GitHub

Certifique-se de que todo o seu código (incluindo `mylle_alves_app_humanized.py`, `requirements.txt` e a pasta `.streamlit` com `secrets.toml`) esteja em um repositório público no GitHub.

**Importante:** O arquivo `secrets.toml` deve estar dentro de uma pasta `.streamlit` na raiz do seu repositório. O Streamlit Cloud detectará automaticamente este arquivo para carregar suas variáveis de ambiente.

### 2. Conecte-se ao Streamlit Cloud

1. Acesse [share.streamlit.io](https://share.streamlit.io/) e faça login com sua conta GitHub.
2. Clique em "New app" no canto superior direito.

### 3. Configure as Opções de Deploy

- **Repository:** Selecione o repositório GitHub onde você fez o upload do seu projeto (`mylle-alves-premium`).
- **Branch:** Escolha a branch principal (geralmente `main` ou `master`).
- **Main file path:** Defina o caminho para o seu arquivo principal do Streamlit, que é `mylle_alves_app_humanized.py`.

### 4. Configure os Segredos (Secrets)

No Streamlit Cloud, você precisa configurar suas chaves de API como segredos. Clique em "Advanced settings" e adicione o conteúdo do seu `secrets.toml` na caixa de texto "Secrets".

```
API_KEY = "sua_chave_api_gemini_aqui"
```

### 5. Deploy do Aplicativo

Clique em "Deploy!" e o Streamlit Cloud fará o resto. Ele instalará as dependências e implantará seu aplicativo. O processo pode levar alguns minutos. Uma vez concluído, você receberá um URL público para acessar seu agente Mylle Alves Premium.

## ⚙️ Personalização e Ajustes

Você pode personalizar diversos aspectos da Mylle Alves Premium:

- **Textos e Respostas:** Edite as strings nas classes `PersonaMylle` para ajustar os cumprimentos, respostas casuais, pitches de vendas e respostas a objeções.
- **Áudios:** Atualize os URLs dos áudios na classe `Config` para usar seus próprios arquivos de áudio.
- **Links de Checkout:** Altere os links de checkout para seus próprios produtos e doações na classe `Config`.
- **Imagens:** Substitua os URLs das imagens de perfil, prévias e galeria na classe `Config`.
- **Redes Sociais:** Atualize os links e ícones das redes sociais na classe `Config`.
- **Lógica de Vendas:** Modifique a função `get_mylle_response` para ajustar a lógica de detecção de intenção e as respostas de vendas.
- **Imperfeições Humanas:** Ajuste as probabilidades e os tipos de delays e erros na classe `Humanizer`.

## ⚠️ Considerações Importantes

- **Segurança da API Key:** Nunca exponha sua chave de API diretamente no código ou em repositórios públicos. Use sempre o mecanismo de segredos do Streamlit ou variáveis de ambiente.
- **Uso Responsável:** Este projeto visa demonstrar a humanização de IAs. Certifique-se de usar a Mylle Alves Premium de forma ética e responsável, respeitando a privacidade e o consentimento dos usuários.
- **Manutenção:** Monitore o desempenho da IA e as interações dos usuários. Ajuste as respostas e a lógica conforme necessário para manter a experiência otimizada e humana.

--- 

Desenvolvido com ❤️ por Manus AI


