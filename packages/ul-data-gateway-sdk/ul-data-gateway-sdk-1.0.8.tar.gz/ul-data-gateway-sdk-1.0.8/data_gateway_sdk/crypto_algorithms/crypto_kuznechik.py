from data_gateway_sdk.crypto_algorithms.constants.constants_kuz import KUZNECHIK_KEY_LENGTH, KUZNECHIK_BLOCK_SIZE, GOST_PI, GOST_LVEC, GOST_PI_INV, ITER_CONST, MULT_TABLE
from data_gateway_sdk.crypto_algorithms.extensions.errors import KuznechikError
from data_gateway_sdk.crypto_algorithms.extensions.type_alias import Vector, VectorArray


def valid_kuznechik_key(key_bytes: bytes) -> int:
    """
    Валидация ключа шифрования (ключ размером 32 байта)
    """
    if len(key_bytes) == KUZNECHIK_KEY_LENGTH:
        return KUZNECHIK_KEY_LENGTH
    else:
        raise KuznechikError(f"invalid length KEY '{len(key_bytes)}' was given, must be '{KUZNECHIK_KEY_LENGTH}'")


def valid_kuznechik_payload(payload_bytes: bytes) -> int:
    """
    Валидация данных (размер блока 16 байт)
    """
    if len(payload_bytes) == KUZNECHIK_BLOCK_SIZE:
        return KUZNECHIK_BLOCK_SIZE
    else:
        raise KuznechikError(f"invalid length PAYLOAD '{len(payload_bytes)}' was given, must be '{KUZNECHIK_BLOCK_SIZE}'")


def kuz_x(array_a: Vector, array_b: Vector) -> Vector:
    """
    X преобразование. Операция наложения раундового ключа или побитовый XOR ключа и входного блока данных.
    """
    return [array_a[kuz_x_i] ^ array_b[kuz_x_i] for kuz_x_i in range(KUZNECHIK_BLOCK_SIZE)]


def kuz_s(in_data: Vector) -> Vector:
    """
    Нелинейное преобразование S, которое представляет собой простую замену одного байта на другой в соответствии с таблицей.
    """
    out_data: Vector = [0 for _ in range(KUZNECHIK_BLOCK_SIZE)]
    for kuz_s_i in range(KUZNECHIK_BLOCK_SIZE):
        out_data[kuz_s_i] = GOST_PI[in_data[kuz_s_i]]
    return out_data


def sum_field(array: Vector) -> int:
    """
    Вспомогательная функция суммирования всех элементов массива.
    """
    summary = 0
    for element in array:
        summary ^= element
    return summary


def kuz_gf_mul(value_a: int, value_b: int) -> int:
    """
    Вспомогательная функция умножения в поле Галуа
    по полиному  x^8+x^7+x^6+x+1.
    """
    constant = 0
    while value_a:
        if value_a & 1:
            constant ^= value_b
        if value_b & 0x80:
            value_b = (value_b << 1) ^ 0x1C3
        else:
            value_b <<= 1
        value_a >>= 1
    return constant


def l_func(array: Vector) -> int:
    """
    Линейное преобразование. Каждый байт из блока умножается в поле Галуа на один из коэффициентов ряда
    (148, 32, 133, 16, 194, 192, 1, 251, 1, 192, 194, 16, 133, 32, 148, 1)
    в зависимости от порядкового номера байта (ряд представлен для порядковых номеров от 15-ого до 0-ого, как представлено на рисунке).
    Байты складываются между собой по модулю 2, и все 16 байт блока сдвигаются в сторону младшего разряда,
    а полученное число записывается на место считанного байта.
    """
    multiplication = [MULT_TABLE[array[i]][GOST_LVEC[i]] for i in range(len(array))]
    return sum_field(multiplication)


def kuz_r(state: Vector) -> Vector:
    """
    Преобразование R сдвигает данные и реализует уравнение, представленное для расчета L-функции.
    """
    return [l_func(state)] + state[:-1]


def kuz_l(in_data: Vector) -> Vector:
    """
    Линейное преобразование.
    """
    internal = in_data
    for _ in range(KUZNECHIK_BLOCK_SIZE):
        internal = kuz_r(internal)
    return internal


