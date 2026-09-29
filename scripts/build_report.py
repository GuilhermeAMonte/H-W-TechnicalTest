# -*- coding: utf-8 -*-
"""Reconstrói o relatório técnico: fonte uniforme, tom corporativo, evidências."""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT

FIG = "figures"
OUT = "Relatorio_Tecnico_HW.docx"
NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x59, 0x59, 0x59)

d = Document()

# ---- Fonte base uniforme ---------------------------------------------------
normal = d.styles["Normal"]
normal.font.name = "Calibri"
normal.font.size = Pt(11)
normal.paragraph_format.space_after = Pt(6)
normal.paragraph_format.line_spacing = 1.15

for i, col in ((1, NAVY), (2, NAVY), (3, NAVY)):
    st = d.styles[f"Heading {i}"]
    st.font.name = "Calibri"
    st.font.color.rgb = col
    st.font.size = Pt(16 - 2 * (i - 1))

# Margens
for s in d.sections:
    s.top_margin = s.bottom_margin = Inches(0.9)
    s.left_margin = s.right_margin = Inches(1.0)

def H(txt, lvl=1):
    d.add_heading(txt, level=lvl)

def P(txt, bold=False):
    p = d.add_paragraph()
    r = p.add_run(txt)
    r.bold = bold
    return p

def bullet(txt):
    d.add_paragraph(txt, style="List Bullet")

def fig(name, caption, width=6.2):
    path = os.path.join(FIG, name)
    if not os.path.exists(path):
        return
    d.add_picture(path, width=Inches(width))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap = d.add_paragraph()
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = cap.add_run(caption)
    r.italic = True
    r.font.size = Pt(9)
    r.font.color.rgb = GREY

def table(headers, rows, widths=None):
    t = d.add_table(rows=1, cols=len(headers))
    t.style = "Light Grid Accent 1"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        run = c.paragraphs[0].add_run(h)
        run.bold = True
        run.font.size = Pt(10)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            run = cells[i].paragraphs[0].add_run(str(v))
            run.font.size = Pt(10)
    d.add_paragraph("")

# ===========================================================================
# CAPA
# ===========================================================================
for _ in range(3):
    d.add_paragraph("")
t = d.add_paragraph()
t.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = t.add_run("Relatório Técnico de Segurança Ofensiva e Defensiva")
r.bold = True
r.font.size = Pt(26)
r.font.color.rgb = NAVY
sub = d.add_paragraph()
sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = sub.add_run("Laboratório de Rede Segmentada — VPN, Firewall, WAF e Cadeia de Ataque")
r.font.size = Pt(14)
r.font.color.rgb = GREY
for _ in range(2):
    d.add_paragraph("")
meta = d.add_paragraph()
meta.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = meta.add_run("Processo Seletivo — Segurança da Informação\nDocumento confidencial — uso restrito à avaliação técnica")
r.font.size = Pt(11)
r.font.color.rgb = GREY
d.add_page_break()

# ===========================================================================
# 1. SUMÁRIO EXECUTIVO
# ===========================================================================
H("1. Sumário Executivo", 1)
P("Este relatório documenta a construção de um ambiente de rede corporativa "
  "segmentada e a execução de um ciclo completo de segurança sobre ele: "
  "reconhecimento, exploração, movimentação lateral, exfiltração de dados e, na "
  "sequência, a contenção de cada vetor identificado. O objetivo foi demonstrar, com "
  "evidência reproduzível, tanto a capacidade ofensiva (comprometer o ambiente) "
  "quanto a defensiva (segmentar, detectar e mitigar).")
P("O ambiente reproduz, em um único host e com um único comando, um recorte "
  "representativo de uma infraestrutura híbrida: uma borda de VPN e firewall, uma DMZ "
  "com aplicação exposta atrás de um WAF, uma camada de aplicação interna e uma "
  "camada de banco de dados isolada. A premissa condutora foi o princípio de menor "
  "privilégio na rede: tudo o que não é explicitamente permitido é negado.")
