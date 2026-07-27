_has_sent_greeting = False


def should_send_greeting() -> bool:
    global _has_sent_greeting

    if _has_sent_greeting:
        return False

    _has_sent_greeting = True
    return True


def reset_greeting() -> None:
    global _has_sent_greeting
    _has_sent_greeting = False