import re

def extract_code(md: str) -> str:
    blocks = re.findall(r"```(?:python)?\n(.*?)```", md, flags=re.DOTALL)
    return blocks[0].strip() if blocks else md.strip()