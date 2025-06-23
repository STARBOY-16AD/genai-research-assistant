import pkg_resources

print("\n📦 Checking installed packages from requirements.txt:\n")

with open("requirements.txt") as f:
    requirements = pkg_resources.parse_requirements(f)
    for req in requirements:
        # Skip comments or empty lines
        if "#" in str(req) or str(req).strip() == "":
            continue
        try:
            pkg_resources.require(str(req))
            print(f"{req} ✅ Installed and Compatible")
        except pkg_resources.DistributionNotFound:
            print(f"{req} ❌ Not Installed")
        except pkg_resources.VersionConflict as e:
            print(f"{req} ⚠️ Version conflict: Installed {e.dist.version}, Required {e.req}")
