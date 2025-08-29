#!/usr/bin/env python3
"""
Logic-LM Framework for MCP Server

This module implements the three-stage Logic-LM pipeline:
1. Problem Formulation: Translate natural language to symbolic program
2. Symbolic Reasoning: Execute with Clingo solver  
3. Result Interpretation: Translate back to natural language
"""

import re
from typing import Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path

try:
    import clingo
    CLINGO_AVAILABLE = True
except ImportError:
    CLINGO_AVAILABLE = False


@dataclass
class LogicResult:
    """Result from Logic-LM framework execution"""
    success: bool
    answer_sets: List[List[str]]
    solution_text: str = ""
    confidence: float = 0.0
    method: str = "asp_reasoning"
    error_message: Optional[str] = None
    asp_program: Optional[str] = None
    reasoning_trace: List[str] = None
    iteration_count: int = 0
    processing_time: float = 0.0
    solver_version: str = ""
    warnings: List[str] = None

    def __post_init__(self):
        if self.reasoning_trace is None:
            self.reasoning_trace = []
        if self.warnings is None:
            self.warnings = []


class ClingoSolver:
    """Wrapper for Clingo ASP solver with enhanced error handling"""
    
    def __init__(self, max_models: int = 10):
        self.max_models = max_models
        self.version = self._get_clingo_version()
    
    def _get_clingo_version(self) -> str:
        """Get Clingo version string"""
        if not CLINGO_AVAILABLE:
            return "not_available"
        try:
            return f"{clingo.__version__}"
        except:
            return "unknown"
    
    def is_available(self) -> bool:
        """Check if Clingo solver is available"""
        return CLINGO_AVAILABLE
    
    def solve_asp_program(self, program: str) -> LogicResult:
        """
        Solve ASP program and return structured results
        
        Args:
            program: ASP program as string
            
        Returns:
            LogicResult with solutions or error information
        """
        if not CLINGO_AVAILABLE:
            return LogicResult(
                success=False,
                answer_sets=[],
                error_message="Clingo not available. Install with: pip install clingo",
                asp_program=program
            )
        
        try:
            # Create Clingo control object
            ctl = clingo.Control(["--models", str(self.max_models)])
            
            # Add the program
            ctl.add("base", [], program)
            ctl.ground([("base", [])])
            
            # Collect answer sets
            answer_sets = []
            
            def on_model(model):
                atoms = [str(atom) for atom in model.symbols(shown=True)]
                answer_sets.append(sorted(atoms))
            
            # Solve
            result = ctl.solve(on_model=on_model)
            
            if result.satisfiable:
                return LogicResult(
                    success=True,
                    answer_sets=answer_sets,
                    asp_program=program,
                    solver_version=self.version,
                    confidence=0.95 if answer_sets else 0.0
                )
            else:
                return LogicResult(
                    success=False,
                    answer_sets=[],
                    error_message="No satisfiable answer sets found",
                    asp_program=program,
                    solver_version=self.version
                )
                
        except Exception as e:
            return LogicResult(
                success=False,
                answer_sets=[],
                error_message=f"Clingo error: {str(e)}",
                asp_program=program,
                solver_version=self.version
            )


