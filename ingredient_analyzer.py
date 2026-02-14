import re

def extract_harmful_ingredients(groq_analysis):
    """
    Extract harmful ingredients from Groq analysis for quick display
    
    Args:
        groq_analysis: The analysis text from Groq
    
    Returns:
        Dict with harmful ingredients summary
    """
    
    if not groq_analysis:
        return {
            "has_harmful": False,
            "harmful_list": [],
            "risk_level": "UNKNOWN"
        }
    
    # Look for harmful ingredients section
    harmful_section = ""
    analysis_lower = groq_analysis.lower()
    
    # Find harmful/concerning section
    if "harmful" in analysis_lower or "concerning" in analysis_lower:
        # Try to extract the harmful section
        lines = groq_analysis.split('\n')
        in_harmful_section = False
        harmful_lines = []
        
        for line in lines:
            line_lower = line.lower()
            
            # Start of harmful section
            if any(keyword in line_lower for keyword in ['harmful', 'concerning ingredients', 'risk']):
                in_harmful_section = True
                harmful_lines.append(line)
            elif in_harmful_section:
                # Check if we've moved to next section
                if line.strip().startswith('##') or line.strip().startswith('**') and ':' in line:
                    if not any(keyword in line_lower for keyword in ['harmful', 'concerning', 'risk']):
                        break
                harmful_lines.append(line)
        
        harmful_section = '\n'.join(harmful_lines)
    
    # Determine if there are harmful ingredients
    has_harmful = False
    harmful_list = []
    risk_level = "LOW"
    
    if "no harmful" in analysis_lower or "no concerning" in analysis_lower or "✅" in groq_analysis:
        has_harmful = False
        risk_level = "SAFE"
    elif "high risk" in analysis_lower:
        has_harmful = True
        risk_level = "HIGH"
        # Extract ingredients marked as high risk
        for line in harmful_section.split('\n'):
            if "high risk" in line.lower() or "⚠️" in line:
                harmful_list.append(line.strip())
    elif "moderate risk" in analysis_lower or "⚠️" in groq_analysis:
        has_harmful = True
        risk_level = "MODERATE"
        for line in harmful_section.split('\n'):
            if "moderate risk" in line.lower() or "risk" in line.lower():
                harmful_list.append(line.strip())
    elif any(keyword in analysis_lower for keyword in ['avoid', 'warning', 'concerning', 'harmful', 'toxic', 'dangerous']):
        has_harmful = True
        risk_level = "MODERATE"
    
    return {
        "has_harmful": has_harmful,
        "harmful_list": harmful_list[:5],  # Top 5 harmful ingredients
        "risk_level": risk_level,
        "harmful_section": harmful_section[:500] if harmful_section else ""
    }


def get_risk_emoji(risk_level):
    """Get emoji for risk level"""
    risk_emojis = {
        "HIGH": "🔴",
        "MODERATE": "🟡",
        "LOW": "🟢",
        "SAFE": "✅",
        "UNKNOWN": "⚪"
    }
    return risk_emojis.get(risk_level, "⚪")
