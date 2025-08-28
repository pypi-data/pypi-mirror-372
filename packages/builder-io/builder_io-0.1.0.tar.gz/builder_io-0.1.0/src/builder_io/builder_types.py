# ruff: noqa: N815
"""Builder.io Types."""

from __future__ import annotations

# -----------------------------
# Explicit module exports
# -----------------------------
__all__: tuple[str, ...] = (
    "Breakpoints",
    "BuilderComponentsProp",
    "BuilderContent",
    "BuilderContentData",
    "BuilderContentVariation",
    "BuilderDataProps",
    "BuilderElement",
    "BuilderLinkComponentProp",
    "BuilderNonceProp",
    "CanTrack",
    "ComponentInfo",
    "ComponentPropsBehavior",
    "ComponentQueryConstraint",
    "ComponentRequirements",
    "Dictionary",
    "EnumOption",
    "Input",
    "JSONValue",
    "Nullable",
    "Permission",
    "PublishedState",
    "RegexRule",
    "Target",
)

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

# -----------------------------
# Modern type aliases (PEP 695)
# -----------------------------

type JSONValue = str | int | float | bool | dict[str, "JSONValue"] | list["JSONValue"]

# Dictionary/Nullable helpers
type Dictionary[T] = dict[str, T]
type Nullable[T] = T | None


# -----------------------------
# element.ts
# -----------------------------


