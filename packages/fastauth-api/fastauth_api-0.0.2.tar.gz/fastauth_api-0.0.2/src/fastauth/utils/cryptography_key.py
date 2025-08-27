from cryptography.fernet import Fernet

if __name__ == "__main__":
    from envfile import write_key, key_in
else:
    from .envfile import write_key, key_in

VAR_NAME = "CRYPTOGRAPHY_KEY"


def generate_cryptography_key(add2env: bool = True):
    """ """
    key = Fernet.generate_key().decode()
    keep = "no"
    if add2env:
        if key_in(VAR_NAME):
            keep = input(
                f"WARNING: This operation will be remplace the currently {VAR_NAME} value, this action can break your token database system based in your {VAR_NAME} value.\nTo continue the operation type (y/yes)."
            )
        else:
            keep = "y"

        if keep == "y" or keep == "yes":
            write_key(key=key, name=VAR_NAME)

    print(
        f"cryptography_key: {key}"
        + (" " if add2env and (keep == "y" or keep == "yes") else " not ")
        + "added to .env file"
    )
    return key


if __name__ == "__main__":
    generate_cryptography_key()
