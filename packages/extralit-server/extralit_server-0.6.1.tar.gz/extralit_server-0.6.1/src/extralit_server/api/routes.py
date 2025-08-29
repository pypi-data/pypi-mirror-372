# Copyright 2024-present, Extralit Labs, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module configures the api routes under /api prefix, and
set the required security dependencies if api security is enabled
"""

from fastapi import FastAPI

from extralit_server._version import __version__ as extralit_version
from extralit_server.api.errors.v1.exception_handlers import add_exception_handlers as add_exception_handlers_v1
from extralit_server.api.handlers.v1 import authentication as authentication_v1
from extralit_server.api.handlers.v1 import (
    datasets as datasets_v1,
)
from extralit_server.api.handlers.v1 import (
    documents as documents_v1,
)
from extralit_server.api.handlers.v1 import (
    fields as fields_v1,
)
from extralit_server.api.handlers.v1 import (
    files as files_v1,
)
from extralit_server.api.handlers.v1 import (
    imports as imports_v1,
)
from extralit_server.api.handlers.v1 import (
    info as info_v1,
)
from extralit_server.api.handlers.v1 import jobs as jobs_v1
from extralit_server.api.handlers.v1 import (
    metadata_properties as metadata_properties_v1,
)
from extralit_server.api.handlers.v1 import (
    models as models_v1,
)
from extralit_server.api.handlers.v1 import (
    oauth2 as oauth2_v1,
)
from extralit_server.api.handlers.v1 import (
    questions as questions_v1,
)
from extralit_server.api.handlers.v1 import (
    records as records_v1,
)
from extralit_server.api.handlers.v1 import (
    responses as responses_v1,
)
from extralit_server.api.handlers.v1 import (
    settings as settings_v1,
)
from extralit_server.api.handlers.v1 import (
    suggestions as suggestions_v1,
)
from extralit_server.api.handlers.v1 import (
    users as users_v1,
)
from extralit_server.api.handlers.v1 import (
    vectors_settings as vectors_settings_v1,
)
from extralit_server.api.handlers.v1 import webhooks as webhooks_v1
from extralit_server.api.handlers.v1 import (
    workflows as workflows_v1,
)
from extralit_server.api.handlers.v1 import (
    workspaces as workspaces_v1,
)
from extralit_server.errors.base_errors import __ALL__
from extralit_server.errors.error_handler import APIErrorHandler


def create_api_v1():
    api_v1 = FastAPI(
        title="Extralit v1",
        description="Extralit Server API v1",
        version=str(extralit_version),
        responses={error.HTTP_STATUS: error.api_documentation() for error in __ALL__},
    )
    # Now, we can control the error responses for the API v1.
    # We keep the same error responses as the API v0 for the moment
    APIErrorHandler.configure_app(api_v1)

    add_exception_handlers_v1(api_v1)

    for router in [
        info_v1.router,
        authentication_v1.router,
        datasets_v1.router,
        fields_v1.router,
        questions_v1.router,
        metadata_properties_v1.router,
        records_v1.router,
        responses_v1.router,
        suggestions_v1.router,
        users_v1.router,
        vectors_settings_v1.router,
        workspaces_v1.router,
        webhooks_v1.router,
        workflows_v1.router,
        jobs_v1.router,
        oauth2_v1.router,
        settings_v1.router,
        documents_v1.router,
        files_v1.router,
        models_v1.router,
        imports_v1.router,
    ]:
        api_v1.include_router(router)

    return api_v1


api_v1 = create_api_v1()
