import calendar
import re
from datetime import datetime, timedelta
from os import getenv

import aiohttp
import ujson


from siga_mcp.constants import (
    DIAS_SEMANA_PT,
    MESES_PT,
    NUMEROS_EXTENSO,
    PERIODOS_DIA,
    TEMPO_FUTURO,
    TEMPO_PASSADO,
    MCP_TRANSPORT,
    MATRICULA_USUARIO_ATUAL,
    MATRICULAS_LIBERADAS
)
from siga_mcp.xml_builder import XMLBuilder


def converter_data_siga(
    data_input: str,
    manter_horas: bool = False,
) -> str:
    """
    Converte uma string de data em linguagem natural para o formato DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS.

    Suporta uma ampla gama de formatos incluindo:

    DATAS BÁSICAS:
    - Datas no formato DD/MM/YYYY, DD/MM/YYYY HH:MM:SS
    - Formatos ISO: YYYY-MM-DD, YYYY/MM/DD, YYYY-MM-DDTHH:MM, YYYY-MM-DDTHH:MM:SS
    - Formato americano: MM/DD/YYYY
    - Outros separadores: DD-MM-YYYY, DD.MM.YYYY
    - Datas curtas: DD/MM, MM/DD (assumindo ano atual)
    - Números sozinhos: "23", "15" (assumindo dia do mês atual)

    REFERÊNCIAS RELATIVAS:
    - 'hoje', 'ontem', 'amanhã', 'agora'
    - 'hoje-X' onde X são dias (ex: 'hoje-5')
    - 'hoje/ontem/amanhã HH:MM' com hora específica

    LINGUAGEM NATURAL AVANÇADA:
    - 'primeiro dia do mês', 'último dia do mês', 'meio do mês'
    - 'primeiro dia do mês passado', 'último dia do ano', 'início do ano'
    - 'mês passado', 'mês que vem', 'ano passado', 'ano que vem'
    - 'semana passada', 'semana que vem', 'próxima semana', 'semana retrasada'
    - 'daqui a X dias/semanas/meses/anos' (números e por extenso)
    - 'há X dias/semanas/meses/anos atrás' (números e por extenso)
    - Dias da semana: 'segunda-feira', 'terça que vem', 'sexta passada', '2ª feira'
    - Meses por nome: 'janeiro de 2025', 'dezembro passado', 'em março'
    - Expressões como 'início do mês', 'fim do ano', 'meio do mês'
    - Períodos: 'início da semana', 'meio da semana', 'fim da semana'
    - Trimestres: 'primeiro trimestre', 'último trimestre', 'trimestre passado'

    CASOS ESPECIAIS:
    - 'anteontem', 'depois de amanhã', 'outro dia'
    - 'esta semana', 'este mês', 'este ano', 'nesta segunda'
    - 'na próxima segunda', 'segunda passada', 'fim de semana'
    - Números ordinais: 'primeiro de janeiro', 'quinze de março'
    - Períodos do dia: 'hoje de manhã', 'ontem à noite', 'amanhã de tarde'
    - Expressões coloquiais: 'esses dias', 'recentemente', 'há pouco tempo'

    Args:
        data_input: String com a data a ser convertida
        manter_horas: Se True, mantém ou adiciona informações de hora

    Returns:
        String no formato DD/MM/YYYY ou DD/MM/YYYY HH:MM:SS

    Raises:
        ValueError: Se o formato da data for inválido ou não reconhecido
    """

    # Define a data de hoje como referência
    # Usar timezone local do Brasil se possível
    try:
        from zoneinfo import ZoneInfo

        hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).replace(tzinfo=None)
    except ImportError:
        # Fallback para datetime normal se zoneinfo não disponível
        hoje = datetime.now()

    # Remove espaços extras e normaliza
    data_input = data_input.strip().lower()
    data_input = re.sub(r"\s+", " ", data_input)  # Remove espaços duplos

    # === NÚMEROS SOZINHOS (NOVO CASO) ===
    # Verifica se é apenas um número (dia do mês atual)
    padrao_numero_sozinho = re.match(r"^(\d{1,2})$", data_input.strip())
    if padrao_numero_sozinho:
        dia = int(padrao_numero_sozinho.group(1))

        # Validar se o dia é válido (1-31)
        if dia < 1 or dia > 31:
            raise ValueError(f"Dia inválido: {dia}. Deve estar entre 1 e 31.")

        try:
            # Tentar criar a data no mês atual
            data_resultado = datetime(hoje.year, hoje.month, dia)

            # Se a data já passou neste mês, assumir próximo mês
            if data_resultado < hoje.replace(hour=0, minute=0, second=0, microsecond=0):
                if hoje.month == 12:
                    data_resultado = datetime(hoje.year + 1, 1, dia)
                else:
                    try:
                        data_resultado = datetime(hoje.year, hoje.month + 1, dia)
                    except ValueError:
                        # Se o dia não existe no próximo mês, usar o último dia válido
                        import calendar

                        ultimo_dia = calendar.monthrange(hoje.year, hoje.month + 1)[1]
                        data_resultado = datetime(
                            hoje.year, hoje.month + 1, min(dia, ultimo_dia)
                        )

            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )

        except ValueError:
            # Se o dia não existe no mês atual, tentar próximo mês
            import calendar

            if hoje.month == 12:
                # Próximo ano, janeiro
                ultimo_dia_janeiro = calendar.monthrange(hoje.year + 1, 1)[1]
                if dia <= ultimo_dia_janeiro:
                    data_resultado = datetime(hoje.year + 1, 1, dia)
                else:
                    data_resultado = datetime(hoje.year + 1, 1, ultimo_dia_janeiro)
            else:
                # Próximo mês
                ultimo_dia_proximo_mes = calendar.monthrange(hoje.year, hoje.month + 1)[
                    1
                ]
                if dia <= ultimo_dia_proximo_mes:
                    data_resultado = datetime(hoje.year, hoje.month + 1, dia)
                else:
                    data_resultado = datetime(
                        hoje.year, hoje.month + 1, ultimo_dia_proximo_mes
                    )

            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )

    # === CASOS ESPECIAIS PRIMEIRO ===

    # Caso especial: agora
    if data_input == "agora":
        if manter_horas:
            return hoje.strftime("%d/%m/%Y %H:%M:%S")
        else:
            return hoje.strftime("%d/%m/%Y")

    # === PROCESSAMENTO DE LINGUAGEM NATURAL ===
    try:
        # Tentar casos específicos em português primeiro
        resultado = _processar_linguagem_natural_pt(data_input, hoje, manter_horas)
        if resultado:
            return resultado
    except Exception:
        pass

    # === FALLBACK PARA CASOS ORIGINAIS ===
    try:
        return _processar_casos_originais(data_input, hoje, manter_horas)
    except Exception:
        pass

    # === ÚLTIMO RECURSO: DATEPARSER ===
    try:
        import dateparser

        # Usar dateparser com configurações básicas
        data_parseada = dateparser.parse(
            data_input,
            languages=["pt"],
            locales=["pt-BR"],
            settings={"RELATIVE_BASE": hoje},
        )

        if data_parseada:
            if manter_horas:
                return data_parseada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_parseada.strftime("%d/%m/%Y")

    except ImportError:
        # Se dateparser não estiver disponível, continua sem ele
        pass
    except Exception:
        pass

    # Se chegou até aqui, formato não reconhecido
    raise ValueError(f"Formato de data não reconhecido: {data_input}")


