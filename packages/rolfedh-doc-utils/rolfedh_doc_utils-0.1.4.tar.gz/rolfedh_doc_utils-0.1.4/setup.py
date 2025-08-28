#!/usr/bin/env python3
"""
Setup script for doc-utils package.
This file is only needed if we want to customize the installation process.
"""

from setuptools import setup
from setuptools.command.install import install
from setuptools.command.develop import develop
from setuptools.command.egg_info import egg_info

def custom_post_install():
    """Display safety message after installation."""
    print("\n" + "="*60)
    print("✅ doc-utils installed successfully!")
    print("\n⚠️  IMPORTANT: Safety First")
    print("   • Work in a git branch (never main/master)")
    print("   • Run without --archive first to preview") 
    print("   • Review changes with git diff")
    print("="*60 + "\n")

class CustomInstallCommand(install):
    """Customized setuptools install command."""
    def run(self):
        install.run(self)
        custom_post_install()

class CustomDevelopCommand(develop):
    """Customized setuptools develop command."""
    def run(self):
        develop.run(self)
        custom_post_install()

class CustomEggInfoCommand(egg_info):
    """Customized setuptools egg_info command."""
    def run(self):
        egg_info.run(self)

setup(
    cmdclass={
        'install': CustomInstallCommand,
        'develop': CustomDevelopCommand,
        'egg_info': CustomEggInfoCommand,
    },
)