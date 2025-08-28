from typing import Any, Dict, TypedDict, Union


class UpdateInstalledMiniApp(TypedDict, total=False):
    name: Union[str, None]
    identifier: Union[str, None]
    data: Union[Dict[str, Any], None]
