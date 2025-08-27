#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configuração compartilhada para testes do projeto Mangaba AI
"""

import pytest
import os
import sys
from unittest.mock import Mock, patch
from datetime import datetime

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangaba_agent import MangabaAgent
from protocols.a2a import A2AProtocol, A2AAgent
from protocols.mcp import MCPProtocol, MCPContext, ContextType, ContextPriority


# Fixtures globais
@pytest.fixture(scope="session")
def test_config():
    """Configuração global para testes"""
    return {
        "api_key": "test_api_key_12345",
        "model_name": "gemini-2.5-flash",
        "max_contexts": 50,
        "test_timeout": 30,
        "mock_responses": True
    }


@pytest.fixture
def mock_genai():
    """Mock global para Google Generative AI"""
    with patch('mangaba_agent.genai') as mock:
        # Configura modelo mock
        mock_model = Mock()
        mock_response = Mock()
        mock_response.text = "Resposta simulada do modelo AI"
        mock_model.generate_content.return_value = mock_response
        mock.GenerativeModel.return_value = mock_model
        
        # Configura método configure
        mock.configure = Mock()
        
        yield mock


@pytest.fixture
def sample_agent(mock_genai, test_config):
    """Fixture para criar um agente de teste padrão"""
    return MangabaAgent(
        api_key=test_config["api_key"],
        agent_name="TestAgent",
        use_mcp=True,
        use_a2a=True
    )


@pytest.fixture
def clean_agent(mock_genai, test_config):
    """Fixture para criar um agente limpo sem protocolos"""
    return MangabaAgent(
        api_key=test_config["api_key"],
        agent_name="CleanAgent",
        use_mcp=False,
        use_a2a=False
    )


@pytest.fixture
def a2a_protocol():
    """Fixture para protocolo A2A"""
    return A2AProtocol()


@pytest.fixture
def mcp_protocol(test_config):
    """Fixture para protocolo MCP"""
    return MCPProtocol(max_contexts=test_config["max_contexts"])


@pytest.fixture
def sample_contexts():
    """Fixture para contextos de exemplo"""
    contexts = []
    
    # Contexto de conversa
    contexts.append(MCPContext.create(
        context_type=ContextType.CONVERSATION,
        content={
            "message": "Olá, como posso ajudar?",
            "user": "test_user",
            "timestamp": datetime.now().isoformat()
        },
        tags=["greeting", "conversation"],
        priority=ContextPriority.MEDIUM
    ))
    
    # Contexto de tarefa
    contexts.append(MCPContext.create(
        context_type=ContextType.TASK,
        content={
            "task": "Analisar documento",
            "status": "pending",
            "priority": "high"
        },
        tags=["analysis", "document", "pending"],
        priority=ContextPriority.HIGH
    ))
    
    # Contexto de conhecimento
    contexts.append(MCPContext.create(
        context_type=ContextType.KNOWLEDGE,
        content={
            "topic": "Inteligência Artificial",
            "summary": "IA é uma área da ciência da computação",
            "keywords": ["AI", "machine learning", "deep learning"]
        },
        tags=["ai", "knowledge", "technology"],
        priority=ContextPriority.MEDIUM
    ))
    
    # Contexto de memória
    contexts.append(MCPContext.create(
        context_type=ContextType.MEMORY,
        content={
            "user_preference": "português brasileiro",
            "interaction_count": 5,
            "last_topic": "programação"
        },
        tags=["user", "preferences", "memory"],
        priority=ContextPriority.LOW
    ))
    
    return contexts


@pytest.fixture
def connected_agents(mock_genai, test_config):
    """Fixture para criar múltiplos agentes conectados"""
    agents = []
    
    # Cria 3 agentes
    for i in range(3):
        agent = MangabaAgent(
            api_key=test_config["api_key"],
            agent_name=f"Agent{i+1}",
            use_mcp=True,
            use_a2a=True
        )
        agents.append(agent)
    
    # Conecta todos os agentes entre si
    for i, agent in enumerate(agents):
        for j, other_agent in enumerate(agents):
            if i != j:
                agent.a2a_protocol.connect_agent(other_agent.a2a_protocol)
    
    return agents


# Fixtures para dados de teste
@pytest.fixture
def sample_text_data():
    """Dados de texto para testes"""
    return {
        "short_text": "Olá mundo!",
        "medium_text": "Este é um texto de exemplo para testes de análise de sentimento e processamento de linguagem natural.",
        "long_text": """Este é um texto longo para testes mais complexos. 
        Ele contém múltiplas frases e parágrafos para simular documentos reais.
        O objetivo é testar a capacidade do sistema de processar textos extensos
        e extrair informações relevantes de forma eficiente.
        
        Este texto também inclui diferentes tipos de conteúdo,
        como listas, números e pontuação variada para garantir
        que o sistema seja robusto em diferentes cenários.""",
        "multilingual_text": "Hello world! Olá mundo! Hola mundo! Bonjour le monde!",
        "technical_text": "A inteligência artificial (IA) utiliza algoritmos de machine learning para processar dados e gerar insights."
    }


@pytest.fixture
def sample_api_responses():
    """Respostas simuladas de API para testes"""
    return {
        "chat_response": "Esta é uma resposta simulada do modelo de IA.",
        "analysis_response": {
            "sentiment": "positive",
            "confidence": 0.85,
            "keywords": ["teste", "análise", "positivo"]
        },
        "translation_response": "This is a simulated translation.",
        "summary_response": "Resumo simulado do conteúdo fornecido.",
        "error_response": "Erro simulado para testes de tratamento de erro."
    }


# Fixtures para configuração de ambiente
@pytest.fixture(autouse=True)
def setup_test_environment(monkeypatch):
    """Configura ambiente de teste"""
    # Define variáveis de ambiente para testes
    monkeypatch.setenv("MANGABA_ENV", "test")
    monkeypatch.setenv("MANGABA_LOG_LEVEL", "DEBUG")
    monkeypatch.setenv("MANGABA_API_KEY", "test_key")
    
    # Desabilita logs durante testes (opcional)
    import logging
    logging.disable(logging.CRITICAL)
    
    yield
    
    # Cleanup após testes
    logging.disable(logging.NOTSET)


# Fixtures para performance
@pytest.fixture
def performance_config():
    """Configuração para testes de performance"""
    return {
        "max_execution_time": 5.0,  # segundos
        "max_memory_usage": 100,    # MB
        "iterations": 100,
        "concurrent_requests": 10
    }


# Helpers para testes
class TestHelpers:
    """Classe com métodos auxiliares para testes"""
    
    @staticmethod
    def create_test_context(context_type=ContextType.CONVERSATION, **kwargs):
        """Cria um contexto de teste personalizado"""
        default_content = {
            "test_data": "dados de teste",
            "timestamp": datetime.now().isoformat()
        }
        
        content = kwargs.pop('content', default_content)
        tags = kwargs.pop('tags', ['test'])
        priority = kwargs.pop('priority', ContextPriority.MEDIUM)
        
        return MCPContext.create(
            context_type=context_type,
            content=content,
            tags=tags,
            priority=priority,
            **kwargs
        )
    
    @staticmethod
    def assert_context_valid(context):
        """Valida se um contexto está bem formado"""
        assert context.id is not None
        assert context.context_type is not None
        assert context.content is not None
        assert context.created_at is not None
        assert context.updated_at is not None
        assert isinstance(context.tags, list)
        assert isinstance(context.metadata, dict)
    
    @staticmethod
    def assert_agent_valid(agent):
        """Valida se um agente está bem configurado"""
        assert agent.agent_name is not None
        assert agent.agent_id is not None
        assert agent.model is not None
        
        if agent.use_mcp:
            assert agent.mcp_protocol is not None
        
        if agent.use_a2a:
            assert agent.a2a_protocol is not None


@pytest.fixture
def test_helpers():
    """Fixture para acessar helpers de teste"""
    return TestHelpers


# Marcadores personalizados
pytestmark = [
    pytest.mark.filterwarnings("ignore::DeprecationWarning"),
    pytest.mark.filterwarnings("ignore::PendingDeprecationWarning")
]


# Configuração de timeout global para testes
def pytest_configure(config):
    """Configuração global do pytest"""
    # Adiciona timeout padrão se não especificado
    if not config.getoption("--timeout"):
        config.option.timeout = 30


# Hook para capturar falhas e gerar relatórios detalhados
def pytest_runtest_makereport(item, call):
    """Hook para personalizar relatórios de teste"""
    if call.when == "call" and call.excinfo is not None:
        # Adiciona informações extras em caso de falha
        item.user_properties.append(("test_file", item.fspath))
        item.user_properties.append(("test_function", item.name))
        item.user_properties.append(("failure_time", datetime.now().isoformat()))