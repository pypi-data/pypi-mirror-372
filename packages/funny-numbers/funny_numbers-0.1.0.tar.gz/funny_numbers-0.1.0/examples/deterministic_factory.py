from funny_numbers import DeterministicFunnyNumberFactory, FunnyNumber


def main() -> None:
    funny_number = FunnyNumber(10, "sexy")

    f = DeterministicFunnyNumberFactory(funny_number)

    print(f)
    print(f.funny_number)
    print(f.get_one())
    print(f.get_many(10))

    print(f.max)
    print(f.min)
    print(f.mean)
    print(f.variance)


if __name__ == "__main__":
    main()
