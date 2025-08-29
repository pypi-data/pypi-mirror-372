"""Artifact generators for the Strangeworks platform."""
from dataclasses import dataclass
from typing import Any, Callable, Iterator


@dataclass
class Artifact:
    """Abstract base class for artifact generators.

    Attributes
    ----------
    data: Any
        artifact contents. This will likely be uploaded as a file
        associated with a job.
    type: str
        type of artifact (text, json, svg, etc.)
    name: str
        what to name the artifact file.
    schema: str
        schema for the artifact (json, svg, etc.) Used by portal to
        determine the best way to display the artifact.
    label: str
        label associated with the artifact.
    url: str
        url for the artifact. This is set by the post_hook.
    file_slug: str
        file slug for the artifact. This is set in the post_hook
        method after the artifact has been pushed on to the platform.
    job_slug: str
        job slug which the artifact is associated with. Typically set in
        the pre_hook or post_hook methods.
    """

    data: Any
    name: str | None = None
    schema: str | None = None
    label: str | None = None
    job_slug: str | None = None
    url: str | None = None
    file_slug: str | None = None
    sort_weight: int = 0
    is_hidden: bool = False

    def pre_hook(
        self,
        **kwargs,
    ):
        """Pre hook for artifact.

        Any updates prior to uploading the artifact should be done here.
        """
        return

    def post_hook(
        self,
        file_slug: str | None = None,
        url: str | None = None,
        **kwargs,
    ):
        """Post hook for artifact.

        Any updates to the artifact can be done here.
        """
        if url:
            self.url = url
        if file_slug:
            self.file_slug = file_slug


ArtifactGenerator = Callable[[str, dict[str, Any], str], Iterator[Artifact]]
