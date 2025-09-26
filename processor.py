import time
from tqdm import tqdm
import bigman


def process_directory(directory: str):
    """
    Stub processor.
    Replace this with your actual logic.
    Must return:
      - total iterations
      - generator that yields progress messages
    """

    bigman.main(directory)

    # Example: pretend there are 10 steps
    total = 10

    def generator():
        for i in tqdm(range(total), desc="Processing"):
            time.sleep(0.3)  # simulate work
            yield f"Step {i+1}/{total} done"

    return total, generator()
