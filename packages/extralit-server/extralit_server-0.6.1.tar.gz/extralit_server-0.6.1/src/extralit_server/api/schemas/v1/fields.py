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

from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, constr
from pydantic import Field as PydanticField

from extralit_server.api.schemas.v1.commons import UpdateSchema
from extralit_server.enums import FieldType

FIELD_CREATE_NAME_MIN_LENGTH = 1
FIELD_CREATE_NAME_MAX_LENGTH = 200

FIELD_CREATE_TITLE_MIN_LENGTH = 1
FIELD_CREATE_TITLE_MAX_LENGTH = 500

FieldName = Annotated[
    constr(
        min_length=FIELD_CREATE_NAME_MIN_LENGTH,
        max_length=FIELD_CREATE_NAME_MAX_LENGTH,
    ),
    PydanticField(..., description="The name of the field"),
]

FieldTitle = Annotated[
    constr(
        min_length=FIELD_CREATE_TITLE_MIN_LENGTH,
        max_length=FIELD_CREATE_TITLE_MAX_LENGTH,
    ),
    PydanticField(..., description="The title of the field"),
]


class TextFieldSettings(BaseModel):
    type: Literal[FieldType.text]
    use_markdown: bool
    use_table: bool


class TextFieldSettingsCreate(BaseModel):
    type: Literal[FieldType.text]
    use_markdown: bool = False
    use_table: bool = False


class TextFieldSettingsUpdate(BaseModel):
    type: Literal[FieldType.text]
    use_markdown: bool
    use_table: bool


class ImageFieldSettings(BaseModel):
    type: Literal[FieldType.image]


class ImageFieldSettingsCreate(BaseModel):
    type: Literal[FieldType.image]


class ImageFieldSettingsUpdate(BaseModel):
    type: Literal[FieldType.image]


class ChatFieldSettings(BaseModel):
    type: Literal[FieldType.chat]
    use_markdown: bool


class ChatFieldSettingsCreate(BaseModel):
    type: Literal[FieldType.chat]
    use_markdown: bool = True


class ChatFieldSettingsUpdate(BaseModel):
    type: Literal[FieldType.chat]
    use_markdown: bool


class CustomFieldSettings(BaseModel):
    type: Literal[FieldType.custom]
    template: str
    advanced_mode: bool


class CustomFieldSettingsCreate(BaseModel):
    type: Literal[FieldType.custom]
    template: str
    advanced_mode: bool = False


class CustomFieldSettingsUpdate(BaseModel):
    type: Literal[FieldType.custom]
    template: str
    advanced_mode: bool


class TableFieldSettings(BaseModel):
    type: Literal[FieldType.table]


class TableFieldSettingsCreate(BaseModel):
    type: Literal[FieldType.table]


class TableFieldSettingsUpdate(BaseModel):
    type: Literal[FieldType.table]


FieldSettings = Annotated[
    TextFieldSettings | ImageFieldSettings | ChatFieldSettings | CustomFieldSettings | TableFieldSettings,
    PydanticField(..., discriminator="type"),
]

FieldSettingsCreate = Annotated[
    TextFieldSettingsCreate
    | ImageFieldSettingsCreate
    | ChatFieldSettingsCreate
    | CustomFieldSettingsCreate
    | TableFieldSettingsCreate,
    PydanticField(..., discriminator="type"),
]

FieldSettingsUpdate = Annotated[
    TextFieldSettingsUpdate
    | ImageFieldSettingsUpdate
    | ChatFieldSettingsUpdate
    | CustomFieldSettingsUpdate
    | TableFieldSettingsUpdate,
    PydanticField(..., discriminator="type"),
]


class Field(BaseModel):
    id: UUID
    name: str
    title: str
    required: bool
    settings: FieldSettings
    dataset_id: UUID
    inserted_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Fields(BaseModel):
    items: list[Field]


class FieldCreate(BaseModel):
    name: FieldName
    title: FieldTitle
    required: bool | None = None
    settings: FieldSettingsCreate


class FieldUpdate(UpdateSchema):
    title: FieldTitle | None = None
    settings: FieldSettingsUpdate | None = None

    __non_nullable_fields__ = {"title", "settings"}
