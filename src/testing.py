import hoffman_method as hm
import trace_hoffman_method as thm
from VARS import PATH_TO_TEST_FILES, PATH_TO_OUTPUT_FILES

# NT = No Trace (tracing)

def test_NT():
    hm.compress(f"{PATH_TO_TEST_FILES}sample1_short.txt", f"{PATH_TO_OUTPUT_FILES}sample1_short.huff")


if __name__ == "__main__":
    test_NT()