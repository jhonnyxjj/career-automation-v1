from career.latex import LaTeXRenderer
from career.models import ResumePersonalDetails, ResumeProject, ResumeTemplateData


def test_project_technologies_are_escaped_once():
    data = ResumeTemplateData(
        personal=ResumePersonalDetails(name="Pessoa"),
        projects=[ResumeProject(name="Projeto", technologies=["C#", "Node.js"])],
    )
    document = LaTeXRenderer().render_tex(data)
    assert r"\entrysub{C\# \textbullet\ Node.js}{}" in document
