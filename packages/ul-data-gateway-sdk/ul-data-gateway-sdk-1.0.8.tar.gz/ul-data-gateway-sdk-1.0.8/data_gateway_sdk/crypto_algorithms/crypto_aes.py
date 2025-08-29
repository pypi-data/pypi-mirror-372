from typing import Any, Iterable

from data_gateway_sdk.crypto_algorithms.constants.constants_aes import KEY_LENGTH_BYTES_AES256, KEY_LENGTH_BYTES_AES128, AES_BLOCK_SIZE, STRAIGHT_BOX, INVERSE_BOX
from data_gateway_sdk.crypto_algorithms.extensions.errors import AesError
from data_gateway_sdk.crypto_algorithms.extensions.type_alias import VectorArray, VectorArrayArray, Vector


def valid_aes_key(key_bytes: bytes) -> int:
    """
    Валидация ключа (проверка чтобы ключ был ровно 16 байт или 32 байта)
    """
    if len(key_bytes) == KEY_LENGTH_BYTES_AES256:
        return KEY_LENGTH_BYTES_AES256
    elif len(key_bytes) == KEY_LENGTH_BYTES_AES128:
        return KEY_LENGTH_BYTES_AES128
    else:
        raise AesError(f"invalid length KEY '{len(key_bytes)}' was given, must be '{KEY_LENGTH_BYTES_AES128}' or '{KEY_LENGTH_BYTES_AES256}'")


def add_round_key(state: VectorArray, key_schedule: VectorArrayArray, round_number: int) -> None:
    """
    Трансформация производит побитовый XOR каждого элемента из State с соответствующим элементом из RoundKey.

    RoundKey — массив такого же размера, как и State,
    который строится для каждого раунда на основе секретного ключа функцией KeyExpansion(), которую и рассмотрим далее.

    State — промежуточный результат шифрования,
    который может быть представлен как прямоугольный массив байтов имеющий 4 строки и Nb колонок.
    Каждая ячейка State содержит значение размером в 1 байт
    """
    round_key = key_schedule[round_number]
    for round_index in range(len(state)):
        state[round_index] = [state[round_index][constant] ^ round_key[round_index][constant] for constant in range(len(state[0]))]


def sub_bytes(state: VectorArray) -> None:
    """
    Преобразование представляет собой замену каждого байта из State на соответствующий ему из константной таблицы STRAIGHT_BOX.
    Значения элементов Sbox представлены в шестнадцатеричной системе счисления.
    """
    for round_index in range(len(state)):
        state[round_index] = [STRAIGHT_BOX[state[round_index][constant]] for constant in range(len(state[0]))]


def shift_rows(state: VectorArray) -> None:
    """
    Простая трансформация.
    Она выполняет циклический сдвиг влево на 1 элемент для первой строки, на 2 для второй и на 3 для третьей.
    Нулевая строка не сдвигается.

    пример:
    [00, 10, 20, 30]     [00, 10, 20, 30]
    [01, 11, 21, 31] --> [11, 21, 31, 01]
    [02, 12, 22, 32]     [22, 32, 02, 12]
    [03, 13, 23, 33]     [33, 03, 13, 23]
    """
    state[0][1], state[1][1], state[2][1], state[3][1] = state[1][1], state[2][1], state[3][1], state[0][1]
    state[0][2], state[1][2], state[2][2], state[3][2] = state[2][2], state[3][2], state[0][2], state[1][2]
    state[0][3], state[1][3], state[2][3], state[3][3] = state[3][3], state[0][3], state[1][3], state[2][3]


def xtime(value: int) -> int:
    """
    Функция, которая выполняет умножение на соответствующую константу в GF(28) по правилам.
    """
    if value & 0x80:
        return ((value << 1) ^ 0x1b) & 0xff
    return value << 1


def mix_column(column: Vector) -> None:
    """
    В рамках этой трансформации каждая колонка в State представляется в виде многочлена
    и перемножается в поле GF(2^8) по модулю x^4 + 1 с фиксированным многочленом 3x^3 + x^2 + x + 2.
    """
    column_zero = column[0]
    all_xor = column[0] ^ column[1] ^ column[2] ^ column[3]
    column[0] ^= all_xor ^ xtime(column[0] ^ column[1])
    column[1] ^= all_xor ^ xtime(column[1] ^ column[2])
    column[2] ^= all_xor ^ xtime(column[2] ^ column[3])
    column[3] ^= all_xor ^ xtime(column_zero ^ column[3])


def mix_columns(state: VectorArray) -> None:
    """
    В рамках этой трансформации каждая колонка в State представляется в виде многочлена
    и перемножается в поле GF(2^8) по модулю x^4 + 1 с фиксированным многочленом 3x^3 + x^2 + x + 2.

    Добавляет диффузию в шифр.
    """
    for round_index in state:
        mix_column(round_index)