P("Principais resultados:", bold=True)
bullet("Nove vulnerabilidades reais foram exploradas na aplicação-alvo, incluindo "
       "SQL Injection, execução remota de código via upload inseguro e injeção de comando.")
bullet("Uma cadeia de ataque de ponta a ponta foi comprovada: da aplicação exposta na "
       "DMZ até a exfiltração de dados sensíveis do banco, atravessando três segmentos de rede.")
bullet("A segmentação de rede demonstrou eficácia: mesmo com a credencial do banco em "
       "poder do atacante, o acesso direto ao banco a partir da DMZ permaneceu bloqueado.")
bullet("O WAF passou a bloquear os ataques (respostas 403) após a ativação do modo de "
       "prevenção; um bypass estrutural (client-side) foi identificado e mitigado com "
       "defesa em profundidade (Content-Security-Policy).")
bullet("Cada elo da cadeia recebeu mitigação, com comprovação de antes e depois.")

# ===========================================================================
# 2. ESCOPO E METODOLOGIA
# ===========================================================================
H("2. Escopo e Metodologia", 1)
P("A avaliação seguiu a metodologia Cyber Kill Chain, percorrendo as fases de "
  "reconhecimento, armamento, entrega, exploração, instalação, comando e controle, e "
  "ações sobre o objetivo. O reconhecimento foi conduzido a partir de três pontos de "
  "vista distintos — externo (internet/host), interno via VPN e interno pós-"
  "comprometimento (DMZ) — de modo a mapear a superfície de ataque visível de cada posição.")
P("A aplicação-alvo é o DVWA (Damn Vulnerable Web Application), executada atrás do "
  "WAF, conforme previsto no escopo do teste. As vulnerabilidades presentes na API "
  "interna (exposição de credencial e injeção de comando) são intencionais e "
  "documentadas, servindo para compor a cadeia de movimentação lateral.")

# ===========================================================================
# 3. ARQUITETURA DA INFRAESTRUTURA
# ===========================================================================
H("3. Arquitetura da Infraestrutura", 1)
P("A infraestrutura é orquestrada com docker-compose em um único host, composta por "
  "quatro redes isoladas e um container-roteador que concentra e filtra todo o "
  "tráfego entre segmentos. As três redes de segmento são internas (sem rota para a "
  "internet); o único ponto de contato externo é a porta da VPN, na rede de borda.")
table(
    ["Segmento", "Rede", "Host", "Papel"],
    [
        ["Borda", "lab_edge", "wg-gateway", "Roteador/firewall (nftables) + entrada VPN (WireGuard)"],
        ["DMZ", "172.30.10.0/24", "waf → dvwa", "WAF (ModSecurity + CRS) à frente do alvo vulnerável"],
        ["APP", "172.30.20.0/24", "app-api", "API interna (pivô de movimentação lateral)"],
        ["DB", "172.30.30.0/24", "postgres", "Banco de dados com informações sensíveis"],
    ],
)

H("3.1. Segmentação e firewall default-deny", 2)
P("Redes Docker isoladas separam no nível de enlace, mas não oferecem controle por "
  "porta, registro de eventos nem rastreamento de estado de conexão. Por isso, o "
  "wg-gateway atua como roteador (multi-homed, conectado às três redes) executando "
  "nftables com política padrão de descarte (default-deny) nas cadeias INPUT e "
  "FORWARD. Apenas dois fluxos entre segmentos são liberados, de forma explícita e comentada:")
bullet("DMZ → APP, somente na porta da aplicação (8000).")
bullet("APP → DB, somente na porta do PostgreSQL (5432).")
P("Qualquer outro caminho — por exemplo, DMZ → DB — recai no default-deny. O "
  "rastreamento de conexões (conntrack) garante que apenas o primeiro pacote de cada "
  "fluxo seja avaliado contra as regras; as respostas retornam pelo estado da conexão.")

H("3.2. VPN e acesso administrativo restrito", 2)
P("O acesso administrativo (SSH) não é exposto à internet. O wg-gateway termina um "
  "túnel WireGuard, e o firewall aceita SSH somente quando a origem pertence à "
  "sub-rede da VPN. Como diferencial de hardening, o login administrativo é feito "
  "exclusivamente por chave, com a autenticação por senha desabilitada — combinando "
  "controle de rede (somente via VPN) com controle de autenticação (somente por chave).")

