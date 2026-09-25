from career.models import SearchProfile


def javascript_profile(**overrides) -> SearchProfile:
    values = {
        "name": "TypeScript / JavaScript",
        "allowed_seniorities": {"intern", "junior", "mid"},
        "allowed_workplaces": {"remote", "hybrid"},
        "role_areas": {"backend", "fullstack", "frontend"},
        "desired_technologies": {"TypeScript", "JavaScript", "Node.js", "PostgreSQL", "Prisma", "AWS", "Docker"},
        "primary_languages": {"TypeScript", "JavaScript"},
        "frameworks": {"Node.js"},
        "databases": {"PostgreSQL"},
        "cloud_devops": {"AWS", "Docker"},
    }
    values.update(overrides)
    return SearchProfile(**values)
