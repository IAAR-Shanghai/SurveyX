import json
import os
import re
from pathlib import Path
from typing import Union

from tqdm import tqdm

from src.configs.config import BASE_DIR, CHAT_AGENT_WORKERS, MD_TEXT_LENGTH
from src.configs.constants import OUTPUT_DIR
from src.configs.logger import get_logger
from src.models.LLM import ChatAgent
from src.models.LLM.utils import cut_text_by_token, load_prompt
from src.models.monitor.time_monitor import TimeMonitor
from src.modules.utils import (
    clean_chat_agent_format,
    load_file_as_string,
    sanitize_filename,
    save_result,
)
from rapidfuzz import process, fuzz

# ----------------- helpers for curated matching and bibtex composing -----------------
def _normalize_arxiv_id(s: str | None) -> str | None:
    if not s:
        return None
    s = str(s).strip()
    if s.lower().startswith("arxiv:"):
        s = s.split(":", 1)[1]
    return s


def _normalize_bibkey(s: str | None) -> str | None:
    if not s:
        return None
    return str(s).strip()


def _extract_bibkey_from_entry(entry: str | None) -> str | None:
    if not entry:
        return None
    match = re.match(r"@\s*\w+\s*\{\s*([^,]+)", entry.strip())
    if match:
        return match.group(1).strip()
    return None


def _parse_filename_info(p: Path) -> tuple[str | None, str | None]:
    """Extract arxiv_id and human title from filename if possible.
    Expected common formats:
      - arxiv_2501.04227v2 - Agent Laboratory_ Using LLM Agents as Research Assistants.md
      - <anything> - Title with spaces.md
    Returns (arxiv_id, title_from_filename)
    """
    try:
        stem = p.stem  # filename without suffix
        parts = stem.split(" - ", 1)
        arxiv_id = None
        title_from_filename = None
        if len(parts) == 2:
            left, right = parts
            # try arxiv_*
            if left.lower().startswith("arxiv_"):
                arxiv_id = left[len("arxiv_") :].strip()
            title_from_filename = right.replace("_", " ").strip(" ")
        else:
            # no delimiter; best effort: if startswith arxiv_*
            left = parts[0]
            if left.lower().startswith("arxiv_"):
                arxiv_id = left[len("arxiv_") :].strip()
        return arxiv_id, title_from_filename
    except Exception:
        return None, None


def _choose_bib_entry_type(venue: str | None) -> str:
    if not venue:
        return "article"
    v = venue.lower()
    conf_markers = [
        "neurips",
        "iclr",
        "icml",
        "kdd",
        "cvpr",
        "eccv",
        "acl",
        "emnlp",
        "naacl",
        "coling",
        "aaai",
        "ijcai",
        "sigkdd",
        "sigir",
        "wsdm",
        "www",
        "conference",
        "workshop",
    ]
    if any(m in v for m in conf_markers):
        return "inproceedings"
    return "article" if "arxiv" in v or "journal" in v else "article"


def _format_authors_for_bib(authors: str | list | None) -> str | None:
    if not authors:
        return None
    if isinstance(authors, list):
        names = [str(a).strip() for a in authors if str(a).strip()]
    else:
        # common separators: ";" or "," between authors in curated file
        if ";" in authors:
            parts = [x.strip() for x in authors.split(";")]
        else:
            parts = [x.strip() for x in authors.split(",")]
        # Heuristic: some titles may include commas; keep it simple
        names = [x for x in parts if x]
    return " and ".join(names) if names else None


