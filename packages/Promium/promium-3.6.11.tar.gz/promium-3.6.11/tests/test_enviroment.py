import os
import sys
import subprocess
import shutil
import pytest


class EnvironmentException(Exception):
    pass


def run_command(command):
    print(f"Running command: {command}")
    process = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    if process.returncode != 0:
        print(process.stdout.decode())
        print(process.stderr.decode())
        raise EnvironmentException(f"Failed to run command: {command}")

    return process


@pytest.fixture
def docs_fixture(scope="function"):
    with open("version", "w") as version_file:
        version_file.write("13.666.2")

    yield

    os.chdir("/work")
    if os.path.exists("doc/_build"):
        shutil.rmtree("doc/_build", ignore_errors=True)
    if os.path.exists("version"):
        os.remove("version")
    if os.path.exists("dist"):
        shutil.rmtree("dist", ignore_errors=True)
    if os.path.exists("Promium.egg-info"):
        shutil.rmtree("Promium.egg-info", ignore_errors=True)


class TestEnvironment:
    @pytest.mark.env
    @pytest.mark.skip("pass")
    def test_check_doc_command(self, docs_fixture):
        run_command(["sphinx-build", "-b", "html", "doc", "public"])
        assert os.path.exists("public/index.html"), "Not Create doc files"

    @pytest.mark.env
    def test_check_publish(self, docs_fixture):
        run_command(["python", "setup.py", "sdist"])
        run_command(["python", "-m", "twine", "check", "dist/*"])
