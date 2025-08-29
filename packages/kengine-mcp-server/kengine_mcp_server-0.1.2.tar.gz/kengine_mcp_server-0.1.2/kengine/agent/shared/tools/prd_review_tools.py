"""
PRD Review Tools

This module provides specialized tools for reviewing Product Requirement Documents (PRD).
These tools extend the base agent tools with PRD-specific analysis capabilities.
"""

import json
import logging
import re
from typing import Dict, List

from .base import BasePathTool
from .exceptions import ToolError

logger = logging.getLogger(__name__)


class PRDDocumentStructureAnalysisTool():
    """Tool for analyzing PRD document structure"""
    
    def __init__(self):
        pass
    
    name = "prd_structure_analysis"
    description = "分析PRD文档的结构完整性、逻辑性和标准化程度"
    
    def run(self, prd_content: str) -> str:
        """Analyze PRD document structure"""
        
        try:
            # Define expected PRD sections
            expected_sections = [
                "项目背景", "需求概述", "功能需求", "非功能需求", 
                "技术方案", "实施计划", "风险评估", "验收标准"
            ]
            
            # Analyze document structure
            structure_analysis = {
                "total_sections": 0,
                "found_sections": [],
                "missing_sections": [],
                "section_hierarchy": {},
                "structure_score": 0,
                "logic_score": 0,
                "standardization_score": 0
            }
            
            # Extract sections from content
            lines = prd_content.split('\n')
            current_section = None
            section_content = {}
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Check for section headers (various formats)
                if re.match(r'^#{1,3}\s+', line):  # Markdown headers
                    current_section = re.sub(r'^#{1,3}\s+', '', line)
                    section_content[current_section] = []
                elif re.match(r'^\d+\.\s+', line):  # Numbered sections
                    current_section = re.sub(r'^\d+\.\s+', '', line)
                    section_content[current_section] = []
                elif re.match(r'^[A-Z][A-Z\s]+$', line):  # ALL CAPS sections
                    current_section = line
                    section_content[current_section] = []
                elif current_section:
                    section_content[current_section].append(line)
            
            # Analyze found sections
            structure_analysis["found_sections"] = list(section_content.keys())
            structure_analysis["total_sections"] = len(section_content)
            
            # Check for missing sections
            for expected in expected_sections:
                found = False
                for found_section in section_content.keys():
                    if expected in found_section or found_section in expected:
                        found = True
                        break
                if not found:
                    structure_analysis["missing_sections"].append(expected)
            
            # Calculate scores
            completeness_ratio = len(structure_analysis["found_sections"]) / len(expected_sections)
            structure_analysis["structure_score"] = int(completeness_ratio * 100)
            
            # Logic score based on section order and relationships
            logic_score = self._calculate_logic_score(section_content)
            structure_analysis["logic_score"] = logic_score
            
            # Standardization score based on format consistency
            standardization_score = self._calculate_standardization_score(prd_content)
            structure_analysis["standardization_score"] = standardization_score
            
            return json.dumps(structure_analysis, ensure_ascii=False, indent=2)
            
        except Exception as e:
            logger.error(f"Error analyzing PRD structure: {e}")
            raise ToolError(f"PRD结构分析失败: {str(e)}", tool_name=self.__class__.__name__)
    
    def _calculate_logic_score(self, section_content: Dict[str, List[str]]) -> int:
        """Calculate logic score based on section relationships"""
        
        # Define logical section order
        logical_order = [
            "项目背景", "需求概述", "功能需求", "非功能需求",
            "技术方案", "实施计划", "风险评估", "验收标准"
        ]
        
        found_sections = list(section_content.keys())
        score = 0
        
        # Check if sections follow logical order
        for i, section in enumerate(logical_order):
            for found_section in found_sections:
                if section in found_section or found_section in section:
                    # Bonus for correct position
                    if i < len(found_sections):
                        score += 10
                    break
        
        return min(score, 100)
    
    def _calculate_standardization_score(self, content: str) -> int:
        """Calculate standardization score based on format consistency"""
        
        score = 0
        
        # Check for consistent formatting
        if re.search(r'#{1,3}\s+', content):  # Markdown headers
            score += 30
        if re.search(r'^\d+\.\s+', content, re.MULTILINE):  # Numbered lists
            score += 20
        if re.search(r'^- \s+', content, re.MULTILINE):  # Bullet points
            score += 20
        if re.search(r'```', content):  # Code blocks
            score += 15
        if re.search(r'\*\*.*\*\*', content):  # Bold text
            score += 15
        
        return min(score, 100)
