from dependency_injector.wiring import inject, Provide

from .services import Service
from .containers import Container
# from .schemas import Settings

def main(service: Service = Provide[Container.service]):
    service.run()

if __name__ == "__main__":
    # from simplegmail import Gmail

    # gmail = Gmail()

    # labels = gmail.list_labels()
    # for label in labels:
    #     print(f"{label.name} / {label.id}")

    container = Container()

    container.config.from_yaml("config.yml")

    container.init_resources()
    container.wire(modules=[__name__])
    main()