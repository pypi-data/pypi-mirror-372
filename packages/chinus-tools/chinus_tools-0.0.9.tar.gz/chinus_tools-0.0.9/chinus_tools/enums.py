from typing import get_origin, Literal, get_args
import copy

__all__ = ['Enum']


class _ImmutableWrapper:
    def __init__(self, attr_name):
        self._attr_name = attr_name

    def _raise_error(self, *args, **kwargs):
        raise AttributeError(f"Enum의 속성 '{self._attr_name}'의 내부는 수정할 수 없습니다.")


class ImmutableDict(dict, _ImmutableWrapper):
    """내부 값 수정을 막고 커스텀 에러를 발생시키는 딕셔너리"""

    # __init__ 메서드를 수정합니다.
    def __init__(self, attr_name, initial_data):
        # dict의 생성자를 명시적으로 호출하여 데이터를 채웁니다.
        dict.__init__(self, initial_data)
        # _ImmutableWrapper의 생성자를 명시적으로 호출하여 속성 이름을 저장합니다.
        _ImmutableWrapper.__init__(self, attr_name)

    def __deepcopy__(self, memo):
        """deepcopy 시, 불변 래퍼를 벗기고 일반 dict로 복사합니다."""
        # 순환 참조를 방지하기 위해 memo 딕셔너리를 사용합니다.
        if id(self) in memo:
            return memo[id(self)]

        # 새로운 '일반' 딕셔너리를 생성합니다.
        new_dict = dict()
        memo[id(self)] = new_dict

        # 내부의 값들을 재귀적으로 deepcopy하여 새 딕셔너리를 채웁니다.
        for k, v in self.items():
            new_dict[k] = copy.deepcopy(v, memo)

        return new_dict

    __setitem__ = _ImmutableWrapper._raise_error
    __delitem__ = _ImmutableWrapper._raise_error
    clear = _ImmutableWrapper._raise_error
    pop = _ImmutableWrapper._raise_error
    popitem = _ImmutableWrapper._raise_error
    setdefault = _ImmutableWrapper._raise_error
    update = _ImmutableWrapper._raise_error


class ImmutableList(list, _ImmutableWrapper):
    """내부 값 수정을 막고 커스텀 에러를 발생시키는 리스트"""

    # __init__ 메서드를 수정합니다.
    def __init__(self, attr_name, initial_data):
        # list의 생성자를 명시적으로 호출하여 데이터를 채웁니다.
        list.__init__(self, initial_data)
        # _ImmutableWrapper의 생성자를 명시적으로 호출하여 속성 이름을 저장합니다.
        _ImmutableWrapper.__init__(self, attr_name)

    def __deepcopy__(self, memo):
        """deepcopy 시, 불변 래퍼를 벗기고 일반 list로 복사합니다."""
        if id(self) in memo:
            return memo[id(self)]

        # 새로운 '일반' 리스트를 생성합니다.
        new_list = list()
        memo[id(self)] = new_list

        # 내부의 값들을 재귀적으로 deepcopy하여 새 리스트를 채웁니다.
        for item in self:
            new_list.append(copy.deepcopy(item, memo))

        return new_list

    __setitem__ = _ImmutableWrapper._raise_error
    __delitem__ = _ImmutableWrapper._raise_error
    append = _ImmutableWrapper._raise_error
    clear = _ImmutableWrapper._raise_error
    extend = _ImmutableWrapper._raise_error
    insert = _ImmutableWrapper._raise_error
    pop = _ImmutableWrapper._raise_error
    remove = _ImmutableWrapper._raise_error
    reverse = _ImmutableWrapper._raise_error
    sort = _ImmutableWrapper._raise_error


# --- 메타클래스와 변환 함수 ---

def _make_immutable_custom(obj, attr_name):
    if isinstance(obj, dict):
        processed_dict = {k: _make_immutable_custom(v, attr_name) for k, v in obj.items()}
        return ImmutableDict(attr_name, processed_dict)

    if isinstance(obj, list):
        processed_list = [_make_immutable_custom(item, attr_name) for item in obj]
        return ImmutableList(attr_name, processed_list)

    return obj


class NoReassign(type):
    def __new__(mcs, name, bases, attrs):
        immutable_attrs = {}
        for k, v in attrs.items():
            if k.startswith('__') and k.endswith('__'):
                immutable_attrs[k] = v
            else:
                immutable_attrs[k] = _make_immutable_custom(v, k)

        return super().__new__(mcs, name, bases, immutable_attrs)

    def __setattr__(cls, k, v):
        raise AttributeError(f"Enum의 속성 '{k}'는 재할당할 수 없습니다.")

    def __getattribute__(self, item):
        attr = object.__getattribute__(self, item)
        if get_origin(attr) is Literal:
            return list(get_args(attr))
        return attr


class Enum(metaclass=NoReassign):
    pass
