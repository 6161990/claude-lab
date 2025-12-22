# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a workshop repository for learning AI-assisted development workflows using Cursor and Claude Code. The repository contains:

- **Cursor Rules 14-step framework**: A structured prompt engineering methodology for full-stack development
- **Practice exercises**: Hands-on tutorials for prompt engineering techniques

## 언어 및 커뮤니케이션 규칙

- **기본 응답 언어**: 한국어
- **코드 주석**: 한국어로 작성
- **커밋 메시지**: 한국어로 작성
- **문서화**: 한국어로 작성
- **변수명/함수명**: 영어 (코드 표준 준수)

## Repository Structure

```
claude-lab/
├── workshop/
│   ├── Cursor_Rules_14steps/    # 14-step development process prompts (.mdc files)
│   │   ├── doc01-requirements.mdc              # Requirements definition
│   │   ├── doc02-adr.mdc                       # Architecture Decision Records
│   │   ├── doc03-database.mdc                  # Database design
│   │   ├── doc04-api-spec.mdc                  # API specifications
│   │   ├── doc05-ui-concept-prototype.mdc      # UI concept & prototyping
│   │   ├── doc06-detailed-design.mdc           # Detailed design (4+1 view)
│   │   ├── doc07-design-review-procedure.mdc   # Design review process
│   │   ├── doc08-prototype-analysis.mdc        # Prototype analysis
│   │   ├── doc09-implementation-plan.mdc       # Implementation planning
│   │   ├── doc10-implementation-generation.mdc # Code generation
│   │   ├── doc11-test-generation.mdc           # Test generation
│   │   ├── doc12-quality-assurance-validation.mdc # Quality assurance
│   │   ├── doc13-debug.mdc                     # Debugging assistance
│   │   └── doc14-ai-task-failure-analysis.mdc  # AI task failure analysis
│   └── practice/                # Practice exercises (Korean)
│       ├── 실습1-*.md           # Prompt engineering basics
│       └── 실습3-*.md           # Advanced exercises
```

## The 14-Step Development Framework

The Cursor Rules framework provides structured prompts for each phase of development:

### Design Phase (5 steps)
1. **Requirements Definition** - Transform user requests into actionable requirements
2. **Architecture Decisions** - Document technical choices and rationale (ADR)
3. **Database Design** - ER diagrams, normalization, schema definition
4. **API Specifications** - RESTful API design in OpenAPI format
5. **UI Prototyping** - Design system and component prototyping

### Detailed Design & Review (2 steps)
6. **Detailed Design** - System specifications using 4+1 view model
7. **Design Review** - Verify understanding and improve quality

### Analysis & Planning (2 steps)
8. **Prototype Analysis** - Evaluate production readiness using 5 quality axes (Security, Performance, Availability, Maintainability, Operability)
9. **Implementation Planning** - Staged production migration strategy

### Implementation & Testing (2 steps)
10. **Code Generation** - Generate production code from specifications
11. **Test Generation** - Create layered tests (unit, integration, E2E)

### Quality Assurance & Improvement (3 steps)
12. **Quality Validation** - Automated validation of design-implementation consistency
13. **Debugging** - Root cause analysis and systematic error resolution
14. **Failure Analysis** - Learn from AI task failures for continuous improvement

## Technology Stack (from framework documentation)

The framework is designed for these technologies, but can be adapted:

**Frontend:**
- Next.js 14+ (App Router), React, TypeScript
- shadcn/ui + Radix UI, Tailwind CSS
- Jest, React Testing Library, Cypress/Playwright

**Backend:**
- Python 3.8+, FastAPI, Pydantic, SQLAlchemy
- PostgreSQL (production), SQLite (development)
- pytest, pytest-mock, TestContainers

**DevOps:**
- Docker, Docker Compose
- Git, GitHub, CI/CD pipelines

**Design:**
- Mermaid diagrams, Figma API integration
- 4+1 view model, ADR documentation

## Working with .mdc Files

The `.mdc` files are Cursor-specific prompt templates. When referencing them in Cursor:

```
@doc01-requirements.mdc를 사용하여 다음 요구 사항을 분석하십시오.
[your requirements here]
```

For Claude Code users: these files contain structured prompts that define roles, tasks, and step-by-step instructions for each development phase. Read the relevant .mdc file to understand the methodology before applying it.

## Practice Exercises

The `workshop/practice/` directory contains Korean-language exercises:
- **실습1 series**: Basic prompt engineering patterns (Role-Task-Instructions format, few-shot examples, Chain-of-Thought)
- **실습3 series**: Advanced exercises including structured output, Python code examples

## Development Workflow Philosophy

This framework emphasizes:
- **Human-in-the-loop validation** at critical decision points
- **Incremental quality gates** - validate before proceeding to next phase
- **Documentation-driven development** - comprehensive design before implementation
- **Risk-based prioritization** - evaluate impact, probability, and effort
- **Prototype-to-production gap analysis** - systematic production readiness evaluation

## Key Principles

1. **Structured prompting**: Use Role-Task-Instructions format with examples
2. **Phase gates**: Complete design validation before implementation
3. **Quality metrics**: Maintain >90% coverage, >95% structural consistency
4. **Iterative refinement**: Each phase includes questioning and clarification steps
5. **Learning from failures**: Document and analyze AI task failures (doc14)
