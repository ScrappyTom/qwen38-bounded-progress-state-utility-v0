from __future__ import annotations

import re
from dataclasses import dataclass


MAX_READ_BYTES = 12_000


@dataclass(frozen=True)
class Region:
    region_id: str
    heading_level: int
    heading_text: str
    part: int
    part_count: int
    start_line: int
    end_line: int
    content: str

    @property
    def raw(self) -> bytes:
        return self.content.encode("utf-8")


def build_regions(data: bytes) -> list[Region]:
    lines = data.decode("utf-8", errors="strict").splitlines(keepends=True)
    headings: list[tuple[int, int, str]] = []
    for number, line in enumerate(lines, start=1):
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.rstrip("\r\n"))
        if match:
            headings.append((number, len(match.group(1)), match.group(2)))
    if not headings or headings[0][0] != 1:
        raise RuntimeError("target must begin with an ATX heading")

    regions: list[Region] = []
    ordinal = 0
    for heading_index, (start, level, heading) in enumerate(headings):
        end = headings[heading_index + 1][0] - 1 if heading_index + 1 < len(headings) else len(lines)
        chunks: list[tuple[int, int]] = []
        chunk_start = start
        chunk_size = 0
        for number in range(start, end + 1):
            line_size = len(lines[number - 1].encode("utf-8"))
            if line_size > MAX_READ_BYTES:
                raise RuntimeError(f"one target line exceeds the transfer limit: {number}")
            if chunk_size and chunk_size + line_size > MAX_READ_BYTES:
                chunks.append((chunk_start, number - 1))
                chunk_start = number
                chunk_size = 0
            chunk_size += line_size
        chunks.append((chunk_start, end))
        for part, (chunk_start, chunk_end) in enumerate(chunks, start=1):
            ordinal += 1
            regions.append(
                Region(
                    region_id=f"R{ordinal:03d}",
                    heading_level=level,
                    heading_text=heading,
                    part=part,
                    part_count=len(chunks),
                    start_line=chunk_start,
                    end_line=chunk_end,
                    content="".join(lines[chunk_start - 1 : chunk_end]),
                )
            )
    if b"".join(region.raw for region in regions) != data:
        raise RuntimeError("region construction did not reassemble the target")
    return regions

