import json
import os.path
import warnings

from lxml import (
    etree,
)


def _load_catalog():
    file_path = os.path.join(os.path.dirname(__file__), 'catalog.json')
    with open(file_path, 'r') as infile:
        result = json.load(infile)
    return result


_catalog = _load_catalog()


class Resolver(etree.Resolver):
    """Резолвер для предварительно загруженных XML-схем.

    Может использоваться в случаях, когда в XML-схемах используются внешние
    документы (<include> и <import>). Для корректной обработки XML-схем
    средствами lxml (по сути, LibXML2), использующих внешние документы,
    необходима настройка каталога, но поскольку этого не делается,
    альтернативой может служить данный резолвер.

    .. code-block:: python

        from lxml import etree

        parser = etree.XMLParser(load_dtd=True)
        parser.resolvers.add(Resolver())
    """

    def resolve(self, url, public_id, context):
        from educommon.utils.misc import (
            md5sum,
        )

        if url in _catalog:
            meta = _catalog[url]
            filepath = os.path.join(os.path.dirname(__file__), meta['file'])
            if meta['md5'] != md5sum(filepath):
                warnings.warn('File {} corrupted.'.format(filepath))
                result = self.resolve_empty(context)
            else:
                result = self.resolve_filename(filepath, context)
        else:
            result = self.resolve_empty(context)

        return result
