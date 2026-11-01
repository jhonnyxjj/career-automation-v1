from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProfilePreset:
    name: str
    seniorities: tuple[str, ...]
    technologies: tuple[str, ...]
    primary_languages: tuple[str, ...]
    frameworks: tuple[str, ...]
    databases: tuple[str, ...]
    cloud_devops: tuple[str, ...]


TECH_CATALOG: dict[str, tuple[str, tuple[str, ...]]] = {
    "TypeScript": ("language", ("typescript", "type script")),
    "JavaScript": ("language", ("javascript", "java script")),
    "C#": ("language", ("c#", "csharp", "c-sharp")),
    "Java": ("language", ("java",)),
    ".NET": ("framework", (".net", "dotnet", "asp.net", "aspnet")),
    "ASP.NET": ("framework", ("asp.net", "aspnet")),
    "Node.js": ("framework", ("node.js", "nodejs", "node")),
    "NestJS": ("framework", ("nestjs", "nest.js")),
    "Fastify": ("framework", ("fastify",)),
    "Express": ("framework", ("express", "expressjs")),
    "React": ("framework", ("react", "reactjs", "react.js")),
    "Next.js": ("framework", ("next.js", "nextjs")),
    "Spring": ("framework", ("spring",)),
    "Spring Boot": ("framework", ("spring boot", "springboot")),
    "PostgreSQL": ("database", ("postgresql", "postgres", "postgre")),
    "SQL": ("database", ("sql", "sql server", "mysql", "sqlite")),
    "Docker": ("cloud_devops", ("docker",)),
    "AWS": ("cloud_devops", ("aws", "amazon web services")),
    "Azure": ("cloud_devops", ("azure",)),
    "Kubernetes": ("cloud_devops", ("kubernetes", "k8s")),
    "Prisma": ("complementary", ("prisma",)),
}

PROFILE_PRESETS: dict[str, ProfilePreset] = {
    "TypeScript / JavaScript": ProfilePreset(
        name="TypeScript / JavaScript",
        seniorities=("intern", "junior", "mid"),
        technologies=(
            "TypeScript", "JavaScript", "Node.js", "NestJS", "Fastify", "Express",
            "React", "Next.js", "PostgreSQL", "Prisma", "AWS", "Docker",
        ),
        primary_languages=("TypeScript", "JavaScript"),
        frameworks=("Node.js", "NestJS", "Fastify", "Express", "React", "Next.js"),
        databases=("PostgreSQL",),
        cloud_devops=("AWS", "Docker"),
    ),
    "C# Junior": ProfilePreset(
        name="C# Junior",
        seniorities=("intern", "junior"),
        technologies=("C#", ".NET", "ASP.NET", "PostgreSQL", "SQL", "Docker", "Azure", "AWS"),
        primary_languages=("C#",),
        frameworks=(".NET", "ASP.NET"),
        databases=("PostgreSQL", "SQL"),
        cloud_devops=("Docker", "Azure", "AWS"),
    ),
    "Java Junior": ProfilePreset(
        name="Java Junior",
        seniorities=("intern", "junior"),
        technologies=("Java", "Spring", "Spring Boot", "PostgreSQL", "SQL", "Docker", "AWS"),
        primary_languages=("Java",),
        frameworks=("Spring", "Spring Boot"),
        databases=("PostgreSQL", "SQL"),
        cloud_devops=("Docker", "AWS"),
    ),
}


def get_profile(name: str) -> ProfilePreset:
    if name == "Todos":
        return ProfilePreset(
            name="Todos",
            seniorities=("intern", "junior", "mid"),
            technologies=tuple(TECH_CATALOG),
            primary_languages=("TypeScript", "JavaScript", "C#", "Java"),
            frameworks=tuple(name for name, (category, _) in TECH_CATALOG.items() if category == "framework"),
            databases=("PostgreSQL", "SQL"),
            cloud_devops=("Docker", "AWS", "Azure"),
        )
    return PROFILE_PRESETS[name]