def _processar_linguagem_natural_pt(
    data_input: str, hoje: datetime, manter_horas: bool
) -> str | None:
    """Processa expressões em linguagem natural em português."""

    # === CASOS ESPECIAIS PRIMEIRO (antes de processar meses/números) ===

    # Expressões coloquiais que podem conflitar com outras palavras
    if "outro dia" in data_input:
        # Alguns dias atrás (não uma data futura)
        data_resultado = hoje - timedelta(days=3)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["esses dias", "recentemente", "ha pouco tempo", "há pouco tempo"]
    ):
        # Aproximadamente uma semana atrás
        data_resultado = hoje - timedelta(days=7)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )
    if data_input == "hoje":
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input == "ontem":
        ontem = hoje - timedelta(days=1)
        return ontem.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input in ["amanha", "amanhã"]:
        amanha = hoje + timedelta(days=1)
        return amanha.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input == "anteontem":
        anteontem = hoje - timedelta(days=2)
        return anteontem.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if data_input in ["depois de amanha", "depois de amanhã"]:
        depois_amanha = hoje + timedelta(days=2)
        return depois_amanha.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === SEMANA RETRASADA ===
    if "semana retrasada" in data_input:
        data_resultado = hoje - timedelta(weeks=2)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === PERÍODOS DA SEMANA ===
    if "inicio da semana" in data_input or "início da semana" in data_input:
        # Segunda-feira desta semana
        dias_ate_segunda = -hoje.weekday()  # 0 = segunda
        if dias_ate_segunda > 0:  # Se já passou a segunda, próxima segunda
            dias_ate_segunda -= 7
        data_resultado = hoje + timedelta(days=dias_ate_segunda)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if "meio da semana" in data_input:
        # Quarta-feira desta semana
        dias_ate_quarta = 2 - hoje.weekday()  # 2 = quarta
        if dias_ate_quarta < -2:  # Se já passou muito da quarta, próxima quarta
            dias_ate_quarta += 7
        data_resultado = hoje + timedelta(days=dias_ate_quarta)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in [
            "fim da semana",
            "final da semana",
            "fim de semana",
            "fds",
            "fim desta semana",
            "final desta semana",
        ]
    ):
        # Sexta-feira desta semana ou próxima se já passou
        dias_ate_sexta = 4 - hoje.weekday()  # 4 = sexta
        if dias_ate_sexta < 0:  # Se já passou sexta, próxima sexta
            dias_ate_sexta += 7
        data_resultado = hoje + timedelta(days=dias_ate_sexta)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === EXPRESSÕES COM "ESTA/ESTE/DESTA/DESTE" ===
    if any(
        termo in data_input for termo in ["esta semana", "nesta semana", "desta semana"]
    ):
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if any(
        termo in data_input
        for termo in [
            "este mes",
            "este mês",
            "neste mes",
            "neste mês",
            "deste mes",
            "deste mês",
        ]
    ):
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    if any(termo in data_input for termo in ["este ano", "neste ano", "deste ano"]):
        return hoje.strftime("%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y")

    # Variações com "desta" para períodos
    if any(
        termo in data_input for termo in ["inicio desta semana", "início desta semana"]
    ):
        dias_ate_segunda = -hoje.weekday()  # 0 = segunda
        if dias_ate_segunda > 0:  # Se já passou a segunda, próxima segunda
            dias_ate_segunda -= 7
        data_resultado = hoje + timedelta(days=dias_ate_segunda)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(termo in data_input for termo in ["meio desta semana"]):
        dias_ate_quarta = 2 - hoje.weekday()  # 2 = quarta
        if dias_ate_quarta < -2:  # Se já passou muito da quarta, próxima quarta
            dias_ate_quarta += 7
        data_resultado = hoje + timedelta(days=dias_ate_quarta)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === CASOS BÁSICOS ===

    # === PERÍODOS DO DIA (verificar primeiro as expressões compostas) ===
    # Detectar frases como "hoje de manhã", "ontem à noite", etc.
    periodos_detectados = []
    for periodo in PERIODOS_DIA.keys():
        if periodo in data_input:
            periodos_detectados.append(periodo)

    # Ordenar por tamanho (mais específico primeiro)
    periodos_detectados.sort(key=len, reverse=True)

    if periodos_detectados:
        periodo = periodos_detectados[0]  # Pegar o mais específico
        hora_padrao = PERIODOS_DIA[periodo]

        # Extrair a referência de tempo (hoje, ontem, amanhã)
        if "hoje" in data_input:
            data_base = hoje
        elif "ontem" in data_input:
            data_base = hoje - timedelta(days=1)
        elif "amanha" in data_input or "amanhã" in data_input:
            data_base = hoje + timedelta(days=1)
        elif "anteontem" in data_input:
            data_base = hoje - timedelta(days=2)
        else:
            data_base = hoje  # Default para hoje

        try:
            data_resultado = data_base.replace(hour=hora_padrao, minute=0, second=0)
            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )
        except ValueError:
            pass

    # === TRIMESTRES ===
    if "primeiro trimestre" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            if hoje.month <= 3:  # Ainda no primeiro trimestre, pegar o do ano passado
                data_resultado = datetime(hoje.year - 1, 1, 1)
            else:
                data_resultado = datetime(hoje.year, 1, 1)
        else:
            data_resultado = datetime(hoje.year, 1, 1)

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "segundo trimestre" in data_input:
        ano = hoje.year
        if any(palavra in data_input for palavra in TEMPO_PASSADO) and hoje.month <= 6:
            ano -= 1
        data_resultado = datetime(ano, 4, 1)
        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "terceiro trimestre" in data_input:
        ano = hoje.year
        if any(palavra in data_input for palavra in TEMPO_PASSADO) and hoje.month <= 9:
            ano -= 1
        data_resultado = datetime(ano, 7, 1)
        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["quarto trimestre", "último trimestre", "ultimo trimestre"]
    ):
        ano = hoje.year
        if any(palavra in data_input for palavra in TEMPO_PASSADO) and hoje.month <= 12:
            ano -= 1
        data_resultado = datetime(ano, 10, 1)
        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "trimestre passado" in data_input:
        if hoje.month <= 3:
            data_resultado = datetime(hoje.year - 1, 10, 1)  # Q4 do ano anterior
        elif hoje.month <= 6:
            data_resultado = datetime(hoje.year, 1, 1)  # Q1 deste ano
        elif hoje.month <= 9:
            data_resultado = datetime(hoje.year, 4, 1)  # Q2 deste ano
        else:
            data_resultado = datetime(hoje.year, 7, 1)  # Q3 deste ano

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    # === HOJE/ONTEM/AMANHÃ COM HORA ===
    for palavra in ["hoje", "ontem", "amanha", "amanhã"]:
        padrao = re.match(rf"{palavra}\s+(\d{{1,2}}):(\d{{1,2}})", data_input)
        if padrao:
            hora, minuto = padrao.groups()
            try:
                if palavra == "hoje":
                    data_resultado = hoje
                elif palavra == "ontem":
                    data_resultado = hoje - timedelta(days=1)
                else:  # amanhã
                    data_resultado = hoje + timedelta(days=1)

                data_resultado = data_resultado.replace(
                    hour=int(hora), minute=int(minuto), second=0
                )
                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )
            except ValueError:
                continue

    # === HOJE-X ===
    padrao_hoje_menos = re.match(r"hoje-(\d+)(?:\s+(\d{1,2}):(\d{1,2}))?", data_input)
    if padrao_hoje_menos:
        dias_subtrair = int(padrao_hoje_menos.group(1))
        hora = padrao_hoje_menos.group(2)
        minuto = padrao_hoje_menos.group(3)

        data_resultado = hoje - timedelta(days=dias_subtrair)

        if hora and minuto:
            try:
                data_resultado = data_resultado.replace(
                    hour=int(hora), minute=int(minuto), second=0
                )
            except ValueError:
                pass

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === EXPRESSÕES COM "DAQUI A" ===
    padrao_daqui = re.match(
        r"daqui\s+a?\s*(\d+)\s*(dia|dias|semana|semanas|mes|mês|meses|ano|anos)",
        data_input,
    )
    if padrao_daqui:
        quantidade = int(padrao_daqui.group(1))
        unidade = padrao_daqui.group(2)

        if unidade in ["dia", "dias"]:
            data_resultado = hoje + timedelta(days=quantidade)
        elif unidade in ["semana", "semanas"]:
            data_resultado = hoje + timedelta(weeks=quantidade)
        elif unidade in ["mes", "mês", "meses"]:
            # Aproximação: assumir 30 dias por mês
            data_resultado = hoje + timedelta(days=quantidade * 30)
        elif unidade in ["ano", "anos"]:
            # Aproximação: assumir 365 dias por ano
            data_resultado = hoje + timedelta(days=quantidade * 365)
        else:
            raise ValueError("Data inválida")

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === EXPRESSÕES COM "HÁ" ===
    padrao_ha = re.match(
        r"h[aá]\s+(\d+)\s*(dia|dias|semana|semanas|mes|mês|meses|ano|anos)(\s+atr[aá]s)?",
        data_input,
    )
    if padrao_ha:
        quantidade = int(padrao_ha.group(1))
        unidade = padrao_ha.group(2)

        if unidade in ["dia", "dias"]:
            data_resultado = hoje - timedelta(days=quantidade)
        elif unidade in ["semana", "semanas"]:
            data_resultado = hoje - timedelta(weeks=quantidade)
        elif unidade in ["mes", "mês", "meses"]:
            data_resultado = hoje - timedelta(days=quantidade * 30)
        elif unidade in ["ano", "anos"]:
            data_resultado = hoje - timedelta(days=quantidade * 365)
        else:
            raise ValueError("Data inválida")

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === ÚLTIMO/PRIMEIRO DIA DO ANO ===
    if "ultimo dia do ano" in data_input or "último dia do ano" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            data_resultado = datetime(hoje.year - 1, 12, 31)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            data_resultado = datetime(hoje.year + 1, 12, 31)
        else:
            data_resultado = datetime(hoje.year, 12, 31)

        return data_resultado.strftime(
            "%d/%m/%Y 23:59:59" if manter_horas else "%d/%m/%Y"
        )

    if (
        "primeiro dia do ano" in data_input
        or "inicio do ano" in data_input
        or "início do ano" in data_input
    ):
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            data_resultado = datetime(hoje.year - 1, 1, 1)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            data_resultado = datetime(hoje.year + 1, 1, 1)
        else:
            data_resultado = datetime(hoje.year, 1, 1)

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    # === MEIO DO MÊS ===
    if "meio do mes" in data_input or "meio do mês" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            if hoje.month == 1:
                data_resultado = datetime(hoje.year - 1, 12, 15)
            else:
                data_resultado = datetime(hoje.year, hoje.month - 1, 15)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            if hoje.month == 12:
                data_resultado = datetime(hoje.year + 1, 1, 15)
            else:
                data_resultado = datetime(hoje.year, hoje.month + 1, 15)
        else:
            data_resultado = datetime(hoje.year, hoje.month, 15)

        return data_resultado.strftime(
            "%d/%m/%Y 12:00:00" if manter_horas else "%d/%m/%Y"
        )

    # === INÍCIO/FIM DO MÊS ===
    if "inicio do mes" in data_input or "início do mês" in data_input:
        return _processar_linguagem_natural_pt(
            "primeiro dia do mês"
            + (
                " passado"
                if any(p in data_input for p in TEMPO_PASSADO)
                else " que vem"
                if any(p in data_input for p in TEMPO_FUTURO)
                else ""
            ),
            hoje,
            manter_horas,
        )

    if "fim do mes" in data_input or "fim do mês" in data_input:
        return _processar_linguagem_natural_pt(
            "último dia do mês"
            + (
                " passado"
                if any(p in data_input for p in TEMPO_PASSADO)
                else " que vem"
                if any(p in data_input for p in TEMPO_FUTURO)
                else ""
            ),
            hoje,
            manter_horas,
        )

    # === NÚMEROS POR EXTENSO ===
    for numero_str, numero_val in NUMEROS_EXTENSO.items():
        # "dois dias atrás", "três semanas", etc.
        padrao_extenso = re.search(
            rf"{numero_str}\s+(dia|dias|semana|semanas|mes|mês|meses|ano|anos)(?:\s+atr[aá]s)?",
            data_input,
        )
        if padrao_extenso:
            unidade = padrao_extenso.group(1)

            # Determinar se é passado ou futuro
            eh_passado = (
                "atrás" in data_input
                or "atras" in data_input
                or any(p in data_input for p in TEMPO_PASSADO)
            )

            delta = None
            if unidade in ["dia", "dias"]:
                delta = timedelta(days=numero_val)
            elif unidade in ["semana", "semanas"]:
                delta = timedelta(weeks=numero_val)
            elif unidade in ["mes", "mês", "meses"]:
                delta = timedelta(days=numero_val * 30)
            elif unidade in ["ano", "anos"]:
                delta = timedelta(days=numero_val * 365)

            if delta is not None:
                if eh_passado:
                    data_resultado = hoje - delta
                else:
                    data_resultado = hoje + delta

                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )
    if "primeiro dia do mes" in data_input or "primeiro dia do mês" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            # Mês passado
            if hoje.month == 1:
                data_resultado = datetime(hoje.year - 1, 12, 1)
            else:
                data_resultado = datetime(hoje.year, hoje.month - 1, 1)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            # Próximo mês
            if hoje.month == 12:
                data_resultado = datetime(hoje.year + 1, 1, 1)
            else:
                data_resultado = datetime(hoje.year, hoje.month + 1, 1)
        else:
            # Mês atual
            data_resultado = datetime(hoje.year, hoje.month, 1)

        return data_resultado.strftime(
            "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
        )

    if "ultimo dia do mes" in data_input or "último dia do mês" in data_input:
        if any(palavra in data_input for palavra in TEMPO_PASSADO):
            # Mês passado
            if hoje.month == 1:
                ultimo_dia = calendar.monthrange(hoje.year - 1, 12)[1]
                data_resultado = datetime(hoje.year - 1, 12, ultimo_dia)
            else:
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month - 1)[1]
                data_resultado = datetime(hoje.year, hoje.month - 1, ultimo_dia)
        elif any(palavra in data_input for palavra in TEMPO_FUTURO):
            # Próximo mês
            if hoje.month == 12:
                ultimo_dia = calendar.monthrange(hoje.year + 1, 1)[1]
                data_resultado = datetime(hoje.year + 1, 1, ultimo_dia)
            else:
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month + 1)[1]
                data_resultado = datetime(hoje.year, hoje.month + 1, ultimo_dia)
        else:
            # Mês atual
            ultimo_dia = calendar.monthrange(hoje.year, hoje.month)[1]
            data_resultado = datetime(hoje.year, hoje.month, ultimo_dia)

        return data_resultado.strftime(
            "%d/%m/%Y 23:59:59" if manter_horas else "%d/%m/%Y"
        )

    # === MÊS PASSADO/PRÓXIMO ===
    if "mes passado" in data_input or "mês passado" in data_input:
        if hoje.month == 1:
            data_resultado = datetime(hoje.year - 1, 12, hoje.day)
        else:
            # Ajustar o dia se necessário
            try:
                data_resultado = datetime(hoje.year, hoje.month - 1, hoje.day)
            except ValueError:
                # Dia não existe no mês anterior (ex: 31 para fevereiro)
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month - 1)[1]
                data_resultado = datetime(hoje.year, hoje.month - 1, ultimo_dia)

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["mes que vem", "mês que vem", "proximo mes", "próximo mês"]
    ):
        if hoje.month == 12:
            data_resultado = datetime(hoje.year + 1, 1, hoje.day)
        else:
            try:
                data_resultado = datetime(hoje.year, hoje.month + 1, hoje.day)
            except ValueError:
                ultimo_dia = calendar.monthrange(hoje.year, hoje.month + 1)[1]
                data_resultado = datetime(hoje.year, hoje.month + 1, ultimo_dia)

        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === SEMANA PASSADA/PRÓXIMA ===
    if "semana passada" in data_input:
        data_resultado = hoje - timedelta(weeks=1)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input
        for termo in ["semana que vem", "proxima semana", "próxima semana"]
    ):
        data_resultado = hoje + timedelta(weeks=1)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === DIAS DA SEMANA COM VARIAÇÕES ===
    # Mapeamento adicional para abreviações numéricas
    dias_numericos = {
        "2ª feira": 0,
        "2a feira": 0,
        "2 feira": 0,
        "3ª feira": 1,
        "3a feira": 1,
        "3 feira": 1,
        "4ª feira": 2,
        "4a feira": 2,
        "4 feira": 2,
        "5ª feira": 3,
        "5a feira": 3,
        "5 feira": 3,
        "6ª feira": 4,
        "6a feira": 4,
        "6 feira": 4,
        "sab": 5,
        "sabado": 5,
        "dom": 6,
    }

    # Combinar ambos os dicionários
    todos_dias = {**DIAS_SEMANA_PT, **dias_numericos}

    # === DIAS DA SEMANA ===
    for dia_nome, dia_num in todos_dias.items():
        if dia_nome in data_input:
            dias_ate_dia = (dia_num - hoje.weekday()) % 7

            # Determinar se é passado ou futuro
            if any(palavra in data_input for palavra in TEMPO_PASSADO + ["passada"]):
                if dias_ate_dia == 0:
                    dias_ate_dia = -7  # Semana passada
                else:
                    dias_ate_dia = dias_ate_dia - 7
            elif any(
                palavra in data_input
                for palavra in TEMPO_FUTURO + ["que vem", "proxima", "próxima"]
            ):
                if dias_ate_dia == 0:
                    dias_ate_dia = 7  # Próxima semana
            elif any(
                termo in data_input
                for termo in ["na proxima", "na próxima", "nesta", "na", "no"]
            ):
                if dias_ate_dia == 0:
                    dias_ate_dia = 7  # Próxima ocorrência
            else:
                # Se for hoje, manter hoje; senão, assumir próxima ocorrência
                if dias_ate_dia == 0 and dia_nome not in data_input:
                    dias_ate_dia = 7

            data_resultado = hoje + timedelta(days=dias_ate_dia)
            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )

    # === EXPRESSÕES COM "EM" ===
    if data_input.startswith("em "):
        resto = data_input[3:]  # Remove "em "

        # "em janeiro", "em dezembro"
        for mes_nome, mes_num in MESES_PT.items():
            if resto == mes_nome or resto.startswith(mes_nome + " "):
                # Extrair ano se presente
                padrao_ano = re.search(r"(\d{4})", resto)
                ano = int(padrao_ano.group(1)) if padrao_ano else hoje.year

                # Se é um mês futuro neste ano ou igual ao atual, usar este ano
                # Se é um mês passado, pode ser que se refira ao próximo ano
                if mes_num < hoje.month and not padrao_ano:
                    ano = hoje.year + 1

                try:
                    data_resultado = datetime(ano, mes_num, 1)
                    return data_resultado.strftime(
                        "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
                    )
                except ValueError:
                    continue

        # "em 2025", "em 2024"
        padrao_ano_so = re.match(r"(\d{4})$", resto)
        if padrao_ano_so:
            ano = int(padrao_ano_so.group(1))
            data_resultado = datetime(ano, 1, 1)
            return data_resultado.strftime(
                "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
            )

    # === TRATAMENTO DE ERROS COMUNS DE DIGITAÇÃO ===
    # Normalizar acentos e espaços comuns
    data_normalizada = data_input
    data_normalizada = data_normalizada.replace("terca", "terça")
    data_normalizada = data_normalizada.replace("proximo", "próximo")
    data_normalizada = data_normalizada.replace("mes", "mês")
    data_normalizada = data_normalizada.replace("apos", "após")
    data_normalizada = data_normalizada.replace("tres", "três")

    # Se normalizou algo, tentar novamente
    if data_normalizada != data_input:
        try:
            return _processar_linguagem_natural_pt(data_normalizada, hoje, manter_horas)
        except Exception:
            pass

    # === CASOS COMPOSTOS MAIS COMPLEXOS ===
    # "segunda da semana que vem"
    if (
        "da semana que vem" in data_input
        or "da proxima semana" in data_input
        or "da próxima semana" in data_input
    ):
        for dia_nome, dia_num in todos_dias.items():
            if dia_nome in data_input:
                # Próxima semana + dia específico
                proxima_semana = hoje + timedelta(weeks=1)
                inicio_semana = proxima_semana - timedelta(
                    days=proxima_semana.weekday()
                )
                data_resultado = inicio_semana + timedelta(days=dia_num)
                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )

    # "sexta da semana passada"
    if "da semana passada" in data_input:
        for dia_nome, dia_num in todos_dias.items():
            if dia_nome in data_input:
                # Semana passada + dia específico
                semana_passada = hoje - timedelta(weeks=1)
                inicio_semana = semana_passada - timedelta(
                    days=semana_passada.weekday()
                )
                data_resultado = inicio_semana + timedelta(days=dia_num)
                return data_resultado.strftime(
                    "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
                )

    # === EXPRESSÕES COM NÚMEROS ORDINAIS MAIS EXTENSOS ===
    ordinais = {
        "primeiro": 1,
        "segunda": 2,
        "terceiro": 3,
        "quarto": 4,
        "quinto": 5,
        "sexto": 6,
        "sétimo": 7,
        "setimo": 7,
        "oitavo": 8,
        "nono": 9,
        "décimo": 10,
        "decimo": 10,
        "vigésimo": 20,
        "vigesimo": 20,
        "trigésimo": 30,
        "trigesimo": 30,
    }

    for ordinal, numero in ordinais.items():
        padrao_ordinal = re.search(
            rf"{ordinal}(?:\s+primeiro)?\s+de\s+(\w+)", data_input
        )
        if padrao_ordinal:
            mes_nome = padrao_ordinal.group(1)
            if mes_nome in MESES_PT:
                try:
                    data_resultado = datetime(hoje.year, MESES_PT[mes_nome], numero)
                    return data_resultado.strftime(
                        "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
                    )
                except ValueError:
                    continue
    for dia_nome, dia_num in DIAS_SEMANA_PT.items():
        if dia_nome in data_input:
            dias_ate_dia = (dia_num - hoje.weekday()) % 7

            # Determinar se é passado ou futuro
            if any(palavra in data_input for palavra in TEMPO_PASSADO):
                if dias_ate_dia == 0:
                    dias_ate_dia = -7  # Semana passada
                else:
                    dias_ate_dia = dias_ate_dia - 7
            elif any(palavra in data_input for palavra in TEMPO_FUTURO + ["que vem"]):
                if dias_ate_dia == 0:
                    dias_ate_dia = 7  # Próxima semana
            else:
                # Se for hoje, manter hoje; senão, assumir próxima ocorrência
                if dias_ate_dia == 0 and dia_nome not in data_input:
                    dias_ate_dia = 7

            data_resultado = hoje + timedelta(days=dias_ate_dia)
            return data_resultado.strftime(
                "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
            )

    # === ANO PASSADO/PRÓXIMO ===
    if "ano passado" in data_input:
        data_resultado = datetime(hoje.year - 1, hoje.month, hoje.day)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    if any(
        termo in data_input for termo in ["ano que vem", "proximo ano", "próximo ano"]
    ):
        data_resultado = datetime(hoje.year + 1, hoje.month, hoje.day)
        return data_resultado.strftime(
            "%d/%m/%Y %H:%M:%S" if manter_horas else "%d/%m/%Y"
        )

    # === MESES POR NOME ===
    for mes_nome, mes_num in MESES_PT.items():
        if mes_nome in data_input:
            # Extrair ano se presente
            padrao_ano = re.search(r"(\d{4})", data_input)
            ano = int(padrao_ano.group(1)) if padrao_ano else hoje.year

            # Extrair dia se presente
            padrao_dia = re.search(r"(\d{1,2})(?:\s+de\s+)?" + mes_nome, data_input)
            dia = int(padrao_dia.group(1)) if padrao_dia else 1

            # Verificar se é passado ou futuro
            if (
                any(palavra in data_input for palavra in TEMPO_PASSADO)
                and not padrao_ano
            ):
                if mes_num > hoje.month:
                    ano = hoje.year - 1
                elif mes_num == hoje.month and dia <= hoje.day:
                    ano = hoje.year - 1
            elif (
                any(palavra in data_input for palavra in TEMPO_FUTURO)
                and not padrao_ano
            ):
                if mes_num < hoje.month:
                    ano = hoje.year + 1
                elif mes_num == hoje.month and dia <= hoje.day:
                    ano = hoje.year + 1

            try:
                data_resultado = datetime(ano, mes_num, dia)
                return data_resultado.strftime(
                    "%d/%m/%Y 00:00:00" if manter_horas else "%d/%m/%Y"
                )
            except ValueError:
                continue

    return None


