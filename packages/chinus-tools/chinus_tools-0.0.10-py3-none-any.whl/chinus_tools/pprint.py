import json


def pprint(data, *, indent: int = 2, default=lambda o: o.__dict__, pretty: bool = True) -> None:
    """
    JSON 직렬화 가능한 파이썬 객체를 예쁘게 출력합니다.
    """
    if not pretty:
        print(
            json.dumps(
                data,
                indent=indent,
                default=default,
            )
        )
        return None

    output_buffer = []
    # 성능을 위한 캐시. 일반적인 경우를 커버하기 위해 적당히 큰 크기로 설정.
    indent_cache = [" " * (i * indent) for i in range(100)]

    def _formatter(obj, level) -> None:
        # --- 1. 기본 타입 우선 처리 ---
        if isinstance(obj, str):
            output_buffer.append(json.dumps(obj))
            return
        if obj is True:
            output_buffer.append('true')
            return
        if obj is False:
            output_buffer.append('false')
            return
        if obj is None:
            output_buffer.append('null')
            return
        if isinstance(obj, (int, float)):
            output_buffer.append(str(obj))
            return

        # --- 2. 컬렉션 타입 확인 및 처리 ---
        # 이 블록 안에서만 len()을 호출하여 안전합니다.
        current_indent = indent_cache[level]
        next_indent = indent_cache[level + 1]

        if isinstance(obj, (list, tuple)):
            if not obj:
                output_buffer.append("[]")
                return
            if len(obj) == 1:
                output_buffer.append('[')
                _formatter(obj[0], level)
                output_buffer.append(']')
                return

            output_buffer.append('[\n')
            for i, item in enumerate(obj):
                if i > 0:
                    output_buffer.append(',\n')
                output_buffer.append(next_indent)
                _formatter(item, level + 1)
            output_buffer.append(f'\n{current_indent}]')
            return

        if isinstance(obj, dict):
            if not obj:
                output_buffer.append("{}")
                return
            if len(obj) == 1:
                key, value = next(iter(obj.items()))
                output_buffer.append('{')
                output_buffer.append(json.dumps(key))
                output_buffer.append(': ')
                _formatter(value, level)
                output_buffer.append('}')
                return

            output_buffer.append('{\n')
            for i, (key, value) in enumerate(obj.items()):
                if i > 0:
                    output_buffer.append(',\n')
                output_buffer.append(next_indent)
                output_buffer.append(json.dumps(key))
                output_buffer.append(': ')
                _formatter(value, level + 1)
            output_buffer.append(f'\n{current_indent}' + '}')
            return

        # --- 3. 위 모든 타입에 해당하지 않는 경우 (사용자 정의 객체 등) ---
        if default:
            # default 핸들러가 반환한 객체로 다시 포매팅 시도
            _formatter(default(obj), level)
        else:
            # default가 없으면 TypeError 발생
            raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")

    _formatter(data, 0)

    print("".join(output_buffer))

    return None
