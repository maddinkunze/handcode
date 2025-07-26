import os
import re
import typing

_ProgressF = typing.Callable[[str, float|int, float|int], typing.Any]

class WritingStyle:
    def __init__(self, sid: int, name: str, image_path: str|None=None):
        self.id = sid
        self.name = name
        self.image_path = image_path

class ModelRunner:
    id: str
    name: str
    alphabet: list[str]
    writing_styles: list[WritingStyle]
    is_supported: bool

    urls: list[tuple[str, str]]  # (name, url)
    description: str
    license: str
    short_info: str # two lines of info
    _base_url = "https://github.com/maddinkunze/handcode/tree/main/src/lib/handwriting/models/"

    def __init__(self, progress_cb: _ProgressF|None=None):
        self.progress_cb = progress_cb

    def load_libraries(self) -> None:
        pass

    def load(self) -> None:
        raise NotImplementedError()

    def invoke(self, text: list[str], biases: list[float], style: int) -> list[list[float]]:
        raise NotImplementedError()

    _re_md_url = re.compile(r"\[([^\]]*)\]\(([^\)]*)\)")
    _re_md_url_sub = r"\1 (see \2)"
    @classmethod
    def _get_info_from_readme(cls, path_readme: str, path_license: str|None=None) -> tuple[str, str, str]:
        if not os.path.exists(path_readme):
            return "", "", ""

        with open(path_readme, "r", encoding="utf-8") as f:
            readme = f.read()

        description = ""
        for title in ["Description", "Attribution"]:
            content = cls._get_section_from_markdown(readme, title)
            if not content:
                continue
            if description:
                description += "\n\n"
            description += content

        if not description:
            description = "No info about this model :("

        description = re.sub(cls._re_md_url, cls._re_md_url_sub, description)

        if path_license and os.path.exists(path_license):
            with open(path_license, "r", encoding="utf-8") as f:
                license = f.read().strip()
        else:
            license = cls._get_section_from_markdown(readme, "License")

        short_info = "❓ Commercial use unknown\n⚖️ Unknown License"

        if "MIT License" in license:
            short_info = "💵 Commercial use allowed\n⚖️ MIT License"

        return description, license, short_info
    
    @staticmethod
    def _get_section_from_markdown(text: str, title: str, level: int = 3) -> str|None:
        _title = f"{'#' * level} {title}"
        if not _title in text:
            return None
        return text.split(_title)[1].split(f"{'#' * (level - 1)} ")[0].rstrip("#").strip()
    
    @classmethod
    def is_available(cls) -> bool:
        ...