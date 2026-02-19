"""
Atlassian Document Format (ADF) Parser
Converts ADF JSON content to readable text
"""

import json
from typing import Any, Dict, List, Union

class ADFParser:
    """
    Parser for Atlassian Document Format (ADF) content
    """
    
    @staticmethod
    def parse_adf_to_text(adf_content: Union[str, Dict, None]) -> str:
        """
        Parse ADF content to plain text
        
        Args:
            adf_content: ADF content as string, dict, or None
            
        Returns:
            Plain text representation of the ADF content
        """
        if not adf_content:
            return ""
        
        # If it's already a string and doesn't look like JSON, return as is
        if isinstance(adf_content, str):
            # Check if it looks like JSON
            if adf_content.strip().startswith('{') and adf_content.strip().endswith('}'):
                try:
                    adf_dict = json.loads(adf_content)
                    return ADFParser._parse_adf_dict(adf_dict)
                except json.JSONDecodeError:
                    # If it's not valid JSON, return as is
                    return adf_content
            else:
                # It's already plain text
                return adf_content
        
        # If it's a dict, parse it directly
        if isinstance(adf_content, dict):
            return ADFParser._parse_adf_dict(adf_content)
        
        # Fallback: convert to string
        return str(adf_content)
    
    @staticmethod
    def _parse_adf_dict(adf_dict: Dict[str, Any]) -> str:
        """
        Parse ADF dictionary to text
        
        Args:
            adf_dict: ADF content as dictionary
            
        Returns:
            Plain text representation
        """
        if not isinstance(adf_dict, dict):
            return str(adf_dict)
        
        # Check if it's an ADF document
        if adf_dict.get('type') == 'doc' and 'content' in adf_dict:
            return ADFParser._parse_content(adf_dict['content'])
        
        # If it's not ADF format, return as JSON string
        return json.dumps(adf_dict, indent=2)
    
    @staticmethod
    def _parse_content(content: List[Dict[str, Any]]) -> str:
        """
        Parse ADF content array to text
        
        Args:
            content: List of ADF content nodes
            
        Returns:
            Plain text representation
        """
        if not content:
            return ""
        
        result = []
        
        for node in content:
            node_text = ADFParser._parse_node(node)
            if node_text:
                result.append(node_text)
        
        return "\n".join(result)
    
    @staticmethod
    def _parse_node(node: Dict[str, Any]) -> str:
        """
        Parse a single ADF node to text
        
        Args:
            node: ADF node dictionary
            
        Returns:
            Plain text representation of the node
        """
        if not isinstance(node, dict):
            return ""
        
        node_type = node.get('type', '')
        content = node.get('content', [])
        attrs = node.get('attrs', {})
        
        # Parse text content
        text_content = ADFParser._extract_text_from_content(content)
        
        # Apply formatting based on node type
        if node_type == 'heading':
            level = attrs.get('level', 1)
            return f"{'#' * level} {text_content}"
        
        elif node_type == 'paragraph':
            return text_content
        
        elif node_type == 'bulletList':
            return ADFParser._parse_list(content, bullet=True)
        
        elif node_type == 'orderedList':
            return ADFParser._parse_list(content, bullet=False)
        
        elif node_type == 'taskList':
            return ADFParser._parse_task_list(content)
        
        elif node_type == 'codeBlock':
            language = attrs.get('language', '')
            return f"```{language}\n{text_content}\n```"
        
        elif node_type == 'blockquote':
            return f"> {text_content}"
        
        elif node_type == 'table':
            return ADFParser._parse_table(content)
        
        else:
            # For unknown node types, just return the text content
            return text_content
    
    @staticmethod
    def _extract_text_from_content(content: List[Dict[str, Any]]) -> str:
        """
        Extract plain text from ADF content array
        
        Args:
            content: List of ADF content nodes
            
        Returns:
            Plain text
        """
        if not content:
            return ""
        
        result = []
        
        for node in content:
            if isinstance(node, dict):
                node_type = node.get('type', '')
                
                if node_type == 'text':
                    text = node.get('text', '')
                    marks = node.get('marks', [])
                    
                    # Apply text formatting
                    for mark in marks:
                        mark_type = mark.get('type', '')
                        if mark_type == 'strong':
                            text = f"**{text}**"
                        elif mark_type == 'em':
                            text = f"*{text}*"
                        elif mark_type == 'code':
                            text = f"`{text}`"
                        elif mark_type == 'link':
                            href = mark.get('attrs', {}).get('href', '')
                            if href:
                                text = f"[{text}]({href})"
                    
                    result.append(text)
                
                elif 'content' in node:
                    # Recursively parse nested content
                    nested_text = ADFParser._extract_text_from_content(node['content'])
                    if nested_text:
                        result.append(nested_text)
        
        return "".join(result)
    
    @staticmethod
    def _parse_list(content: List[Dict[str, Any]], bullet: bool = True) -> str:
        """
        Parse list content to text
        
        Args:
            content: List of ADF list item nodes
            bullet: Whether this is a bullet list (True) or ordered list (False)
            
        Returns:
            Formatted list text
        """
        if not content:
            return ""
        
        result = []
        
        for i, item in enumerate(content):
            if isinstance(item, dict) and item.get('type') == 'listItem':
                item_content = ADFParser._extract_text_from_content(item.get('content', []))
                if item_content:
                    if bullet:
                        result.append(f"• {item_content}")
                    else:
                        result.append(f"{i + 1}. {item_content}")
        
        return "\n".join(result)
    
    @staticmethod
    def _parse_task_list(content: List[Dict[str, Any]]) -> str:
        """
        Parse task list content to text
        
        Args:
            content: List of ADF task item nodes
            
        Returns:
            Formatted task list text
        """
        if not content:
            return ""
        
        result = []
        
        for item in content:
            if isinstance(item, dict) and item.get('type') == 'taskItem':
                item_content = ADFParser._extract_text_from_content(item.get('content', []))
                state = item.get('attrs', {}).get('state', 'TODO')
                
                if item_content:
                    checkbox = "[x]" if state == "DONE" else "[ ]"
                    result.append(f"{checkbox} {item_content}")
        
        return "\n".join(result)
    
    @staticmethod
    def _parse_table(content: List[Dict[str, Any]]) -> str:
        """
        Parse table content to text
        
        Args:
            content: List of ADF table nodes
            
        Returns:
            Formatted table text
        """
        if not content:
            return ""
        
        # This is a simplified table parser
        # For complex tables, you might want to implement more sophisticated formatting
        result = []
        
        for node in content:
            if isinstance(node, dict) and node.get('type') == 'tableRow':
                row_content = ADFParser._extract_text_from_content(node.get('content', []))
                if row_content:
                    result.append(f"| {row_content} |")
        
        return "\n".join(result) 