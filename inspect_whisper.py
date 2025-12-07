import inspect
from pywhispercpp.model import Model

try:
    print("Signature of Model.transcribe:")
    print(inspect.signature(Model.transcribe))
    print("\nDocstring:")
    print(Model.transcribe.__doc__)
except Exception as e:
    print(f"Error: {e}")
