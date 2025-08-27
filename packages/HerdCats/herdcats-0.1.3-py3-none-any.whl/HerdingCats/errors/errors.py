from typing import Optional


# TODO: Define better custom errors for each explorer and dataloader types
class CatSessionError(Exception):
    """
    Custom exception class for CatSession errors.
    Used when there are issues with establishing or maintaining catalogue sessions.
    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        original_error: Optional[Exception] = None,
    ) -> None:
        """
        Initialize the CatSession error with enhanced error information.

        Args:
            message: The main error message
            url: The URL that caused the error (if applicable)
            original_error: The original exception that was caught (if any)
        """
        self.message = message
        self.url = url
        self.original_error = original_error

        error_msg = f"{self.RED}[CatSession Error] 🐈: {message}{self.RESET}"

        if url:
            error_msg += f"\n{self.YELLOW}Failed URL: {url}{self.RESET}"

        if original_error:
            error_msg += (
                f"\n{self.YELLOW}Original error: {str(original_error)}{self.RESET}"
            )

        super().__init__(error_msg)

    def __str__(self) -> str:
        return self.args[0]


class CatExplorerError(Exception):
    pass


class OpenDataSoftExplorerError(Exception):
    """
    Custom exception class for OpenDataSoft Explorer errors.
    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def __init__(
        self, message: str, original_error: Optional[Exception] = None
    ) -> None:
        self.message = message
        self.original_error = original_error

        error_msg = f"{self.RED}OpenDataSoftExplorer Error 🐈‍⬛: {message}{self.RESET}"

        if original_error:
            error_msg += (
                f"\n{self.YELLOW}Original error: {str(original_error)}{self.RESET}"
            )

        super().__init__(error_msg)

    def __str__(self) -> str:
        return self.args[0]


class FrenchCatDataLoaderError(Exception):
    """
    Custom exception class for OpenDataSoft Explorer errors.
    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def __init__(
        self, message: str, original_error: Optional[Exception] = None
    ) -> None:
        self.message = message
        self.original_error = original_error

        error_msg = (
            f"{self.RED}FrenchCatDataLoaderError Error 🐈‍⬛: {message}{self.RESET}"
        )

        if original_error:
            error_msg += (
                f"\n{self.YELLOW}Original error: {str(original_error)}{self.RESET}"
            )

        super().__init__(error_msg)

    def __str__(self) -> str:
        return self.args[0]


class WrongCatalogueError(CatExplorerError):
    """
    Custom exception class for when the wrong catalogue type is used with an explorer.
    """

    RED = "\033[91m"
    YELLOW = "\033[93m"
    RESET = "\033[0m"

    def __init__(
        self,
        message: str,
        expected_catalogue: str,
        received_catalogue: Optional[str] = None,
    ) -> None:
        self.message = message
        self.expected_catalogue = expected_catalogue
        self.received_catalogue = received_catalogue

        error_msg = (
            f"{self.RED}[Wrong Catalogue Error]: {message}{self.RESET}\n"
            f"{self.YELLOW}Expected catalogue: {expected_catalogue}"
        )
        if received_catalogue:
            error_msg += f"\nReceived catalogue: {received_catalogue}"
        error_msg += f"{self.RESET}"

        super().__init__(error_msg)

    def __str__(self) -> str:
        return self.args[0]