def state_from_bytes(data: bytes) -> VectorArray:
    """
    Массив байтов преобразуется в прямоугольный массив State.
    """
    state = [data[i * 4:(i + 1) * 4] for i in range(len(data) // 4)]
    return state  # type: ignore


def bytes_from_state(state: VectorArray) -> bytes:
    """
    State превращается в массив байтов.
    """
    return bytes(state[0] + state[1] + state[2] + state[3])


def sub_word(word: Vector) -> bytes:
    """
    Функция для перестановки байт.
    """
    substituted_word = bytes(STRAIGHT_BOX[i] for i in word)
    return substituted_word


def rcon(i: int) -> bytes:
    """
    Rcon — константная таблица, значения которой в шестнадцатеричной системе счисления, определена для преобразований.
    """
    # From Wikipedia
    rcon_lookup = bytearray.fromhex('01020408102040801b36')
    rcon_value = bytes([rcon_lookup[i - 1], 0, 0, 0])
    return rcon_value


def xor_bytes(array_a: bytes, array_b: bytes) -> bytes:
    """
    Вспомогательная функция для перемножения двух массивов байт.
    """
    return bytes([array_a_value ^ array_b_value for (array_a_value, array_b_value) in zip(array_a, array_b)])


def rot_word(word: Vector) -> Vector:
    """
    Вспомогательная функция.
    """
    return word[1:] + word[:1]


def key_expansion(key: bytes, nb: int = 4) -> VectorArrayArray:
    """

    State — промежуточный результат шифрования, который может быть представлен как прямоугольный массив байтов
        имеющий 4 строки и Nb колонок. Каждая ячейка State содержит значение размером в 1 байт
    Nb — число столбцов (32-х битных слов), составляющих State. Для стандарта регламентировано Nb = 4
    Nk — длина ключа в 32-х битных словах. Для AES, Nk = 4, 6, 8. Мы уже определились, что будем использовать Nk = 4
    Nr — количество раундов шифрования. В зависимости от длины ключа, Nr = 10, 12 или 14


    Эта вспомогательная трансформация формирует набор раундовых ключей — KeySchedule.

    KeySchedule представляет собой длинную таблицу, состоящую из Nb*(Nr + 1) столбцов или (Nr + 1) блоков,
    каждый из которых равен по размеру State.
    Первый раундовый ключ заполняется на основе секретного ключа, который вы придумаете, по формуле:

    KeySchedule[r][c] = SecretKey[r + 4c], r = 0,1...4; c = 0,1..Nk.
    """
    nk = len(key) // 4
    key_bit_length = len(key) * 8

    if key_bit_length == 128:
        nr = 10
    elif key_bit_length == 192:
        nr = 12
    else:  # 256-bit keys
        nr = 14

    w = state_from_bytes(key)

    for i in range(nk, nb * (nr + 1)):
        temp = w[i - 1]
        if i % nk == 0:
            temp = xor_bytes(sub_word(rot_word(temp)), rcon(i // nk))  # type: ignore
        elif nk > 6 and i % nk == 4:
            temp = sub_word(temp)  # type: ignore
        w.append(xor_bytes(w[i - nk], temp))  # type: ignore

    return [w[i * 4:(i + 1) * 4] for i in range(len(w) // 4)]


def aes_encryption(data: bytes, key: bytes) -> bytes:
    """
    Функция шифровки.
    """
    valid_aes_key(key)
    key_bit_length = len(key) * 8

    if key_bit_length == 128:
        nr = 10
    elif key_bit_length == 192:
        nr = 12
    else:  # 256-bit keys
        nr = 14

    state = state_from_bytes(data)

    key_schedule = key_expansion(key)

    add_round_key(state, key_schedule, round_number=0)

    for round_numer in range(1, nr):
        sub_bytes(state)
        shift_rows(state)
        mix_columns(state)
        add_round_key(state, key_schedule, round_numer)

    sub_bytes(state)
    shift_rows(state)
    add_round_key(state, key_schedule, round_number=nr)

    cipher = bytes_from_state(state)
    return cipher


def inv_shift_rows(state: VectorArray) -> None:
    """
    Обратная функция циклического сдвига.

    пример:
    [00, 10, 20, 30]     [00, 10, 20, 30]
    [01, 11, 21, 31] <-- [11, 21, 31, 01]
    [02, 12, 22, 32]     [22, 32, 02, 12]
    [03, 13, 23, 33]     [33, 03, 13, 23]
    """
    state[1][1], state[2][1], state[3][1], state[0][1] = state[0][1], state[1][1], state[2][1], state[3][1]
    state[2][2], state[3][2], state[0][2], state[1][2] = state[0][2], state[1][2], state[2][2], state[3][2]
    state[3][3], state[0][3], state[1][3], state[2][3] = state[0][3], state[1][3], state[2][3], state[3][3]


def inv_sub_bytes(state: VectorArray) -> None:
    """
    Обратная функция замены.
    """
    for round_index in range(len(state)):
        state[round_index] = [INVERSE_BOX[state[round_index][constant]] for constant in range(len(state[0]))]


def xtimes_0e(b: int) -> int:
    """
    Вспомогательная функция, которая выполняет умножение на соответствующую константу в GF(2^8).
    """
    # 0x0e = 14 = b1110 = ((x * 2 + x) * 2 + x) * 2
    return xtime(xtime(xtime(b) ^ b) ^ b)


def xtimes_0b(b: int) -> int:
    """
    Вспомогательная функция, которая выполняет умножение на соответствующую константу в GF(2^8).
    """
    # 0x0b = 11 = b1011 = ((x*2)*2+x)*2+x
    return xtime(xtime(xtime(b)) ^ b) ^ b


def xtimes_0d(b: int) -> int:
    """
    Вспомогательная функция, которая выполняет умножение на соответствующую константу в GF(2^8).
    """
    # 0x0d = 13 = b1101 = ((x*2+x)*2)*2+x
    return xtime(xtime(xtime(b) ^ b)) ^ b


def xtimes_09(b: int) -> int:
    """
    Вспомогательная функция, которая выполняет умножение на соответствующую константу в GF(2^8).
    """
    # 0x09 = 9  = b1001 = ((x*2)*2)*2+x
    return xtime(xtime(xtime(b))) ^ b


def inv_mix_column(column: Vector) -> None:
    """
    Обратная функция преобразования в многочлен.
    """
    column_zero, column_1, column_2, column_3 = column[0], column[1], column[2], column[3]
    column[0] = xtimes_0e(column_zero) ^ xtimes_0b(column_1) ^ xtimes_0d(column_2) ^ xtimes_09(column_3)
    column[1] = xtimes_09(column_zero) ^ xtimes_0e(column_1) ^ xtimes_0b(column_2) ^ xtimes_0d(column_3)
    column[2] = xtimes_0d(column_zero) ^ xtimes_09(column_1) ^ xtimes_0e(column_2) ^ xtimes_0b(column_3)
    column[3] = xtimes_0b(column_zero) ^ xtimes_0d(column_1) ^ xtimes_09(column_2) ^ xtimes_0e(column_3)


def inv_mix_columns(state: VectorArray) -> None:
    """
    Обратная функция преобразования в многочлен.
    """
    for r in state:
        inv_mix_column(r)


def inv_mix_column_optimized(column: Vector) -> None:
    """
    Обратная функция преобразования в многочлен. Оптимизированная.
    """
    u = xtime(xtime(column[0] ^ column[2]))
    v = xtime(xtime(column[1] ^ column[3]))
    column[0] ^= u
    column[1] ^= v
    column[2] ^= u
    column[3] ^= v


def inv_mix_columns_optimized(state: VectorArray) -> None:
    """
    Обратная функция преобразования в многочлен. Оптимизированная.
    """
    for r in state:
        inv_mix_column_optimized(r)
    mix_columns(state)


def aes_decryption(cipher: bytes, key: bytes) -> bytes:
    """
    Функция расшифровки.
    """
    valid_aes_key(key)
    key_byte_length = len(key)
    key_bit_length = key_byte_length * 8
    # nk = key_byte_length // 4

    if key_bit_length == 128:
        nr = 10
    elif key_bit_length == 192:
        nr = 12
    else:  # 256-bit keys
        nr = 14

    state = state_from_bytes(cipher)
    key_schedule = key_expansion(key)
    add_round_key(state, key_schedule, round_number=nr)

    for round_index in range(nr - 1, 0, -1):
        inv_shift_rows(state)
        inv_sub_bytes(state)
        add_round_key(state, key_schedule, round_index)
        inv_mix_columns(state)

    inv_shift_rows(state)
    inv_sub_bytes(state)
    add_round_key(state, key_schedule, round_number=0)

    plain = bytes_from_state(state)
    return plain


def aes_ecb_encryption(plain: bytes, key: bytes) -> bytes:
    """
    Функция шифровки набора блоков по 16 байт.
    """
    cipher: Iterable[Any] = []
    valid_aes_key(key)

    for j in range(len(plain) // AES_BLOCK_SIZE):
        p_j = plain[j * AES_BLOCK_SIZE:(j + 1) * AES_BLOCK_SIZE]
        c_j = aes_encryption(p_j, key)
        cipher += c_j  # type: ignore
    return bytes(cipher)


def aes_ecb_decryption(cipher: bytes, key: bytes) -> bytes:
    """
    Функция расшифровки набора блоков по 16 байт.
    """
    plain: Iterable[Any] = list()
    valid_aes_key(key)

    for j in range(len(cipher) // AES_BLOCK_SIZE):
        c_j = cipher[j * AES_BLOCK_SIZE:(j + 1) * AES_BLOCK_SIZE]
        p_j = aes_decryption(c_j, key)
        plain += p_j  # type: ignore
    return bytes(plain)