H("3.3. Serviços e WAF", 2)
P("Os serviços foram implantados nos segmentos corretos: o DVWA na DMZ, atrás do WAF; "
  "a API interna na camada APP; e o PostgreSQL na camada DB, fechado, sem exposição de "
  "porta ao host. À frente do DVWA, um Nginx com ModSecurity e o OWASP Core Rule Set "
  "atua como reverse proxy. O WAF inicia em modo de detecção (observa e registra sem "
  "bloquear) e, na fase defensiva, passa a operar em modo de prevenção (bloqueio com 403).")

# ===========================================================================
# 4. RECONHECIMENTO E ENUMERAÇÃO
# ===========================================================================
H("4. Reconhecimento e Enumeração", 1)
P("O reconhecimento foi conduzido a partir de três pontos de vista, mapeando o que "
  "está exposto de cada posição — e, igualmente importante, o que não está.")

H("4.1. Ponto de vista externo (sem VPN)", 2)
P("A partir do host, sem a VPN ativa, a superfície do laboratório resume-se a uma "
  "única porta UDP (a da VPN, WireGuard). Nenhum serviço da DMZ, APP ou DB é "
  "enumerável externamente — a segmentação cumpre seu papel antes mesmo de qualquer "
  "autenticação.")
fig("fig_01.png", "Figura 1 — Varredura externa sem VPN: superfície mínima, nenhum serviço do laboratório visível.")

H("4.2. Ponto de vista interno via VPN", 2)
P("Com a VPN ativa, o único serviço alcançável passa a ser o WAF. O alvo (DVWA) não é "
  "acessível diretamente: todo o tráfego de entrada é obrigado a passar pelo WAF, "
  "conforme o desenho pretendido.")
fig("fig_02.png", "Figura 2 — Com a VPN ativa, a aplicação torna-se alcançável através do WAF.")
fig("fig_03.png", "Figura 3 — A partir da VPN, apenas o WAF responde; o alvo não é acessível de forma direta.")

H("4.3. Enumeração da aplicação", 2)
P("A identificação de tecnologia por meio dos cabeçalhos HTTP e dos cookies revelou o "
  "backend em PHP e expôs o nível de segurança da aplicação em um cookie legível — "
  "informação útil para o atacante. A enumeração de diretórios identificou arquivos "
  "sensíveis e o mapa completo dos módulos vulneráveis disponíveis para exploração.")
fig("fig_04.png", "Figura 4 — Identificação de tecnologia pelos cabeçalhos HTTP.")
fig("fig_05.png", "Figura 5 — Cookies expondo o nível de segurança da aplicação.")
fig("fig_06.png", "Figura 6 — Arquivos e diretórios de interesse identificados na enumeração.")

# ===========================================================================
# 5. EXPLORAÇÃO E CADEIA DE ATAQUE
# ===========================================================================
H("5. Exploração e Cadeia de Ataque", 1)
P("Foram exploradas nove vulnerabilidades reais. Em seguida, os achados foram "
  "encadeados em uma cadeia de ataque de ponta a ponta, da aplicação exposta até a "
  "exfiltração do banco de dados.")

H("5.1. SQL Injection", 2)
P("O campo de identificação de usuário concatena a entrada diretamente na consulta "
  "SQL, sem validação nem parametrização. Um payload de condição sempre verdadeira "
  "transforma a consulta e retorna todos os registros da tabela de usuários, em vez de "
  "um único. Impacto: exposição integral de dados de autenticação. Severidade: Crítica.")
fig("fig_07.png", "Figura 7 — SQL Injection: a consulta manipulada retorna todos os usuários.")
fig("fig_08.png", "Figura 8 — SQL Injection: dados de autenticação expostos.")

