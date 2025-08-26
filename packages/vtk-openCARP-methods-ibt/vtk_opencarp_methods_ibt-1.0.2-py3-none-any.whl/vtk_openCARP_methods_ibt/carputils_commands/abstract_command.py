from typing import List


class BaseCommand:
    """Base class for commands.

    This class serves as a base for implementing command-line interface commands.
    """

    def to_cmd(self) -> List:
        """Convert command to list of command line arguments.

        Returns
        -------
        List[str]
            List of command line arguments representing this command.

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this method.
        """
        raise NotImplementedError("to_cmd method must be implemented by subclass")

    def create_from_cmd_list(self, cmd_list: List) -> 'BaseCommand':
        """Create command from list of command line arguments.

        Parameters
        ----------
        cmd_list : List[str]
            List of command line arguments to parse.

        Returns
        -------
        BaseCommand
            New instance of command.

        Raises
        ------
        NotImplementedError
            If the subclass does not implement this method.
        """
        raise NotImplementedError("create_from_cmd_list method must be implemented by subclass")
