from hive_cli.config import HiveConfig

from .base import Platform


class OnPremPlatform(Platform):
    def __init__(self, name: str):
        super().__init__(name)

    def create(self, config: HiveConfig):
        print(f"Creating hive on-premise with name: {self.experiment_name} and config: {config}")

    def update(self, name: str, config: HiveConfig):
        print(f"Updating hive on-premise with name: {name} and config: {config}")

    def delete(self, name: str):
        print("Deleting hive on-premise...")

    def login(self, args):
        print("Logging in to hive on-premise...")

    def show_experiments(self, args):
        print("Showing experiments on-premise...")

    def show_dashboard(self, args):
        print("Showing dashboard on-premise...")
