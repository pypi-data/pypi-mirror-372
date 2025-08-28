from textwrap import indent

from chopdiff.docs import (
    BOF_TOK,
    EOF_TOK,
    PARA_BR_TOK,
    SENT_BR_TOK,
    SentIndex,
    TextDoc,
    TextUnit,
    TokenMapping,
    search_tokens,
)
from chopdiff.html import ContentNotFound, TimestampExtractor

from kash.config.logger import get_logger
from kash.exec import kash_action
from kash.exec.preconditions import has_simple_text_body, has_timestamps
from kash.media_base.timestamp_citations import add_citation_to_text, format_timestamp_citation
from kash.model import Format, Item, ItemType, common_params
from kash.utils.common.format_utils import fmt_loc
from kash.utils.common.type_utils import not_none
from kash.utils.errors import InvalidInput, UnexpectedError
from kash.workspaces.source_items import find_upstream_item, find_upstream_resource

log = get_logger(__name__)


@kash_action(
    precondition=has_simple_text_body & ~has_timestamps,
    params=common_params("chunk_unit"),
)
def backfill_timestamps(item: Item, chunk_unit: TextUnit = TextUnit.paragraphs) -> Item:
    """
    Backfill timestamps from a source document.
    Seeks through the document this doc is derived from for timestamps and inserts them
    into the text of the current doc. Source must have similar tokens.
    """
    if chunk_unit not in (TextUnit.sentences, TextUnit.paragraphs):
        raise InvalidInput(f"Only support sentences and paragraphs for chunk unit: {chunk_unit}")

    if chunk_unit == TextUnit.sentences:
        citation_tokens = [SENT_BR_TOK, PARA_BR_TOK, EOF_TOK]
    elif chunk_unit == TextUnit.paragraphs:
        citation_tokens = [PARA_BR_TOK, EOF_TOK]
    else:
        raise UnexpectedError(f"Invalid text unit: {chunk_unit}")

    source_item = find_upstream_item(item, has_timestamps)
    # Find the original resource (video or audio) this timestamped item came from.
    orig_resource = find_upstream_resource(source_item)
    source_path = orig_resource.store_path
    source_url = orig_resource.url

    if not item.body:
        raise InvalidInput(f"Item must have a body: {item}")
    if not source_item.body:
        raise InvalidInput(f"Source item must have a body: {source_item}")
    if not source_path:
        raise InvalidInput(f"Source item must have a store path: {source_item}")
    if not source_url:
        log.warning(
            "Source item has no URL, so will not create timestamp hotlinks: %s", source_item
        )

    log.message(
        "Pulling timestamps from source item: %s", fmt_loc(not_none(source_item.store_path))
    )

    # Parse current doc.
    item_doc = TextDoc.from_text(item.body)
    item_wordtoks = list(item_doc.as_wordtoks(bof_eof=True))

    # Don't bother parsing sentences on the source document, which may be long and with HTML.
    extractor = TimestampExtractor(source_item.body)
    source_wordtoks = extractor.wordtoks

    log.message(
        "Mapping source doc with %s wordtoks back to this item, %s.",
        len(source_wordtoks),
        item_doc.size_summary(),
    )

    token_mapping = TokenMapping(source_wordtoks, item_wordtoks)

    log.info(
        "Timestamp extractor mapping diff:\n%s",
        indent(token_mapping.diff.as_diff_str(include_equal=False), prefix="    "),
    )

    log.save_object("Token mapping", None, token_mapping.full_mapping_str())

    output_item = item.derived_copy(type=ItemType.doc, format=Format.md_html)

    sent_index_list: list[SentIndex] = []
    timestamp_list: list[float] = []

    for wordtok_offset, (wordtok, sent_index) in enumerate(
        item_doc.as_wordtok_to_sent(bof_eof=True)
    ):
        if wordtok in citation_tokens:
            # If we're inserting citations at paragraph breaks, we need to back up to the beginning of the paragraph.
            # If we're inserting citations at sentence breaks, we can just use the per-sentence timestamps.
            if chunk_unit == TextUnit.paragraphs:
                start_para_index, start_para_wordtok = (
                    search_tokens(item_wordtoks)
                    .at(wordtok_offset)
                    .seek_back([BOF_TOK, PARA_BR_TOK])
                    .next()
                    .get_token()
                )

                log.info(
                    "Searching to previous para break behind %s (%s) got %s (%s)",
                    wordtok_offset,
                    wordtok,
                    start_para_index,
                    start_para_wordtok,
                )

                wordtok_offset = start_para_index

            source_wordtok_offset = token_mapping.map_back(wordtok_offset)

            log.info(
                "Mapping token at offset back to source doc: %s (%s) -> %s (%s)",
                wordtok_offset,
                wordtok,
                source_wordtok_offset,
                source_wordtoks[source_wordtok_offset],
            )

            try:
                timestamp, _index, _offset = extractor.extract_preceding(source_wordtok_offset)

                timestamp_list.append(timestamp)
                sent_index_list.append(sent_index)

                sent = item_doc.get_sent(sent_index)
                if sent.is_markup():
                    log.info("Skipping markup-only sentence: %s", sent.text)
                    continue

                sent.text = add_citation_to_text(
                    sent.text,
                    format_timestamp_citation(source_url, source_path, timestamp),
                )
            except ContentNotFound:
                # Missing timestamps aren't fatal since it might be meta text like "Speaker 1:".
                log.warning(
                    "Failed to extract timestamp at doc token %s (%s) -> source token %s (%s): %s",
                    wordtok_offset,
                    wordtok,
                    source_wordtok_offset,
                    source_wordtoks[source_wordtok_offset],
                    sent_index,
                )

    first = timestamp_list[0] if timestamp_list else "none"
    last = timestamp_list[-1] if timestamp_list else "none"
    log.message(
        "Found %s timestamps in source doc from %s to %s.", len(timestamp_list), first, last
    )

    output_item.body = item_doc.reassemble()

    return output_item
