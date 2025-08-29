"""
Email Template Review Rules

Contains the review rules and validation logic for email templates.
"""

from typing import Dict, List, Any


def get_review_rules() -> Dict[str, Any]:
    """
    Get structured review rules for email templates.
    
    Returns:
        Dictionary containing comprehensive review rules
    """
    return {
        "variables": {
            "title": {
                "allowed": ["{{ Greeting }}"]
            },
            "html_body": {
                "required": [
                    "{{ Salutation }}",
                    "{{ Opening }}",
                    "{{ ClosingPhrase }}",
                    "{{ ClosingSalutation }}"
                ],
                "optional": [
                    "{{ Email }}",
                    "{{ First name }}",
                    "{{ Middle name }}",
                    "{{ Last name }}",
                    "{{ Title }}",
                    "{{ Affiliation }}",
                    "{{ Roles }}",
                    "{{ Note }}"
                ]
            },
            "structure": {
                "order": [
                    "{{ Salutation }}",
                    "{{ Opening }}",
                    "[主体内容]",
                    "{{ ClosingPhrase }}",
                    "{{ ClosingSalutation }}",
                    "[落款]"
                ]
            }
        },
        "content_rules": {
            "variable_usage": {
                "description": "所有的邮件变量都在规则中，用{{和}}包裹，没有列出来的邮件变量在邮件模版中不能使用",
                "allowed_pattern": r"\{\{\s*[A-Za-z\s]+\s*\}\}"
            },
            "content_uniqueness": {
                "description": "邮件模版的内容不能和邮件变量名重复",
                "rule": "Template content should not duplicate variable names"
            },
            "text_html_consistency": {
                "description": "邮件模板的text正文和Html正文内容，其主体内容（不包括格式、Html便签、换行等特殊字符）必须保持相同",
                "rule": "Text and HTML body content must be consistent"
            },
            "semantic_consistency": {
                "description": "邮件正文和变量之间语义不得冲突",
                "rule": "No semantic conflicts between email content and variables"
            }
        },
        "sensitive_words": {
            "limit": 10,
            "category_restrictions": {
                "description": "邮件模板敏感词不能超过10个，10个以内的敏感词不能同时包含涉及'政治、金钱、利益、暴力'等其中两种类型的",
                "categories": ["政治", "金钱", "利益", "暴力"],
                "max_category_overlap": 1
            }
        },
        "template_structure": {
            "required_fields": [
                "email_template_id",
                "subject",
                "text_body",
                "html_body"
            ],
            "optional_fields": [
                "is_public",
                "remark",
                "status"
            ]
        }
    }


def validate_template_variables(text_body: str, html_body: str) -> Dict[str, Any]:
    """
    Validate template variables usage.
    
    Args:
        text_body: Plain text body content
        html_body: HTML body content
        
    Returns:
        Dictionary containing validation results
    """
    rules = get_review_rules()
    allowed_vars = (
        rules["variables"]["html_body"]["required"] + 
        rules["variables"]["html_body"]["optional"] +
        rules["variables"]["title"]["allowed"]
    )
    
    import re
    variable_pattern = r'\{\{\s*([^}]+)\s*\}\}'
    
    # Extract variables from both bodies
    text_vars = re.findall(variable_pattern, text_body)
    html_vars = re.findall(variable_pattern, html_body)
    
    all_used_vars = set([f"{{{{ {var.strip()} }}}}" for var in text_vars + html_vars])
    
    # Check for invalid variables
    invalid_vars = []
    for var in all_used_vars:
        if var not in allowed_vars:
            invalid_vars.append(var)
    
    return {
        "valid": len(invalid_vars) == 0,
        "used_variables": list(all_used_vars),
        "invalid_variables": invalid_vars,
        "allowed_variables": allowed_vars
    }


def validate_sensitive_words(span_list: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Validate sensitive words compliance.
    
    Args:
        span_list: List of sensitive word entries
        
    Returns:
        Dictionary containing validation results
    """
    rules = get_review_rules()
    max_count = rules["sensitive_words"]["limit"]
    restricted_categories = rules["sensitive_words"]["category_restrictions"]["categories"]
    max_category_overlap = rules["sensitive_words"]["category_restrictions"]["max_category_overlap"]
    
    # Count total sensitive words
    total_count = len(span_list)
    
    # Count categories
    category_count = {}
    for item in span_list:
        category = item.get("category", "")
        category_count[category] = category_count.get(category, 0) + 1
    
    # Check category overlap
    restricted_category_count = 0
    for category in restricted_categories:
        if category in category_count:
            restricted_category_count += 1
    
    return {
        "valid": (
            total_count <= max_count and 
            restricted_category_count <= max_category_overlap
        ),
        "total_count": total_count,
        "max_allowed": max_count,
        "category_distribution": category_count,
        "restricted_category_count": restricted_category_count,
        "max_category_overlap": max_category_overlap
    }