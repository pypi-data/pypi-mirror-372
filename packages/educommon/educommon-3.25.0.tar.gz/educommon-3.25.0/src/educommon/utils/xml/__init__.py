from lxml import (
    etree,
)

from educommon.utils.xml.resolver import (
    Resolver,
)


def load_xml_schema(uri):
    """Возвращает XML-схему по указанному URI.

    При создании объекта схемы используется ``.resolver.Resolver``.

    :rtype: lxml.etree.XMLSchema
    """
    parser = etree.XMLParser(load_dtd=True)
    parser.resolvers.add(Resolver())

    schema_doc = etree.parse(uri, parser=parser)

    schema = etree.XMLSchema(schema_doc)

    return schema


def load_xml_document(document_uri, schema_uri):
    """Возвращает XML-документ, проверенный на соответствие XML-схеме.

    :rtype: lxml.etree._ElementTree

    :raises lxml.etree.DocumentInvalid: Если документ не соответствует
        XML-схеме.
    """
    document = etree.parse(document_uri)
    if schema_uri:
        schema = load_xml_schema(schema_uri)
        schema.assertValid(document)
    return document


def parse_xml(xml):
    """Возвращает дерево XML-документа.

    :param basestring xml: Текст XML-документа.
    :rtype: lxml.etree.ElementTree or None
    """
    if xml:
        if isinstance(xml, str):
            xml = xml.encode('utf-8')

        try:
            root = etree.fromstring(xml)
        except etree.XMLSyntaxError:
            result = None
        else:
            result = root.getroottree()
    else:
        result = None

    return result


def get_text(elements):
    """Возвращает текст первого элемента найденного с помощью make_xpath_query."""
    return elements[0].text if elements else ''


def make_xpath_query(*tags):
    """Возвращает запрос, извлекающий элементы дерева XML-документа.

    :param tags: Имена тэгов XML-документа в порядке иерархии (без учета
        пространств имен).
    """
    result = '/' + ''.join("/*[local-name()='{}']".format(tag) for tag in tags)

    return result
