from typing import Optional

from pydantic import BaseModel


class CreateBundleRequestBody(BaseModel):
    """In sync with apps/web/src/lib/bundle-requests/cli-types.ts"""

    input_path: str
    input_hash: str
    force_recreate: Optional[bool] = False
