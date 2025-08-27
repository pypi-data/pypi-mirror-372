# src/llm_guard/main.py (VERSÃO COM ERROS ESPECÍFICOS)

import json
import re
from typing import Any, Type, TypeVar, Dict

from pydantic import BaseModel, ValidationError

T = TypeVar("T", bound="GuardSchema")

class ParseError(Exception):
    """Exceção base para todos os erros de parsing do LLM-Guard."""
    pass

# --- MUDANÇA 1: Novas classes de erro específicas ---
class ExtractionError(ParseError):
    """Levantado quando a extração de dados de texto puro falha."""
    pass

class RepairError(ParseError):
    """Levantado quando o reparo de um JSON quebrado falha."""
    pass
# --- FIM DA MUDANÇA 1 ---

class GuardSchema(BaseModel):
    """
    Classe base que herda de pydantic.BaseModel e adiciona o método .parse().
    """
    @classmethod
    def parse(cls: Type[T], text: str, llm_client: Any = None, llm_config: Dict[str, Any] = None) -> T:
        default_config = {"model": "gpt-3.5-turbo", "temperature": 0.0}
        if llm_config:
            default_config.update(llm_config)
        final_config = default_config
        
        match = re.search(r"\{.*\}|\[.*\]", text, re.DOTALL)
        
        if not match:
            if not llm_client:
                raise ParseError("Nenhum bloco de JSON encontrado e nenhum cliente LLM foi fornecido para extração.")
            
            try:
                extraction_prompt = f"""
Extraia as informações do texto original para preencher um objeto JSON.
O esquema JSON necessário é:
{cls.model_json_schema()}

Texto Original:
"{text}"

Responda APENAS com o objeto JSON válido.
"""
                response = llm_client.chat.completions.create(
                    messages=[{"role": "user", "content": extraction_prompt}],
                    **final_config
                )
                json_string_from_extraction = response.choices[0].message.content
                return cls.model_validate_json(json_string_from_extraction)
            except Exception as e:
                # --- MUDANÇA 2: Usando a exceção específica ---
                raise ExtractionError(f"Falha ao extrair e validar a partir do texto: {e}") from e

        json_string = match.group(0)

        try:
            return cls.model_validate_json(json_string)
        except (ValidationError, json.JSONDecodeError):
            if not llm_client:
                raise ParseError("Falha ao validar o JSON e nenhum cliente LLM foi fornecido para reparo.")

            try:
                repair_prompt = f"""O JSON a seguir está quebrado ou malformado. Por favor, corrija a sintaxe e retorne APENAS o JSON corrigido, sem nenhum texto adicional.

JSON Quebrado:
{json_string}"""
                response = llm_client.chat.completions.create(
                    messages=[{"role": "user", "content": repair_prompt}],
                    **final_config
                )
                repaired_json_string = response.choices[0].message.content
                return cls.model_validate_json(repaired_json_string)
            except Exception as e:
                # --- MUDANÇA 3: Usando a exceção específica ---
                raise RepairError(f"Falha ao reparar e validar o JSON: {e}") from e