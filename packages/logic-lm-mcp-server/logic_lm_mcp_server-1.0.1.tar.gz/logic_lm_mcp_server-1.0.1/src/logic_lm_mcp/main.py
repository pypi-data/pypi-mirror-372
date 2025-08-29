#!/usr/bin/env python3
"""
Logic-LM MCP Server

A Model Context Protocol (MCP) server that provides symbolic reasoning capabilities
using Logic-LM framework and Answer Set Programming (ASP).
"""

import asyncio
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from fastmcp import FastMCP

from .logic_framework import LogicFramework, LogicResult
from .asp_templates import ASPTemplateLibrary


# Initialize the MCP server
mcp = FastMCP("Logic-LM Reasoning Server")

# Initialize the Logic-LM framework
logic_framework = LogicFramework()
template_library = ASPTemplateLibrary()

# Global cache for ASP guidelines to avoid repeated large context injection
_asp_guidelines_cache = None



# Input/Output Models
class LogicalProblemInput(BaseModel):
    """Input model for solve_logical_problem tool"""
    problem: str = Field(..., description="Natural language logical problem to solve", min_length=5)
    max_iterations: int = Field(default=3, ge=1, le=10, description="Maximum self-refinement iterations")
    include_asp_program: bool = Field(default=False, description="Include generated ASP program in response")
    include_trace: bool = Field(default=False, description="Include detailed reasoning trace")


class ASPProgramInput(BaseModel):
    """Input model for verify_asp_program tool"""
    program: str = Field(..., description="ASP program code to verify and solve", min_length=10)
    max_models: int = Field(default=10, ge=1, le=100, description="Maximum number of models to find")


class LogicalProblemOutput(BaseModel):
    """Output model for logical reasoning results"""
    success: bool = Field(..., description="Whether the reasoning was successful")
    solution: Optional[str] = Field(None, description="Natural language solution")
    confidence: float = Field(0.0, ge=0.0, le=1.0, description="Confidence score (0-1)")
    method: str = Field("asp_reasoning", description="Reasoning method used")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    warnings: list[str] = Field(default_factory=list, description="Warning messages")
    debug_info: Optional[Dict[str, Any]] = Field(None, description="Debug information (optional)")


class ASPVerificationOutput(BaseModel):
    """Output model for ASP program verification"""
    success: bool = Field(..., description="Whether the ASP program was satisfiable")
    models: list[list[str]] = Field(default_factory=list, description="Found answer sets/models")
    model_count: int = Field(0, description="Number of models found")
    error_message: Optional[str] = Field(None, description="Error message if verification failed")
    solver_info: Dict[str, Any] = Field(default_factory=dict, description="Solver information")


class HealthCheckOutput(BaseModel):
    """Output model for health check"""
    server_status: str = Field(..., description="Overall server status")
    clingo_available: bool = Field(..., description="Whether Clingo solver is available")
    components: Dict[str, str] = Field(..., description="Status of individual components")
    capabilities: Dict[str, Any] = Field(default_factory=dict, description="Server capabilities")
    recommendations: list[str] = Field(default_factory=list, description="Setup recommendations")




def format_logic_result(result: LogicResult, include_asp: bool = False, include_trace: bool = False) -> LogicalProblemOutput:
    """Convert LogicResult to standardized output format"""
    
    metadata = {
        "solver_version": result.solver_version,
        "processing_time": result.processing_time,
        "iteration_count": result.iteration_count
    }
    
    debug_info = None
    if include_asp or include_trace:
        debug_info = {}
        if include_asp and result.asp_program:
            debug_info["asp_program"] = result.asp_program
        if include_trace and result.reasoning_trace:
            debug_info["reasoning_trace"] = result.reasoning_trace
    
    return LogicalProblemOutput(
        success=result.success,
        solution=result.solution_text if result.success else None,
        confidence=result.confidence,
        method=result.method,
        metadata=metadata,
        warnings=result.warnings or [],
        debug_info=debug_info
    )


@mcp.tool()
async def get_asp_guidelines() -> str:
    """
    Get comprehensive ASP translation guidelines (cached for efficiency).
    
    Returns the complete ASP Logic Translation Guidelines document that provides
    comprehensive instructions for translating natural language into Answer Set
    Programming format. This is cached to avoid repeated context consumption.
    """
    global _asp_guidelines_cache
    
    if _asp_guidelines_cache is None:
        try:
            from pathlib import Path
            guidelines_path = Path(__file__).parent.parent / "docs" / "asp_logic_guidelines.md"
            with open(guidelines_path, 'r') as f:
                _asp_guidelines_cache = f.read()
        except Exception as e:
            return f"Error loading ASP guidelines: {str(e)}"
    
    return _asp_guidelines_cache


