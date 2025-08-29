"""
PRD Review Agent Service

This module provides a specialized agent service for reviewing Product Requirement Documents (PRD).
It extends the BaseAgentChatService with PRD-specific tools and capabilities.
"""

import logging
import json
from typing import Iterator, Dict, Any, List, Optional
from datetime import datetime

from kengine.rag.interface import DocumentInfo, RAGService
from kengine.agent.shared.tools.factory import PRDStructureAnalysisInput
from langchain.agents import AgentExecutor
from langchain.tools import StructuredTool, Tool
from kengine.agent.shared.tools.prd_review_tools import PRDDocumentStructureAnalysisTool

from .base_agent_chat_service import BaseAgentChatService
from .models import ChatRequest, StreamChunk, ConversationContext
from .components import MetadataProvider, StreamProcessor, MessageHandler

logger = logging.getLogger(__name__)


class PRDReviewMetadataProvider(MetadataProvider):
    """PRD Review specific metadata provider"""
    
    def get_metadata(self, context: ConversationContext, **kwargs) -> Dict[str, Any]:
        """Get PRD review specific metadata"""
        metadata = {
            "agent_type": "prd_review",
            "review_mode": kwargs.get("review_mode", "comprehensive"),
            "review_focus": kwargs.get("review_focus", "all"),
            "quality_threshold": kwargs.get("quality_threshold", 70),
            "timestamp": datetime.now().isoformat()
        }
        
        # Add PRD-specific metadata if available
        if context.metadata and "prd_document" in context.metadata:
            prd_info = context.metadata["prd_document"]
            metadata.update({
                "document_title": prd_info.get("title", "Unknown"),
                "document_version": prd_info.get("version", "1.0"),
                "document_type": prd_info.get("type", "feature_request"),
                "review_scope": prd_info.get("scope", "full")
            })
        
        return metadata


class PRDReviewStreamProcessor(StreamProcessor):
    """PRD Review specific stream processor"""
    
    def process_stream(self, 
                      stream: Iterator[StreamChunk], 
                      context: ConversationContext,
                      **kwargs) -> Iterator[StreamChunk]:
        """Process PRD review stream with specialized handling"""
        
        review_phase = "initialization"
        review_progress = 0
        
        for chunk in stream:
            # Track review progress
            if chunk.type == "thought":
                if "文档结构分析" in chunk.content:
                    review_phase = "structure_analysis"
                    review_progress = 20
                elif "需求质量评估" in chunk.content:
                    review_phase = "requirement_analysis"
                    review_progress = 40
                elif "技术可行性分析" in chunk.content:
                    review_phase = "technical_analysis"
                    review_progress = 60
                elif "业务逻辑验证" in chunk.content:
                    review_phase = "business_analysis"
                    review_progress = 80
                elif "综合评估" in chunk.content:
                    review_phase = "final_assessment"
                    review_progress = 90
                
                # Add review progress metadata
                chunk.metadata = chunk.metadata or {}
                chunk.metadata.update({
                    "review_phase": review_phase,
                    "review_progress": review_progress
                })
            
            # Process final answer for structured output
            if chunk.type == "final_answer":
                try:
                    # Try to parse as JSON for structured review report
                    review_data = json.loads(chunk.content)
                    chunk.metadata = chunk.metadata or {}
                    chunk.metadata.update({
                        "review_report": review_data,
                        "review_complete": True,
                        "review_progress": 100
                    })
                except json.JSONDecodeError:
                    # If not JSON, treat as regular text
                    pass
            
            yield chunk


class PRDReviewMessageHandler(MessageHandler):
    """PRD Review specific message handler"""
    
    def handle_message(self, 
                      message: str, 
                      context: ConversationContext,
                      **kwargs) -> str:
        """Handle PRD review specific message processing"""
        
        # Extract PRD document content if present
        if "PRD" in message or "需求文档" in message or "product requirement" in message.lower():
            # Add PRD context to the message
            enhanced_message = f"""
PRD Review Request: {message}

Please provide a comprehensive review of the PRD document including:
1. Document structure analysis
2. Requirement quality assessment  
3. Technical feasibility analysis
4. Business logic validation
5. Implementation risk assessment

Focus on providing actionable insights and improvement recommendations.
"""
            return enhanced_message
        
        return message


