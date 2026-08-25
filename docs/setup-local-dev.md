# Setting Up Your Local Machine

This is a quick set of notes written to help you setup your development
environment. Ideally, you should not need to refer to these much, and should
use them mostly as a reference to various tools that will need to be installed
on your system.

This repository uses a lot of tools, mostly provided via the
[uv](https://docs.astral.sh/uv/) Python package and project manager.

## uv

`uv` has an [installation
guide](https://docs.astral.sh/uv/getting-started/installation/) which should
work for Mac, Windows and Linux.

Once you have `uv` installed, it can be used to manage the Python environment
along with most of the tools used in the project.

## Code Editor

The project should be agnostic to your code editor. Be it [Visual Studio
Code](https://code.visualstudio.com/), Vim, Emacs,
[PyCharm](https://www.jetbrains.com/pycharm/), or even Notepad.

As mentioned in the README,
[basedpyright](https://docs.basedpyright.com/latest/) is used for type
checking. You can use this in your IDE as an LSP by following the provided
[guides](https://docs.basedpyright.com/latest/installation/ides/).

## Git

The project uses [git](https://git-scm.com/). You should be familiar with its
use. Installation [guides](https://git-scm.com/install/) are provided on their
site.

### prek

[prek](https://prek.j178.dev/) is used for pre-commit hooks. The install of
this is explained in the README. It requires you have `uv` and `git` installed.