@mcp.tool()
async def translate_to_asp_instructions(
    problem: str
) -> LogicalProblemOutput:
    """
    Get lightweight instructions for translating a specific natural language problem to ASP.
    
    This tool provides concise, problem-specific instructions for LLM-based ASP translation.
    For full guidelines, call get_asp_guidelines() first (cached for efficiency).
    
    Examples:
    - "All cats are mammals. Fluffy is a cat. Therefore, is Fluffy a mammal?"
    - "If it's raining, then the ground is wet. It's raining. Is the ground wet?"
    - "All birds can fly. Penguins are birds. Can penguins fly?"
    
    Args:
        problem: Natural language logical problem to translate
    """
    try:
        # Validate parameters
        if len(problem.strip()) < 5:
            return LogicalProblemOutput(
                success=False,
                solution=None,
                confidence=0.0,
                method="validation_error",
                metadata={},
                warnings=["Problem must be at least 5 characters long"]
            )
        
        # Generate lightweight, problem-specific instructions
        instructions = f"""TRANSLATE TO ASP: {problem}

INSTRUCTIONS:
1. If you haven't already, call get_asp_guidelines() for complete translation patterns
2. Analyze this problem for logical structure (facts, rules, constraints)
3. Apply appropriate ASP syntax from guidelines:
   - Facts: unconditional statements → predicate(args).
   - Rules: "All X are Y" → Y(Z) :- X(Z).
   - Constraints: "X cannot Y" → :- X, Y.
4. Use meaningful predicates, define domains, add comments
5. Include #show statements for query results
6. Return ONLY the ASP code

Then use verify_asp_program() to execute the generated ASP code.
"""
        
        # Return the lightweight instructions
        return LogicalProblemOutput(
            success=True,
            solution=instructions,
            confidence=1.0,
            method="lightweight_translation_instructions", 
            metadata={
                "problem_length": len(problem),
                "guidelines_cached": _asp_guidelines_cache is not None,
                "next_steps": ["Call get_asp_guidelines() if needed", "Generate ASP code", "Call verify_asp_program()"]
            },
            warnings=[]
        )
        
    except Exception as e:
        return LogicalProblemOutput(
            success=False,
            solution=None,
            confidence=0.0,
            method="error_handling",
            metadata={"error_type": type(e).__name__},
            warnings=[f"Unexpected error: {str(e)}"]
        )


@mcp.tool()
async def verify_asp_program(
    program: str,
    max_models: int = 10
) -> ASPVerificationOutput:
    """
    Directly verify and solve an ASP program using the Clingo solver.
    
    This tool allows direct input of Answer Set Programming code for verification
    and solution finding. Useful for testing ASP programs or working with
    pre-formulated logical constraints.
    
    Example ASP program:
    ```
    % Facts
    cat(fluffy).
    cat(whiskers).
    
    % Rule: All cats are mammals
    mammal(X) :- cat(X).
    
    % Query
    #show mammal/1.
    ```
    
    Args:
        program: ASP program code to verify and solve
        max_models: Maximum number of models to find (1-100)
    """
    try:
        # Validate parameters
        if len(program.strip()) < 10:
            return ASPVerificationOutput(
                success=False,
                models=[],
                model_count=0,
                error_message="ASP program must be at least 10 characters long",
                solver_info={"validation_error": True}
            )
        
        if not (1 <= max_models <= 100):
            max_models = 10
        
        # Verify the ASP program
        result = logic_framework.verify_asp_program(
            program=program,
            max_models=max_models
        )
        
        return ASPVerificationOutput(
            success=result.success,
            models=result.answer_sets,
            model_count=len(result.answer_sets),
            error_message=result.error_message if not result.success else None,
            solver_info={
                "solver_version": result.solver_version,
                "processing_time": result.processing_time,
                "max_models_requested": max_models
            }
        )
        
    except Exception as e:
        return ASPVerificationOutput(
            success=False,
            models=[],
            model_count=0,
            error_message=f"Verification failed: {str(e)}",
            solver_info={"error_type": type(e).__name__}
        )


