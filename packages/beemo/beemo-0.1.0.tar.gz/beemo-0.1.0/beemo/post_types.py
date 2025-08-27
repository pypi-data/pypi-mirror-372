import re
from datetime import datetime, timezone
from pathlib import Path

from markdown import markdown
from pydantic import BaseModel, model_validator

from .settings import get_settings
from .utils import get_excerpt, get_text


settings = get_settings()


class PostType(BaseModel):
    post_type: str
    slug: str | None = None
    title: str
    html_title: str | None = None
    content: str
    text: str | None = None
    html: str | None = None
    description: str | None = None
    excerpt: str | None = None
    link: Path | None = None
    full_width: bool = False

    @model_validator(mode="after")
    def set_html(self):
        self.html = markdown(self.content, extensions=["fenced_code", "codehilite", "tables"])
        return self

    @model_validator(mode="after")
    def set_text(self):
        self.text = get_text(self.html)
        return self

    @model_validator(mode="after")
    def set_excerpt(self):
        if not self.excerpt:
            self.excerpt = get_excerpt(self.text)
        return self

    @model_validator(mode="after")
    def set_description(self):
        if not self.description:
            self.description = self.excerpt
        return self

    @property
    def output_path(self):
        return settings.output_dir / self.link


class Page(PostType):
    post_type: str = "page"

    @model_validator(mode="after")
    def set_link(self):
        if self.slug is None:
            self.link = Path()
        else:
            self.link = Path(self.slug)
        return self


class Post(PostType):
    post_type: str = "post"
    slug: str
    published: datetime
    modified: datetime | None = None
    modified_diff: bool = False
    tags: list[str] = []
    images: list[Path] = []

    @model_validator(mode="after")
    def set_timezone(self):
        self.published = self.published.replace(tzinfo=timezone.utc)
        return self

    @model_validator(mode="after")
    def set_html_title(self):
        self.html_title = f"Ben Nuttall - {self.title}"
        return self

    @model_validator(mode="after")
    def set_link(self):
        self.link = (
            Path("blog") / str(self.published.year) / self.published.strftime("%m") / self.slug
        )
        return self

    @model_validator(mode="after")
    def set_modified(self):
        if not self.modified:
            self.modified = self.published
        else:
            self.modified = self.modified.replace(tzinfo=timezone.utc)
        return self

    @model_validator(mode="after")
    def set_modified_diff(self):
        if self.modified and self.modified.date() != self.published.date():
            self.modified_diff = True
        return self

    @model_validator(mode="after")
    def validate_tags(self):
        for tag in self.tags:
            if not re.fullmatch(r"[a-z0-9-]+", tag):
                raise ValueError(f"Invalid tag: {tag}")
        return self
