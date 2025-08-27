# tests/test_parsing.py (VERSÃO FINAL E COMPLETA)

import pytest
from llm_guard import GuardSchema, ParseError, ExtractionError, RepairError
from unittest.mock import Mock

class UserInfo(GuardSchema):
    name: str
    age: int

# Testes do MVP
def test_parse_com_json_limpo():
    text = '{"name": "Alice", "age": 30}'
    user = UserInfo.parse(text)
    assert user.name == "Alice"
    assert user.age == 30

def test_parse_com_json_cercado_de_texto():
    text = "Aqui estão os dados: ```json\n{\"name\": \"Bob\", \"age\": 25}\n```."
    user = UserInfo.parse(text)
    assert user.name == "Bob"
    assert user.age == 25

def test_falha_quando_nao_ha_json_sem_cliente():
    text = "Não há dados aqui."
    with pytest.raises(ParseError, match="Nenhum bloco de JSON encontrado"):
        UserInfo.parse(text)

def test_falha_com_tipo_invalido_sem_cliente():
    text = '{"name": "Charlie", "age": "vinte"}'
    with pytest.raises(ParseError, match="Falha ao validar o JSON e nenhum cliente LLM foi fornecido para reparo."):
        UserInfo.parse(text)

# Testes da Fase 2 com mock
def test_reparo_de_json_com_virgula_sobrando(repair_prompt_fixture):
    texto_quebrado = '{"name": "Alice", "age": 30,}'
    texto_corrigido = '{"name": "Alice", "age": 30}'
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = texto_corrigido
    mock_client.chat.completions.create.return_value = mock_response
    
    user = UserInfo.parse(texto_quebrado, llm_client=mock_client)
    
    assert user.name == "Alice"
    assert user.age == 30
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": repair_prompt_fixture}],
        model="gpt-3.5-turbo",
        temperature=0.0
    )

def test_extracao_de_dados_de_texto_puro(extraction_prompt_fixture):
    texto_puro = "O usuário se chama Bruno e tem 42 anos."
    json_esperado = '{"name": "Bruno", "age": 42}'
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = json_esperado
    mock_client.chat.completions.create.return_value = mock_response

    user = UserInfo.parse(texto_puro, llm_client=mock_client)

    assert user.name == "Bruno"
    assert user.age == 42
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": extraction_prompt_fixture}],
        model="gpt-3.5-turbo",
        temperature=0.0
    )

def test_configuracao_do_llm_e_passada_corretamente(extraction_prompt_fixture_carlos):
    texto_puro = "O usuário se chama Carlos e tem 50 anos."
    json_esperado = '{"name": "Carlos", "age": 50}'
    custom_config = {"model": "gpt-4o", "temperature": 0.8}
    mock_client = Mock()
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message = Mock()
    mock_response.choices[0].message.content = json_esperado
    mock_client.chat.completions.create.return_value = mock_response

    user = UserInfo.parse(texto_puro, llm_client=mock_client, llm_config=custom_config)

    assert user.name == "Carlos"
    assert user.age == 50
    mock_client.chat.completions.create.assert_called_once_with(
        messages=[{"role": "user", "content": extraction_prompt_fixture_carlos}],
        model="gpt-4o",
        temperature=0.8
    )

def test_falha_na_extracao_levanta_erro_especifico(extraction_prompt_fixture):
    texto_puro = "O usuário se chama Bruno e tem 42 anos."
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API fora do ar")

    with pytest.raises(ExtractionError, match="Falha ao extrair e validar"):
        UserInfo.parse(texto_puro, llm_client=mock_client)

def test_falha_no_reparo_levanta_erro_especifico(repair_prompt_fixture):
    texto_quebrado = '{"name": "Alice", "age": 30,}'
    mock_client = Mock()
    mock_client.chat.completions.create.side_effect = Exception("API fora do ar")
    
    with pytest.raises(RepairError, match="Falha ao reparar e validar"):
        UserInfo.parse(texto_quebrado, llm_client=mock_client)

# --- CORPO DAS FIXTURES COMPLETO ABAIXO ---
@pytest.fixture
def repair_prompt_fixture():
    json_quebrado = '{"name": "Alice", "age": 30,}'
    return f"""O JSON a seguir está quebrado ou malformado. Por favor, corrija a sintaxe e retorne APENAS o JSON corrigido, sem nenhum texto adicional.

JSON Quebrado:
{json_quebrado}"""

@pytest.fixture
def extraction_prompt_fixture():
    texto_original = "O usuário se chama Bruno e tem 42 anos."
    schema_json = UserInfo.model_json_schema()
    return f"""
Extraia as informações do texto original para preencher um objeto JSON.
O esquema JSON necessário é:
{schema_json}

Texto Original:
"{texto_original}"

Responda APENAS com o objeto JSON válido.
"""

@pytest.fixture
def extraction_prompt_fixture_carlos():
    texto_original = "O usuário se chama Carlos e tem 50 anos."
    schema_json = UserInfo.model_json_schema()
    return f"""
Extraia as informações do texto original para preencher um objeto JSON.
O esquema JSON necessário é:
{schema_json}

Texto Original:
"{texto_original}"

Responda APENAS com o objeto JSON válido.
"""