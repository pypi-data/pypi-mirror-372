import json, re

def find_and_parse_json_from_string(response: str) -> dict:
    """
    Finds and parses JSON from a string. It can be encapsulated in triple backticks or not.
    """
    try:
        pattern_json_encapsulated = r"```json\n([\s\S]*?)\n```"
        pattern_json_non_encapsulated = r"\{[\s\S]*?\}"
        json_encapsulated = re.search(pattern_json_encapsulated, response)
        json_non_encapsulated = re.search(pattern_json_non_encapsulated, response)
        if json_encapsulated:
            return json.loads(json_encapsulated.group(1))
        elif json_non_encapsulated:
            return json.loads(json_non_encapsulated.group(0))
        return json.loads(response)

    except Exception:
        pass

    return None

def extract_markdown_content(response: str, tag: str = "") -> str:
    """
    Extracts content from a specified markdown tag (e.g., sql, json) or just triple backticks.
    
    :param response: The input string containing markdown-encapsulated content.
    :param tag: The markdown tag to look for (e.g., 'sql', 'json'). Use an empty string for plain triple backticks.
    :return: Extracted content as a string or None if no match is found.
    """
    try:
        pattern_encapsulated = rf"```{tag}\n([\s\S]*?)\n```"
        pattern_plain = r"```\n([\s\S]*?)\n```"
        
        match_encapsulated = re.search(pattern_encapsulated, response) if tag else None
        match_plain = re.search(pattern_plain, response)
        
        if match_encapsulated:
            return match_encapsulated.group(1)
        elif match_plain:
            return match_plain.group(1)
        
    except Exception:
        pass
    
    return None
