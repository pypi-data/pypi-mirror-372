# ASP Logic Translation Guidelines

## Overview
This guide provides comprehensive instructions for translating natural language prompts into Answer Set Programming (ASP) logic statements. ASP uses a declarative approach where problems are described through logical rules and constraints.

## Core ASP Syntax Elements

### 1. Facts
**Purpose**: State unconditional truths
**Syntax**: `predicate(arguments).`

**Natural Language Patterns**:
- "X is Y" → `is(X, Y).`
- "X has property Y" → `has_property(X, Y).`
- "X is connected to Y" → `connected(X, Y).`

**Examples**:
- "Alice is a student" → `student(alice).`
- "Room 101 is on floor 2" → `on_floor(room101, 2).`
- "The sky is blue" → `color(sky, blue).`

### 2. Rules (Implications)
**Purpose**: Express conditional relationships
**Syntax**: `head :- body.`

**Natural Language Patterns**:
- "If X then Y" → `Y :- X.`
- "X implies Y" → `Y :- X.`
- "All X are Y" → `Y(Z) :- X(Z).`
- "X when Y" → `X :- Y.`

**Examples**:
- "If someone is a student, they need books" → `needs(X, books) :- student(X).`
- "A person is happy if they are healthy and wealthy" → `happy(X) :- healthy(X), wealthy(X).`
- "All birds can fly" → `can_fly(X) :- bird(X).`

### 3. Constraints
**Purpose**: Eliminate unwanted answer sets
**Syntax**: `:- body.`

**Natural Language Patterns**:
- "X cannot be Y" → `:- X, Y.`
- "It is impossible that X and Y" → `:- X, Y.`
- "X and Y are incompatible" → `:- X, Y.`
- "No X can be Y" → `:- X(Z), Y(Z).`

**Examples**:
- "A person cannot be both tall and short" → `:- tall(X), short(X).`
- "No student can fail and pass the same course" → `:- fail(X, Course), pass(X, Course).`
- "It's impossible to be in two places at once" → `:- at(X, Place1), at(X, Place2), Place1 != Place2.`

### 4. Choice Rules
**Purpose**: Express non-deterministic choices
**Syntax**: `{head} :- body.` or `L {head} U :- body.`

**Natural Language Patterns**:
- "X may be Y" → `{Y(X)}.`
- "Choose some X" → `{chosen(X) : item(X)}.`
- "Select between 1 and 3 items" → `1 {selected(X) : item(X)} 3.`
- "Optionally X" → `{X}.`

**Examples**:
- "A person may be tall" → `{tall(X)} :- person(X).`
- "Choose exactly one color for each object" → `1 {color(X, C) : color_option(C)} 1 :- object(X).`
- "Select at most 2 courses" → `{enrolled(X) : course(X)} 2.`

### 5. Negation as Failure
**Purpose**: Express absence of information
**Syntax**: `not predicate`

**Natural Language Patterns**:
- "X unless Y" → `X :- not Y.`
- "X if not Y" → `X :- not Y.`
- "X by default" → `X :- not -X.` (with explicit negative)
- "Assume X unless proven otherwise" → `X :- not -X.`

**Examples**:
- "Birds fly unless they are penguins" → `flies(X) :- bird(X), not penguin(X).`
- "A student passes unless they fail" → `pass(X) :- student(X), not fail(X).`
- "Assume innocent unless proven guilty" → `innocent(X) :- person(X), not guilty(X).`

### 6. Disjunctive Rules
**Purpose**: Express alternative conclusions
**Syntax**: `head1; head2; ... :- body.`

**Natural Language Patterns**:
- "X or Y" → `X; Y.`
- "Either X or Y must be true" → `X; Y :- condition.`
- "X can be Y or Z" → `Y(X); Z(X) :- condition.`

**Examples**:
- "A traffic light is red, yellow, or green" → `red(X); yellow(X); green(X) :- traffic_light(X).`
- "A student either passes or fails" → `pass(X); fail(X) :- student(X), took_exam(X).`

### 7. Aggregates
**Purpose**: Express counting, summing, and other aggregate operations
**Syntax**: `#count{...}`, `#sum{...}`, `#max{...}`, etc.

**Natural Language Patterns**:
- "Count the number of X" → `#count{Y : X(Y)}`
- "Sum of all X" → `#sum{N,Y : X(Y,N)}`
- "At least N X exist" → `N #count{Y : X(Y)}.`
- "The total cost is C" → `cost(C) :- C = #sum{Price,X : item(X,Price), selected(X)}.`

**Examples**:
- "Each class has at most 30 students" → `:- class(C), #count{S : enrolled(S,C)} > 30.`
- "The total budget is 1000" → `budget(1000) :- #sum{Cost,X : expense(X,Cost)} = 1000.`
- "At least 5 people must attend" → `:- #count{P : attending(P)} < 5.`

