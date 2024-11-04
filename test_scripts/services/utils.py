from itertools import cycle
from typing import Generator, List, Tuple


def chunks(lst: list, chunk_size: int) -> Generator[list]:
    print(f"Splitting list in chunks of {chunk_size}...")
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i + chunk_size]


def get_identifier_digit_from_id_number(id_number: str) -> str:
    reversed_digits = map(int, reversed(str(id_number)))
    factors = cycle(range(2, 8))
    s = sum(d * f for d, f in zip(reversed_digits, factors))
    number = (-s) % 11
    if number > 9:
        return "k"
    return str(number)


def get_document_number_from_voultech_type_to_cl(document_number: str) -> str:
    number = document_number.split("/")[0]
    return f"{number}-{get_identifier_digit_from_id_number(number)}"


def get_document_number_from_cl_type_to_voultech(document_number: str) -> str:
    number = document_number.replace("-", "")[:-1]
    return f"{number}/60"


def get_document_number_without_chars(document_number: str) -> str:
    return document_number.replace("-", "").replace(".", "").replace(" ", "")


def get_document_number_with_dash(document_number: str) -> str:
    return f"{document_number[:-1]}-{document_number[-1]}"


def get_users_ruts_clean(users_ruts: List[str]) -> List[str]:
    users_ruts_clean = []
    for user_rut in users_ruts:
        user_rut_clean = user_rut.replace(".", "").replace("-", "")
        if "/" in user_rut_clean:
            user_rut_clean = user_rut_clean.split("/")[0]
            user_rut_clean = f"{user_rut_clean}{get_identifier_digit_from_id_number(user_rut_clean)}"

        users_ruts_clean.append(user_rut_clean)

    return users_ruts_clean


def find_approximate_values(
    ref_list: List[float],
    target_list: List[float],
    tolerance: float = 0.01,
    unique: bool = False,
) -> List[Tuple[float, float]]:
    approximate_pairs = []

    for idx, ref_value in enumerate(ref_list):
        for target_value in target_list:
            difference = abs(ref_value - target_value) / ref_value
            if difference <= tolerance:
                if unique and idx in [pair[0] for pair in approximate_pairs]:
                    continue
                approximate_pairs.append((idx, ref_value, target_value))

    return list(map(lambda x: (x[1], x[2]), approximate_pairs))
