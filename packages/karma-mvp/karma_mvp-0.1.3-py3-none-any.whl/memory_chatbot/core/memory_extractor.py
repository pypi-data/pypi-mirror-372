"""Memory extractor for extracting insights from conversations."""

import re
import asyncio
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .session_manager import Message, ExtractedInsight
from ..config.settings import Mem0Config
from ..utils.crypto import CryptoManager, CryptoError

logger = logging.getLogger(__name__)


@dataclass
class ExtractionRule:
    """Rule for extracting specific types of information."""
    pattern: str
    insight_type: str  # 'preference', 'knowledge', 'pattern'
    target_layer: str  # 'global' or 'workspace'
    confidence_base: float
    keywords: List[str] = None


class MemoryExtractorError(Exception):
    """Memory extractor related errors."""
    pass


class MemoryExtractor:
    """Extracts valuable information from conversation messages."""
    
    def __init__(self, mem0_config: Optional[Mem0Config] = None):
        self.extraction_rules = self._initialize_rules()
        self.tech_keywords = {
            'python', 'javascript', 'react', 'nodejs', 'django', 'flask', 'fastapi',
            'postgresql', 'mysql', 'mongodb', 'redis', 'docker', 'kubernetes',
            'aws', 'azure', 'gcp', 'terraform', 'jenkins', 'git', 'github',
            'rest', 'graphql', 'api', 'microservices', 'oauth', 'jwt'
        }
        
        self.preference_indicators = {
            'style': ['prefer', 'like', 'love', 'hate', 'dislike', 'always use', 'never use'],
            'depth': ['detailed', 'brief', 'simple', 'complex', 'in-depth', 'high-level'],
            'format': ['examples', 'code', 'explanation', 'documentation']
        }
        
        # Mem0 integration
        self.mem0_config = mem0_config
        self.mem0_client = None
        self.crypto_manager = CryptoManager()
        self._mem0_init_error = None
        
        # Initialize Mem0 client if enabled
        if self.mem0_config and self.mem0_config.enabled:
            self._initialize_mem0_client()
    
    def _initialize_mem0_client(self):
        """Initialize Mem0 client based on configuration."""
        try:
            # Try to import Mem0 (optional dependency)
            try:
                from mem0 import MemoryClient as Mem0
            except ImportError:
                # Mem0 not available, disable functionality
                return
            
            if self.mem0_config.use_platform:
                # Platform version with API key
                if self.mem0_config.api_key_encrypted:
                    try:
                        # Try to use as plaintext key first, then try decryption
                        api_key = self.mem0_config.api_key_encrypted
                        if api_key.startswith('Z0FBQUFBQm'):  # Base64 encrypted format
                            # This looks like encrypted key, decrypt it
                            api_key = self.crypto_manager.decrypt(api_key)
                        
                        self.mem0_client = Mem0(api_key=api_key)
                        # If we reach here, client was created successfully
                    except CryptoError as e:
                        # Failed to decrypt API key
                        self.mem0_client = None
                        self._mem0_init_error = f"Decryption failed: {str(e)}"
                    except Exception as e:
                        # API key validation or other client creation error
                        # This is expected if API key is invalid
                        self.mem0_client = None
                        # Store error for debugging (optional)
                        self._mem0_init_error = str(e)
            else:
                # OSS version with local configuration
                try:
                    self.mem0_client = Mem0(config=self.mem0_config.oss_config)
                except Exception as e:
                    self.mem0_client = None
                    self._mem0_init_error = str(e)
                
        except Exception as e:
            # Any initialization failure - gracefully disable Mem0
            self.mem0_client = None
            self._mem0_init_error = str(e)
    
    def _initialize_rules(self) -> List[ExtractionRule]:
        """Initialize extraction rules for different types of insights."""
        return [
            # User preferences
            ExtractionRule(
                pattern=r'I (prefer|like|love|always use|usually use) (.+)',
                insight_type='preference',
                target_layer='global',
                confidence_base=0.7,
                keywords=['prefer', 'like', 'love']
            ),
            ExtractionRule(
                pattern=r'I (hate|dislike|never use|avoid) (.+)',
                insight_type='preference', 
                target_layer='global',
                confidence_base=0.7,
                keywords=['hate', 'dislike', 'never', 'avoid']
            ),
            
            # Technical knowledge
            ExtractionRule(
                pattern=r'(best practice|pattern|approach) (?:for|is to|when) (.+)',
                insight_type='knowledge',
                target_layer='workspace',
                confidence_base=0.6,
                keywords=['best practice', 'pattern', 'approach']
            ),
            
            # Architecture decisions
            ExtractionRule(
                pattern=r'we (decided|chose|selected|use) (.+) (because|since|for) (.+)',
                insight_type='knowledge',
                target_layer='workspace',
                confidence_base=0.8,
                keywords=['decided', 'chose', 'selected']
            ),
            
            # Common patterns
            ExtractionRule(
                pattern=r'(usually|typically|often|always) (implement|use|do) (.+)',
                insight_type='pattern',
                target_layer='workspace',
                confidence_base=0.5,
                keywords=['usually', 'typically', 'often', 'always']
            )
        ]
    
    def extract_from_conversation(self, messages: List[Message], 
                                context: Optional[Dict[str, Any]] = None) -> List[ExtractedInsight]:
        """Extract insights from a conversation using both rule-based and AI-enhanced methods."""
        insights = []
        
        # Phase 1: Rule-based extraction (existing logic)
        rule_based_insights = self._extract_with_rules(messages, context)
        insights.extend(rule_based_insights)
        
        # Phase 2: AI-enhanced extraction with Mem0 (if available and enabled)
        if (self.mem0_client and 
            self.mem0_config and 
            self.mem0_config.enabled and 
            self.mem0_config.enhance_extraction):
            try:
                # Run async extraction in new event loop to avoid conflicts
                loop = None
                try:
                    loop = asyncio.get_event_loop()
                    if loop.is_running():
                        # If loop is running, create new thread for async operation
                        import concurrent.futures
                        with concurrent.futures.ThreadPoolExecutor() as executor:
                            future = executor.submit(asyncio.run, self._extract_with_mem0(messages, context))
                            ai_insights = future.result(timeout=self.mem0_config.extraction_timeout + 5)
                    else:
                        ai_insights = asyncio.run(self._extract_with_mem0(messages, context))
                except RuntimeError:
                    # No event loop, use asyncio.run
                    ai_insights = asyncio.run(self._extract_with_mem0(messages, context))
                
                insights.extend(ai_insights)
            except Exception as e:
                # AI extraction failed, continue with rule-based results
                logger.debug(f"Mem0 AI extraction failed: {e}")
                pass
        
        # Deduplicate and rank all insights
        insights = self._deduplicate_insights(insights)
        insights = self._rank_insights(insights)
        
        return insights
    
    def _extract_with_rules(self, messages: List[Message], 
                           context: Optional[Dict[str, Any]] = None) -> List[ExtractedInsight]:
        """Extract insights using rule-based methods (original logic)."""
        insights = []
        
        for message in messages:
            if message.role == 'user':
                # Extract from user messages
                user_insights = self._extract_user_insights(message, context)
                insights.extend(user_insights)
            
            elif message.role == 'assistant':
                # Extract from assistant messages (technical knowledge, patterns)
                assistant_insights = self._extract_assistant_insights(message, context)
                insights.extend(assistant_insights)
        
        return insights
    
    async def _extract_with_mem0(self, messages: List[Message], 
                                context: Optional[Dict[str, Any]] = None) -> List[ExtractedInsight]:
        """Extract insights using AI-enhanced methods via Mem0."""
        insights = []
        
        try:
            # Get user identifier for Mem0
            user_id = self._get_user_identifier(context)
            
            # Prepare messages for Mem0 analysis
            analysis_messages = self._prepare_messages_for_analysis(messages)
            
            # Use Mem0 for AI-enhanced memory extraction
            response = await asyncio.wait_for(
                self._call_mem0_analysis(analysis_messages, user_id, context),
                timeout=self.mem0_config.extraction_timeout
            )
            
            # Parse Mem0 response and convert to ExtractedInsight format
            ai_insights = self._parse_mem0_response(response, messages[0].session_id if messages else None)
            insights.extend(ai_insights)
            
        except asyncio.TimeoutError:
            # Mem0 call timed out
            pass
        except Exception:
            # Any other error in AI extraction
            pass
        
        return insights
    
    def _get_user_identifier(self, context: Optional[Dict[str, Any]]) -> str:
        """Get user identifier for Mem0 based on workspace context."""
        if context and 'workspace' in context:
            workspace_name = context['workspace'].get('name', 'default')
            return f"workspace_{workspace_name}"
        return "default_user"
    
    def _prepare_messages_for_analysis(self, messages: List[Message], max_messages: int = 5) -> List[Dict[str, str]]:
        """Prepare conversation messages for Mem0 analysis."""
        # Take the most recent messages for analysis
        recent_messages = messages[-max_messages:] if len(messages) > max_messages else messages
        
        analysis_messages = [
            {
                "role": "system",
                "content": """分析这段对话并提取重要的用户偏好、知识点和洞察。

请识别以下类型的信息：
1. 用户偏好：喜好、厌恶、工作风格等
2. 技术知识：讨论的技术、工具、最佳实践
3. 工作模式：常用的开发模式、架构决策等

对于每个洞察，请评估其重要性和可信度。"""
            }
        ]
        
        # Add conversation messages
        for message in recent_messages:
            analysis_messages.append({
                "role": message.role,
                "content": message.content
            })
        
        return analysis_messages
    
    async def _call_mem0_analysis(self, messages: List[Dict[str, str]], user_id: str, 
                                 context: Optional[Dict[str, Any]]) -> Any:
        """Call Mem0 for conversation analysis."""
        # Prepare metadata for Mem0
        metadata = {
            "extraction_type": "conversation_analysis",
            "timestamp": datetime.now().isoformat()
        }
        
        if context:
            if 'workspace' in context:
                metadata["workspace"] = context['workspace'].get('name')
                metadata["domain"] = context.get('current_domain', 'general')
        
        # Use Mem0's chat completion with automatic memory storage
        response = await self.mem0_client.chat.completions.create(
            messages=messages,
            model=self.mem0_config.oss_config.get('llm', {}).get('config', {}).get('model', 'gpt-4o-mini'),
            user_id=user_id,
            metadata=metadata,
            limit=self.mem0_config.retrieval_limit
        )
        
        return response
    
    def _parse_mem0_response(self, response: Any, session_id: Optional[str]) -> List[ExtractedInsight]:
        """Parse Mem0 response and convert to ExtractedInsight objects."""
        insights = []
        
        try:
            # Extract the analysis content
            analysis_content = response.choices[0].message.content
            
            # Simple parsing - look for structured patterns in the response
            # This is a basic implementation; in production, you might use more sophisticated NLP
            patterns = [
                (r'偏好[:：](.+)', 'preference', 'global'),
                (r'技术[:：](.+)', 'knowledge', 'workspace'),
                (r'模式[:：](.+)', 'pattern', 'workspace'),
                (r'洞察[:：](.+)', 'knowledge', 'global')
            ]
            
            for pattern, insight_type, target_layer in patterns:
                matches = re.findall(pattern, analysis_content, re.IGNORECASE | re.MULTILINE)
                for match in matches:
                    content = match.strip()
                    if len(content) > 5:  # Filter out very short matches
                        insights.append(ExtractedInsight(
                            id=None,
                            session_id=session_id,
                            insight_type=insight_type,
                            target_layer=target_layer,
                            content=content,
                            confidence=0.7  # AI-extracted insights get higher base confidence
                        ))
            
            # If no structured patterns found, create a general insight from the content
            if not insights and analysis_content and len(analysis_content.strip()) > 20:
                insights.append(ExtractedInsight(
                    id=None,
                    session_id=session_id,
                    insight_type='knowledge',
                    target_layer='global',
                    content=f"AI Analysis: {analysis_content[:100]}...",
                    confidence=0.5
                ))
        
        except Exception:
            # Parsing failed - return empty list
            pass
        
        return insights
    
    def _extract_user_insights(self, message: Message, context: Optional[Dict[str, Any]]) -> List[ExtractedInsight]:
        """Extract insights from user messages."""
        insights = []
        content = message.content.lower()
        
        # Apply extraction rules
        for rule in self.extraction_rules:
            matches = re.findall(rule.pattern, content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    match_text = ' '.join(match)
                else:
                    match_text = match
                
                confidence = self._calculate_confidence(rule, match_text, content, context)
                
                if confidence > 0.3:  # Minimum confidence threshold
                    insights.append(ExtractedInsight(
                        id=None,
                        session_id=message.session_id,
                        insight_type=rule.insight_type,
                        target_layer=rule.target_layer,
                        content=match_text.strip(),
                        confidence=confidence
                    ))
        
        # Extract technology preferences
        tech_insights = self._extract_tech_preferences(message, context)
        insights.extend(tech_insights)
        
        # Extract communication style preferences
        style_insights = self._extract_style_preferences(message, context)
        insights.extend(style_insights)
        
        return insights
    
    def _extract_assistant_insights(self, message: Message, context: Optional[Dict[str, Any]]) -> List[ExtractedInsight]:
        """Extract insights from assistant messages."""
        insights = []
        content = message.content.lower()
        
        # Extract technical patterns and best practices mentioned
        if any(keyword in content for keyword in ['pattern', 'practice', 'approach', 'method']):
            # Look for code examples or technical explanations
            code_blocks = re.findall(r'```[\s\S]*?```', message.content)
            if code_blocks:
                for block in code_blocks:
                    if len(block) > 50:  # Significant code block
                        insights.append(ExtractedInsight(
                            id=None,
                            session_id=message.session_id,
                            insight_type='pattern',
                            target_layer='workspace',
                            content=f"Code pattern: {block[:100]}...",
                            confidence=0.4
                        ))
        
        # Extract mentioned tools and technologies
        mentioned_tech = []
        for tech in self.tech_keywords:
            if tech in content:
                mentioned_tech.append(tech)
        
        if mentioned_tech:
            insights.append(ExtractedInsight(
                id=None,
                session_id=message.session_id,
                insight_type='knowledge',
                target_layer='workspace',
                content=f"Technologies discussed: {', '.join(mentioned_tech[:5])}",
                confidence=0.3
            ))
        
        return insights
    
    def _extract_tech_preferences(self, message: Message, context: Optional[Dict[str, Any]]) -> List[ExtractedInsight]:
        """Extract technology preferences from user messages."""
        insights = []
        content = message.content.lower()
        
        # Look for technology preferences
        for tech in self.tech_keywords:
            if tech in content:
                # Check for positive sentiment
                if any(pos in content for pos in ['prefer', 'like', 'love', 'great', 'excellent']):
                    insights.append(ExtractedInsight(
                        id=None,
                        session_id=message.session_id,
                        insight_type='preference',
                        target_layer='global',
                        content=f"Prefers {tech}",
                        confidence=0.6
                    ))
                # Check for negative sentiment
                elif any(neg in content for neg in ['hate', 'dislike', 'avoid', 'terrible', 'awful']):
                    insights.append(ExtractedInsight(
                        id=None,
                        session_id=message.session_id,
                        insight_type='preference',
                        target_layer='global',
                        content=f"Dislikes {tech}",
                        confidence=0.6
                    ))
        
        return insights
    
    def _extract_style_preferences(self, message: Message, context: Optional[Dict[str, Any]]) -> List[ExtractedInsight]:
        """Extract communication style preferences."""
        insights = []
        content = message.content.lower()
        
        # Look for style indicators
        if any(word in content for word in ['detailed', 'thorough', 'comprehensive']):
            insights.append(ExtractedInsight(
                id=None,
                session_id=message.session_id,
                insight_type='preference',
                target_layer='global',
                content="Prefers detailed explanations",
                confidence=0.5
            ))
        
        elif any(word in content for word in ['brief', 'short', 'concise', 'quick']):
            insights.append(ExtractedInsight(
                id=None,
                session_id=message.session_id,
                insight_type='preference',
                target_layer='global',
                content="Prefers brief responses",
                confidence=0.5
            ))
        
        # Check for code example preferences
        if 'example' in content and ('code' in content or 'show' in content):
            insights.append(ExtractedInsight(
                id=None,
                session_id=message.session_id,
                insight_type='preference',
                target_layer='global',
                content="Likes code examples",
                confidence=0.4
            ))
        
        return insights
    
    def _calculate_confidence(self, rule: ExtractionRule, match_text: str, 
                            full_content: str, context: Optional[Dict[str, Any]]) -> float:
        """Calculate confidence score for an extracted insight."""
        confidence = rule.confidence_base
        
        # Boost confidence for longer, more specific matches
        if len(match_text) > 20:
            confidence += 0.1
        
        # Boost confidence if keywords are present
        if rule.keywords:
            keyword_count = sum(1 for keyword in rule.keywords if keyword in full_content)
            confidence += keyword_count * 0.05
        
        # Boost confidence if context supports the insight
        if context:
            workspace_info = context.get('workspace', {})
            if rule.target_layer == 'workspace' and workspace_info:
                # Check if insight is relevant to workspace tech stack
                tech_stack = workspace_info.get('tech_stack', {})
                if any(tech.lower() in match_text.lower() 
                      for tech_list in tech_stack.values() 
                      for tech in tech_list):
                    confidence += 0.15
        
        # Cap confidence at 0.95
        return min(confidence, 0.95)
    
    def _deduplicate_insights(self, insights: List[ExtractedInsight]) -> List[ExtractedInsight]:
        """Remove duplicate insights based on content similarity."""
        unique_insights = []
        
        for insight in insights:
            # Check for similar existing insights
            is_duplicate = False
            for existing in unique_insights:
                if (existing.insight_type == insight.insight_type and 
                    existing.target_layer == insight.target_layer and
                    self._are_similar(existing.content, insight.content)):
                    # Keep the one with higher confidence
                    if insight.confidence > existing.confidence:
                        unique_insights.remove(existing)
                        unique_insights.append(insight)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_insights.append(insight)
        
        return unique_insights
    
    def _are_similar(self, content1: str, content2: str) -> bool:
        """Check if two insight contents are similar."""
        # Simple similarity check based on word overlap
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        if len(words1) == 0 or len(words2) == 0:
            return False
        
        overlap = len(words1.intersection(words2))
        similarity = overlap / min(len(words1), len(words2))
        
        return similarity > 0.7
    
    def _rank_insights(self, insights: List[ExtractedInsight]) -> List[ExtractedInsight]:
        """Rank insights by confidence and relevance."""
        return sorted(insights, key=lambda x: x.confidence, reverse=True)
    
    def get_extraction_stats(self) -> Dict[str, Any]:
        """Get statistics about extraction rules and Mem0 integration."""
        stats = {
            'total_rules': len(self.extraction_rules),
            'rules_by_type': {
                'preference': len([r for r in self.extraction_rules if r.insight_type == 'preference']),
                'knowledge': len([r for r in self.extraction_rules if r.insight_type == 'knowledge']),
                'pattern': len([r for r in self.extraction_rules if r.insight_type == 'pattern'])
            },
            'rules_by_layer': {
                'global': len([r for r in self.extraction_rules if r.target_layer == 'global']),
                'workspace': len([r for r in self.extraction_rules if r.target_layer == 'workspace'])
            },
            'tech_keywords': len(self.tech_keywords),
            'mem0_integration': {
                'enabled': self.mem0_config.enabled if self.mem0_config else False,
                'client_available': self.mem0_client is not None,
                'use_platform': self.mem0_config.use_platform if self.mem0_config else False,
                'enhance_extraction': (self.mem0_config.enhance_extraction 
                                     if self.mem0_config else False),
                'extraction_timeout': (self.mem0_config.extraction_timeout 
                                     if self.mem0_config else 0),
                'retrieval_limit': (self.mem0_config.retrieval_limit 
                                  if self.mem0_config else 0),
                'init_error': getattr(self, '_mem0_init_error', None)
            }
        }
        
        return stats
    
    def is_mem0_available(self) -> bool:
        logger.info(f"Mem0 client: {self.mem0_client}")
        logger.info(f"Mem0 config: {self.mem0_config}")
        logger.info(f"Mem0 enabled: {self.mem0_config.enabled}")
        """Check if Mem0 is available and properly configured."""
        return (self.mem0_client is not None and 
                self.mem0_config is not None and 
                self.mem0_config.enabled)