class LogicFramework:
    """
    Main Logic-LM framework implementation with self-refinement
    """
    
    def __init__(self, max_refinement_iterations: int = 3):
        self.solver = ClingoSolver()
        self.max_refinement_iterations = max_refinement_iterations
    
    def check_solver_health(self) -> Dict[str, Union[bool, str, Dict]]:
        """
        Check Logic-LM server and Clingo solver health status
        
        Returns:
            Dictionary with health status information
        """
        health_status = {
            "server_status": "healthy",
            "clingo_available": CLINGO_AVAILABLE,
            "clingo_version": self.solver.version,
            "max_models": self.solver.max_models,
            "max_refinement_iterations": self.max_refinement_iterations,
            "components": {
                "solver": "available" if CLINGO_AVAILABLE else "unavailable",
                "framework": "initialized",
                "templates": "loaded"
            }
        }
        
        if CLINGO_AVAILABLE:
            # Test basic functionality
            try:
                test_program = "test_fact(a). #show test_fact/1."
                result = self.solver.solve_asp_program(test_program)
                health_status["basic_test"] = "passed" if result.success else "failed"
                if not result.success:
                    health_status["basic_test_error"] = result.error_message
            except Exception as e:
                health_status["basic_test"] = "failed"
                health_status["basic_test_error"] = str(e)
        else:
            health_status["installation_hint"] = "pip install clingo"
        
        return health_status
    
    def translate_natural_language_to_asp(self, natural_language_problem: str) -> str:
        """
        Stage 1: Generate LLM instructions for translating natural language to ASP
        
        This method returns instructions for the LLM to translate natural language
        into Answer Set Programming, referencing the comprehensive guidelines.
        """
        with open(Path(__file__).parent.parent / "docs" / "asp_logic_guidelines.md", 'r') as f:
            guidelines = f.read()
        
        instructions = f"""
You are tasked with translating a natural language logical problem into Answer Set Programming (ASP) format.

## PROBLEM TO TRANSLATE:
{natural_language_problem}

## ASP TRANSLATION GUIDELINES:
{guidelines}

## YOUR TASK:
1. Analyze the natural language problem carefully
2. Identify the logical structure (facts, rules, constraints, etc.)
3. Apply the appropriate ASP syntax patterns from the guidelines
4. Generate ONLY the ASP program code - no explanations or commentary
5. Ensure the program is syntactically correct and ready for Clingo solver
6. Include #show statements to display relevant predicates

## REQUIREMENTS:
- Use meaningful predicate names
- Define the domain explicitly when needed
- Include proper comments with % for clarity
- End statements with periods
- Use variables (uppercase) appropriately
- Add #show statements for query predicates

## OUTPUT FORMAT:
Return ONLY the ASP program code, nothing else. The program should be complete and ready for execution.
"""
        return instructions
    
    
    def refine_program_with_error(self, program: str, error_message: str, trace: List[str]) -> str:
        """
        Self-refinement: Fix ASP program based on solver error message
        """
        trace.append(f"Refinement needed: {error_message}")
        
        # Syntax error fixes
        if "syntax error" in error_message.lower():
            trace.append("Applying syntax error fixes")
            lines = program.split('\n')
            fixed_lines = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith('%') and not line.endswith('.') and not line.endswith('{') and not line.endswith('}'):
                    line += '.'
                fixed_lines.append(line)
            program = '\n'.join(fixed_lines)
        
        # Unbound variable fixes
        if "unbound variable" in error_message.lower() or "unsafe" in error_message.lower():
            trace.append("Applying variable binding fixes")
            var_match = re.search(r"variable ['\"](\w+)['\"]", error_message)
            if var_match:
                var_name = var_match.group(1)
                # Add domain restriction for the variable
                program = f"% Auto-fix for variable {var_name}\ndomain_element({var_name.lower()}).\n{program}"
        
        trace.append("Program refinement completed")
        return program
    
    def interpret_results(self, result: LogicResult, original_problem: str, trace: List[str]) -> str:
        """
        Stage 3: Interpret ASP results back to natural language
        """
        trace.append("Stage 3: Result Interpretation - converting ASP results to natural language")
        
        if not result.success:
            return f"Unable to solve the logical problem: {result.error_message}"
        
        if not result.answer_sets:
            return "The logical problem has no valid solutions under the given constraints."
        
        # Analyze answer sets and provide interpretation
        interpretation_parts = []
        
        for i, answer_set in enumerate(result.answer_sets):
            if len(result.answer_sets) > 1:
                interpretation_parts.append(f"Solution {i+1}:")
            
            # Group by predicate
            predicates = {}
            for atom in answer_set:
                if '(' in atom:
                    pred_name = atom.split('(')[0]
                    if pred_name not in predicates:
                        predicates[pred_name] = []
                    predicates[pred_name].append(atom)
                else:
                    # Propositional atom
                    if 'facts' not in predicates:
                        predicates['facts'] = []
                    predicates['facts'].append(atom)
            
            # Interpret common patterns
            for pred_name, atoms in predicates.items():
                if pred_name == 'can_fly':
                    entities = [atom.split('(')[1].rstrip(')') for atom in atoms]
                    interpretation_parts.append(f"The following can fly: {', '.join(entities)}")
                elif pred_name == 'mammal':
                    entities = [atom.split('(')[1].rstrip(')') for atom in atoms]
                    interpretation_parts.append(f"The following are mammals: {', '.join(entities)}")
                elif pred_name == 'facts':
                    interpretation_parts.append(f"Additional facts: {', '.join(atoms)}")
                else:
                    interpretation_parts.append(f"{pred_name.replace('_', ' ').title()}: {', '.join(atoms)}")
        
        if interpretation_parts:
            result_text = " ".join(interpretation_parts)
            trace.append(f"Generated interpretation: {result_text}")
            return result_text
        else:
            return "The logical reasoning completed successfully, but no specific conclusions could be drawn."
    
    
    def verify_asp_program(self, program: str, max_models: int = 10) -> LogicResult:
        """
        Directly verify and solve an ASP program
        
        Args:
            program: ASP program code to verify and solve
            max_models: Maximum number of models to find
            
        Returns:
            LogicResult with verification results
        """
        import time
        start_time = time.time()
        
        if not CLINGO_AVAILABLE:
            return LogicResult(
                success=False,
                answer_sets=[],
                error_message="Clingo not installed. Run: pip install clingo",
                asp_program=program,
                processing_time=time.time() - start_time
            )
        
        # Temporarily adjust solver max_models
        original_max_models = self.solver.max_models
        self.solver.max_models = max_models
        
        try:
            result = self.solver.solve_asp_program(program)
            result.processing_time = time.time() - start_time
            result.asp_program = program
            
            if result.success:
                result.solution_text = f"Found {len(result.answer_sets)} satisfiable model(s)"
                result.confidence = 1.0
            
            return result
        finally:
            # Restore original max_models
            self.solver.max_models = original_max_models