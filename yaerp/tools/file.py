from contextlib import ContextDecorator
import logging

from .text import container2str

logging.basicConfig(level=logging.INFO)

class append_file(ContextDecorator):
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.content = []
        return self.content
        # logging.info('Entering: %s', self.name)

    def __exit__(self, exc_type, exc, exc_tb):
        with open(self.name, "a") as file:
            new_content = container2str(self.content)
            file.write(new_content)
            file.write('\n')
        # logging.info('Exiting: %s', self.name)

# with append_file("test.txt") as f:
#     f.append(2)
#     f.extend(["4353", {4:7}])
