import re

def extract_tracebacks(log_text):
    """
    Извлекает все блоки Traceback из текста логов.
    Возвращает список словарей с ключами 'traceback' и 'exception'.
    """
    pattern = re.compile(
        r'(Traceback \(most recent call last\):\n(?:^(?!Traceback \(most recent call last\):).*\n)*?)(^[\w.]+Error: .*)',
        re.MULTILINE
    )
    matches = pattern.findall(log_text)
    tracebacks = []
    for tb, exc in matches:
        tracebacks.append({
            'traceback': tb.strip(),
            'exception': exc.strip()
        })
    return tracebacks