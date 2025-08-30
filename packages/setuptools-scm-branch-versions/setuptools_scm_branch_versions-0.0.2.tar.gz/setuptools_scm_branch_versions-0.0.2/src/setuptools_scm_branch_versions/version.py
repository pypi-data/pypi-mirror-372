from setuptools_scm.version import ScmVersion, _parse_version_tag, guess_next_version


def branch_versions(version: ScmVersion) -> str:
    if version.exact:
        return version.format_with("{tag}")
    if version.branch is not None:
        # Does the branch name (stripped of namespace) parse as a version?
        branch_ver_data = _parse_version_tag(
            version.branch.split("/")[-1], version.config
        )
        if branch_ver_data is not None:
            branch_ver = branch_ver_data["version"]
            if branch_ver[0] == "v":
                # Allow branches that start with 'v', similar to Version.
                branch_ver = branch_ver[1:]
            branch_ver_split = branch_ver.split(".")
            tag_ver_up_to_branch_ver = str(version.tag).split(".")[
                : len(branch_ver_split)
            ]
            if branch_ver_split == tag_ver_up_to_branch_ver:
                # We're in a release/maintenance branch, next is a patch/rc/beta bump:
                return version.format_next_version(guess_next_version)
            else:
                return version.format_next_version(lambda *k, **kw: branch_ver)
    # We're not in a branch nor a tag, go back to default
    return version.format_next_version(guess_next_version)
