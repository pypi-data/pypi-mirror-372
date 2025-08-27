from argparse import ArgumentParser


def main():
    from . import __version__

    parser = ArgumentParser('assman', description="Work in progress.")
    parser.add_argument('--version', action='version', version=__version__)
    parser.parse_args()

    print("Hello, World!")


if __name__ == '__main__':
    main()
