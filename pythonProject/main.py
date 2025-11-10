def is_valid_brackets(s: str) -> bool:

    stack = []
    # Сопоставление закрывающих скобок с открывающими
    mapping = {')': '(', '}': '{', ']': '['}

    for char in s:
        if char in mapping.values():  # открывающая скобка
            stack.append(char)
        elif char in mapping:  # закрывающая скобка
            if not stack or stack[-1] != mapping[char]:
                return False  # либо стек пуст, либо скобка не совпадает
            stack.pop()  # удаляем совпавшую открывающую
        else:
            # на всякий случай если есть другие символы
            return False

    return not stack  # True, если стек пуст (все открывающие закрыты)