@mcp.tool()
async def check_solver_health() -> HealthCheckOutput:
    """
    Check Logic-LM server and Clingo solver health status.
    
    Returns comprehensive health information including:
    - Server status and component initialization
    - Clingo solver availability and version
    - System capabilities and configuration
    - Basic functionality test results
    - Setup recommendations if issues are detected
    """
    try:
        # Get health status from the Logic-LM framework
        health_data = logic_framework.check_solver_health()
        
        # Build recommendations
        recommendations = []
        if not health_data.get("clingo_available", False):
            recommendations.append("Install Clingo solver: pip install clingo")
        
        if health_data.get("basic_test") == "failed":
            recommendations.append("Clingo solver test failed - check installation")
        
        if not recommendations:
            recommendations.append("System is healthy and ready for logical reasoning")
        
        # Build capabilities info
        capabilities = {
            "max_refinement_iterations": health_data.get("max_refinement_iterations", 3),
            "max_models": health_data.get("max_models", 10),
            "supported_reasoning_types": [
                "syllogistic_reasoning",
                "conditional_logic", 
                "universal_quantification",
                "constraint_satisfaction"
            ],
            "template_count": len(template_library.list_templates()),
            "available_templates": template_library.list_templates()
        }
        
        return HealthCheckOutput(
            server_status=health_data.get("server_status", "unknown"),
            clingo_available=health_data.get("clingo_available", False),
            components=health_data.get("components", {}),
            capabilities=capabilities,
            recommendations=recommendations
        )
        
    except Exception as e:
        return HealthCheckOutput(
            server_status="error",
            clingo_available=False,
            components={"framework": "error", "solver": "error"},
            capabilities={},
            recommendations=[f"Health check failed: {str(e)}", "Check server configuration and dependencies"]
        )




# Resource: ASP Template Library
@mcp.resource(
    uri="logic://templates",
    name="ASP Template Library",
    description="Collection of Answer Set Programming templates for logical reasoning",
    mime_type="application/json"
)
async def get_template_library() -> dict:
    """Get complete ASP template library"""
    try:
        templates = template_library.list_templates()
        result = {
            "templates": [],
            "count": len(templates)
        }
        
        for template_name in templates:
            info = template_library.get_template_info(template_name)
            template = template_library.get_template(template_name)
            if info and template:
                result["templates"].append({
                    "name": template_name,
                    "description": info["description"],
                    "variables": info["variables"],
                    "example": info.get("example", ""),
                    "template_code": template.template
                })
        
        return result
    except Exception as e:
        return {"error": f"Failed to load templates: {str(e)}", "templates": [], "count": 0}

@mcp.resource(
    uri="logic://template/{name}",
    name="Individual ASP Template",
    description="Get specific ASP template by name",
    mime_type="text/plain"
)
async def get_individual_template(name: str) -> str:
    """Get specific ASP template code"""
    try:
        template = template_library.get_template(name)
        if template:
            info = template_library.get_template_info(name)
            header = f"% Template: {name}\n% Description: {info['description']}\n% Variables: {', '.join(info['variables'])}\n\n"
            return header + template.template
        else:
            return f"% Template '{name}' not found\n% Available templates: {', '.join(template_library.list_templates())}"
    except Exception as e:
        return f"% Error loading template: {str(e)}"

@mcp.resource(
    uri="logic://health",
    name="Server Health Status",
    description="Logic-LM MCP server health and diagnostic information",
    mime_type="application/json"
)
async def get_server_health() -> dict:
    """Get server health status"""
    try:
        return logic_framework.check_solver_health()
    except Exception as e:
        return {"error": str(e), "status": "unhealthy"}




def main():
    """Run the Logic-LM MCP server"""
    print("Starting Logic-LM MCP Server...")
    
    # Display server information
    health = logic_framework.check_solver_health()
    print(f"Server Status: {health.get('server_status', 'unknown')}")
    print(f"Clingo Available: {health.get('clingo_available', False)}")
    print(f"Available Templates: {len(template_library.list_templates())}")
    
    if not health.get('clingo_available', False):
        print("\nWARNING: Clingo solver not available!")
        print("Install with: pip install clingo")
        print("Server will run with limited functionality.")
    
    print("\nTools available:")
    print("- solve_logical_problem: Natural language logical reasoning")
    print("- verify_asp_program: Direct ASP program verification") 
    print("- check_solver_health: System health and diagnostics")
    print("\nResources available:")
    print("- logic://templates: Complete ASP template library")
    print("- logic://template/{name}: Individual ASP templates")
    print("- logic://health: Server health and diagnostic information")
    
    print("\nStarting MCP server on stdio...")
    mcp.run()


if __name__ == "__main__":
    main()