def _processar_casos_originais(
    data_input: str, hoje: datetime, manter_horas: bool
) -> str:
    """Processa os casos da função original."""

    # Caso especial: Formato ISO 8601 com T: YYYY-MM-DDTHH:MM:SS ou YYYY-MM-DDTHH:MM
    padrao_iso_t = re.match(
        r"(\d{4})-(\d{1,2})-(\d{1,2})t(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", data_input
    )
    if padrao_iso_t:
        ano, mes, dia, hora, minuto, segundo = padrao_iso_t.groups()
        segundo = segundo or "00"

        try:
            data_validada = datetime(
                int(ano), int(mes), int(dia), int(hora), int(minuto), int(segundo)
            )
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data/hora inválida: {data_input}")

    # Caso 4: Data com horas no formato DD/MM/YYYY HH:MM:SS ou DD/MM/YYYY HH:MM
    padrao_data_com_horas = re.match(
        r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", data_input
    )
    if padrao_data_com_horas:
        dia, mes, ano, hora, minuto, segundo = padrao_data_com_horas.groups()
        segundo = segundo or "00"

        try:
            data_validada = datetime(
                int(ano), int(mes), int(dia), int(hora), int(minuto), int(segundo)
            )
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data/hora inválida: {data_input}")

    # Caso 5: Formato ISO com hora: YYYY-MM-DD HH:MM:SS ou YYYY-MM-DD HH:MM
    padrao_iso_com_horas = re.match(
        r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?", data_input
    )
    if padrao_iso_com_horas:
        ano, mes, dia, hora, minuto, segundo = padrao_iso_com_horas.groups()
        segundo = segundo or "00"

        try:
            data_validada = datetime(
                int(ano), int(mes), int(dia), int(hora), int(minuto), int(segundo)
            )
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y %H:%M:%S")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data/hora inválida: {data_input}")

    # Caso 6: Formato ISO: YYYY-MM-DD
    padrao_iso = re.match(r"(\d{4})-(\d{1,2})-(\d{1,2})$", data_input)
    if padrao_iso:
        ano, mes, dia = padrao_iso.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 7: Formato YYYY/MM/DD
    padrao_ano_primeiro_barra = re.match(r"(\d{4})/(\d{1,2})/(\d{1,2})$", data_input)
    if padrao_ano_primeiro_barra:
        ano, mes, dia = padrao_ano_primeiro_barra.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 8: Formato DD-MM-YYYY
    padrao_traco = re.match(r"(\d{1,2})-(\d{1,2})-(\d{4})$", data_input)
    if padrao_traco:
        dia, mes, ano = padrao_traco.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 9: Formato DD.MM.YYYY
    padrao_ponto = re.match(r"(\d{1,2})\.(\d{1,2})\.(\d{4})$", data_input)
    if padrao_ponto:
        dia, mes, ano = padrao_ponto.groups()
        try:
            data_validada = datetime(int(ano), int(mes), int(dia))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            raise ValueError(f"Data inválida: {data_input}")

    # Caso 10: Formato americano MM/DD/YYYY (com validação para distinguir de DD/MM/YYYY)
    padrao_americano = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})$", data_input)
    if padrao_americano:
        parte1, parte2, ano = padrao_americano.groups()

        # Tenta interpretar como DD/MM/YYYY primeiro (formato brasileiro padrão)
        try:
            data_validada = datetime(int(ano), int(parte2), int(parte1))  # DD/MM/YYYY
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta como MM/DD/YYYY (formato americano)
            try:
                data_validada = datetime(
                    int(ano), int(parte1), int(parte2)
                )  # MM/DD/YYYY
                if manter_horas:
                    return data_validada.strftime("%d/%m/%Y 00:00:00")
                else:
                    return data_validada.strftime("%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Data inválida: {data_input}")

    # Caso 11: Formato curto DD/MM (assumindo ano atual)
    padrao_data_curta = re.match(r"(\d{1,2})/(\d{1,2})$", data_input)
    if padrao_data_curta:
        parte1, parte2 = padrao_data_curta.groups()

        # Tenta DD/MM primeiro
        try:
            data_validada = datetime(hoje.year, int(parte2), int(parte1))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta MM/DD
            try:
                data_validada = datetime(hoje.year, int(parte1), int(parte2))
                if manter_horas:
                    return data_validada.strftime("%d/%m/%Y 00:00:00")
                else:
                    return data_validada.strftime("%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Data inválida: {data_input}")

    # Caso 12: Formato curto DD-MM ou MM-DD
    padrao_curto_traco = re.match(r"(\d{1,2})-(\d{1,2})$", data_input)
    if padrao_curto_traco:
        parte1, parte2 = padrao_curto_traco.groups()

        # Tenta DD-MM primeiro
        try:
            data_validada = datetime(hoje.year, int(parte2), int(parte1))
            if manter_horas:
                return data_validada.strftime("%d/%m/%Y 00:00:00")
            else:
                return data_validada.strftime("%d/%m/%Y")
        except ValueError:
            # Se falhar, tenta MM-DD
            try:
                data_validada = datetime(hoje.year, int(parte1), int(parte2))
                if manter_horas:
                    return data_validada.strftime("%d/%m/%Y 00:00:00")
                else:
                    return data_validada.strftime("%d/%m/%Y")
            except ValueError:
                raise ValueError(f"Data inválida: {data_input}")

    # Se chegou até aqui, lança exceção
    raise ValueError(
        f"Formato de data não reconhecido nos casos originais: {data_input}"
    )