class PRDReviewService(BaseAgentChatService):
    """
    PRD Review Agent Service
    
    This service provides specialized functionality for reviewing Product Requirement Documents.
    It extends the BaseAgentChatService with PRD-specific tools and processing capabilities.
    
    Key Features:
        1. PRD document structure analysis
        2. Requirement quality assessment
        3. Technical feasibility analysis
        4. Business logic validation
        5. Implementation risk assessment
        6. Quality scoring and recommendations
    """
    
    def __init__(self, **kwargs):
        """
        Initialize PRD Review service with custom components.
        
        This constructor creates custom metadata provider, stream processor, and message handler
        instances specific to PRD review, then initializes the base class with these components
        using dependency injection.
        
        Args:
            **kwargs: Additional keyword arguments passed to the base class.
        """
        # Initialize base class with custom components via dependency injection
        super().__init__(
            agent_prompt_name='PRDReviewPrompt',
            # metadata_provider=PRDReviewMetadataProvider(),
            # stream_processor=PRDReviewStreamProcessor(),
            # message_handler=PRDReviewMessageHandler(),
            **kwargs
        )
        
        logger.info("PRDReviewService initialized with custom components")
    
    def _prepare_agent(self, context: ConversationContext, agent_executor: AgentExecutor, repo_status: Dict[str, Any]) -> Iterator[StreamChunk]:
        """Prepare PRD review agent with specialized initialization"""
        
        # Add PRD review specific context
        review_context = {
            "review_mode": "comprehensive",
            "quality_threshold": 70,
            "focus_areas": ["structure", "requirements", "technical", "business", "risk"],
            "repo_status": repo_status
        }
        
        context.metadata = context.metadata or {}
        context.metadata.update(review_context)
        
        # Yield initialization message
        yield StreamChunk(
            type="thinking",
            data="🔍 开始PRD文档审查分析...",
            metadata={"review_phase": "initialization", "review_progress": 0}
        )
        
        yield StreamChunk(
            type="thinking", 
            data="📋 审查范围：文档结构、需求质量、技术可行性、业务逻辑、实施风险",
            metadata={"review_phase": "initialization", "review_progress": 5}
        )
    
    def build_agent_input(self, request: ChatRequest, context: ConversationContext, relevant_docs: List[DocumentInfo]) -> Dict[str, Any]:
        """Build PRD review specific agent input"""
        
        # Extract PRD document content if present in the request
        prd_content = self._extract_prd_content(request.message)
        
        # Build enhanced context for PRD review
        agent_input = super().build_agent_input(request, context, relevant_docs)
        agent_input["prd_content"] = prd_content
        
        return agent_input

    def _create_agent_tools(self, repo_name: str, rag_service: RAGService) -> List[Tool]:
        """Create agent tools for the conversation"""
        tools = super()._create_agent_tools(repo_name, rag_service)
        tools.append(
            StructuredTool.from_function(
                func=PRDDocumentStructureAnalysisTool().run,
                name="PRDStructureAnalysis",
                description="分析PRD文档的结构完整性、逻辑性和标准化程度",
                args_schema=PRDStructureAnalysisInput
            )
        )
        return tools
    def _extract_prd_content(self, message: str) -> Optional[str]:
        """Extract PRD document content from message"""
        
        # Look for PRD content markers
        prd_markers = [
            "```prd", "```PRD", "```markdown", "```json",
            "PRD文档内容：", "需求文档：", "Product Requirement Document:"
        ]
        
        for marker in prd_markers:
            if marker in message:
                # Extract content between markers
                start_idx = message.find(marker) + len(marker)
                end_marker = "```"
                end_idx = message.find(end_marker, start_idx)
                
                if end_idx != -1:
                    return message[start_idx:end_idx].strip()
        
        return message
    
    
    def _finalize_chat(self, context: ConversationContext, relevant_docs: List[DocumentInfo], full_response: str) -> Iterator[StreamChunk]:
        """Finalize PRD review chat with summary and recommendations"""
        
        try:
            # Try to parse the final result as structured review report
            review_report = json.loads(full_response)
            
            # Generate summary
            summary = self._generate_review_summary(review_report)
            
            yield StreamChunk(
                type="content",
                data="✅ PRD审查完成！",
                metadata={"review_phase": "completion", "review_progress": 100}
            )
            
            yield StreamChunk(
                type="content",
                data=summary,
                metadata={"review_report": review_report, "review_complete": True}
            )
            
        except json.JSONDecodeError:
            # If not structured, return as is
            yield StreamChunk(
                type="content",
                data=full_response,
                metadata={"review_complete": True}
            )
    
    def _generate_review_summary(self, review_report: Dict[str, Any]) -> str:
        """Generate a summary of the PRD review report"""
        
        try:
            summary = review_report.get("review_summary", {})
            overall_score = summary.get("overall_score", "N/A")
            document_title = summary.get("document_title", "Unknown")
            
            recommendations = review_report.get("recommendations", {})
            critical_issues = recommendations.get("critical_issues", [])
            action_items = recommendations.get("action_items", [])
            
            summary_text = f"""
## PRD审查报告摘要

**文档标题**: {document_title}
**总体评分**: {overall_score}/100
**审查状态**: 完成

### 关键发现
"""
            
            if critical_issues:
                summary_text += "\n**关键问题**:\n"
                for issue in critical_issues[:3]:  # Show top 3 issues
                    summary_text += f"- {issue}\n"
            
            if action_items:
                summary_text += "\n**主要行动项目**:\n"
                for item in action_items[:3]:  # Show top 3 items
                    summary_text += f"- {item}\n"
            
            summary_text += "\n请查看完整审查报告获取详细分析和建议。"
            
            return summary_text
            
        except Exception as e:
            logger.warning(f"Failed to generate review summary: {e}")
            return "PRD审查已完成，请查看详细报告。"
    
    def get_review_statistics(self, conversation_id: str) -> Dict[str, Any]:
        """Get PRD review statistics for a conversation"""
        
        context = self.conversation_manager.get_conversation(conversation_id)
        if not context:
            return {}
        
        # Extract review statistics from conversation metadata
        metadata = context.metadata or {}
        
        return {
            "review_phases": metadata.get("review_phases", []),
            "review_progress": metadata.get("review_progress", 0),
            "quality_score": metadata.get("quality_score"),
            "review_duration": metadata.get("review_duration"),
            "tools_used": metadata.get("tools_used", []),
            "issues_found": metadata.get("issues_found", 0),
            "recommendations_count": metadata.get("recommendations_count", 0)
        }