H("5.2. SQL Injection Blind (baseado em tempo)", 2)
P("Quando a aplicação não exibe o resultado da consulta, a injeção ainda é "
  "comprovável pelo tempo de resposta. Um payload com função de atraso condicional faz "
  "a resposta demorar cinco segundos ou mais quando a condição é verdadeira, enquanto "
  "um payload de controle responde imediatamente — confirmando a execução do SQL "
  "injetado sem retorno visível de dados. Severidade: Crítica.")
fig("fig_09.png", "Figura 9 — SQL Injection Blind: atraso condicional confirma a injeção.")

H("5.3. Cross-Site Scripting (XSS)", 2)
P("Foram identificadas três variantes de XSS. O XSS Refletido injeta script que é "
  "devolvido e executado na resposta imediata; embora dependa de o usuário acessar um "
  "link preparado, é uma vulnerabilidade real, com potencial de roubo de sessão e "
  "phishing. O XSS Armazenado é mais grave: o script é persistido pela aplicação e "
  "executado no navegador de todos os usuários que acessarem a página. O XSS baseado "
  "em DOM ocorre inteiramente no cliente — o servidor não chega a processar o payload — "
  "e será determinante na análise dos limites do WAF (Seção 6).")
fig("fig_10.png", "Figura 10 — XSS Refletido.")
fig("fig_11.png", "Figura 11 — XSS Armazenado (persistido pela aplicação).")
fig("fig_12.png", "Figura 12 — XSS baseado em DOM (executado no cliente).")
fig("fig_13.png", "Figura 13 — Construção do payload de XSS DOM, encerrando as tags para injetar o script.")

H("5.4. Upload inseguro e execução remota de código", 2)
P("O módulo de upload não valida extensão, tipo MIME nem assinatura do arquivo. Foi "
  "enviado um webshell em PHP, que passou a residir no diretório de uploads e, ao ser "
  "acessado, permitiu a execução de comandos no servidor. A confirmação do usuário do "
  "sistema (www-data) caracteriza execução remota de código e estabelece o foothold na "
  "DMZ. Severidade: Crítica.")
fig("fig_14.png", "Figura 14 — Upload do arquivo malicioso aceito sem validação.")
fig("fig_15.png", "Figura 15 — Webshell ativa: execução de comando confirmada (foothold na DMZ).")

H("5.5. Command Injection", 2)
P("Uma funcionalidade que executa um comando de sistema com parâmetro fornecido pelo "
  "usuário, sem sanitização, permite encadear comandos adicionais por meio de "
  "separadores de shell. O resultado é execução arbitrária de comandos além da função "
  "pretendida. Severidade: Crítica.")
fig("fig_16.png", "Figura 16 — Command Injection: execução de comando adicional além do previsto.")

H("5.6. File Inclusion (LFI)", 2)
P("O parâmetro que determina qual arquivo será carregado não é validado, permitindo, "
  "por travessia de diretórios, a leitura de arquivos sensíveis do sistema — como o "
  "/etc/passwd. Essa exposição de arquivos locais pode revelar informações úteis para "
  "o aprofundamento do ataque. Severidade: Alta.")
fig("fig_17.png", "Figura 17 — Local File Inclusion: leitura de /etc/passwd por travessia de diretórios.")

H("5.7. CSRF (Cross-Site Request Forgery)", 2)
P("Este vetor não explora a falta de validação de entrada, mas a confiança do "
  "navegador na sessão autenticada. Sem um token anti-CSRF, uma requisição de troca de "
  "senha pode ser disparada a partir de uma página externa: ao clicar em um link "
  "aparentemente inofensivo, o próprio navegador da vítima envia o cookie de sessão, e "
  "a senha é alterada sem a ação consciente do usuário. Nota técnica: navegadores "
  "modernos aplicam a proteção SameSite por padrão, que bloqueia o vetor via requisição "
  "embutida (por exemplo, uma tag de imagem), mas não a navegação de topo (clique em "
  "link) — o que foi utilizado para concluir o ataque. Severidade: Alta.")
fig("fig_18.png", "Figura 18 — Página de ataque CSRF preparada.")
fig("fig_19.png", "Figura 19 — Execução do CSRF por meio de navegação de topo.")
fig("fig_20.png", "Figura 20 — Resultado: alteração de senha sem interação legítima do usuário.")

