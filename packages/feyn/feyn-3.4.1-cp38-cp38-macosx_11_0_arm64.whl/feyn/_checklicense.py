from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
import nacl.encoding

from pathlib import Path

LICENSE_FILE_SEARCH_PATHS = [
    Path.home().joinpath(".config/.feynkey"),
    Path.home().joinpath(".config/feyn.key"),
    Path.home().joinpath(".feynkey"),
    Path.home().joinpath("feyn.key"),
]


def _find_license_file():
    existing_license_files = [x for x in LICENSE_FILE_SEARCH_PATHS if Path(x).exists()]

    if len(existing_license_files) > 1:
        raise ValueError(f"Multiple configuration files found: {[str(x) for x in existing_license_files]}.")

    if existing_license_files:
        return existing_license_files[0]

    return None

def read_license(filename:str = None) -> str:
    if filename is None:
        filename = _find_license_file()

    if filename is None:
        # No license found
        return None

    verify_key = VerifyKey(
        b"HtDcPfEkDiFWuSx2x2fcDnMRSO9u0UDOVyy7REvsOeU=",
        nacl.encoding.Base64Encoder
    )

    with open(filename,"rb") as f:
        signed_content = nacl.encoding.HexEncoder().decode(f.read().strip())

    try:
        content = verify_key.verify(signed_content)
    except BadSignatureError:
        raise Exception(f"Invalid license key found in {filename}")

    return content.decode("utf-8")


def verify_license():
    from feyn import _logger
    license_data = read_license()
    if license_data:
        _, name, org, _ = [elem.strip() for elem in license_data.split("\n", maxsplit=3)]
        _logger.info(
            f"This Feyn package and QLattice is licensed to {name}, {org}. "
            "By using this software you agree to the terms and conditions which can be found at https://abzu.ai/eula."
        )
    else:
        _logger.info(
            "This version of Feyn and the QLattice is available for academic, personal, and non-commercial use. "
            "By using the community version of this software you agree to the terms and conditions which can be found at https://abzu.ai/eula."
        )


if __name__ == "__main__":
    import sys
    if len(sys.argv) == 2:
        filename = sys.argv[1]
    else:
        filename = None

    print(read_license(filename))
