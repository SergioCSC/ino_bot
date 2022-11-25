import config as cfg


def clear_inos(inos: dict[str, int]) -> dict[str, int]:
    cleared_inos = {name.strip(): post_id for name, post_id in inos.items()}
    if '' in cleared_inos:
        del cleared_inos['']
    return cleared_inos


def retrieve_inos() -> dict[str, int]:
    with open(cfg.INOS_FILENAME) as f:
        result = (ino.strip().split() for ino in f if ino.strip())
        result = (ino if len(ino) > 1 else (ino[0], -1) for ino in result)
        result = {name: int(post_id) for name, post_id in result}
        return result


def update_inos(new_inos: dict[str, int]) -> None:
    
    def rewrite_inos(inos: dict[str, int]) -> None:
        with open(cfg.INOS_FILENAME, 'w') as f:
            for ino_name, ino_post_id in inos.items():
                f.write(f'{ino_name} {ino_post_id}\n')

    old_inos = retrieve_inos()
    all_inos = old_inos | new_inos
    rewrite_inos(all_inos)
