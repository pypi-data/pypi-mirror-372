import getpass


def get_current_ad_user() -> str:
    """
    Retorna o usuário AD atual do usuário logado no Windows.

    Returns:
        str: Nome do usuário AD no formato DOMINIO\\usuario ou apenas usuario
    """
    return getpass.getuser()
