# Python‑агент, работающий с DeepSeek API и управляющий стадиями CI/CD.
import os
import re
import json
import subprocess
import requests

from langchain import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from functools import wraps

load_dotenv()

def handle_errors(default_msg: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except subprocess.CalledProcessError as e:
                err = e.output.decode() if e.output else str(e)
                return f"{default_msg} (code {e.returncode}): {err}"
        return wrapper
    return decorator

def parse_response(text: str) -> list:
    cleaned = re.sub(r"```\w*", "", text).strip()
    return json.loads(cleaned)

def get_plan(task_description: str) -> list[dict]:
    prompt_template = PromptTemplate(
        input_variables=['task_description'],
        template=(
            "You are an AI assistant that translates a CI/CD task into a list of tool actions. "
            "Available operations: git(pull|push|commit:message), test, build(tag), deploy(tag). "
            "Respond with a JSON array of objects: [{{\"action\":..., \"args\":...}}, ...]."
            "----\n"
            "{task_description}\n"
        )
    )    

    llm = ChatOpenAI(
        model_name="deepseek-chat",
        base_url='https://api.proxyapi.ru/deepseek',
        api_key=os.getenv("PROXYAPI_KEY"),
        temperature=0.7
    )

    prompt = prompt_template.format(task_description=task_description)
    response = llm.invoke(prompt)

    content = response.content.strip()
    return parse_response(content)

@handle_errors("Tests execution failed")
def run_tests() -> str:
    return subprocess.check_output(['pytest', '-q'], stderr=subprocess.STDOUT).decode()

@handle_errors("Docker compose failed")
def run_docker_compose() -> str:
    """Run Docker Compose."""
    return subprocess.check_output(['docker-compose', 'up', '-d'], stderr=subprocess.STDOUT).decode()

@handle_errors("Git operation failed")
def git_operations(args) -> str:
    """Perform git actions: pull, push, commit."""
    if isinstance(args, str) and args.startswith("commit"):
        msg = args.split(":", 1)[1].strip().strip("'\"")
        try:
            subprocess.check_call(['git', 'add', '.'])
            return subprocess.check_output(
                #['git', 'commit', '-m', msg],
                #stderr=subprocess.STDOUT
            ).decode()
        except subprocess.CalledProcessError as e:
            err = e.output.decode() if e.output else str(e)
            return f"Git commit failed (code {e.returncode}): {err}"

    if args == 'pull':
        # return subprocess.check_output(['git', 'pull'], stderr=subprocess.STDOUT).decode()
        return subprocess.check_output(['git', '-C', 'src/', 'pull', 'https://github.com/kostinvv/career-assistant-bot', 'main'], stderr=subprocess.STDOUT).decode()

    if args == 'push':
        return subprocess.check_output(['git', 'push'], stderr=subprocess.STDOUT).decode()
    return f"Unknown git action: {args}"

def execute_plan(plan: list) -> None:
    print(f'{plan=}')
    for step in plan:
        action = step.get('action')
        args = step.get('args')
        # Normalize args if list
        if isinstance(args, list) and args:
            args = args[0]

        if isinstance(args, str) and "=" in args:
            key, val = args.split("=", 1)
            if key == "tag":
                args = val

        print(f"==> {action} {args}")

        if action == 'git':
            print(git_operations(args))
        elif action == 'test':
            print(run_tests())
        elif action == 'deploy':
            print(run_docker_compose())
        else:
            print(f"Unknown action: {action}")         

def main():
    # Чтение задач из README.md
    with open("README.md", "r", encoding="utf-8") as f:
        readme_content = f.read()

    # Извлекаем только текст между <!-- LLM_INSTRUCTION_START --> и <!-- LLM_INSTRUCTION_END -->
    match = re.search(r'<!-- LLM_INSTRUCTION_START -->(.*?)<!-- LLM_INSTRUCTION_END -->', readme_content, re.DOTALL)
    task = match.group(1).strip() if match else ""

    plan = get_plan(task)
    execute_plan(plan)

if __name__ == '__main__':
    main()