def _build_bibtex_from_curated(
    curated: dict, title_fallback: str | None = None, bib_key: str = "tmpkey"
) -> str:
    title = curated.get("title") or title_fallback or "Untitled"
    venue = curated.get("venue")
    year = curated.get("year")
    doi = curated.get("doi") or curated.get("DOI")
    url = curated.get("url_pdf") or curated.get("url") or curated.get("url_landing")
    arxiv_id = _normalize_arxiv_id(curated.get("arxiv_id") or curated.get("id"))
    authors = _format_authors_for_bib(curated.get("authors"))

    entry_type = _choose_bib_entry_type(venue)

    # Build fields using simple concatenation to avoid brace escaping pitfalls
    fields = ["title={" + str(title) + "}"]
    if authors:
        fields.append("author={" + str(authors) + "}")
    if year:
        fields.append("year={" + str(year) + "}")
    if entry_type == "inproceedings":
        if venue:
            fields.append("booktitle={" + str(venue) + "}")
    else:  # article
        if venue:
            fields.append("journal={" + str(venue) + "}")
        # arXiv extras when applicable
        if venue and "arxiv" in venue.lower():
            if arxiv_id:
                fields.append("eprint={" + str(arxiv_id) + "}")
                fields.append("archivePrefix={arXiv}")
    if doi:
        fields.append("doi={" + str(doi) + "}")
    if url:
        fields.append("url={" + str(url) + "}")

    # compose
    body = ",\n".join(fields)
    return f"@{entry_type}{{{bib_key},\n{body}\n}}"


def _make_bib_key(
    curated: dict | None,
    paper: dict | None,
    used: set[str],
) -> str:
    """Generate a stable, ASCII-only BibTeX key.
    Priority: arxiv_id -> title (+year) -> fallback counter. Ensure uniqueness via suffixes.
    """
    base = None
    # Prefer arxiv id
    aid = None
    if curated:
        aid = _normalize_arxiv_id(curated.get("arxiv_id") or curated.get("id"))
    if not aid and paper:
        aid = paper.get("_arxiv_id_from_filename")
    if aid:
        base = f"arxiv_{aid}"
    # Else from title
    if not base:
        title = None
        if curated:
            title = curated.get("title")
        if not title and paper:
            title = paper.get("_title_from_filename") or paper.get("title")
        if not title and paper:
            title = ""
        title = str(title or "untitled")
        # normalize title into ascii-ish key
        # keep letters+digits, collapse whitespace to _, trim
        import re as _re
        t_ascii = (
            _re.sub(r"[^A-Za-z0-9]+", "_", title).strip("_")
        )
        # shorten for readability
        if len(t_ascii) > 40:
            t_ascii = t_ascii[:40]
        year = None
        if curated and curated.get("year"):
            year = str(curated.get("year"))
        base = t_ascii + (f"_{year}" if year else "")
        if not base:
            base = "ref"

    # ensure ascii and uniqueness
    import re as _re
    key = _re.sub(r"[^A-Za-z0-9_]+", "", base)
    if not key:
        key = "ref"
    candidate = key
    suffix_idx = 1
    while candidate in used:
        suffix_idx += 1
        candidate = f"{key}_{suffix_idx}"
    used.add(candidate)
    return candidate

logger = get_logger("src.modules.preprocessor.DataCleaner")


