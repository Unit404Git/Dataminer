# processor.py
import time
from tqdm import tqdm
import converter.bigman as bigman


def process_directory(directory: str):
    """
    Return:
      total: int               # number of progress steps
      iterator: iterable[str]  # yields human-readable progress messages
    Replace the dummy loop with your real logic.
    """

    bigman.main(directory)

    # Example: pretend work over 50 steps
    total = 50

    def iterator():
        # You can structure this exactly like your current tqdm loops
        for i in tqdm(range(total), desc="Processing", unit="step"):
            # Simulate work
            time.sleep(0.05)
            # Emit a short status message (filename, phase, etc.)
            yield f"Processing step {i + 1}"

    return total, iterator()
