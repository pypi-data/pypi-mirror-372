"""Intelligent domain detection for conversation context."""

import re
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class DomainDetector:
    """Detects conversation domain based on content analysis."""
    
    def __init__(self):
        # Domain keywords and patterns
        self.domain_keywords = {
            'technology': [
                # Programming and development
                'code', 'programming', 'software', 'development', 'api', 'database',
                'algorithm', 'function', 'class', 'variable', 'bug', 'debug',
                'framework', 'library', 'package', 'module', 'testing', 'deployment',
                'git', 'version control', 'ci/cd', 'docker', 'kubernetes',
                # Technologies and languages
                'python', 'javascript', 'java', 'c++', 'rust', 'go', 'sql',
                'react', 'vue', 'angular', 'fastapi', 'django', 'flask',
                'aws', 'azure', 'gcp', 'cloud', 'microservices', 'architecture',
                # Technical concepts
                'machine learning', 'ai', 'data science', 'neural network',
                'blockchain', 'cryptocurrency', 'devops', 'security', 'encryption'
            ],
            'academic': [
                # Research and scholarship
                'research', 'study', 'paper', 'journal', 'publication', 'thesis',
                'dissertation', 'methodology', 'hypothesis', 'experiment', 'analysis',
                'literature review', 'citation', 'reference', 'peer review',
                'conference', 'symposium', 'academic', 'scholar', 'university',
                # Scientific terms
                'theory', 'model', 'framework', 'paradigm', 'empirical', 'quantitative',
                'qualitative', 'statistical', 'correlation', 'causation', 'significance',
                'sample', 'population', 'variable', 'control', 'bias', 'validity',
                # Academic fields
                'psychology', 'sociology', 'biology', 'chemistry', 'physics',
                'mathematics', 'economics', 'linguistics', 'philosophy', 'history'
            ],
            'creative': [
                # Art and design
                'design', 'art', 'creative', 'artistic', 'visual', 'aesthetic',
                'composition', 'color', 'typography', 'layout', 'branding',
                'logo', 'illustration', 'photography', 'drawing', 'painting',
                # Writing and content
                'writing', 'story', 'narrative', 'character', 'plot', 'dialogue',
                'poetry', 'prose', 'blog', 'article', 'content', 'copywriting',
                # Media and production
                'video', 'film', 'animation', 'editing', 'sound', 'music',
                'production', 'recording', 'mixing', 'mastering', 'streaming',
                # Creative process
                'inspiration', 'brainstorm', 'ideation', 'concept', 'prototype',
                'iteration', 'feedback', 'revision', 'portfolio', 'showcase'
            ],
            'business': [
                # Business operations
                'business', 'company', 'corporation', 'startup', 'entrepreneur',
                'revenue', 'profit', 'loss', 'budget', 'finance', 'investment',
                'marketing', 'sales', 'customer', 'client', 'market', 'competition',
                # Management and strategy
                'strategy', 'planning', 'goal', 'objective', 'kpi', 'metric',
                'management', 'leadership', 'team', 'employee', 'hr', 'hiring',
                'project', 'timeline', 'deadline', 'milestone', 'deliverable',
                # Business concepts
                'roi', 'growth', 'scale', 'efficiency', 'productivity', 'innovation',
                'disruption', 'pivot', 'partnership', 'acquisition', 'merger',
                'stakeholder', 'board', 'investor', 'shareholder', 'valuation'
            ],
            'personal': [
                # Personal development
                'personal', 'self', 'habit', 'routine', 'goal', 'motivation',
                'discipline', 'mindset', 'growth', 'improvement', 'learning',
                'skill', 'hobby', 'interest', 'passion', 'wellness', 'health',
                # Life and relationships
                'family', 'friend', 'relationship', 'social', 'communication',
                'emotion', 'feeling', 'stress', 'anxiety', 'confidence',
                'life', 'lifestyle', 'balance', 'time management', 'organization',
                # Activities and interests
                'travel', 'cooking', 'exercise', 'sport', 'music', 'reading',
                'game', 'movie', 'book', 'entertainment', 'leisure', 'vacation'
            ]
        }
        
        # Domain patterns (regex)
        self.domain_patterns = {
            'technology': [
                r'\b(?:def|class|function|var|let|const)\s+\w+',  # Code definitions
                r'\b(?:import|from|include|require)\s+\w+',       # Imports
                r'\b(?:git|npm|pip|docker)\s+\w+',               # Commands
                r'\b\w+\.\w+\(\)',                               # Method calls
                r'https?://github\.com',                         # GitHub URLs
                r'\b(?:API|REST|GraphQL|JSON|XML|HTTP)\b'        # Technical acronyms
            ],
            'academic': [
                r'\b(?:et al\.|ibid\.|cf\.|viz\.|i\.e\.|e\.g\.)', # Academic abbreviations
                r'\b(?:p|pp)\.\s*\d+',                            # Page references
                r'\(\d{4}\)',                                     # Year citations
                r'\b(?:DOI|ISBN|ISSN)\b',                         # Publication identifiers
                r'\b(?:significant|correlation|hypothesis|methodology)\b'
            ],
            'creative': [
                r'\b(?:rgb|hex|cmyk|pantone)\b',                  # Color references
                r'\b(?:font|typeface|serif|sans-serif)\b',        # Typography
                r'\b(?:canvas|photoshop|illustrator|figma)\b',    # Design tools
                r'\b(?:draft|edit|revise|feedback)\b',            # Creative process
                r'\b(?:portfolio|showcase|gallery)\b'             # Creative output
            ],
            'business': [
                r'\$[\d,]+(?:\.\d{2})?',                         # Money amounts
                r'\b\d+%\b',                                     # Percentages
                r'\bQ[1-4]\s+\d{4}\b',                          # Quarters
                r'\b(?:CEO|CTO|CFO|VP|COO)\b',                  # Executive titles
                r'\b(?:B2B|B2C|SaaS|ROI|KPI|CRM|ERP)\b'         # Business acronyms
            ],
            'personal': [
                r'\b(?:I|my|me|myself)\b',                       # Personal pronouns
                r'\b(?:daily|weekly|monthly|yearly)\b',          # Time references
                r'\b(?:habit|routine|goal|target)\b',            # Personal development
                r'\b(?:feel|think|believe|want|need)\b'          # Personal expressions
            ]
        }
    
    def detect_domain(self, text: str, workspace_domain: Optional[str] = None) -> Tuple[str, float]:
        """
        Detect the primary domain of a text.
        
        Args:
            text: Input text to analyze
            workspace_domain: Current workspace domain for context
            
        Returns:
            Tuple of (domain_name, confidence_score)
        """
        text_lower = text.lower()
        domain_scores = defaultdict(float)
        
        # Keyword matching
        for domain, keywords in self.domain_keywords.items():
            for keyword in keywords:
                if keyword in text_lower:
                    # Weight by keyword length (longer keywords are more specific)
                    weight = len(keyword.split()) * 1.0
                    domain_scores[domain] += weight
        
        # Pattern matching
        for domain, patterns in self.domain_patterns.items():
            for pattern in patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                domain_scores[domain] += len(matches) * 2.0  # Patterns are weighted higher
        
        # Workspace context boost
        if workspace_domain and workspace_domain in domain_scores:
            domain_scores[workspace_domain] *= 1.5  # 50% boost for workspace domain
        
        # Normalize scores
        total_score = sum(domain_scores.values())
        if total_score == 0:
            return 'general', 0.0
        
        # Get top domain
        top_domain = max(domain_scores.keys(), key=lambda d: domain_scores[d])
        confidence = domain_scores[top_domain] / total_score
        
        return top_domain, confidence
    
    def analyze_conversation(self, messages: List[Dict[str, str]], 
                           workspace_domain: Optional[str] = None) -> Dict[str, float]:
        """
        Analyze entire conversation for domain distribution.
        
        Args:
            messages: List of message dictionaries with 'content' key
            workspace_domain: Current workspace domain for context
            
        Returns:
            Dictionary mapping domain names to confidence scores
        """
        domain_totals = defaultdict(float)
        message_count = 0
        
        for message in messages:
            if 'content' in message:
                domain, confidence = self.detect_domain(
                    message['content'], workspace_domain
                )
                if domain != 'general':
                    domain_totals[domain] += confidence
                    message_count += 1
        
        # Average confidences
        if message_count > 0:
            for domain in domain_totals:
                domain_totals[domain] /= message_count
        
        return dict(domain_totals)
    
    def suggest_workspace_domain(self, conversation_history: List[Dict[str, str]]) -> str:
        """
        Suggest optimal workspace domain based on conversation history.
        
        Args:
            conversation_history: List of message dictionaries
            
        Returns:
            Suggested domain name
        """
        domain_analysis = self.analyze_conversation(conversation_history)
        
        if not domain_analysis:
            return 'personal'  # Default for general conversations
        
        # Get domain with highest confidence
        top_domain = max(domain_analysis.keys(), key=lambda d: domain_analysis[d])
        
        # Require minimum confidence threshold
        if domain_analysis[top_domain] < 0.3:
            return 'personal'
        
        return top_domain
    
    def get_domain_keywords(self, domain: str) -> List[str]:
        """Get keywords for a specific domain."""
        return self.domain_keywords.get(domain, [])
    
    def get_all_domains(self) -> List[str]:
        """Get list of all supported domains."""
        return list(self.domain_keywords.keys())