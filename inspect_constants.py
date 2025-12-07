from pywhispercpp import constants

try:
    print("PARAMS_SCHEMA keys:")
    print(list(constants.PARAMS_SCHEMA.keys()))
except Exception as e:
    print(f"Error: {e}")