def kuz_reverse_s(in_data: Vector) -> Vector:
    """
    Обратное S преобразовнаие.
    """
    out_data: Vector = [0 for _ in range(len(in_data))]
    for kuz_reverse_s_i in range(KUZNECHIK_BLOCK_SIZE):
        data = in_data[kuz_reverse_s_i]
        if data < 0:
            data = data + 256
        out_data[kuz_reverse_s_i] = GOST_PI_INV[data]
    return out_data


def kuz_reverse_r(state: Vector) -> Vector:
    """
    Обратное R преобразование.
    """
    return state[1:] + [l_func(state[1:] + [state[0]])]


def kuz_reverse_l(in_data: Vector) -> Vector:
    """
    Обратное L преобразование.
    """
    internal = in_data
    for _ in range(KUZNECHIK_BLOCK_SIZE):
        internal = kuz_reverse_r(internal)
    out_data = internal
    return out_data


def kuz_f(in_key: VectorArray, iter_const: Vector) -> VectorArray:
    """
    Функция, выполняющая преобразования ячейки Фейстеля.

    Блок разбивается на две равные части — левую L и правую R.
    Левый подблок L изменяется функцией f с использованием ключа K: X = f(L, K). В качестве функции может быть любое преобразование.
    Полученный подблок X складывается по модулю 2 с правым подблоком R, который остался без изменений: X = X + R.
    Полученные части меняются местами и склеиваются.

    """
    internal = kuz_x(in_key[0], iter_const)
    internal = kuz_s(internal)
    internal = kuz_l(internal)
    out_key_1 = kuz_x(internal, in_key[1])
    return [out_key_1, in_key[0]]


def kuz_expand_key(key: VectorArray) -> VectorArray:
    """
    Функция расчета раундовых ключей

    Итерационные (или раундовые) ключи получаются путем определенных преобразований на основе мастер-ключа,
    длина которого, как мы уже знаем, составляет 256 бит.
    Этот процесс начинается с разбиения мастер-ключа пополам, так получается первая пара раундовых ключей.
    Для генерации каждой последующей пары раундовых ключей применяется восемь итераций сети Фейстеля,
    в каждой итерации используется константа, которая вычисляется путем применения линейного преобразования алгоритма к значению номера итерации.
    """
    round_keys = []
    for expand_i in range(4):
        for k in range(8):
            key = kuz_f(key, ITER_CONST[k + 8 * expand_i])
        round_keys.append(key[0])
        round_keys.append(key[1])
    return round_keys


def _kuz_encrypt(block: Vector, round_keys: VectorArray) -> Vector:
    """
    Функция шифрования блока.
    """
    out_block = block
    for encrypt_i in range(9):
        out_block = kuz_x(round_keys[encrypt_i], out_block)
        out_block = kuz_s(out_block)
        out_block = kuz_l(out_block)
    out_block = kuz_x(out_block, round_keys[9])
    return out_block


def _kuz_decrypt(block: Vector, round_keys: VectorArray) -> Vector:
    """
    Функция расшифровки блока.
    """
    out_block = block
    for decrypt_i in range(9, 0, -1):
        out_block = kuz_x(round_keys[decrypt_i], out_block)
        out_block = kuz_reverse_l(out_block)
        out_block = kuz_reverse_s(out_block)
    out_block = kuz_x(out_block, round_keys[0])
    return out_block


def kuznechik_encryption(plain_text: bytes, key: bytes) -> bytes:
    """
    Обертка функции шифровки блока с разрезом ключа и валидацией входных данных.
    """
    valid_kuznechik_payload(plain_text)
    plain_text_list = list(plain_text)
    valid_kuznechik_key(key)
    key_list = list(key)

    round_key_enc = [key_list[:16], key_list[16:]]
    round_key_enc += kuz_expand_key(round_key_enc)
    result = _kuz_encrypt(plain_text_list, round_key_enc)
    return bytes(result)


def kuznechik_decryption(encrypted_text: bytes, key: bytes) -> bytes:
    """
    Обертка функции расшифровки блока с разрезом ключа и валидацией входных данных.
    """
    valid_kuznechik_payload(encrypted_text)
    encrypted_text_list = list(encrypted_text)
    valid_kuznechik_key(key)
    key_list = list(key)

    round_key_dec = [key_list[:16], key_list[16:]]
    round_key_dec += kuz_expand_key(round_key_dec)
    result = _kuz_decrypt(encrypted_text_list, round_key_dec)
    return bytes(result)
