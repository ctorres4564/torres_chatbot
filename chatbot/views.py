# chatbot/views.py
from django.shortcuts import render, redirect # Adicione redirect
from django.urls import reverse # Adicione reverse se quiser usá-lo explicitamente
from django.conf import settings
import requests
import json
from .forms import ChatForm

# Sua chatbot_view existente ...
def chatbot_view(request):
    form = ChatForm()
    # resposta_ai = None # Removido, pois está no histórico
    historico_conversa = request.session.get('historico_conversa', [])

    if request.method == 'POST':
        form = ChatForm(request.POST)
        if form.is_valid():
            prompt_usuario = form.cleaned_data['prompt']
            
            # Adiciona a pergunta do usuário ao histórico ANTES de enviar para a API
            historico_para_api = list(historico_conversa) # Cria uma cópia para não modificar o original diretamente aqui
            historico_para_api.append({"role": "user", "content": prompt_usuario})

            api_url = "https://api.deepseek.com/chat/completions"
            api_key = settings.DEEPSEEK_API_KEY

            if not api_key:
                # Se a API key não estiver configurada, não faz a chamada e informa o usuário/admin
                resposta_ai_conteudo = "Erro de configuração: A chave da API DeepSeek não foi definida."
                # Adiciona a pergunta do usuário ao histórico da sessão
                historico_conversa.append({"role": "user", "content": prompt_usuario})
                 # Adiciona a mensagem de erro como resposta do assistente ao histórico da sessão
                historico_conversa.append({"role": "assistant", "content": resposta_ai_conteudo})
                request.session['historico_conversa'] = historico_conversa
                form = ChatForm() # Limpa o formulário
                return render(request, 'chatbot/chat.html', {
                    'form': form,
                    'historico_conversa': historico_conversa,
                })

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }

            payload = {
                "model": "deepseek-chat",
                "messages": historico_para_api, # Envia o histórico atualizado com a nova pergunta
                "max_tokens": 1500, # Aumentei um pouco, ajuste conforme necessário
                "temperature": 0.7,
            }

            resposta_ai_conteudo = "" # Inicializa

            try:
                response = requests.post(api_url, headers=headers, json=payload, timeout=45) # Timeout aumentado
                response.raise_for_status()
                dados_resposta = response.json()

                if dados_resposta.get("choices") and len(dados_resposta["choices"]) > 0:
                    resposta_ai_conteudo = dados_resposta["choices"][0]["message"]["content"].strip()
                else:
                    erro_msg = "Não recebi uma escolha válida da API."
                    if dados_resposta.get("error"):
                        erro_msg += f" Detalhe: {dados_resposta['error'].get('message', 'Erro desconhecido da API.')}"
                    resposta_ai_conteudo = f"Desculpe, não consegui obter uma resposta. {erro_msg}"

            except requests.exceptions.Timeout:
                resposta_ai_conteudo = "A API demorou muito para responder. Tente novamente mais tarde."
            except requests.exceptions.RequestException as e:
                resposta_ai_conteudo = f"Erro ao contatar a API DeepSeek: {e}"
            except json.JSONDecodeError:
                resposta_ai_conteudo = "Erro ao decodificar a resposta da API (formato inválido)."
            except KeyError:
                resposta_ai_conteudo = "Resposta da API em formato inesperado."
            
            # Adiciona a pergunta original do usuário e a resposta da IA ao histórico da sessão
            historico_conversa.append({"role": "user", "content": prompt_usuario})
            historico_conversa.append({"role": "assistant", "content": resposta_ai_conteudo})

            request.session['historico_conversa'] = historico_conversa
            form = ChatForm()

    return render(request, 'chatbot/chat.html', {
        'form': form,
        'historico_conversa': historico_conversa,
    })


# NOVA VIEW para limpar o chat
def limpar_chat_view(request):
    if 'historico_conversa' in request.session:
        del request.session['historico_conversa']
    # Modifica a sessão para garantir que seja salva (útil em algumas configurações)
    request.session.modified = True 
    return redirect('chatbot:chat') # Redireciona de volta para a página principal do chat