async def buscar_info_colaboradores() -> str:
    """Lista os atendimentos avulsos abertos do usuario.

    Args:
        matricula (str | int): a matricula do usuario
        codigo_os (str): a Ordem de Serviço (OS)
        data_inicio (str): a data de inicio dos atendimentos
        data_final(str): a data final dos atendimentos


    Returns:
        str: um XML bem formatado indicando os atendimentos das OS.
    """
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/usuarios/buscarInformacoesUsuariosSIGA/",
            json={"apiKey": getenv("AVA_API_KEY")},
        ) as response:
            json = await response.json(content_type=None)
            retorno = XMLBuilder().build_xml(
                data=json["result"],
                root_element_name="colaboradores",
                item_element_name="colaborador",
            )

            return retorno


def verificar_permissao_acesso_matricula(matricula_desejada: str) -> bool | None:
    """
    Verifica se o usuário tem permissão para acessar os dados da matrícula.

    Args:
        matricula (str): A matrícula do usuário.

    Returns:
        bool: True se o usuário tem permissão, False caso contrário.
    """
    if MATRICULA_USUARIO_ATUAL in MATRICULAS_LIBERADAS:
        return True

    if MCP_TRANSPORT == "stdio":
        return matricula_desejada == MATRICULA_USUARIO_ATUAL

    return None


if __name__ == "__main__":
    print(converter_data_siga("25"))
