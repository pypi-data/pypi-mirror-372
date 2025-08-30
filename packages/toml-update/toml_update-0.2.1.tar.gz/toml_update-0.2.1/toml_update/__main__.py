import toml_update
import subprocess

def main():

    result = subprocess.run(["pip", "freeze"], capture_output=True, text=True)

    if (result.returncode):
        raise RuntimeError(f"Some error occurred! It may be due to your pip.\
                           \nerror context : {result.stderr}")

    lines = result.stdout.splitlines()

    # ==을 >=로 바꾸기 (git 링크는 제외)
    converted: list[str] = []
    for line in lines:
        if "==" not in line:
            continue
        converted.append(line.replace("==", ">="))

    toml_update.set_dependencies(converted)

if __name__ == "__main__":
    main()