H("5.8. Brute Force e identificador de sessão fraco", 2)
P("A ausência de limitação de tentativas (rate limiting) permite testar exaustivamente "
  "combinações de usuário e senha até obter acesso. Com o uso de listas de credenciais "
  "comuns, foram identificadas credenciais válidas. Adicionalmente, o gerador de "
  "identificadores de sessão produz valores estritamente sequenciais (incremento de um "
  "a cada chamada) — um identificador previsível que permitiria antecipar sessões de "
  "outros usuários sem qualquer roubo de credencial. Severidade: Alta.")
fig("fig_21.png", "Figura 21 — Brute Force: ausência de limitação de tentativas.")
fig("fig_22.png", "Figura 22 — Credenciais válidas identificadas.")
fig("fig_23.png", "Figura 23 — Requisição do atacante durante o ataque.")

H("5.9. Cadeia de ataque completa — da DMZ ao banco de dados", 2)
P("Com o foothold estabelecido na DMZ (webshell no DVWA), o ataque avançou para as "
  "camadas internas, respeitando — e evidenciando — a segmentação de rede:")
bullet("Movimentação lateral: a partir do webshell (origem na DMZ), a API interna na "
       "camada APP tornou-se alcançável, pois a regra de firewall permite o fluxo DMZ → APP.")
bullet("Exposição de credencial: um endpoint interno sem autenticação revelou a "
       "credencial de acesso ao banco de dados.")
bullet("Contenção pela segmentação: mesmo de posse da credencial, o acesso direto ao "
       "banco a partir da DMZ permaneceu bloqueado — a regra de firewall só permite o "
       "fluxo APP → DB. A credencial, isoladamente, não foi suficiente.")
bullet("Reúso de credencial via pivô: a partir de execução de comando na camada APP, a "
       "credencial roubada foi utilizada com o cliente de banco de dados para alcançar o "
       "PostgreSQL (fluxo legítimo APP → DB) e exfiltrar os dados sensíveis.")
P("Essa distinção é relevante para a avaliação de risco: a defesa de rede funcionou — "
  "neutralizou o uso direto da credencial — e a exfiltração só foi possível através da "
  "cadeia legítima, explorando falhas de aplicação. É precisamente essa brecha de "
  "aplicação que a fase de contenção (Seção 7) endereça.")
fig("fig_24.png", "Figura 24 — Aprofundamento do ataque: alcance à camada de aplicação.")
fig("fig_25.png", "Figura 25 — Exfiltração dos dados sensíveis do banco de dados.")

# ===========================================================================
# 6. DEFESA REATIVA — WAF
# ===========================================================================
H("6. Defesa Reativa — WAF (Bloqueio, Bypass e Correção)", 1)
P("Concluída a fase ofensiva, o WAF foi migrado do modo de detecção para o modo de "
  "prevenção. As mesmas requisições que antes eram apenas registradas passaram a ser "
  "bloqueadas com resposta 403.")
fig("fig_26.png", "Figura 26 — WAF em modo de prevenção: SQL Injection bloqueado (403).")

H("6.1. Tentativas de bypass", 2)
P("A evasão por dupla codificação foi testada e não obteve sucesso: o Core Rule Set "
  "aplica funções de transformação que decodificam a entrada antes da análise, "
  "desfazendo a codificação e detectando o ataque. Isso demonstra a robustez do "
  "controle contra técnicas básicas de evasão.")
fig("fig_27.png", "Figura 27 — Tentativa de bypass por dupla codificação, bloqueada pelo WAF.")
P("O bloqueio de XSS também foi confirmado. Em seguida, um bypass estrutural foi "
  "identificado: o XSS baseado em DOM, quando entregue pelo fragmento da URL (após o "
  "caractere '#'), não trafega até o servidor. Como o WAF inspeciona requisições, ele "
  "é estruturalmente incapaz de bloquear um ataque que ocorre inteiramente no cliente — "
  "não existe regra que feche essa lacuna, pois o payload nunca chega ao WAF.")
