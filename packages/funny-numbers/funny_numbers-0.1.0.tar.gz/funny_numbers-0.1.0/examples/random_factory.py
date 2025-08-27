from funny_numbers import RandomFunnyNumberFactory, FunnyNumber


def main() -> None:
    f = RandomFunnyNumberFactory([FunnyNumber(10, "test")])

    print(f)
    print(f.funny_numbers)
    print(f.get_one())
    print(f.get_many(10))
    print(f.get_many_unique(1))

    print(f.max)
    print(f.min)
    print(f.mean)
    print(f.variance)


if __name__ == "__main__":
    main()
