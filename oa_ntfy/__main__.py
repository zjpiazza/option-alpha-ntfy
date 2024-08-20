from dependency_injector.wiring import inject, Provide

from .services import OANtfyService
from .containers import Container
import argparse

# from .schemas import Settings


def main(mode: str, service: OANtfyService = Provide[Container.service]):
    if mode == "list_labels":
        service.list_gmail_labels()
    elif mode == "daemon":
        service.run()
    else:
        exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="A Python application with modes.")

    # Adding the 'mode' argument with 'daemon' as the default
    parser.add_argument(
        "--mode",  # Changed from '-m' to '--mode'
        type=str,
        choices=["daemon", "list_labels"],
        default="daemon",
        help='Mode of operation: "daemon" (default) or "list_labels"',
    )

    # Parse arguments
    args = parser.parse_args()

    container = Container()

    container.config.from_yaml("config.yml")

    container.init_resources()
    container.wire(modules=[__name__])
    main(mode=args.mode)