class BuilderElement(BaseModel):
    """Approximation of the TS `BuilderElement` interface.

    Notes:
    - TS uses "@type" and "@version"; here exposed as `at_type` and `at_version` with
    aliases.
    - Many fields are kept broad (dict[str, Any]) as the original TS types are highly
    dynamic.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    at_type: Literal["@builder.io/sdk:Element"] = Field(alias="@type")
    at_version: int | None = Field(default=None, alias="@version")

    id: str | None = None
    tagName: str | None = None
    layerName: str | None = None
    groupLocked: bool | None = None

    component: dict[str, Any] | None = None
    children: list[BuilderElement] | None = None

    bindings: dict[str, Any] | None = None
    properties: dict[str, Any] | None = None
    meta: dict[str, Any] | None = None

    responsiveStyles: dict[str, dict[str, Any]] | None = None
    css: str | None = None
    className: str | None = None

    actions: dict[str, str] | None = None
    repeat: dict[str, str | None] | None = None
    animations: list[dict[str, Any]] | None = None


# -----------------------------
# input.ts
# -----------------------------


class RegexRule(BaseModel):
    """String validation via RegExp-like data."""

    pattern: str
    options: str | None = None  # flags like "gi"
    message: str | None = None  # friendly error message


class EnumOption(BaseModel):
    """Represents an option in an enum-like structure."""

    label: str
    value: Any
    helperText: str | None = None


class Input(BaseModel):
    """Pydantic model for the `Input` interface (best-effort reconstruction)."""

    model_config = ConfigDict(extra="allow")

    # Identity & naming
    name: str
    friendlyName: str | None = None
    description: str | None = None  # deprecated in TS but still accepted

    # Typing & defaults
    type: str
    defaultValue: Any | None = None

    # Object input helpers
    folded: bool | None = None
    keysHelperText: str | None = None
    helperText: str | None = None

    # Media / file helpers
    allowedFileTypes: list[str] | None = None
    imageHeight: int | None = None
    imageWidth: int | None = None
    mediaHeight: int | None = None
    mediaWidth: int | None = None
    hideFromUI: bool | None = None
    modelId: str | None = None

    # Numeric constraints
    max: float | None = None
    min: float | None = None
    step: float | None = None

    # Editor behavior
    broadcast: bool | None = None
    bubble: bool | None = None
    localized: bool | None = None
    options: dict[str, Any] | None = None

    # Enum (dropdown) support
    enum: list[str] | list[EnumOption] | None = None

    # String validation
    regex: RegexRule | None = None

    # Advanced / flags
    advanced: bool | None = None
    code: bool | None = None
    richText: bool | None = None

    # Conditional visibility & defaults
    showIf: str | dict[str, Any] | None = None  # functions serialized as strings
    copyOnAdd: bool | None = None

    # Reference helpers
    model: str | None = None
    behavior: str | None = None
    valueType: dict[str, str | None] | None = None

    # Change hook (function|string) - represented as string token
    onChange: str | None = None

    # Nesting
    subFields: list[Input] | None = None

    # Arbitrary metadata
    meta: dict[str, Any] | None = None


# -----------------------------
# components.ts
# -----------------------------

type Permission = Literal[
    "read", "publish", "editCode", "editDesigns", "admin", "create"
]


class ComponentQueryConstraint(BaseModel):
    """MongoDB/sift-like query constraint used in child/parent requirements."""

    model_config = ConfigDict(extra="allow")  # allow arbitrary filters

    message: str | None = None
    component: str | None = None  # simple 'component name' restriction
    query: dict[str, Any] | None = None  # advanced filter (sift.js-like)


class ComponentRequirements(BaseModel):
    """Requirements that a parent element must satisfy."""

    model_config = ConfigDict(extra="allow")
    message: str | None = None
    component: str | None = None
    query: dict[str, Any] | None = None


class ComponentPropsBehavior(BaseModel):
    """Behavioral flags controlling special Builder SDK props provision."""

    model_config = ConfigDict(extra="allow")

    builderBlock: bool | None = None
    builderContext: bool | None = None
    builderLinkComponent: bool | None = None


class ComponentInfo(BaseModel):
    """Pydantic model mirroring the TS `ComponentInfo` interface (best-effort)."""

    model_config = ConfigDict(extra="allow")

    # Identity & docs
    name: str
    description: str | None = None
    docsLink: str | None = None
    image: str | None = None

    # Inputs & defaults
    inputs: list[Input] | None = None
    defaultChildren: list[BuilderElement] | None = None
    defaults: dict[str, Any] | None = None  # Partial<BuilderElement> - keep open

    # Rendering type
    type: Literal["angular", "webcomponent", "react", "vue"] | None = None
    class_: Any | None = Field(default=None, alias="class")  # reserved keyword
    defaultStyles: dict[str, str] | None = None
    canHaveChildren: bool | None = None
    fragment: bool | None = None
    noWrap: bool | None = None
    isRSC: bool | None = None  # react server component

    # Availability
    models: list[str] | None = None

    # Structure constraints
    childRequirements: ComponentQueryConstraint | None = None
    requiresParent: ComponentRequirements | None = None

    # Authoring & access
    friendlyName: str | None = None
    requiredPermissions: list[Permission] | None = None
    hidden: bool | None = None

    # Builder SDK behavior flags
    hooks: ComponentPropsBehavior | None = None

    # Misc
    meta: dict[str, Any] | None = None


# -----------------------------
# builder-props.ts
# -----------------------------


class BuilderDataProps(BaseModel):
    """Props injected into Builder components for data binding."""

    builderBlock: BuilderElement
    builderContext: Any  # framework-level signal/context; opaque


class BuilderComponentsProp(BaseModel):
    """Props injected into Builder components for data binding."""

    builderComponents: dict[str, Any]  # RegisteredComponents - framework registry


class BuilderLinkComponentProp(BaseModel):
    """Props injected into Builder components for data binding."""

    builderLinkComponent: Any | None = None


class BuilderNonceProp(BaseModel):
    """Props injected into Builder components for data binding."""

    nonce: str


# -----------------------------
# targets.ts
# -----------------------------

type Target = Literal[
    "vue", "reactNative", "svelte", "qwik", "react", "solid", "rsc", "angular"
]


# -----------------------------
# can-track.ts
# -----------------------------


class CanTrack(BaseModel):
    """Represents the ability to track changes."""

    canTrack: bool


# -----------------------------
# builder-content.ts
# -----------------------------


class Breakpoints(BaseModel):
    """Represents responsive design breakpoints."""

    xsmall: int | None = None
    small: int
    medium: int


class BuilderContentData(BaseModel):
    """The `data` payload inside a variation/content - narrow, best-effort."""

    title: str | None = None
    blocks: list[BuilderElement] | None = None
    inputs: list[Input] | None = None
    state: dict[str, Any] | None = None
    jsCode: str | None = None


class BuilderContentVariation(BaseModel):
    """Represents a variation of content within the Builder framework."""

    data: BuilderContentData | None = None


type PublishedState = Literal["published", "draft", "archived"]


class BuilderContent(BaseModel):
    """Approximation of the TS `BuilderContent` shape from builder-content.ts."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str | None = None
    name: str | None = None

    # Top-level data block (some SDKs place it here)
    data: BuilderContentData | None = None

    # Misc dynamic fields - kept open to allow SDK/runtime additions
    #' query: dict[str, Any] | None = None
    testRatio: float | None = None

    # Versioning & publication
    at_version: int | None = Field(default=None, alias="@version")
    published: PublishedState | None = None
    modelId: str | None = None
    priority: int | None = None
    firstPublished: int | None = None
    lastUpdated: int | None = None
    startDate: int | None = None
    endDate: int | None = None

    # A/B testing variations
    variations: dict[str, BuilderContentVariation] | None = None
    testVariationId: str | None = None
    testVariationName: str | None = None


# -----------------------------
# Forward-ref resolution
# -----------------------------
BuilderElement.model_rebuild()
Input.model_rebuild()
ComponentInfo.model_rebuild()
BuilderContentData.model_rebuild()
BuilderContentVariation.model_rebuild()
BuilderContent.model_rebuild()
