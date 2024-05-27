from urllib.parse import urljoin


def montar_href_absoluto(href, url):
    href_relativo = href
    url_padrao = url
    href_absoluto = urljoin(url_padrao, href_relativo)
    return href_absoluto
