import os

from code_context_analyzer.analyzer.repository_handler import RepositoryHandler


def test_local_path_resolution(tmp_path):
    for path in [tmp_path, "https://github.com/ahasanular/classScheduleMaker"]:
        handler = RepositoryHandler(default_branch="main")
        result = handler.resolve_source(str(path), branch="main")
        assert os.path.exists(result)