class DataCleaner:
    def __init__(self, papers: list[dict] = []):
        self.papers: list[dict] = papers
        self.chat_agent_workers = CHAT_AGENT_WORKERS

    def _extract_title_from_md(self, md_text: str) -> str:
        """Best-effort extraction of a title from Markdown text for matching.
        Looks for first heading (#/##/###) near the beginning, else first non-empty line.
        Used only for curated metadata matching; does not change default title logic.
        """
        if not md_text:
            return ""
        lines = md_text.splitlines()
        for line in lines[:120]:
            m = re.match(r"^\s{0,3}(#{1,4})\s+(.+?)\s*$", line)
            if m:
                return m.group(2).strip(" #")
        for line in lines[:80]:
            t = line.strip(" #")
            if t:
                return t
        for line in lines:
            t = line.strip(" #")
            if t:
                return t
        return ""

    def _safe_batch(self, chat_agent: ChatAgent, prompts: list[str], desc: str) -> list[str]:
        """Attempt batch call; on failure, fall back to per-item calls so only
        problematic papers are skipped instead of failing the whole run."""
        try:
            return chat_agent.batch_remote_chat(prompts, desc=desc)
        except Exception as e:
            logger.error(f"batch_remote_chat failed ({e}); falling back to sequential remote_chat")
            results: list[str] = []
            for p in tqdm(prompts, desc=f"fallback: {desc}"):
                try:
                    results.append(chat_agent.remote_chat(p))
                except Exception as ee:
                    msg = str(ee)
                    logger.error(f"remote_chat failed for one prompt: {msg}")
                    non_retryable = (
                        "Invalid prompt" in msg or "limited access" in msg or "safety" in msg
                    )
                    token = chat_agent.NonRetryToken if non_retryable else chat_agent.RetryToken
                    results.append(f"{token}: {msg}")
            return results

    def load_json_dir(self, json_path_dir: Path):
        """load papers from json directory."""
        papers = []
        cnt_total = 0
        for file in os.listdir(json_path_dir):
            if file.endswith(".json"):
                p = os.path.join(json_path_dir, file)
                dic = json.loads(load_file_as_string(p))
                if (
                    "md_text" in dic
                ):  # Only consider those with `md_text` as available papers.
                    papers.append(dic)
                cnt_total += 1
        logger.info(f"Find {len(papers)} out of {cnt_total} papers available.")
        self.papers = papers

    def complete_title(self):
        for paper in tqdm(self.papers, desc="completing title..."):
            if "title" not in paper:
                paper["title"] = paper["md_text"].splitlines()[0].strip(" #")
                # paper["title"] = paper["title"][:32]  # avoid too long title

    def complete_abstract(self):
        pattern = r"\s*a\s*b\s*s\s*t\s*r\s*a\s*c\s*t\s*"  # find "abstract" substring, with whitespace bettween letters.
        for paper in tqdm(self.papers, desc="completing abstract..."):
            if "abstract" in paper and len(paper["abstract"]) > 500:
                continue
            match = re.search(pattern, paper["md_text"], re.IGNORECASE)
            if match:
                index = match.start()
                paper["abstract"] = paper["md_text"][index : index + 2000]
            else:
                paper["abstract"] = paper["md_text"][:2000]

    def complete_bib(self, bib_file_save_path: str):
        """Not only complete the bib_name, also need to save all bibnames into a references.bib file"""
        var_name_i = 0
        bib_all = []

        def sanitize_bib_key(candidate: str | None) -> str:
            if not candidate:
                return ""
            ascii_only = candidate.encode("ascii", "ignore").decode("ascii")
            ascii_only = ascii_only.replace(" ", "")
            return re.sub(r"[^A-Za-z0-9_\-]", "", ascii_only)

        used_bib_names: set[str] = set()

        def ensure_unique_key(candidate: str) -> str:
            nonlocal var_name_i
            if not candidate:
                candidate = f"ref{var_name_i}"
                var_name_i += 1
            base_candidate = candidate
            suffix = 1
            while candidate in used_bib_names:
                candidate = f"{base_candidate}{suffix}"
                suffix += 1
            used_bib_names.add(candidate)
            return candidate

        def rewrite_reference_with_key(reference: str, new_key: str) -> str:
            if not reference:
                return reference
            updated = re.sub(
                r"(@\s*\w+\s*\{)\s*[^,\s\}]*",
                lambda match: f"{match.group(1)}{new_key}",
                reference,
                count=1,
            )
            header_pattern = rf"@\s*\w+\s*\{{\s*{re.escape(new_key)}"
            match = re.search(header_pattern, updated)
            if match:
                insert_pos = match.end()
                remainder = updated[insert_pos:]
                stripped_remainder = remainder.lstrip()
                if stripped_remainder.startswith(","):
                    # keep single comma and drop leading spaces before it
                    comma_index = remainder.index(",")
                    updated = (
                        updated[:insert_pos]
                        + remainder[comma_index:]
                    )
                elif not remainder.startswith(","):
                    updated = updated[:insert_pos] + "," + remainder
            return updated

        for paper in tqdm(self.papers, desc="completing bibname..."):
            if "reference" in paper:
                reference_header = paper["reference"].splitlines()[0]
                raw_bib_name = _extract_bibkey_from_entry(reference_header)
                sanitized_bib_name = sanitize_bib_key(raw_bib_name)
                new_bib_name = ensure_unique_key(sanitized_bib_name)

                paper["bib_name"] = new_bib_name
                paper["reference"] = rewrite_reference_with_key(
                    paper["reference"], new_bib_name
                )
            else:
                # Prefer stable key from arxiv_id if available
                if paper.get("arxiv_id"):
                    arxiv_based = sanitize_bib_key(str(paper["arxiv_id"]))
                    bib_name = ensure_unique_key(arxiv_based)
                else:
                    title = paper.get("title", "")
                    title_ascii = title.encode("ascii", "ignore").decode("ascii")
                    title_compact = "".join(
                        [c for c in title_ascii if not c.isspace()][:10]
                    )
                    fallback_candidate = sanitize_bib_key(title_compact)
                    bib_name = ensure_unique_key(fallback_candidate)
                # Ensure title present in bib
                title_field = (
                    paper.get("title", "")
                    .encode("ascii", "ignore")
                    .decode("ascii")
                    .replace("{", "")
                    .replace("}", "")
                )
                bib_tex = f"@article{{{bib_name},\ntitle={{{title_field}}}\n}}"

                paper["reference"] = bib_tex
                paper["bib_name"] = bib_name

            bib_all.append(paper["reference"])

        save_result("\n".join(bib_all), bib_file_save_path)

    def check_md_text_length(self):
        for paper in self.papers:
            if "md_text" not in paper:
                continue
            md_text = paper["md_text"]
            paper["md_text"] = cut_text_by_token(md_text, MD_TEXT_LENGTH)

    def __process_paper_type_response(self, res: str, paper_index: int):
        kinds = ["method", "benchmark", "theory", "survey"]
        for k in kinds:
            if k in res.lower():
                self.papers[paper_index]["paper_type"] = k
                return True
        logger.error(
            f"failed to extract papertype of {self.papers[paper_index]['title']}"
        )
        logger.error(f"The response from gpt is {res}")
        return False

    def get_paper_type(self, chat_agent: ChatAgent):
        """complete the paper type field with chatgpt."""
        # load prompts
        prompts_and_index = []
        for i, paper in enumerate(self.papers):
            abstract = paper["abstract"]
            prompt = load_prompt(
                f"{BASE_DIR}/resources/LLM/prompts/preprocessor/paper_type_classification.md",
                abstract=abstract,
            )
            prompts_and_index.append([prompt, i])
        # batch_chat
        cnt = 0
        while prompts_and_index and cnt < 3:
            prompts = [x[0] for x in prompts_and_index]
            res_l = self._safe_batch(chat_agent, prompts, desc="getting paper type...")
            prompts_and_index = [
                (prompt, paper_index)
                for res, (prompt, paper_index) in zip(res_l, prompts_and_index)
                if not (
                    isinstance(res, str)
                    and res.startswith(chat_agent.NonRetryToken)
                ) and not self.__process_paper_type_response(res, paper_index)
            ]
            cnt += 1

    def __process_attri_response(self, res: str, paper_index: int):
        res = clean_chat_agent_format(content=res)
        try:
            res_dic = json.loads(res)
            self.papers[paper_index]["attri"] = {**res_dic}
            return True
        except Exception as e:
            logger.debug(
                f"Failed to process {self.papers[paper_index]['title']}; The res: {res[:100]}; {e}"
            )
            return False

    def get_attri(self, chat_agent: ChatAgent):
        """extract attribute tree from paper"""
        # 获取所有含 "md_text" 的文件并生成 prompts
        prompts_and_index = []
        for i, paper in enumerate(self.papers):
            # 根据 paper_type 加载对应的 prompt
            paper_type = paper["paper_type"].lower()
            prompt = load_prompt(
                f"{BASE_DIR}/resources/LLM/prompts/preprocessor/attri_tree_for_{paper_type}.md",
                paper=paper["md_text"],
            )
            prompts_and_index.append([prompt, i])

        # 批量处理 prompts
        cnt = 0
        while prompts_and_index and cnt < 3:
            prompts = [x[0] for x in prompts_and_index]
            res_l = self._safe_batch(
                chat_agent, prompts, desc="getting attribute tree from paper......"
            )

            prompts_and_index = [
                (prompt, paper_index)
                for res, (prompt, paper_index) in zip(res_l, prompts_and_index)
                if not (
                    isinstance(res, str)
                    and res.startswith(chat_agent.NonRetryToken)
                ) and not self.__process_attri_response(res, paper_index)
            ]
            cnt += 1

    def save_papers(
        self, save_dir: Union[str, Path], file_name_attr: str = "title"
    ) -> None:
        """save every cleaned paper."""
        filter_field = [
            "from",
            "scholar_id",
            "detail_id",
            "title",
            "abstract",
            "bib_name",
            "md_text",
            "paper_type",
            "attri",
            "mount_outline",
            "similarity_score",
            "image",
        ]
        for paper in self.papers:
            try:
                file_name = paper[file_name_attr] + ".json"
                file_name = sanitize_filename(file_name)
                file_path = os.path.join(save_dir, file_name)
                save_dic = {key: paper.get(key, None) for key in filter_field}
                save_result(json.dumps(save_dic, indent=4), file_path)
            except Exception as e:
                logger.error(
                    f"There is an error when saving {file_path}. The error is: {e}"
                )
        return self.papers

    def quick_check(self) -> list[dict]:
        """Used in PaperRecaller for quick check"""
        papers_with_md = [paper for paper in self.papers if "md_text" in paper]
        self.papers = papers_with_md
        self.complete_title()
        self.complete_abstract()
        return self.papers

    def offline_proc(
        self,
        task_id: str,
        ref_path: str,
        curated_json: str | None = None,
        skip_llm: bool = False,
    ) -> None:
        ref_data_path = Path(ref_path)
        md_files = [p for p in ref_data_path.glob("*.md") if p.is_file()]
        self.papers = []
        for p in md_files:
            md_text = p.read_text(encoding="utf-8", errors="ignore")
            arxiv_id_from_fn, title_from_fn = _parse_filename_info(p)
            self.papers.append(
                {
                    "md_text": md_text,
                    "_md_filename": p.name,
                    "_md_stem": p.stem,
                    "_arxiv_id_from_filename": _normalize_arxiv_id(arxiv_id_from_fn),
                    "_title_from_filename": title_from_fn,
                }
            )

        # Merge curated metadata when provided
        curated_list: list[dict] = []
        if curated_json:
            cpath = Path(curated_json)
            if cpath.exists():
                try:
                    data = json.loads(cpath.read_text(encoding="utf-8"))
                    if isinstance(data, list):
                        curated_list = data
                    else:
                        logger.warning("Curated JSON is not a list; skipping.")
                except Exception as e:
                    logger.error(f"Failed to read curated JSON: {e}")
            else:
                logger.warning(f"Curated JSON not found: {curated_json}")

        if curated_list:
            # Build indices for robust matching
            curated_by_arxiv: dict[str, dict] = {}
            curated_by_id: dict[str, dict] = {}
            curated_titles = []
            curated_title_index = []
            for item in curated_list:
                aid = _normalize_arxiv_id(item.get("arxiv_id") or item.get("id"))
                if aid:
                    curated_by_arxiv[aid] = item
                cid = _normalize_bibkey(item.get("id"))
                if cid:
                    curated_by_id[cid.lower()] = item
                t = str(item.get("title") or "").strip()
                curated_titles.append(t)
                curated_title_index.append(item)
            used_keys: set[str] = set()
            for paper in self.papers:
                chosen = None
                # 0) Try exact id/bibkey match via filename stem
                stem = _normalize_bibkey(paper.get("_md_stem"))
                if stem:
                    chosen = curated_by_id.get(stem.lower())
                # 1) Try exact arxiv id by filename
                if not chosen:
                    aid = paper.get("_arxiv_id_from_filename")
                    if aid and aid in curated_by_arxiv:
                        chosen = curated_by_arxiv[aid]
                # 2) Try exact title match by filename-derived title
                if not chosen:
                    tfn = str(paper.get("_title_from_filename") or "").strip()
                    if tfn:
                        # exact case-insensitive compare
                        for item in curated_list:
                            if str(item.get("title") or "").strip().lower() == tfn.lower():
                                chosen = item
                                break
                # 3) Fallback: fuzzy match using MD-extracted title
                if not chosen:
                    md_title = self._extract_title_from_md(paper.get("md_text", ""))
                    if md_title:
                        match, score, idx = process.extractOne(
                            md_title, curated_titles, scorer=fuzz.token_set_ratio
                        )
                        if score is not None and score >= 80:
                            chosen = curated_title_index[idx]

                # Merge when matched
                if chosen:
                    # generate stable unique bib key now
                    provided_bibtex = str(chosen.get("bibtex") or "").strip()
                    bib_key = None
                    if provided_bibtex:
                        if not provided_bibtex.endswith("\n"):
                            provided_bibtex += "\n"
                        paper["reference"] = provided_bibtex
                        bib_key = _extract_bibkey_from_entry(provided_bibtex)
                        if bib_key:
                            paper["bib_name"] = bib_key
                            used_keys.add(bib_key)
                    if not provided_bibtex:
                        bib_key = _make_bib_key(chosen, paper, used_keys)
                        try:
                            paper["reference"] = _build_bibtex_from_curated(
                                curated=chosen, title_fallback=paper.get("title"), bib_key=bib_key
                            )
                            paper["bib_name"] = bib_key
                        except Exception as e:
                            logger.debug(f"Failed to build curated bibtex for one paper: {e}")
                    if chosen.get("title"):
                        paper["title"] = str(chosen["title"]).strip()
                    if chosen.get("abstract"):
                        paper["abstract"] = str(chosen["abstract"]).strip()
                    if chosen.get("arxiv_id") or chosen.get("id"):
                        paper["arxiv_id"] = str(
                            _normalize_arxiv_id(chosen.get("arxiv_id") or chosen.get("id"))
                        ).strip()
                    # Build a full BibTeX in advance so complete_bib will preserve fields

        # Fill missing fields via existing fallbacks
        self.complete_title()
        self.complete_abstract()
        bib_file_path = Path(OUTPUT_DIR) / task_id / "latex" / "references.bib"
        self.complete_bib(bib_file_path)

        self.check_md_text_length()
        if not skip_llm:
            chat_agent = ChatAgent()
            self.get_paper_type(chat_agent=chat_agent)
            self.get_attri(chat_agent=chat_agent)

        save_path = Path(f"{OUTPUT_DIR}/{task_id}/papers")
        self.save_papers(save_dir=save_path)
        logger.info(f"========== {len(self.papers)} remain after cleaning. ==========")

    def run(self, task_id: str, chat_agent: ChatAgent = None):
        time_monitor = TimeMonitor(task_id)
        time_monitor.start("clean paper")

        self.load_json_dir(Path(OUTPUT_DIR) / task_id / "jsons")
        self.complete_title()
        self.complete_abstract()
        bib_file_path = Path(OUTPUT_DIR) / task_id / "latex" / "references.bib"
        self.complete_bib(bib_file_path)

        self.check_md_text_length()
        if chat_agent is None:
            chat_agent = ChatAgent()
        self.get_paper_type(chat_agent=chat_agent)
        self.get_attri(chat_agent=chat_agent)

        save_path = Path(f"{OUTPUT_DIR}/{task_id}/papers")
        self.save_papers(save_dir=save_path)
        logger.info(f"========== {len(self.papers)} remain after cleaning. ==========")

        time_monitor.end("clean paper")


# python -m src.modules.preprocessor.data_cleaner
if __name__ == "__main__":
    dc = DataCleaner()
    dc.offline_proc("ref1")
    print(len(dc.papers))
