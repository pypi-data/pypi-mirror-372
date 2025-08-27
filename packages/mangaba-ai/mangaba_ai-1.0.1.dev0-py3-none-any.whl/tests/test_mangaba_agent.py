#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes unitários para MangabaAgent
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Adiciona o diretório pai ao path para imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mangaba_agent import MangabaAgent
from protocols.a2a import A2AMessage, MessageType
from protocols.mcp import MCPContext, ContextType, ContextPriority


class TestMangabaAgent:
    """Testes para a classe MangabaAgent"""
    
    @pytest.fixture
    def mock_genai(self):
        """Mock para Google Generative AI"""
        with patch('google.generativeai.configure') as mock_configure, \
             patch('google.generativeai.GenerativeModel') as mock_model:
            
            # Mock do modelo
            mock_instance = Mock()
            mock_instance.generate_content.return_value.text = "Resposta mockada do AI"
            mock_model.return_value = mock_instance
            
            yield mock_configure, mock_model, mock_instance
    
    @pytest.fixture
    def mock_config(self):
        """Mock para configuração"""
        with patch('config.config') as mock_cfg:
            mock_cfg.api_key = "test_api_key"
            mock_cfg.model = "gemini-2.5-flash"
            mock_cfg.log_level = "INFO"
            yield mock_cfg
    
    @pytest.fixture
    def agent(self, mock_genai, mock_config):
        """Fixture para criar um agente de teste"""
        return MangabaAgent(api_key="test_key", model="test-model")
    
    def test_agent_initialization(self, mock_genai, mock_config):
        """Testa inicialização do agente"""
        agent = MangabaAgent(api_key="test_key", model="test-model")
        
        assert agent.api_key == "test_key"
        assert agent.model_name == "test-model"
        assert agent.agent_id.startswith("mangaba_")
        assert agent.mcp_enabled is True
        assert hasattr(agent, 'mcp')
        assert hasattr(agent, 'current_session_id')
    
    def test_agent_initialization_without_mcp(self, mock_genai, mock_config):
        """Testa inicialização do agente sem MCP"""
        agent = MangabaAgent(api_key="test_key", enable_mcp=False)
        
        assert agent.mcp_enabled is False
        assert not hasattr(agent, 'mcp')
    
    def test_chat_basic(self, agent, mock_genai):
        """Testa funcionalidade básica de chat"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Olá! Como posso ajudar?"
        
        response = agent.chat("Olá")
        
        assert response == "Olá! Como posso ajudar?"
        mock_instance.generate_content.assert_called_once()
    
    def test_chat_with_context(self, agent, mock_genai):
        """Testa chat com contexto MCP"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Resposta com contexto"
        
        response = agent.chat("Teste com contexto", use_context=True)
        
        assert response == "Resposta com contexto"
        # Verifica se o contexto foi adicionado ao MCP
        assert len(agent.mcp.contexts) > 0
    
    def test_chat_without_context(self, agent, mock_genai):
        """Testa chat sem usar contexto MCP"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Resposta sem contexto"
        
        initial_context_count = len(agent.mcp.contexts)
        response = agent.chat("Teste sem contexto", use_context=False)
        
        assert response == "Resposta sem contexto"
        # Verifica se não foi adicionado contexto
        assert len(agent.mcp.contexts) == initial_context_count
    
    def test_analyze_text(self, agent, mock_genai):
        """Testa análise de texto"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Análise: Texto positivo"
        
        response = agent.analyze_text("Texto para análise", "Analise o sentimento")
        
        assert response == "Análise: Texto positivo"
        mock_instance.generate_content.assert_called_once()
    
    def test_translate(self, agent, mock_genai):
        """Testa tradução de texto"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Hello world"
        
        response = agent.translate("Olá mundo", "inglês")
        
        assert response == "Hello world"
        mock_instance.generate_content.assert_called_once()
    
    def test_get_context_summary(self, agent):
        """Testa obtenção do resumo de contexto"""
        # Adiciona alguns contextos
        agent.chat("Primeira mensagem")
        agent.chat("Segunda mensagem")
        
        summary = agent.get_context_summary()
        
        assert isinstance(summary, str)
        assert "contextos" in summary.lower()
    
    def test_handle_mangaba_request_chat(self, agent, mock_genai):
        """Testa handler de requisição A2A para chat"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Resposta via A2A"
        
        message = A2AMessage.create(
            sender_id="test_sender",
            message_type=MessageType.REQUEST,
            content={
                "action": "chat",
                "params": {"message": "Olá via A2A"}
            },
            receiver_id=agent.agent_id
        )
        
        with patch.object(agent.a2a_protocol, 'send_message') as mock_send:
            agent.handle_mangaba_request(message)
            mock_send.assert_called_once()
    
    def test_handle_mangaba_request_analyze(self, agent, mock_genai):
        """Testa handler de requisição A2A para análise"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.return_value.text = "Análise via A2A"
        
        message = A2AMessage.create(
            sender_id="test_sender",
            message_type=MessageType.REQUEST,
            content={
                "action": "analyze",
                "params": {
                    "text": "Texto para análise",
                    "instruction": "Analise este texto"
                }
            },
            receiver_id=agent.agent_id
        )
        
        with patch.object(agent.a2a_protocol, 'send_message') as mock_send:
            agent.handle_mangaba_request(message)
            mock_send.assert_called_once()
    
    def test_handle_mangaba_request_unknown_action(self, agent):
        """Testa handler com ação desconhecida"""
        message = A2AMessage.create(
            sender_id="test_sender",
            message_type=MessageType.REQUEST,
            content={
                "action": "unknown_action",
                "params": {}
            },
            receiver_id=agent.agent_id
        )
        
        with patch.object(agent.a2a_protocol, 'send_message') as mock_send:
            agent.handle_mangaba_request(message)
            mock_send.assert_called_once()
            # Verifica se a resposta contém erro
            call_args = mock_send.call_args[0][0]
            assert "não reconhecida" in call_args.content.get('result', '')
    
    def test_send_agent_request(self, agent):
        """Testa envio de requisição para outro agente"""
        with patch.object(agent.a2a_protocol, 'send_message') as mock_send:
            result = agent.send_agent_request(
                "target_agent",
                "chat",
                {"message": "Olá"}
            )
            
            assert "Requisição enviada" in result
            mock_send.assert_called_once()
    
    def test_broadcast_message(self, agent):
        """Testa broadcast de mensagem"""
        with patch.object(agent.a2a_protocol, 'send_message') as mock_send:
            result = agent.broadcast_message(
                "Mensagem de broadcast",
                ["tag1", "tag2"]
            )
            
            assert "Broadcast enviado" in result
            mock_send.assert_called_once()
    
    def test_error_handling_in_chat(self, agent, mock_genai):
        """Testa tratamento de erro no chat"""
        _, _, mock_instance = mock_genai
        mock_instance.generate_content.side_effect = Exception("API Error")
        
        response = agent.chat("Teste de erro")
        
        assert "Erro" in response or "erro" in response
    
    def test_agent_id_uniqueness(self, mock_genai, mock_config):
        """Testa se IDs de agentes são únicos"""
        agent1 = MangabaAgent()
        agent2 = MangabaAgent()
        
        assert agent1.agent_id != agent2.agent_id
        assert agent1.agent_id.startswith("mangaba_")
        assert agent2.agent_id.startswith("mangaba_")
    
    def test_custom_agent_id(self, mock_genai, mock_config):
        """Testa criação de agente com ID customizado"""
        custom_id = "custom_agent_123"
        agent = MangabaAgent(agent_id=custom_id)
        
        assert agent.agent_id == custom_id


if __name__ == "__main__":
    pytest.main([__file__])