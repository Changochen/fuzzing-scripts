"""Nox sessions for the project.
"""
import nox


@nox.session
def test(session):
  if session.posargs:
    session.run("pytest", "--disable-warnings", "-k", *session.posargs, external=True)
  else:
    session.run("pytest", "-n", "auto", "--disable-warnings", external=True)


@nox.session
def format(session):  # pylint: disable=redefined-builtin
  session.run("yapf", "-i", "-p", "--recursive", "srcs", "tests", "noxfile.py", external=True)
  session.notify("lint")


@nox.session
def format_check(session):
  assert session.run("yapf",
                     "-d",
                     "-p",
                     "--recursive",
                     "srcs",
                     "tests",
                     "noxfile.py",
                     external=True)


@nox.session
def lint(session):
  session.run("pylint", "./srcs", "./tests", external=True)
  session.notify("type_check")


@nox.session
def type_check(session):
  session.run("mypy", "./srcs", "./tests", external=True)
  session.run("pyright", "./srcs", "./tests", external=True)
  #session.notify("pytype_check")


@nox.session
def pytype_check(session):
  session.run("pytype", "./srcs", "./tests", external=True)


@nox.session
def cov(session):
  session.run("pytest",
              "--cov=src",
              "--cov-report",
              "term-missing",
              "-n",
              "auto",
              "--disable-warnings",
              external=True)


@nox.session
def commit(session):
  session.run("git", "add", ".", external=True)
  session.run("git", "commit", "-m", f"\"{session.posargs[0]}\"", external=True)


@nox.session
def push(session):
  session.run("git", "push", "-u", "origin", "HEAD", external=True)
