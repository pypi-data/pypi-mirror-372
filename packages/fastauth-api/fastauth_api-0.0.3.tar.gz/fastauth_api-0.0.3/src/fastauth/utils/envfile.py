import os


def write_key(key, name, file_path=".env", override: bool = True) -> None:
    base_dir = os.getcwd()
    file_path = os.path.join(base_dir, file_path)
    dir_path = "/".join(file_path.split("/")[:-1]) + os.path.sep
    
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            file.write("")

    # os.makedirs(os.path.dirname(dir_path), exist_ok=True)

    new_lines = []
    with open(file_path, "r+") as file:
        lines = file.readlines()
        crypto_line = False
        for line in lines:
            if line.replace(" ", "").startswith(name + "="):
                if override:
                    new_lines.append(f"{name}={key}\n")
                else:
                    new_lines.append(line)
                    print(
                        f"key with name = {name} already exist and `override arg` was marked as `False`"
                    )

                crypto_line = True
            else:
                new_lines.append(line)

        if not crypto_line:
            new_lines.append(f"{name}={key}")

    with open(file_path, "w") as file:
        file.writelines(new_lines)


def read_key(name, file_path=".env") -> str | None:
    base_dir = os.getcwd()
    file_path = os.path.join(base_dir, file_path)
    if not os.path.exists(file_path):
        return None

    with open(file_path, "r+") as file:
        lines = file.readlines()
        for line in lines:
            if line.startswith(name):
                spaces = 0
                for char in line[len(name) :]:
                    if char == "=" or char == " ":
                        spaces += 1
                    else:
                        return line[len(line) + spaces :]
    return None


def key_in(name, file_path=".env") -> bool:
    if os.path.exists(file_path) is False:
        return False

    with open(file_path, "r+") as file:
        lines = file.readlines()
        for line in lines:
            if line.replace(" ", "").startswith(name + "="):
                return True
    return False
