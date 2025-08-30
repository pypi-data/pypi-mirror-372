def set_dependencies(dependency_list: list[str], pyproject_path: str = "pyproject.toml"):
    # TOML 파일 읽기
    with open(pyproject_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # dependencies 항목 시작/끝 찾기
    start_idx = None
    end_idx: int | None = 0
    for i, line in enumerate(lines):
        if line.strip().startswith("dependencies"):
            start_idx = i
            break

    if start_idx is not None:
        # 기존 dependencies 끝 찾기
        for j in range(start_idx, len(lines)):
            if lines[j].strip().endswith("]"):
                end_idx = j
                break
        # 새 dependencies 문자열 생성
        new_deps = "dependencies = [\n" + "".join(f'    "{dep}",\n' for dep in dependency_list) + "]\n"
        # 기존 부분 대체
        lines[start_idx:end_idx+1] = [new_deps]
    else:
        # dependencies 항목이 없으면 새로 추가
        new_deps = "dependencies = [\n" + "".join(f'    "{dep}",\n' for dep in dependency_list) + "]\n"
        # [project] 섹션 끝에 추가
        for i, line in enumerate(lines):
            if line.strip() == "[project]":
                insert_idx = i + 1
                break
        else:
            insert_idx = len(lines)
        lines.insert(insert_idx, new_deps)

    # 파일에 다시 쓰기
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.writelines(lines)


if __name__ == "__main__":
    # 사용 예제
    deps: list[str] = []
    set_dependencies(deps)
