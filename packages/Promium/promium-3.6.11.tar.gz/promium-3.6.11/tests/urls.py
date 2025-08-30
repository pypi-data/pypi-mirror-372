from tests.config import PROJECT_HOST, PROJECT_PORT, WIKI_HOST


def collect_url(path, sub_domain=""):
    """
    Collects url
    :param str path:
    :param str sub_domain:
    :return str url
    """
    return f"https://{sub_domain}{PROJECT_HOST}{PROJECT_PORT}/{path}"


def case_url(case_id):
    """
    Returns check-list page by id
    :param int case_id: Page id
    :return str url
    """
    return f"https://{WIKI_HOST}{case_id}"
