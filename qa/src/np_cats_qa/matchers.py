from hamcrest import all_of, not_none, not_


def not_empty():
    return all_of(
        not_none(),
        not_('')
    )
