#!/usr/bin/env python3
"""
ASP Templates for Common Logical Reasoning Patterns

This module provides templates for translating common logical structures
into Answer Set Programming format for use with Clingo.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass
class ASPTemplate:
    """Template for ASP program generation"""
    name: str
    description: str
    template: str
    variables: List[str]
    example: Optional[str] = None


class ASPTemplateLibrary:
    """Library of ASP templates for common reasoning patterns"""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, ASPTemplate]:
        """Initialize the template library"""
        templates = {}
        
        # Universal quantification: "All X are Y"
        templates["universal"] = ASPTemplate(
            name="universal",
            description="Universal quantification: All X are Y",
            template="""% Universal rule: All {subject} are {predicate}
{predicate}(X) :- {subject}(X).

% Facts about {subject}
{facts}

% Query
#show {predicate}/1.""",
            variables=["subject", "predicate", "facts"],
            example="All birds can fly"
        )
        
        # Conditional rules: "If X then Y"
        templates["conditional"] = ASPTemplate(
            name="conditional",
            description="Conditional rule: If X then Y",
            template="""% Conditional rule: If {condition} then {conclusion}
{conclusion} :- {condition}.

% Facts
{facts}

% Query
#show {conclusion}/0.
#show {condition}/0.""",
            variables=["condition", "conclusion", "facts"],
            example="If it's raining then the ground is wet"
        )
        
        # Syllogistic reasoning
        templates["syllogism"] = ASPTemplate(
            name="syllogism",
            description="Basic syllogistic reasoning pattern",
            template="""% Major premise: All {major_subject} are {major_predicate}
{major_predicate}(X) :- {major_subject}(X).

% Minor premise: {minor_subject} is a {major_subject}
{major_subject}({minor_subject}).

% Query: Is {minor_subject} a {major_predicate}?
#show {major_predicate}/1.""",
            variables=["major_subject", "major_predicate", "minor_subject"],
            example="All cats are mammals. Fluffy is a cat. Is Fluffy a mammal?"
        )
        
        # Existential quantification: "Some X are Y"
        templates["existential"] = ASPTemplate(
            name="existential",
            description="Existential quantification: Some X are Y",
            template="""% Domain elements
{domain}

% Some {subject} are {predicate}
{predicate}(X) :- {subject}(X), selected(X).

% Select at least one element
1 {{ selected(X) : {subject}(X) }}.

% Query
#show {predicate}/1.
#show selected/1.""",
            variables=["subject", "predicate", "domain"],
            example="Some birds are penguins"
        )
        
        # Negation patterns: "No X are Y"
        templates["negation"] = ASPTemplate(
            name="negation",
            description="Negation pattern: No X are Y",
            template="""% Facts about {subject}
{subject_facts}

% Facts about {predicate}
{predicate_facts}

% No {subject} are {predicate}
:- {subject}(X), {predicate}(X).

% Query
#show {subject}/1.
#show {predicate}/1.""",
            variables=["subject", "predicate", "subject_facts", "predicate_facts"],
            example="No mammals are cold-blooded"
        )
        
        # Set membership and relationships
        templates["set_membership"] = ASPTemplate(
            name="set_membership",
            description="Set membership and subset relationships",
            template="""% Set definitions
{set_definitions}

% Membership rules
member(X, {superset}) :- member(X, {subset}).

% Query: Show all memberships
#show member/2.""",
            variables=["set_definitions", "superset", "subset"],
            example="All elements in set A are also in set B"
        )
        
        # Transitive relationships
        templates["transitive"] = ASPTemplate(
            name="transitive",
            description="Transitive relationships: If aRb and bRc then aRc",
            template="""% Base relationships
{base_relations}

% Transitive rule
{relation}(X, Z) :- {relation}(X, Y), {relation}(Y, Z).

% Query
#show {relation}/2.""",
            variables=["relation", "base_relations"],
            example="If A is taller than B and B is taller than C, then A is taller than C"
        )
        
        return templates
    
    def get_template(self, template_name: str) -> Optional[ASPTemplate]:
        """Get a specific template by name"""
        return self.templates.get(template_name)
    
    def list_templates(self) -> List[str]:
        """List all available template names"""
        return list(self.templates.keys())
    
    def get_template_info(self, template_name: str) -> Optional[Dict[str, str]]:
        """Get information about a specific template"""
        template = self.templates.get(template_name)
        if template:
            return {
                "name": template.name,
                "description": template.description,
                "variables": template.variables,
                "example": template.example
            }
        return None
    
    def instantiate_template(self, template_name: str, bindings: Dict[str, str]) -> Optional[str]:
        """
        Instantiate a template with specific variable bindings
        
        Args:
            template_name: Name of the template to instantiate
            bindings: Dictionary mapping variable names to their values
            
        Returns:
            Instantiated ASP program or None if template not found
        """
        template = self.templates.get(template_name)
        if not template:
            return None
        
        program = template.template
        
        # Replace variables with bindings
        for variable in template.variables:
            if variable in bindings:
                program = program.replace(f"{{{variable}}}", bindings[variable])
        
        return program
    
    def find_suitable_template(self, problem_text: str) -> Optional[str]:
        """
        Find a suitable template based on problem text analysis
        
        Args:
            problem_text: Natural language problem description
            
        Returns:
            Template name or None if no suitable template found
        """
        problem_lower = problem_text.lower()
        
        # Pattern matching for template selection
        if "all" in problem_lower and ("are" in problem_lower or "can" in problem_lower):
            return "universal"
        elif "if" in problem_lower and "then" in problem_lower:
            return "conditional"
        elif ("some" in problem_lower or "at least one" in problem_lower) and "are" in problem_lower:
            return "existential"
        elif "no" in problem_lower and "are" in problem_lower:
            return "negation"
        elif any(word in problem_lower for word in ["therefore", "thus", "hence", "so"]):
            return "syllogism"
        elif "taller than" in problem_lower or "greater than" in problem_lower or "before" in problem_lower:
            return "transitive"
        elif "set" in problem_lower and ("member" in problem_lower or "element" in problem_lower):
            return "set_membership"
        
        # Default to universal quantification for basic logical statements
        return "universal"
    
    def get_all_templates_info(self) -> Dict[str, Dict[str, str]]:
        """Get information about all templates"""
        return {
            name: {
                "description": template.description,
                "variables": template.variables,
                "example": template.example
            }
            for name, template in self.templates.items()
        }


def demonstrate_templates():
    """Demonstrate the ASP template library usage"""
    library = ASPTemplateLibrary()
    
    print("Available ASP Templates:")
    print("=" * 40)
    
    for template_name in library.list_templates():
        template = library.get_template(template_name)
        print(f"\n{template.name.upper()}: {template.description}")
        if template.example:
            print(f"Example: {template.example}")
        print(f"Variables: {', '.join(template.variables)}")
    
    print("\n" + "=" * 40)
    print("Sample instantiation:")
    
    # Example instantiation
    bindings = {
        "major_subject": "cat",
        "major_predicate": "mammal", 
        "minor_subject": "fluffy"
    }
    
    program = library.instantiate_template("syllogism", bindings)
    if program:
        print("\nSyllogism template with bindings:")
        print(program)


if __name__ == "__main__":
    demonstrate_templates()