fig("fig_28.png", "Figura 28 — Teste de bloqueio de XSS pelo WAF.")
fig("fig_29.png", "Figura 29 — Bloqueio de XSS confirmado e análise do bypass via fragmento.")

H("6.2. Correção — defesa em profundidade com CSP", 2)
P("Uma vez que o WAF não pode inspecionar o fragmento, a correção adequada é de outra "
  "natureza: o WAF passou a injetar, na resposta, o cabeçalho Content-Security-Policy. "
  "Ele não depende de enxergar o payload — instrui o navegador a recusar a execução de "
  "scripts inline, neutralizando o XSS baseado em DOM no cliente. Confirmou-se que "
  "requisições legítimas continuam a ser atendidas (resposta 200, sem falso positivo) e "
  "que as proteções anteriores contra SQL Injection e XSS permanecem ativas.")
fig("fig_30.png", "Figura 30 — Correção aplicada: Content-Security-Policy neutraliza o XSS baseado em DOM.")
P("Como recomendação, o Content-Security-Policy estrito bloqueia todo script inline, "
  "inclusive o legítimo da aplicação; em um ambiente de produção, o correto é adotar "
  "nonces ou hashes por script, permitindo os legítimos e barrando os injetados. A "
  "correção definitiva, no entanto, é de aplicação: o código cliente não deve escrever "
  "dados não confiáveis diretamente no documento.")

# ===========================================================================
# 7. CONTENÇÃO E HARDENING
# ===========================================================================
H("7. Contenção e Hardening", 1)
P("Cada elo da cadeia de ataque recebeu uma mitigação, comprovada com a mesma "
  "tentativa agora barrada. A abordagem foi de defesa em camadas — corrigindo tanto na "
  "rede quanto na aplicação.")

H("7.1. Movimentação lateral (rede)", 2)
P("A regra de firewall que permitia o fluxo DMZ → APP aceitava toda a sub-rede da DMZ "
  "como origem — foi o que permitiu ao host comprometido pivotar. A mitigação "
  "restringiu a regra a aceitar apenas o WAF como origem legítima. Resultado: o host "
  "comprometido (DVWA) passou a receber timeout ao tentar alcançar a API interna, "
  "enquanto o caminho legítimo (WAF → API) foi preservado. Uma única regra de rede "
  "interrompe a cadeia a partir da movimentação lateral.")

H("7.2. Exposição de credencial e injeção de comando (aplicação)", 2)
P("O endpoint interno que expunha a credencial do banco foi removido, reduzindo a "
  "superfície de ataque; após a correção, a requisição retorna 404. A funcionalidade "
  "vulnerável a injeção de comando passou a validar a entrada por allowlist e a "
  "executar o comando sem shell, com argumentos isolados; após a correção, tentativas "
  "de injeção são rejeitadas com 400, enquanto o uso legítimo permanece funcional.")

H("7.3. Redução de superfície e egress", 2)
P("A política default-deny na cadeia FORWARD impede que os segmentos iniciem conexões "
  "para fora, contendo reverse shells e exfiltração para a internet. Comprovou-se que "
  "nenhum segmento (DMZ ou APP) alcança a internet. Como recomendação adicional, o "
  "acesso ao banco deve utilizar um usuário com privilégio mínimo (somente leitura das "
  "tabelas necessárias, sem superusuário), reduzindo o impacto de um eventual reúso de credencial.")

# ===========================================================================
# 8. MAPA DE PORTAS
# ===========================================================================
H("8. Mapa de Mapeamento de Portas", 1)
P("Nenhuma porta dos serviços de back-end é publicada no host; apenas a VPN e o acesso "
  "ao WAF através do túnel são expostos. A tabela consolida o mapa após o hardening.")
