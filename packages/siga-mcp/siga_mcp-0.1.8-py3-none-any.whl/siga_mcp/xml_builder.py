
import html
import re
from collections.abc import Mapping, Sequence
from typing import Any, cast
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, tostring


class XMLBuilder:
    """Classe genérica para montagem dinâmica de XML a partir de dados estruturados."""

    @staticmethod
    def normalize_field_name(field_name: str) -> str:
        """Converte automaticamente nomes de campos para formato XML válido.

        Args:
            field_name (str): Nome do campo original

        Returns:
            str: Nome do campo normalizado para XML
        """
        if not field_name:
            return "campo_vazio"

        # Converter para lowercase
        normalized = field_name.lower()

        # Remover acentos e caracteres especiais, manter apenas letras, números e underscore
        normalized = re.sub(r"[^\w\s]", "", normalized)

        # Substituir espaços por underscore
        normalized = re.sub(r"\s+", "_", normalized)

        # Remover underscores consecutivos
        normalized = re.sub(r"_+", "_", normalized)

        # Remover underscore do início e fim
        normalized = normalized.strip("_")

        # Se começar com número, adicionar prefixe
        if normalized and normalized[0].isdigit():
            normalized = f"campo_{normalized}"

        # Se ficou vazio, usar nome padrão
        if not normalized:
            normalized = "campo_sem_nome"

        return normalized

    @staticmethod
    def clean_html_entities(text: str) -> str:
        """Remove entidades HTML e limpa o texto.

        Args:
            text (str): Texto a ser limpo

        Returns:
            str: Texto limpo
        """
        # Converter para string se não for
        text = str(text)

        # Fazer unescape de entidades HTML
        text = html.unescape(text)

        # Remover tags HTML se existirem
        text = re.sub(r"<[^>]+>", "", text)

        # Limpar espaços extras
        text = re.sub(r"\s+", " ", text).strip()

        return text

    def build_xml(
        self,
        data: Sequence[Mapping[str, Any]] | Mapping[str, Any],
        root_element_name: str = "root",
        item_element_name: str = "item",
        root_attributes: Mapping[str, str] | None = None,
        custom_attributes: Mapping[str, Any] | None = None,
    ) -> str:
        """Constrói XML dinamicamente a partir de uma lista de dicionários.

        Args:
            data (Sequence[Mapping[str, Any]]): Lista de dicionários com os dados
            root_element_name (str): Nome do elemento raiz
            item_element_name (str): Nome do elemento para cada item da lista
            root_attributes (Mapping[str, str]]) | None Atributos para o elemento raiz
            custom_attributes (Mapping[str, Any]]) | None Atributos customizados adicionais

        Returns:
            str: XML bem formatado
        """
        # Criar elemento raiz
        root = Element(root_element_name)

        # Adicionar atributos padrão
        if root_attributes:
            for key, value in root_attributes.items():
                root.set(key, str(value))

        # Adicionar total de itens como atributo
        root.set("total", str(len(data)))

        # Adicionar atributos customizados
        if custom_attributes:
            for key, value in custom_attributes.items():
                root.set(key, str(value))

        if isinstance(data, Mapping):
            data = [data]

        # Processar cada item automaticamente
        for item_data in data:
            item_element = SubElement(root, item_element_name)

            # Adicionar todos os campos automaticamente
            for key, value in item_data.items():
                # Normalizar nome do campo automaticamente
                xml_field_name = self.normalize_field_name(key)

                # Criar elemento filho
                field_element = SubElement(item_element, xml_field_name)

                # Limpar valor de entidades HTML e definir texto
                cleaned_value = self.clean_html_entities(value)
                field_element.text = cleaned_value

        return self._format_xml(root)

    def build_single_item_xml(
        self,
        data: Mapping[str, Any],
        root_element_name: str = "root",
        root_attributes: Mapping[str, str] | None = None,
    ) -> str:
        """Constrói XML para um único item (dicionário).

        Args:
            data (Dict[str, Any]): Dicionário com os dados
            root_element_name (str): Nome do elemento raiz
            root_attributes (Mapping[str, str]]) | None Atributos para o elemento raiz

        Returns:
            str: XML bem formatado
        """
        # Criar elemento raiz
        root = Element(root_element_name)

        # Adicionar atributos
        if root_attributes:
            for key, value in root_attributes.items():
                root.set(key, str(value))

        # Adicionar todos os campos automaticamente
        for key, value in data.items():
            # Normalizar nome do campo automaticamente
            xml_field_name = self.normalize_field_name(key)

            # Criar elemento filho
            field_element = SubElement(root, xml_field_name)

            # Limpar valor de entidades HTML e definir texto
            cleaned_value = self.clean_html_entities(value)
            field_element.text = cleaned_value

        return self._format_xml(root)

    def build_nested_xml(
        self,
        data: Mapping[str, Any],
        root_element_name: str = "root",
        root_attributes: Mapping[str, str] | None = None,
    ) -> str:
        """Constrói XML para estruturas aninhadas (dicionários e listas).

        Args:
            data (Dict[str, Any]): Dados com estrutura aninhada
            root_element_name (str): Nome do elemento raiz
            root_attributes (Mapping[str, str]]) | None Atributos para o elemento raiz

        Returns:
            str: XML bem formatado
        """
        root = Element(root_element_name)

        if root_attributes:
            for key, value in root_attributes.items():
                root.set(key, str(value))

        self._add_nested_elements(root, data)
        return self._format_xml(root)

    def _add_nested_elements(self, parent: Element, data: Any) -> None:
        """Adiciona elementos aninhados recursivamente.

        Args:
            parent (Element): Elemento pai
            data (Any): Dados a serem processados
        """
        if isinstance(data, dict):
            for key, value in data.items():
                xml_field_name = self.normalize_field_name(cast(Any, key))

                if isinstance(value, (dict, list)):
                    # Criar elemento para estrutura aninhada
                    nested_element = SubElement(parent, xml_field_name)
                    self._add_nested_elements(nested_element, value)
                else:
                    # Elemento simples
                    field_element = SubElement(parent, xml_field_name)
                    cleaned_value = self.clean_html_entities(cast(Any, value))
                    field_element.text = cleaned_value

        elif isinstance(data, list):
            for i, item in enumerate(cast(Any, data)):
                item_element = SubElement(parent, f"item_{i}")
                self._add_nested_elements(item_element, item)
        else:
            # Valor simples
            parent.text = self.clean_html_entities(data)

    def _format_xml(self, root: Element) -> str:
        """Formata o XML com indentação bonita.

        Args:
            root (Element): Elemento raiz

        Returns:
            str: XML formatado
        """
        # Converter para string com formatação bonita e encoding UTF-8
        rough_string = tostring(root, encoding="unicode")
        reparsed = minidom.parseString(rough_string)

        # Remover linha em branco extra do toprettyxml
        pretty_xml = reparsed.toprettyxml(indent="  ", encoding=None)

        # Limpar linhas vazias extras
        lines = [line for line in pretty_xml.split("\n") if line.strip()]
        return "\n".join(lines)
