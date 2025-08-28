"""Este módulo guarda todas as funções do MCP visíveis para o Agente usar"""

from os import getenv
from typing import Literal, Sequence

import aiohttp
import ujson
from siga_mcp.decorators import controlar_acesso_matricula, resolve_matricula
from siga_mcp.constants import TYPE_TO_NUMBER
from siga_mcp.utils import converter_data_siga
from siga_mcp.xml_builder import XMLBuilder


async def buscar_informacoes_atendimentos_os(codigo_atendimento: int) -> str:
    """Busca informações detalhadas de um atendimento de Ordem de Serviço (OS) específico.

    Esta função realiza uma consulta ao sistema SIGA através da API do AVA para obter
    todas as informações relacionadas a um atendimento de OS específico. É especialmente
    útil para consultar dados antes de realizar edições no atendimento.

    Funcionalidades:
    - Consulta dados completos de um atendimento OS pelo código
    - Retorna informações estruturadas em formato XML
    - Inclui tratamento de erros para requisições mal-sucedidas
    - Utiliza autenticação via API Key do AVA

    Endpoint utilizado:
    - URL: https://ava3.uniube.br/ava/api/atendimentosOs/buscarInfoAtendimentosOsSigaIA/
    - Método: POST
    - Autenticação: API Key (AVA_API_KEY)

    Estrutura do XML retornado:
    - Elemento raiz: <info_atendimentos_os>
    - Atributos do elemento raiz: atendimento (código do atendimento)
    - Atributos customizados: sistema="SIGA"
    - Contém todos os dados do atendimento retornados pela API

    Args:
        codigo_atendimento (int): Código único identificador do atendimento OS.
                                 Deve ser um número inteiro válido correspondente
                                 a um atendimento existente no sistema SIGA.

    Returns:
        str: XML bem formatado contendo as informações do atendimento OS.
             Em caso de erro na requisição ou processamento, retorna a mensagem:
             "Erro ao buscar as informações do atendimento."

    Raises:
        Exception: Captura qualquer exceção durante a requisição HTTP ou
                  processamento dos dados, retornando mensagem de erro amigável.

    Example:
        >>> resultado = await buscar_informacoes_atendimentos_os(12345)
        >>> print(resultado)
        <?xml version="1.0" ?>
        <info_atendimentos_os atendimento="12345" sistema="SIGA">
          <campo1>valor1</campo1>
          <campo2>valor2</campo2>
          ...
        </info_atendimentos_os>

    Note:
        - Requer variável de ambiente AVA_API_KEY configurada
        - A função é assíncrona e deve ser chamada com await
        - Utiliza aiohttp para requisições HTTP assíncronas
        - O XML é formatado usando a classe XMLBuilder interna
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarInfoAtendimentosOsSigaIA/",
            json={
                "atendimento": codigo_atendimento,
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="info_atendimentos_os",
                    item_element_name="info_atendimentos_os",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao buscar as informações do atendimento."

@resolve_matricula
@controlar_acesso_matricula
async def buscar_pendencias_lancamentos_atendimentos(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    dataIni: str,
    dataFim: str,
) -> str:
    """Busca pendências de lançamentos de atendimentos no sistema SIGA para um analista específico.

    Esta função identifica os dias em que o usuário (analista) não efetuou nenhum tipo de
    registro no sistema SIGA, incluindo criação de OS, Atendimentos OS ou Atendimentos Avulsos.
    É uma ferramenta essencial para controle de produtividade e identificação de lacunas
    nos registros de trabalho.

    Funcionalidades:
    - Identifica dias sem registros de atividades no SIGA
    - Suporte a diferentes formatos de data (incluindo linguagem natural)
    - Filtragem por período específico (data início e fim)
    - Tratamento robusto de erros HTTP e de processamento
    - Retorno estruturado em formato XML

    Endpoint utilizado:
    - URL: https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarPendenciasRegistroAtendimentosSigaIA/
    - Método: POST
    - Autenticação: API Key (AVA_API_KEY)

    Estrutura do XML retornado:
    - Elemento raiz: <pendencias_lançamentos>
    - Atributos do elemento raiz: matricula (matrícula do analista)
    - Atributos customizados: sistema="SIGA"
    - Contém lista de dias/períodos sem registros

    Tipos de registros verificados:
    - Criação de Ordens de Serviço (OS)
    - Atendimentos de OS
    - Atendimentos Avulsos
    - Qualquer outro tipo de lançamento no SIGA

    Args:
        matricula (str | int | Literal["CURRENT_USER"], optional): Matrícula do analista para consulta.
                                                   Pode ser string, número inteiro ou "CURRENT_USER".
                                                    Se "CURRENT_USER", utiliza matrícula do usuário atual do arquivo .env.
                                                    Defaults to "CURRENT_USER".
        dataIni (str): Data de início do período de consulta.
                                                          Aceita formatos de data padrão ou
                                                          palavras-chave em português.
        dataFim (str): Data de fim do período de consulta.
                                                          Aceita formatos de data padrão ou
                                                          palavras-chave em português.

    Returns:
        str: XML bem formatado contendo as pendências de lançamentos encontradas.
             Em caso de erro na requisição ou processamento, retorna a mensagem:
             "Erro ao consultar todas as pendências de registros SIGA do usuário."

    Raises:
        Exception: Captura qualquer exceção durante a requisição HTTP ou
                  processamento dos dados, retornando mensagem de erro amigável.

    Example:
        >>> resultado = await buscar_pendencias_lancamentos_atendimentos(
        ...     matricula="12345",
        ...     dataIni="01/01/2024",
        ...     dataFim="hoje"
        ... )
        >>> print(resultado)
        <?xml version="1.0" ?>
        <pendencias_lançamentos matricula="12345" sistema="SIGA">
          <pendencia>
            <data>02/01/2024</data>
            <tipo>Sem registros</tipo>
          </pendencia>
          ...
        </pendencias_lançamentos>

    Note:
        - Requer variável de ambiente AVA_API_KEY configurada
        - A função é assíncrona e deve ser chamada com await
        - Utiliza a função converter_data_siga() para processar datas
        - Suporte a linguagem natural para datas ("hoje", "ontem", "agora")
        - Utiliza aiohttp para requisições HTTP assíncronas
        - O XML é formatado usando a classe XMLBuilder interna
        - Parâmetros são keyword-only (uso obrigatório de nomes dos parâmetros)
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarPendenciasRegistroAtendimentosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(dataIni),
                "dataFim": converter_data_siga(dataFim),
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                response.raise_for_status()

                # Converte a resposta para JSON, permitindo qualquer content-type
                data = await response.json(content_type=None)

                retorno = XMLBuilder().build_xml(
                    # Usa [] se 'result' não existir ou for None
                    data=data.get("result", []),
                    root_element_name="pendencias_lançamentos",
                    item_element_name="pendencias_lançamentos",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Captura qualquer outro erro não previsto
                return "Erro ao consultar todas as pendências de registros SIGA do usuário."


@resolve_matricula
async def buscar_todas_os_usuario(
    *,
    matricula: str | Sequence[str] | Literal["CURRENT_USER"] | None = "CURRENT_USER",
    os: str | Sequence[str] | None = None,
    filtrar_por: Sequence[
        Literal[
            "Pendente-Atendimento",
            "Em Teste",
            "Pendente-Teste",
            "Em Atendimento",
            "Em Implantação",
            "Pendente-Liberação",
            "Concluída por Encaminhamento",
            "Concluída",
            "Concluída por substituição",
            "Não Planejada",
            "Pendente-Sist. Administrativos",
            "Pendente-AVA",
            "Pendente-Consultoria",
            "Solicitação em Aprovação",
            "Pendente-Aprovação",
            "Pendente-Sist. Acadêmicos",
            "Pendente-Marketing",
            "Pendente-Equipe Manutenção",
            "Pendente-Equipe Infraestrutura",
            "Pendente-Atualização de Versão",
            "Pendente-Help-Desk",
            "Cancelamento DTI | Arquivado",
            "Cancelada-Usuário",
            "Pendente-Fornecedor",
            "Pendente-Usuário",
        ]
    ]
    | Literal["Todas OS em Aberto"]
    | str
    | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> str:
    """Busca Ordens de Serviço (OS) do sistema SIGA com filtros avançados e flexíveis.

    Esta função oferece uma interface completa para consulta de OS no sistema SIGA,
    permitindo filtros por matrícula, código de OS, status, e período. Suporta consultas
    tanto individuais quanto em lote, sendo ideal para relatórios e análises.

    Funcionalidades:
    - Consulta por matrícula única ou múltiplas matrículas
    - Busca por código de OS específico ou múltiplas OS
    - Filtros por status predefinidos ou customizados
    - Filtro por período (data início e fim)
    - Grupo especial "Todas OS em Aberto" para consultas rápidas
    - Suporte a linguagem natural para datas
    - Validação de parâmetros obrigatórios

    Endpoint utilizado:
    - URL: https://ava3.uniube.br/ava/api/os/buscarTodasOsPorMatriculaSigaIA/
    - Método: POST
    - Autenticação: API Key (AVA_API_KEY)

    Estrutura do XML retornado:
    - Elemento raiz: <ordens_servico>
    - Elemento item: <ordem_servico>
    - Atributos do elemento raiz: matricula (matrícula consultada)
    - Atributos customizados: sistema="SIGA"

    Status de OS disponíveis:
    - Pendente-Atendimento, Em Teste, Pendente-Teste, Em Atendimento
    - Em Implantação, Pendente-Liberação, Concluída, Concluída por Encaminhamento
    - Concluída por substituição, Não Planejada, Pendente-Sist. Administrativos
    - Pendente-AVA, Pendente-Consultoria, Solicitação em Aprovação
    - Pendente-Aprovação, Pendente-Sist. Acadêmicos, Pendente-Marketing
    - Pendente-Equipe Manutenção, Pendente-Equipe Infraestrutura
    - Pendente-Atualização de Versão, Pendente-Help-Desk
    - Cancelamento DTI | Arquivado, Cancelada-Usuário
    - Pendente-Fornecedor, Pendente-Usuário

    Args:
        matricula (str | Sequence[str] | Literal["CURRENT_USER"] | None, optional): Matrícula(s) do(s) usuário(s).
                                                                    - String única: "12345"
                                                                    - Lista: ["12345", "67890"] para múltiplas
                                                                    - None: busca de todos os usuários
                                                                    - "CURRENT_USER": usar matrícula do usuário atual do .env
                                                                    Defaults to None.
        os (str | Sequence[str] | None, optional): Código(s) da(s) OS para consulta específica.
                                                  - String única: "98765"
                                                  - Lista: ["98765", "54321"] para múltiplas
                                                  - None: sem filtro por OS específica
                                                  Defaults to None.
        filtrar_por (Sequence[Literal] | Literal["Todas OS em Aberto"] | str | None, optional):
                   Status para filtrar as OS.
                   - "Todas OS em Aberto": grupo pré-definido de status em aberto
                   - Lista: ["Concluída", "Pendente-Teste"] para múltiplos status
                   - String: status único
                   - None: sem filtro de status
                   Defaults to None.
        data_inicio (str | None, optional):
                   Data de início do período de consulta.
                   Aceita formatos de data padrão ou palavras-chave em português.
                   Defaults to None.
        data_fim (str | None, optional):
                 Data de fim do período de consulta.
                 Aceita formatos de data padrão ou palavras-chave em português.
                 Defaults to None.

    Returns:
        str: XML bem formatado contendo as OS encontradas.
             Em caso de parâmetros inválidos, retorna:
             "Erro: É necessário informar pelo menos a matrícula ou o código da OS para realizar a consulta."
             Em caso de erro na requisição, retorna:
             "Erro ao consultar dados da(s) OS."

    Raises:
        Exception: Captura qualquer exceção durante a requisição HTTP ou
                  processamento dos dados, retornando mensagem de erro amigável.

    Examples:
        Casos de uso principais:

        1. OS em aberto de uma matrícula:
        >>> resultado = await buscar_todas_os_usuario(
        ...     matricula="12345",
        ...     filtrar_por="Todas OS em Aberto"
        ... )

        2. OS em aberto de múltiplas matrículas:
        >>> resultado = await buscar_todas_os_usuario(
        ...     matricula=["12345", "67890"],
        ...     filtrar_por="Todas OS em Aberto"
        ... )

        3. OS por status específico:
        >>> resultado = await buscar_todas_os_usuario(
        ...     matricula="12345",
        ...     filtrar_por=["Concluída", "Concluída por Encaminhamento"]
        ... )

        4. OS específicas por código:
        >>> resultado = await buscar_todas_os_usuario(
        ...     os=["1001", "1002"],
        ...     matricula=None
        ... )

        5. OS com filtro de período:
        >>> resultado = await buscar_todas_os_usuario(
        ...     matricula="12345",
        ...     data_inicio="01/01/2024",
        ...     data_fim="hoje"
        ... )

    Note:
        - Pelo menos 'matricula' ou 'os' deve ter valor válido para executar a consulta
        - Requer variável de ambiente AVA_API_KEY configurada
        - A função é assíncrona e deve ser chamada com await
        - Utiliza a função converter_data_siga() para processar datas
        - Suporte a linguagem natural para datas ("hoje", "ontem", "agora")
        - Utiliza aiohttp para requisições HTTP assíncronas
        - O XML é formatado usando a classe XMLBuilder interna
        - Parâmetros são keyword-only (uso obrigatório de nomes dos parâmetros)
        - O filtro "Todas OS em Aberto" é expandido automaticamente para todos os status em aberto
    """

    if not matricula and not os:
        return "Erro: É necessário informar pelo menos a matrícula ou o código da OS para realizar a consulta."

    if filtrar_por == "Todas OS em Aberto":
        filtrar_por = [
            "Pendente-Atendimento",
            "Em Teste",
            "Pendente-Teste",
            "Em Atendimento",
            "Em Implantação",
            "Pendente-Liberação",
            "Não Planejada",
            "Pendente-Sist. Administrativos",
            "Pendente-AVA",
            "Pendente-Consultoria",
            "Solicitação em Aprovação",
            "Pendente-Aprovação",
            "Pendente-Sist. Acadêmicos",
            "Pendente-Marketing",
            "Pendente-Equipe Manutenção",
            "Pendente-Equipe Infraestrutura",
            "Pendente-Atualização de Versão",
            "Pendente-Help-Desk",
            "Pendente-Fornecedor",
            "Pendente-Usuário",
        ]

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/os/buscarTodasOsPorMatriculaSigaIA/",
            json={
                "descricaoStatusOs": filtrar_por or "",  # Array ou string puro
                "matricula": matricula or "",  # Array ou string puro
                "codOs": os or "",  # Array ou string puro
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                # response.raise_for_status()

                data = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=data["result"],
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception as e:
                # Captura qualquer outro erro não previsto
                return f"Erro ao consultar dados da(s) OS. {e} Matrícula: {matricula}"

async def editar_atendimentos_os(
    codigo_atendimento: int,
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo_atendimento: Literal[
        "Suporte Sistema",
        "Implementação",
        "Manutenção Corretiva",
        "Reunião",
        "Treinamento",
        "Mudança de Escopo",
        "Anexo",
        "Suporte Infraestrutura",
        "Monitoramento",
        "Incidente",
        "Requisição",
    ] = "Implementação",
    data_fim: str | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    """Edita as informações de um atendimento de Ordem de Serviço (OS) no sistema SIGA.

    Esta função permite atualizar todos os campos de um atendimento existente, incluindo
    datas, descrição, tipo, tempo gasto e flags de controle. Realiza validação do tipo
    de atendimento e conversão automática de datas para o formato esperado pelo SIGA.

    **Endpoint utilizado:** `updateAtendimentosOsSigaIA`

    **Estrutura do XML retornado:**
    ```xml
    <ordens_servico os="123" dataIni="2024-01-15 09:00:00" analista="456"
                    descricao="Descrição" tipo="Implementação" dataFim="2024-01-15 17:00:00"
                    tempoGasto="480" primeiroAtendimento="False" apresentaSolucao="True"
                    sistema="SIGA">
        <ordem_servico sistema="SIGA">
            <status>sucesso</status>
            <mensagem>Atendimento editado com sucesso!</mensagem>
        </ordem_servico>
    </ordens_servico>
    ```

    **Em caso de erro de validação:**
    ```xml
    <erro_validacao sistema="SIGA" funcao="editar_atendimentos_os">
        <erro sistema="SIGA">
            <status>erro</status>
            <tipo_erro>tipo_invalido</tipo_erro>
            <tipo_informado>Tipo Inválido</tipo_informado>
            <mensagem>Tipo 'Tipo Inválido' não encontrado na constante TYPE_TO_NUMBER</mensagem>
            <tipos_validos>['Suporte Sistema', 'Implementação', ...]</tipos_validos>
        </erro>
    </erro_validacao>
    ```

    Args:
        codigo_atendimento (int): Código único do atendimento a ser editado
        codigo_os (int): Código da Ordem de Serviço à qual o atendimento pertence
        data_inicio (str): Data e hora de início do atendimento (formato aceito pelo converter_data_siga)
        codigo_analista (int): Matrícula do analista/usuário responsável pelo atendimento
        descricao_atendimento (str): Descrição detalhada do atendimento realizado
        tipo_atendimento (Literal): Tipo do atendimento, deve ser um dos valores válidos:
            - "Suporte Sistema" (código 1)
            - "Implementação" (código 2) - padrão
            - "Manutenção Corretiva" (código 3)
            - "Reunião" (código 4)
            - "Treinamento" (código 5)
            - "Mudança de Escopo" (código 20)
            - "Anexo" (código 12)
            - "Suporte Infraestrutura" (código 13)
            - "Monitoramento" (código 21)
            - "Incidente" (código 23)
            - "Requisição" (código 24)
        data_fim (str | Literal | None, optional): Data e hora de fim do atendimento.
            Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem".
            Se None, será enviado como string vazia. Defaults to None.
        primeiro_atendimento (bool, optional): Flag indicando se é o primeiro atendimento da OS.
            Defaults to False.
        apresenta_solucao (bool, optional): Flag indicando se o atendimento apresenta solução.
            Defaults to False.

    Returns:
        str: XML formatado contendo:
            - Em caso de sucesso: confirmação da edição com status "sucesso"
            - Em caso de erro de validação: detalhes do erro com tipos válidos
            - Em caso de erro de API: mensagem de erro específica
            - Em caso de erro interno: mensagem de erro genérica

            O XML sempre inclui os parâmetros enviados como atributos do elemento raiz.

    Raises:
        Não levanta exceções diretamente. Todos os erros são capturados e retornados
        como XML formatado com informações detalhadas do erro.

    Examples:
        >>> # Editar atendimento básico
        >>> xml = await editar_atendimentos_os(
        ...     codigo_atendimento=123,
        ...     codigo_os=456,
        ...     data_inicio="2024-01-15 09:00:00",
        ...     codigo_analista=789,
        ...     descricao_atendimento="Implementação de nova funcionalidade",
        ...     tipo_atendimento="Implementação"
        ... )

        >>> # Editar atendimento completo com solução
        >>> xml = await editar_atendimentos_os(
        ...     codigo_atendimento=123,
        ...     codigo_os=456,
        ...     data_inicio="hoje 09:00",
        ...     codigo_analista=789,
        ...     descricao_atendimento="Correção de bug crítico",
        ...     tipo_atendimento="Manutenção Corretiva",
        ...     data_fim="hoje 17:00",
        ...     primeiro_atendimento=True,
        ...     apresenta_solucao=True
        ... )

        >>> # Exemplo com tipo inválido (retorna erro)
        >>> xml = await editar_atendimentos_os(
        ...     codigo_atendimento=123,
        ...     codigo_os=456,
        ...     data_inicio="2024-01-15 09:00:00",
        ...     codigo_analista=789,
        ...     descricao_atendimento="Teste",
        ...     tipo_atendimento="Tipo Inexistente"  # Erro!
        ... )

    Notes:
        - A função realiza validação case-insensitive do tipo_atendimento
        - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
        - A função utiliza a constante TYPE_TO_NUMBER para mapear tipos para códigos numéricos
        - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
        - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
        - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    """

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Busca o tipo correto na constante TYPE_TO_NUMBER ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TYPE_TO_NUMBER
        (
            key
            for key in TYPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo_atendimento).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo_atendimento,
                    "mensagem": f"Tipo '{tipo_atendimento}' não encontrado na constante TYPE_TO_NUMBER",
                    "tipos_validos": list(TYPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TYPE_TO_NUMBER[tipo_normalizado]

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/updateAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim if data_fim else "",
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível editar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao editar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_normalizado),
                        "dataFim": str(data_fim),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )

async def excluir_atendimentos_os(
    codigo_atendimento: int,
) -> str:
    """Exclui um atendimento de Ordem de Serviço (OS) do sistema SIGA.

    Esta função remove permanentemente um atendimento específico do sistema,
    utilizando apenas o código do atendimento como identificador. A operação
    é irreversível e deve ser usada com cautela.

    **Endpoint utilizado:** `excluiAtendimentosOsSigaIA`

    **Estrutura do XML retornado:**
    ```xml
    <exclusões_atendimento_os atendimento="123" sistema="SIGA">
        <exclusão sistema="SIGA">
            <status>sucesso</status>
            <mensagem>Atendimento excluído com sucesso!</mensagem>
        </exclusão>
    </exclusões_atendimento_os>
    ```

    **Em caso de erro:**
    ```xml
    <exclusões_atendimento_os atendimento="123" sistema="SIGA">
        <exclusão sistema="SIGA">
            <status>erro</status>
            <mensagem>Não foi possível excluir o atendimento. Verifique as informações digitadas.</mensagem>
        </exclusão>
    </exclusões_atendimento_os>
    ```

    Args:
        codigo_atendimento (int): Código único do atendimento a ser excluído.
            Este código deve corresponder a um atendimento existente no sistema.

    Returns:
        str: XML formatado contendo:
            - Em caso de sucesso: confirmação da exclusão com status "sucesso"
            - Em caso de erro de validação: mensagem indicando problema com os dados
            - Em caso de erro de API: mensagem de erro específica
            - Em caso de erro interno: mensagem de erro genérica

            O XML sempre inclui o código do atendimento como atributo do elemento raiz.

    Raises:
        Não levanta exceções diretamente. Todos os erros são capturados e retornados
        como XML formatado com informações detalhadas do erro.

    Examples:
        >>> # Excluir atendimento específico
        >>> xml = await excluir_atendimentos_os(codigo_atendimento=12345)

        >>> # Exemplo de uso em contexto de limpeza
        >>> atendimentos_para_excluir = [123, 456, 789]
        >>> for codigo in atendimentos_para_excluir:
        ...     resultado = await excluir_atendimentos_os(codigo_atendimento=codigo)
        ...     print(f"Resultado para atendimento {codigo}: {resultado}")

    Notes:
        - **ATENÇÃO**: Esta operação é irreversível. Uma vez excluído, o atendimento
          não pode ser recuperado através da API
        - A função valida apenas se o código do atendimento existe no sistema
        - Não há validação de permissões - qualquer usuário com acesso à API pode excluir
        - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
        - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
        - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente

    Warning:
        Use esta função com extrema cautela em ambientes de produção. Considere
        implementar validações adicionais ou logs de auditoria antes da exclusão.
    """

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/excluiAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível excluir o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento excluído com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao excluir o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="exclusões_atendimento_os",
                    item_element_name="exclusão",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )

async def inserir_atendimentos_os(
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo: Literal[
        "Suporte Sistema",
        "Implementação",
        "Manutenção Corretiva",
        "Reunião",
        "Treinamento",
        "Mudança de Escopo",
        "Anexo",
        "Suporte Infraestrutura",
        "Monitoramento",
        "Incidente",
        "Requisição",
    ] = "Implementação",
    data_fim: str | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    """Insere um novo atendimento em uma Ordem de Serviço (OS) no sistema SIGA.

    Esta função cria um novo registro de atendimento associado a uma OS existente,
    incluindo informações como datas, descrição, tipo, tempo gasto e flags de controle.
    Realiza validação do tipo de atendimento e conversão automática de datas.

    **Endpoint utilizado:** `inserirAtendimentosOsSigaIA`

    **Estrutura do XML retornado:**
    ```xml
    <ordens_servico os="123" dataIni="2024-01-15 09:00:00" analista="456"
                    descricao="Descrição" tipo="Implementação" dataFim="2024-01-15 17:00:00"
                    tempoGasto="480" primeiroAtendimento="False" apresentaSolucao="True"
                    sistema="SIGA">
        <ordem_servico sistema="SIGA">
            <status>sucesso</status>
            <mensagem>Atendimento cadastrado com sucesso!</mensagem>
        </ordem_servico>
    </ordens_servico>
    ```

    **Em caso de erro de validação:**
    ```xml
    <erro_validacao sistema="SIGA" funcao="inserir_atendimentos_os">
        <erro sistema="SIGA">
            <status>erro</status>
            <tipo_erro>tipo_invalido</tipo_erro>
            <tipo_informado>Tipo Inválido</tipo_informado>
            <mensagem>Tipo 'Tipo Inválido' não encontrado na constante TYPE_TO_NUMBER</mensagem>
            <tipos_validos>['Suporte Sistema', 'Implementação', ...]</tipos_validos>
        </erro>
    </erro_validacao>
    ```

    Args:
        codigo_os (int): Código da Ordem de Serviço à qual o atendimento será associado
        data_inicio (str | Literal): Data e hora de início do atendimento.
            Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
        codigo_analista (int): Matrícula do analista/usuário responsável pelo atendimento
        descricao_atendimento (str): Descrição detalhada do atendimento a ser realizado
        tipo (Literal): Tipo do atendimento, deve ser um dos valores válidos:
            - "Suporte Sistema" (código 1)
            - "Implementação" (código 2) - padrão
            - "Manutenção Corretiva" (código 3)
            - "Reunião" (código 4)
            - "Treinamento" (código 5)
            - "Mudança de Escopo" (código 20)
            - "Anexo" (código 12)
            - "Suporte Infraestrutura" (código 13)
            - "Monitoramento" (código 21)
            - "Incidente" (código 23)
            - "Requisição" (código 24)
        data_fim (str | Literal | None, optional): Data e hora de fim do atendimento.
            Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem".
            Se None, será enviado como string vazia. Defaults to None.
        primeiro_atendimento (bool, optional): Flag indicando se é o primeiro atendimento da OS.
            Defaults to False.
        apresenta_solucao (bool, optional): Flag indicando se o atendimento apresenta solução.
            Defaults to False.

    Returns:
        str: XML formatado contendo:
            - Em caso de sucesso: confirmação da inserção com status "sucesso"
            - Em caso de erro de validação: detalhes do erro com tipos válidos
            - Em caso de erro de API: mensagem de erro específica
            - Em caso de erro interno: mensagem de erro genérica

            O XML sempre inclui os parâmetros enviados como atributos do elemento raiz.

    Raises:
        Não levanta exceções diretamente. Todos os erros são capturados e retornados
        como XML formatado com informações detalhadas do erro.

    Examples:
        >>> # Inserir atendimento básico
        >>> xml = await inserir_atendimentos_os(
        ...     codigo_os=456,
        ...     data_inicio="2024-01-15 09:00:00",
        ...     codigo_analista=789,
        ...     descricao_atendimento="Implementação de nova funcionalidade",
        ...     tipo="Implementação"
        ... )

        >>> # Inserir atendimento completo com solução
        >>> xml = await inserir_atendimentos_os(
        ...     codigo_os=456,
        ...     data_inicio="hoje 09:00",
        ...     codigo_analista=789,
        ...     descricao_atendimento="Correção de bug crítico",
        ...     tipo="Manutenção Corretiva",
        ...     data_fim="hoje 17:00",
        ...     primeiro_atendimento=True,
        ...     apresenta_solucao=True
        ... )

        >>> # Inserir primeiro atendimento de uma OS
        >>> xml = await inserir_atendimentos_os(
        ...     codigo_os=789,
        ...     data_inicio="agora",
        ...     codigo_analista=123,
        ...     descricao_atendimento="Análise inicial do problema",
        ...     tipo="Suporte Sistema",
        ...     primeiro_atendimento=True
        ... )

        >>> # Exemplo com tipo inválido (retorna erro)
        >>> xml = await inserir_atendimentos_os(
        ...     codigo_os=456,
        ...     data_inicio="2024-01-15 09:00:00",
        ...     codigo_analista=789,
        ...     descricao_atendimento="Teste",
        ...     tipo="Tipo Inexistente"  # Erro!
        ... )

    Notes:
        - A função realiza validação case-insensitive do tipo de atendimento
        - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
        - A função utiliza a constante TYPE_TO_NUMBER para mapear tipos para códigos numéricos
        - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
        - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
        - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
        - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
        - Esta função cria um novo atendimento, diferente de editar_atendimentos_os que modifica existente
    """

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Busca o tipo correto na constante TYPE_TO_NUMBER ignorando maiúsculas/minúsculas
    tipo_normalizado = next(
        # Expressão geradora que itera sobre todas as chaves do dicionário TYPE_TO_NUMBER
        (
            key
            for key in TYPE_TO_NUMBER.keys()
            # Compara a chave atual em minúsculas com o tipo recebido em minúsculas
            if str(key).lower() == str(tipo).lower()
        ),
        # Se nenhuma correspondência for encontrada, retorna None como valor padrão
        None,
    )

    # Verifica se foi encontrado um tipo válido após a busca case-insensitive
    if tipo_normalizado is None:
        # Retorna XML de erro em vez de levantar exceção
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "tipo_invalido",
                    "tipo_informado": tipo,
                    "mensagem": f"Tipo '{tipo}' não encontrado na constante TYPE_TO_NUMBER",
                    "tipos_validos": list(TYPE_TO_NUMBER.keys()),
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    tipo_final = TYPE_TO_NUMBER[tipo_normalizado]

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/inserirAtendimentosOsSigaIA/",
                json={
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim if data_fim else "",
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_normalizado),
                        "dataFim": str(data_fim),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )

@resolve_matricula
async def listar_atendimentos_avulsos(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    data_inicio: str,
    data_fim: str,
) -> str:
    """Lista todos os atendimentos avulsos registrados por um usuário em um período específico.

    Esta função busca atendimentos avulsos (não vinculados a Ordens de Serviço) realizados
    por um analista em um intervalo de datas. Os atendimentos avulsos são atividades
    registradas independentemente de OSs específicas.

    **Endpoint utilizado:** `buscarAtendimentosAvulsosSigaIA`

    **Estrutura do XML retornado:**
    ```xml
    <atendimentos_avulsos matricula="123" sistema="SIGA">
        <atendimentos_avulsos sistema="SIGA">
            <id>456</id>
            <matricula>123</matricula>
            <data_inicio>2024-01-15 09:00:00</data_inicio>
            <data_fim>2024-01-15 17:00:00</data_fim>
            <descricao>Atendimento avulso realizado</descricao>
            <tempo_gasto>480</tempo_gasto>
            <tipo>Suporte Sistema</tipo>
        </atendimentos_avulsos>
        <!-- Mais atendimentos... -->
    </atendimentos_avulsos>
    ```

    **Em caso de erro:**
    ```
    Erro ao listar atendimentos avulsos.
    ```

    Args:
        matricula (str | int | Literal["CURRENT_USER"]): Matrícula do usuário/analista cujos atendimentos
            avulsos serão listados. Se "CURRENT_USER", busca atendimentos do usuário atual
              (matrícula do .env). Defaults to "CURRENT_USER".
        data_inicio (str | Literal): Data de início do período de busca.
            Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
            Este parâmetro é obrigatório.
        data_fim (str | Literal): Data de fim do período de busca.
            Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
            Este parâmetro é obrigatório.

    Returns:
        str: XML formatado contendo:
            - Lista de atendimentos avulsos encontrados no período
            - Cada atendimento inclui: id, matrícula, datas, descrição, tempo gasto, tipo
            - Atributos do elemento raiz incluem a matrícula consultada
            - Em caso de erro na requisição: mensagem de erro simples

            O XML sempre inclui o atributo "sistema" com valor "SIGA".

    Raises:
        Não levanta exceções diretamente. Erros são capturados e retornados
        como string de erro simples.

    Examples:
        >>> # Listar atendimentos avulsos de hoje
        >>> xml = await listar_atendimentos_avulsos(
        ...     matricula=12345,
        ...     data_inicio="hoje",
        ...     data_fim="hoje"
        ... )

        >>> # Listar atendimentos avulsos da semana passada
        >>> xml = await listar_atendimentos_avulsos(
        ...     matricula=12345,
        ...     data_inicio="2024-01-08",
        ...     data_fim="2024-01-12"
        ... )

        >>> # Listar atendimentos de ontem
        >>> xml = await listar_atendimentos_avulsos(
        ...     matricula=12345,
        ...     data_inicio="ontem",
        ...     data_fim="ontem"
        ... )

        >>> # Buscar sem especificar matrícula (se suportado pela API)
        >>> xml = await listar_atendimentos_avulsos(
        ...     data_inicio="hoje",
        ...     data_fim="hoje"
        ... )

    Notes:
        - As datas são automaticamente convertidas usando converter_data_siga()
        - A função utiliza a API de atendimentos avulsos do sistema SIGA
        - Atendimentos avulsos são diferentes de atendimentos de OS (Ordens de Serviço)
        - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
        - Em caso de falha na requisição HTTP ou parsing JSON, retorna mensagem de erro simples
        - O parâmetro matricula usa o tipo Literal["CURRENT_USER"] para permitir valores opcionais
        - Os parâmetros data_inicio e data_fim são obrigatórios (não têm valor padrão)
        - A resposta da API é processada através do XMLBuilder para formatação consistente
    """
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio)

    if data_fim:
        data_fim = converter_data_siga(data_fim)

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarAtendimentosAvulsosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": data_inicio,
                "dataFim": data_fim,
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos avulsos."

@resolve_matricula
@controlar_acesso_matricula
async def listar_atendimentos_os(
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    codigo_os: str | int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> str:
    """Lista todos os atendimentos de Ordens de Serviço (OS) de um usuário com filtros opcionais.

    Esta função busca atendimentos vinculados a Ordens de Serviço realizados por um analista,
    permitindo filtrar por OS específica, período de datas, ou buscar todos os atendimentos.
    Diferente dos atendimentos avulsos, estes estão sempre associados a uma OS.

    **Endpoint utilizado:** `buscarAtendimentosOsSigaIA`

    **Estrutura do XML retornado:**
    ```xml
    <atendimentos_os matricula="123" os="456" dataIni="2024-01-15"
                     dataFim="2024-01-16" sistema="SIGA">
        <atendimentos_os sistema="SIGA">
            <id>789</id>
            <codigo_os>456</codigo_os>
            <matricula>123</matricula>
            <data_inicio>2024-01-15 09:00:00</data_inicio>
            <data_fim>2024-01-15 17:00:00</data_fim>
            <descricao>Implementação de funcionalidade</descricao>
            <tipo>Implementação</tipo>
            <tempo_gasto>480</tempo_gasto>
            <primeiro_atendimento>true</primeiro_atendimento>
            <apresenta_solucao>false</apresenta_solucao>
        </atendimentos_os>
        <!-- Mais atendimentos... -->
    </atendimentos_os>
    ```

    **Em caso de erro:**
    ```
    Erro ao listar atendimentos OS.
    ```

    Args:
        matricula (str | int | Literal["CURRENT_USER"], optional): Matrícula do usuário/analista cujos
            atendimentos de OS serão listados. Se "CURRENT_USER", busca atendimentos do usuário atual
              (matrícula do .env). Defaults to "CURRENT_USER".
        codigo_os (str | int | None, optional): Código específico da Ordem de Serviço
            para filtrar atendimentos. Se None ou não fornecido, busca atendimentos
            de todas as OSs. Defaults to None.
        data_inicio (str | Literal | None, optional): Data de início do período de busca.
            Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
            Se None, não aplica filtro de data inicial. Defaults to None.
        data_fim (str | Literal | None, optional): Data de fim do período de busca.
            Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
            Se None, não aplica filtro de data final. Defaults to None.

    Returns:
        str: XML formatado contendo:
            - Lista de atendimentos de OS encontrados com os filtros aplicados
            - Cada atendimento inclui: id, código da OS, matrícula, datas, descrição,
              tipo, tempo gasto, flags de primeiro atendimento e apresentação de solução
            - Atributos do elemento raiz incluem todos os parâmetros de filtro utilizados
            - Em caso de erro na requisição: mensagem de erro simples

            O XML sempre inclui o atributo "sistema" com valor "SIGA".

    Raises:
        Não levanta exceções diretamente. Erros são capturados e retornados
        como string de erro simples.

    Examples:
        >>> # Listar todos os atendimentos de OS de um usuário
        >>> xml = await listar_atendimentos_os(
        ...     matricula=12345
        ... )

        >>> # Listar atendimentos de uma OS específica
        >>> xml = await listar_atendimentos_os(
        ...     matricula=12345,
        ...     codigo_os=456
        ... )

        >>> # Listar atendimentos de OS de hoje
        >>> xml = await listar_atendimentos_os(
        ...     matricula=12345,
        ...     data_inicio="hoje",
        ...     data_fim="hoje"
        ... )

        >>> # Listar atendimentos de OS em período específico
        >>> xml = await listar_atendimentos_os(
        ...     matricula=12345,
        ...     data_inicio="2024-01-15",
        ...     data_fim="2024-01-20"
        ... )

        >>> # Listar atendimentos de OS específica em período
        >>> xml = await listar_atendimentos_os(
        ...     matricula=12345,
        ...     codigo_os=789,
        ...     data_inicio="ontem",
        ...     data_fim="hoje"
        ... )

        >>> # Buscar sem filtros específicos (todos os parâmetros opcionais)
        >>> xml = await listar_atendimentos_os()

    Notes:
        - As datas são automaticamente convertidas usando converter_data_siga() quando fornecidas
        - A função utiliza a API de atendimentos de OS do sistema SIGA
        - Atendimentos de OS são diferentes de atendimentos avulsos (vinculados a OSs específicas)
        - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
        - Em caso de falha na requisição HTTP ou parsing JSON, retorna mensagem de erro simples
        - Todos os parâmetros são opcionais, permitindo buscas flexíveis
        - Parâmetros None ou vazios são enviados como strings vazias para a API
        - O parâmetro matricula usa o tipo Literal["CURRENT_USER"] para permitir valores verdadeiramente opcionais
        - A resposta da API é processada através do XMLBuilder para formatação consistente
        - Os atributos do XML de resposta refletem exatamente os filtros aplicados na busca
    """

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarAtendimentosOsSigaIA/",
            json={
                "matricula": str(matricula),
                "os": str(codigo_os) if codigo_os else "",
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_os",
                    item_element_name="atendimentos_os",
                    root_attributes={
                        "matricula": str(matricula),
                        "os": str(codigo_os) if codigo_os else "",
                        "dataIni": str(data_inicio) if data_inicio else "",
                        "dataFim": str(data_fim) if data_fim else "",
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos OS."

@resolve_matricula
@controlar_acesso_matricula
async def listar_horas_trabalhadas(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    data_inicio: str,
    data_fim: str,
) -> str:
    """Calcula e lista o total de horas trabalhadas de um analista em um período específico.

    Esta função consolida as horas trabalhadas de um analista considerando tanto os
    atendimentos de Ordens de Serviço (OS) quanto os atendimentos avulsos realizados
    no período especificado. Fornece um resumo completo da produtividade do analista.

    **Endpoint utilizado:** `buscarTotalHorasTrabalhadasSigaIA`

    **Estrutura do XML retornado:**
    ```xml
    <atendimentos_avulsos matricula="123" sistema="SIGA">
        <atendimentos_avulsos sistema="SIGA">
            <total_horas_os>32.5</total_horas_os>
            <total_horas_avulsos>8.0</total_horas_avulsos>
            <total_horas_geral>40.5</total_horas_geral>
            <periodo_inicio>2024-01-15</periodo_inicio>
            <periodo_fim>2024-01-19</periodo_fim>
            <dias_trabalhados>5</dias_trabalhados>
            <media_horas_dia>8.1</media_horas_dia>
        </atendimentos_avulsos>
    </atendimentos_avulsos>
    ```

    **Em caso de erro:**
    ```
    Erro ao listar horas trabalhadas.
    ```

    Args:
        matricula (str | int | Literal["CURRENT_USER"], optional): Matrícula do analista cujas horas
            trabalhadas serão calculadas. Se "CURRENT_USER", calcula para o usuário atual
              (matrícula do .env). Defaults to "CURRENT_USER".
        data_inicio (str | Literal): Data de início do período para cálculo das horas.
            Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
            Este parâmetro é obrigatório.
        data_fim (str | Literal): Data de fim do período para cálculo das horas.
            Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
            Este parâmetro é obrigatório.

    Returns:
        str: XML formatado contendo:
            - Total de horas trabalhadas em atendimentos de OS
            - Total de horas trabalhadas em atendimentos avulsos
            - Total geral de horas trabalhadas no período
            - Informações do período consultado (início e fim)
            - Estatísticas adicionais como dias trabalhados e média por dia
            - Atributos do elemento raiz incluem a matrícula consultada
            - Em caso de erro na requisição: mensagem de erro simples

            O XML sempre inclui o atributo "sistema" com valor "SIGA".

    Raises:
        Não levanta exceções diretamente. Erros são capturados e retornados
        como string de erro simples.

    Examples:
        >>> # Calcular horas trabalhadas de hoje
        >>> xml = await listar_horas_trabalhadas(
        ...     matricula=12345,
        ...     data_inicio="hoje",
        ...     data_fim="hoje"
        ... )

        >>> # Calcular horas trabalhadas da semana
        >>> xml = await listar_horas_trabalhadas(
        ...     matricula=12345,
        ...     data_inicio="2024-01-15",
        ...     data_fim="2024-01-19"
        ... )

        >>> # Calcular horas trabalhadas de ontem
        >>> xml = await listar_horas_trabalhadas(
        ...     matricula=12345,
        ...     data_inicio="ontem",
        ...     data_fim="ontem"
        ... )

        >>> # Calcular horas trabalhadas do mês
        >>> xml = await listar_horas_trabalhadas(
        ...     matricula=12345,
        ...     data_inicio="2024-01-01",
        ...     data_fim="2024-01-31"
        ... )

        >>> # Buscar sem especificar matrícula (se suportado pela API)
        >>> xml = await listar_horas_trabalhadas(
        ...     data_inicio="hoje",
        ...     data_fim="hoje"
        ... )

    Notes:
        - As datas são automaticamente convertidas usando converter_data_siga() quando fornecidas
        - A função utiliza a API de cálculo de horas trabalhadas do sistema SIGA
        - O cálculo inclui tanto atendimentos de OS quanto atendimentos avulsos
        - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
        - Em caso de falha na requisição HTTP ou parsing JSON, retorna mensagem de erro simples
        - O parâmetro matricula usa o tipo Literal["CURRENT_USER"] para permitir valores opcionais
        - Os parâmetros data_inicio e data_fim são obrigatórios (não têm valor padrão)
        - A resposta da API é processada através do XMLBuilder para formatação consistente
        - Esta função é útil para relatórios de produtividade e controle de horas
        - O resultado consolida informações de múltiplas fontes (OS e atendimentos avulsos)
        - Pode incluir estatísticas adicionais como média de horas por dia trabalhado
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarTotalHorasTrabalhadasSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                resultado = json["result"]

                retorno = XMLBuilder().build_xml(
                    data=resultado,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar horas trabalhadas."