table(
    ["Host", "Porta", "Proto", "Quem pode acessar", "Justificativa"],
    [
        ["wg-gateway (borda)", "51820", "UDP", "Internet/host", "Entrada da VPN — único ponto público"],
        ["wg-gateway", "22", "TCP", "Sub-rede da VPN", "Administração via VPN; login por chave"],
        ["waf", "8080", "TCP", "Via VPN", "Ponto de entrada web; proxy para o DVWA"],
        ["dvwa", "80", "TCP", "Somente o WAF", "Alvo atrás do WAF; nunca direto"],
        ["app-api", "8000", "TCP", "Somente o WAF", "API interna; DMZ não alcança (hardening)"],
        ["postgres", "5432", "TCP", "Somente a camada APP", "Banco fechado; DMZ e internet nunca"],
    ],
)
P("Comprovação do caminho que deve ser sempre bloqueado: o fluxo DMZ → banco de dados "
  "resulta em timeout (recusado), enquanto o fluxo legítimo APP → banco é atendido. O "
  "timeout — estado 'filtered' em uma varredura — é a assinatura do firewall "
  "descartando o pacote em silêncio, característica de uma segmentação ativa.")

# ===========================================================================
# 9. RESUMO DOS ACHADOS
# ===========================================================================
H("9. Resumo dos Achados", 1)
table(
    ["#", "Vulnerabilidade", "Localização", "Severidade (CVSS aprox.)"],
    [
        ["1", "SQL Injection", "DVWA — módulo SQLi", "Crítica (9.8)"],
        ["2", "SQL Injection Blind (time-based)", "DVWA — módulo SQLi Blind", "Crítica (9.1)"],
        ["3", "XSS Refletido", "DVWA — módulo XSS-R", "Média (6.1)"],
        ["4", "XSS Armazenado", "DVWA — módulo XSS-S", "Alta (7.4)"],
        ["5", "XSS baseado em DOM", "DVWA — módulo XSS-D", "Média (6.1)"],
        ["6", "Upload inseguro → RCE", "DVWA — módulo Upload", "Crítica (9.8)"],
        ["7", "Command Injection", "DVWA — módulo Exec", "Crítica (9.8)"],
        ["8", "Local File Inclusion", "DVWA — módulo File Inclusion", "Alta (7.5)"],
        ["9", "CSRF", "DVWA — módulo CSRF", "Alta (8.8)"],
        ["10", "Brute Force / Session ID fraco", "DVWA — Brute / Weak ID", "Alta (7.5)"],
        ["11", "Exposição de credencial + RCE no pivô", "API interna", "Crítica (9.8)"],
    ],
)

# ===========================================================================
# 10. CONCLUSÃO
# ===========================================================================
H("10. Conclusão, Trade-offs e Escala para a Nuvem", 1)
P("O laboratório demonstrou o ciclo completo — atacar, entender e conter — com "
  "evidência em cada etapa. A infraestrutura é reproduzível com um único comando e "
  "nenhum segredo é versionado no repositório.")
H("Trade-offs e limitações", 2)
bullet("O WAF é um controle importante, porém não suficiente isoladamente: o XSS "
       "baseado em DOM via fragmento evidenciou um ponto cego estrutural, mitigado com "
       "defesa em profundidade (CSP), e não com uma regra adicional.")
bullet("O CSP estrito bloqueia todo script inline; em produção, o correto é o uso de "
       "nonces ou hashes por script.")
bullet("O alvo é o DVWA, deliberadamente vulnerável, conforme previsto no escopo; as "
       "vulnerabilidades da API interna são intencionais e documentadas.")
H("Mapeamento para a infraestrutura real", 2)
bullet("Firewall nftables no gateway → Security Groups e NACLs (AWS) ou regras de "
       "roteamento no Proxmox; a camada de rede do provedor libera o trânsito até o "
       "appliance, que aplica a política fina.")
bullet("Segmentos internos → subnets/VPCs separadas por camada, sem rota para a "
       "internet, com filtragem de egress explícita.")
bullet("WAF Nginx + ModSecurity + CRS → WAF gerenciado (AWS WAF) ou Cloudflare na borda.")
bullet("Gateway WireGuard + SSH por chave via VPN → VPN gerenciada ou bastion host isolado.")
bullet("Default-deny em INPUT e FORWARD → postura deny-all com liberações explícitas, "
       "aplicando menor privilégio à rede.")

d.save(OUT)
print("OK ->", OUT, "| paragrafos:", len(d.paragraphs), "| tabelas:", len(d.tables))
