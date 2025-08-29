"""Memory extractor for extracting insights from conversations."""

import re
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass

from .session_manager import Message, ExtractedInsight


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
    
    def __init__(self):
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
        """Extract insights from a conversation."""
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
        
        # Deduplicate and rank insights
        insights = self._deduplicate_insights(insights)
        insights = self._rank_insights(insights)
        
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
        """Get statistics about extraction rules."""
        return {
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
            'tech_keywords': len(self.tech_keywords)
        }