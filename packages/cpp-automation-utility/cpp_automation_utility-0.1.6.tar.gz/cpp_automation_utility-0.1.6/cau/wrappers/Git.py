"""Git wrapper around git commands."""
import logging
import pathlib

import attrs
import git

PathCollection = list[pathlib.Path]

logger = logging.getLogger("CAU")

#pylint: disable=too-few-public-methods
@attrs.define()
class Git:
    """Git wrapper class around commands to work with repository."""
    main_branch: pathlib.Path = attrs.field(
        factory=lambda: pathlib.Path("origin")/"main",
        converter=pathlib.Path,
        validator=attrs.validators.instance_of(pathlib.Path),
    )
    _repo = attrs.field(factory=lambda: git.Repo(pathlib.Path.cwd()), init=False, repr=False, eq=False)

    def changed_files(self) -> PathCollection:
        """
        Interrogates git to get a list of changed files between working directory and the remote main line branch.

        Returns:
            PathCollection: changed file paths
        """
        remote: git.Remote = self._repo.remote(name=str(self.main_branch.parent))
        logger.debug(remote.refs)

        if remote.refs:
            try:
                main: git.RemoteReference = next(ref for ref in remote.refs if str(self.main_branch) == ref.name)
            except StopIteration:
                logger.exception(
                    "Could not find the main branch!\n"
                    "If running in CI/CD, make sure the repository is setup to clone and not fetch.\n"
                    "Also, need to set the 'Git shallow clone' option to 0 to fetch all branches and tags.\n"
                    "Found remote references: %s",
                    remote.refs,
                )
                return []
            remote_head: git.Commit = self._repo.rev_parse(main.name)
            logger.debug("Mainline: %s, Remote head: %s", main.name, remote_head)
            diffs = set(remote_head.diff("HEAD") + self._repo.index.diff("HEAD") + self._repo.index.diff(None))
        else:
            diffs = set(self._repo.index.diff("HEAD") + self._repo.index.diff(None))

        paths = [_parse_diff(diff) for diff in list(diffs)]
        return [path for path in paths if path]

    def all_files(self) -> PathCollection:
        """
        Gets all files in git repo.

        Returns:
            PathCollection: file paths
        """
        return [pathlib.Path(path) for path in self._repo.git.ls_files().split()]

def _parse_diff(diff: git.Diff) -> pathlib.Path:
    """
    Based on the change type of the diff, take the file path of the appropriate side of the diff.

    Args:
        diff (git.Diff): git diff to parse

    Returns:
        pathlib.Path: path to modified file
    """
    if diff.change_type == "M":
        return pathlib.Path(diff.a_path)
    if diff.change_type in "AR":
        return pathlib.Path(diff.b_path)
    return None
