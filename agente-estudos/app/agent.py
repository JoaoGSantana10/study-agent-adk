# ruff: noqa
import datetime
import os
from pathlib import Path

from google.adk.agents import Agent
from google.adk.agents.readonly_context import ReadonlyContext
from google.adk.apps import App
from google.adk.environment import LocalEnvironment
from google.adk.models import Gemini
from google.adk.skills import load_skill_from_dir
from google.adk.tools.environment import EnvironmentToolset
from google.adk.tools.skill_toolset import SkillToolset
from google.genai import types

MODEL = os.environ.get("MODEL", "gemini-3.8-flash")

BASE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = BASE_DIR / "skills" / "plano-de-estudos"
PLANOS_DIR = BASE_DIR.parent / "planos"
PLANOS_DIR.mkdir(parents=True, exist_ok=True)


class FerramentasDeArquivo(EnvironmentToolset):
    """Toolset de ambiente filtrado para expor apenas ReadFile e WriteFile."""

    async def get_tools(self, readonly_context=None):
        tools = await super().get_tools(readonly_context)
        return [t for t in tools if t.name in ("ReadFile", "WriteFile")]


def get_instruction(context: ReadonlyContext | None = None) -> str:
    hoje = datetime.date.today()
    data_formatada = hoje.strftime("%Y-%m-%d")
    dia_semana = hoje.strftime("%A")
    return (
        f"A data de hoje é {data_formatada} ({dia_semana}).\n"
        "Você é um mentor especialista em estudos. Você ajuda estudantes a organizarem sua rotina e a criarem planos de estudo personalizados, "
        "com técnicas eficientes de aprendizagem, cronograma realista e exportação para calendário.\n"
        "Utilize a skill 'plano-de-estudos' e siga estritamente o seu fluxo de trabalho e as regras de gating.\n"
        "Para manipular arquivos de agenda, utilize as ferramentas ReadFile e WriteFile disponíveis no seu ambiente."
    )


skill_plano = load_skill_from_dir(SKILLS_DIR)
skill_toolset = SkillToolset(skills=[skill_plano])
ferramentas_arquivo = FerramentasDeArquivo(
    environment=LocalEnvironment(working_dir=PLANOS_DIR.resolve())
)

root_agent = Agent(
    name="agente_estudos",
    model=Gemini(
        model=MODEL,
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=get_instruction,
    tools=[skill_toolset, ferramentas_arquivo],
)

app = App(
    root_agent=root_agent,
    name="app",
)