### 8. Weak Constraints (Optimization)
**Purpose**: Express preferences and optimization goals
**Syntax**: `:~ body. [weight@level]`

**Natural Language Patterns**:
- "Prefer X over Y" → `:~ Y. [1@1]` (penalize Y)
- "Minimize X" → `:~ X. [1@1]`
- "It's better to have X" → `:~ not X. [1@1]`
- "Avoid X if possible" → `:~ X. [weight@level]`

**Examples**:
- "Prefer shorter routes" → `:~ route(R), length(R,L). [L@1]`
- "Minimize the number of conflicts" → `:~ conflict(X,Y). [1@1]`
- "Try to satisfy all preferences" → `:~ preference(X), not satisfied(X). [1@1]`

## Advanced Constructs

### 9. Conditional Literals
**Syntax**: `literal : condition`

**Examples**:
- "For each student in a class, assign a grade" → `grade(S,G) : student_in_class(S,C), grade_option(G)`

### 10. Anonymous Variables
**Syntax**: `_` (underscore)

**Use when**: Variable appears only once and its specific value doesn't matter
**Example**: "Someone is tall" → `tall(_).`

### 11. Arithmetic Operations
**Operators**: `+`, `-`, `*`, `/`, `\`, `**`, `|X|` (absolute value)
**Comparisons**: `=`, `!=`, `<`, `<=`, `>`, `>=`

**Examples**:
- "Age must be at least 18" → `:- person(X), age(X,A), A < 18.`
- "Total is the sum of parts" → `total(T) :- T = A + B, part1(A), part2(B).`

## Translation Strategies

### 1. Identify Statement Type
- **Fact**: Unconditional statement
- **Rule**: Conditional relationship
- **Constraint**: Prohibition or requirement
- **Choice**: Optional or alternative selection
- **Optimization**: Preference or goal

### 2. Handle Quantification
- **Universal** ("all", "every"): Use variables in rules
- **Existential** ("some", "there exists"): Use facts or choice rules
- **Numerical** ("at least 3", "exactly 2"): Use aggregates

### 3. Manage Negation
- **Explicit negation**: Use separate predicates (e.g., `tall(X)` vs `short(X)`)
- **Negation as failure**: Use `not` for default assumptions
- **Strong negation**: Use `-` for explicit falsity (less common)

### 4. Domain Definition
Always define the domain of discourse:
```asp
% Define entities
person(alice; bob; charlie).
course(math; physics; chemistry).
```

## Common Translation Patterns

### Scheduling Problems
- "X cannot happen at the same time as Y" → `:- scheduled(X,T), scheduled(Y,T), X != Y.`
- "Each task needs exactly one time slot" → `1 {scheduled(T,S) : slot(S)} 1 :- task(T).`

### Assignment Problems  
- "Each person gets exactly one role" → `1 {assigned(P,R) : role(R)} 1 :- person(P).`
- "No role can be assigned to more than one person" → `:- assigned(P1,R), assigned(P2,R), P1 != P2.`

### Graph Problems
- "There is a path from X to Y" → `path(X,Y) :- edge(X,Y). path(X,Y) :- edge(X,Z), path(Z,Y).`
- "X and Y are connected" → `connected(X,Y) :- path(X,Y). connected(X,Y) :- path(Y,X).`

### Resource Allocation
- "Don't exceed capacity" → `:- resource(R), #sum{Amount,X : uses(X,R,Amount)} > capacity(R,Cap), capacity(R,Cap).`
- "Meet minimum requirements" → `:- requirement(R,Min), #sum{Amount,X : provides(X,R,Amount)} < Min.`

## Best Practices

1. **Use meaningful predicate names**: `enrolled(student, course)` rather than `p(X,Y)`
2. **Define domains explicitly**: List all entities that can appear in predicates
3. **Check for typos**: ASP treats `student(alice)` and `students(alice)` as different
4. **Use comments**: `% This rule assigns grades to students`
5. **Test constraints**: Verify that constraints eliminate unwanted solutions
6. **Order matters in some contexts**: Place domain definitions before rules that use them

## Debugging Tips

1. **Start simple**: Begin with basic facts and rules, then add complexity
2. **Use show statements**: `#show predicate/arity.` to display specific predicates
3. **Check satisfiability**: Ensure your constraints don't make the problem unsatisfiable
4. **Verify domains**: Make sure all referenced entities are defined
5. **Test edge cases**: Consider boundary conditions and special cases

This guideline provides a framework for systematically translating natural language requirements into precise ASP logic statements, covering all major constructs and common patterns encountered in logic programming tasks.