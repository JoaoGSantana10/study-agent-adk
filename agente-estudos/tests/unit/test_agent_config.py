import datetime
import os
import pytest
from app.agent import FerramentasDeArquivo, get_instruction, root_agent, MODEL, PLANOS_DIR, SKILLS_DIR
from google.adk.tools.skill_toolset import SkillToolset


def test_model_name():
    expected_model = os.environ.get("MODEL", "gemini-3.8-flash")
    assert MODEL == expected_model
    assert root_agent.model.model == expected_model


def test_instruction_contains_today():
    today_str = datetime.date.today().strftime("%Y-%m-%d")
    inst = get_instruction()
    assert today_str in inst
    assert "plano-de-estudos" in inst


def test_toolsets_configured():
    toolset_types = [type(t) for t in root_agent.tools]
    assert SkillToolset in toolset_types
    assert FerramentasDeArquivo in toolset_types


@pytest.mark.asyncio
async def test_file_tools_filter():
    file_toolset = next(t for t in root_agent.tools if isinstance(t, FerramentasDeArquivo))
    tools = await file_toolset.get_tools()
    tool_names = [t.name for t in tools]
    assert set(tool_names) == {"ReadFile", "WriteFile"}


@pytest.mark.asyncio
async def test_write_and_read_file_tool():
    file_toolset = next(t for t in root_agent.tools if isinstance(t, FerramentasDeArquivo))
    tools = {t.name: t for t in await file_toolset.get_tools()}
    write_tool = tools["WriteFile"]
    read_tool = tools["ReadFile"]

    test_filename = "test_run.csv"
    test_content = "Subject,Start Date\nTeste,2026-11-05"

    # Simula tool execution
    res = await write_tool.run_async(args={"path": test_filename, "content": test_content}, tool_context=None)
    assert res.get("status") == "ok", f"Erro na escrita: {res}"

    read_res = await read_tool.run_async(args={"path": test_filename}, tool_context=None)
    assert read_res.get("status") == "ok", f"Erro na leitura: {read_res}"
    assert "Subject,Start Date" in read_res.get("content", "")

    # Cleanup
    (PLANOS_DIR / test_filename).unlink(missing_ok=True)


def test_paths():
    assert SKILLS_DIR.exists()
    assert (SKILLS_DIR / "SKILL.md").exists()
    assert PLANOS_DIR.exists()
