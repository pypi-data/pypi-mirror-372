from amsatop.htop.htop_mock import HtopMock
from amsatop.tui import HtopTUI


def main():
    htop = HtopMock()
    app = HtopTUI(htop=htop)
    app.run()


if __name__ == "__main__":
    main()
