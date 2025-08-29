"""
Logic-LM MCP Server

A Model Context Protocol (MCP) server that provides symbolic reasoning capabilities
using Logic-LM framework and Answer Set Programming (ASP).
"""

__version__ = "1.0.1"

from .logic_framework import LogicFramework, LogicResult, ClingoSolver
from .asp_templates import ASPTemplateLibrary, ASPTemplate

__all__ = [
    "LogicFramework",
    "LogicResult", 
    "ClingoSolver",
    "ASPTemplateLibrary",
    "ASPTemplate"
]