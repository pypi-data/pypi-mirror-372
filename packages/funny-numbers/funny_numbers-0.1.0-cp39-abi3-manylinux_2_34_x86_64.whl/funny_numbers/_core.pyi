from typing import List, Optional, Sequence, Union

class FunnyNumber:
    """
    A representation of a 'funny number' with an associated explanation.

    This class provides an interface for working with numbers that are
    considered unusual, humorous, or noteworthy for some reason.
    """

    def __init__(self, number: Union[int, float], reason: str) -> None: ...
    @property
    def number(self) -> float:
        """
        Returns:
            `float`: The funny number provided at initialization.
        """
        ...

    @property
    def reason(self) -> str:
        """
        Returns:
            `str`: The reason why the funny number provided at initialization is considered funny.
        """
        ...

    def __repr__(self) -> str: ...

class DeterministicFunnyNumberFactory:
    """
    A factory that consistently produces the same funny number.
    """

    def __init__(self, funny_number: FunnyNumber) -> None:
        """
        Initializes the factory with a single FunnyNumber instance.

        Args:
            funny_number (`FunnyNumber`): The number that will be consistently produced by this factory.
        """
        ...

    @property
    def funny_number(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: The underlying funny number that this factory consistently produces.
        """
        ...

    @property
    def min(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: The minimum value produced by this factory.
        """
        ...

    @property
    def max(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: The maximum value produced by this factory.
        """
        ...

    @property
    def mean(self) -> float:
        """
        Returns:
            `float`: The mean of the numbers produced by this factory.
        """
        ...

    @property
    def variance(self) -> float:
        """
        Returns:
            `float`: The variance of the numbers produced by this factory.
        """
        ...

    def get_one(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: The single funny number associated with this factory.
        """
        ...

    def get_many(self, count: int) -> List[FunnyNumber]:
        """
        Produces a list containing multiple copies of the funny number.

        Args:
            count (`int`): The number of funny numbers to return.

        Returns:
            `List[FunnyNumber]`: A list of repeated instances of the funny number.
        """
        ...

    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...

class RandomFunnyNumberFactory:
    """
    A factory that can produce funny numbers at random from a given set.
    """

    def __init__(self, funny_numbers: Optional[Sequence[FunnyNumber]] = None) -> None:
        """
        Initializes the factory with an optional set of funny numbers.

        Args:
            funny_numbers (`Optional[Sequence[FunnyNumber]]`): An initial
            collection of funny numbers. If not provided, the factory fallsback onto a predefined list.
        """
        ...

    @property
    def funny_numbers(self) -> List[FunnyNumber]:
        """
        Returns:
            `List[FunnyNumber]`: The list of funny numbers produced by this factory.
        """
        ...

    @property
    def min(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: The minimum value produced by this factory.
        """
        ...

    @property
    def max(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: The maximum value produced by this factory.
        """
        ...

    @property
    def mean(self) -> float:
        """
        Returns:
            `float`: The mean of the numbers produced by this factory.
        """
        ...

    @property
    def variance(self) -> float:
        """
        Returns:
            `float`: The variance of the numbers produced by this factory.
        """
        ...

    def get_one(self) -> FunnyNumber:
        """
        Returns:
            `FunnyNumber`: A randomly selected funny number from the factory.
        """
        ...

    def get_many(self, count: int) -> List[FunnyNumber]:
        """
        Produces a list of funny numbers, each selected randomly
        (with replacement) from the factory.

        Args:
            count (`int`): The number of funny numbers to select.

        Returns:
            `List[FunnyNumber]`: A list of randomly selected funny numbers.
        """
        ...

    def get_many_unique(self, count: int) -> List[FunnyNumber]:
        """
        Produces a list of unique funny numbers selected randomly
        (without replacement) from the factory.

        Args:
            count (`int`): The number of unique funny numbers to select.

        Returns:
            `List[FunnyNumber]`: A list of unique randomly selected funny numbers.

        Raises:
            `ValueError`: If `count` exceeds the number of available funny numbers.
        """
        ...

    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
