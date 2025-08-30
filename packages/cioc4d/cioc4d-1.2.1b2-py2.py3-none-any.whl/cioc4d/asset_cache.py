"""
Singleton that caches the results of an asset scrape.

Not only does this allow us to optimize the asset scrape, it also means we can prepare asset paths
for Linux, while providing the original paths for the payload to be uploaded.
"""
import c4d
from cioc4d import const as k


__data__ = None


def data():
    """
    Provide the list of assets if they are already cached.

    Otherwise, scrape the scene and cache the results.

    Handle changes to the GetAssets API after R21.

    The assets should be in the same form as the output of the GetAllAssets API. Howeever,
    GetAllAssets() might not give all the assets we want. We may have to do additional scraping
    to get the assets we want.

    The data should NOT include the C4d file itself.
    """

    global __data__

    if __data__:
        return __data__

    document = c4d.documents.GetActiveDocument()

    if k.C4D_VERSION < 22:
        # ASSETDATA_FLAG_MISSING seems to work in the opposite way as advertised in the docs for R21
        __data__ = c4d.documents.GetAllAssets(
            document,
            False,
            "",
            flags=c4d.ASSETDATA_FLAG_WITHCACHES
            | c4d.ASSETDATA_FLAG_MULTIPLEUSE
            | c4d.ASSETDATA_FLAG_NODOCUMENT
            | c4d.ASSETDATA_FLAG_MISSING,
        )
    else:
        asset_list = []
        success = c4d.documents.GetAllAssetsNew(
            document,
            False,
            "",
            flags=c4d.ASSETDATA_FLAG_WITHCACHES
            | c4d.ASSETDATA_FLAG_NODOCUMENT
            | c4d.ASSETDATA_FLAG_MULTIPLEUSE,
            assetList=asset_list,
        )
        if success == c4d.GETALLASSETSRESULT_FAILED:
            raise ValueError("c4d.GetAllAssetsNew gave an error.")
        else:
            __data__ = asset_list

    return __data__


def clear():
    global __data__
    __data__ = None
