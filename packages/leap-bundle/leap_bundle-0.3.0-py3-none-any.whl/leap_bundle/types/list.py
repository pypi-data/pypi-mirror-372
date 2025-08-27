from typing import List, Optional

from pydantic import BaseModel


class BundleRequestResponse(BaseModel):
    """In sync with apps/web/src/lib/bundle-requests/cli-types.ts"""

    external_id: int
    input_path: str
    status: str
    created_at: str
    user_message: Optional[str] = None


class BundleRequestDetailsResponse(BundleRequestResponse):
    """In sync with apps/web/src/lib/bundle-requests/cli-types.ts"""

    updated_at: str


class GetBundleRequestsResponse(BaseModel):
    """Response model for listing bundle requests.

    In sync with apps/web/src/lib/bundle-requests/cli-types.ts
    """

    requests: List[BundleRequestResponse]


class GetBundleRequestDetailsResponse(BaseModel):
    """Response model for getting details of a specific bundle request.

    In sync with apps/web/src/lib/bundle-requests/cli-types.ts
    """

    request: BundleRequestDetailsResponse
