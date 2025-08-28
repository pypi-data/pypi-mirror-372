# SPDX-FileCopyrightText: 2024–2025 Mattia Rubino
# SPDX-License-Identifier: AGPL-3.0-or-later

from textwizard.wizard_cleaners.tw_html_cleaner.html_cleaner import HTMLCleaner
from textwizard.wizard_cleaners.tw_xml_cleaner.xml_cleaner import XMLCleaner
from textwizard.wizard_cleaners.tw_csv_cleaner.csv_cleaner import CSVCleaner, CsvDialect
import csv
from pathlib import Path
from typing import Union, Optional,Iterable,List, Dict, Any
from textwizard.wizard_extractors.extraction_text import TextExtractor
from textwizard.utils.errors.errors_handle import handle_errors
from textwizard.wizard_ner.wizard_ner import WizardNER, EntitiesResult


from textwizard.wizard_analyze_text.wizzard_correctness.correctness import CorrectnessAnalyzer
from textwizard.wizard_analyze_text.wizzard_lang_detect.model_io import load_model, Model
from textwizard.wizard_analyze_text.wizzard_lang_detect.detect_lang import detect_lang as _detect_lang

from textwizard.wizard_analyze_text.statistical import StatisticalAnalyzer
from textwizard.wizard_analyze_text.similarity import TextSimilarity
import threading

class TextWizard:
    def __init__(self):
        self._text_extractor = TextExtractor()
        self._html_cleaner = HTMLCleaner()
        self._xml_cleaner = XMLCleaner()
        self._csv_cleaner = CSVCleaner()
        self._lang_model: Model | None = None
        self._lang_lock = threading.Lock()

    
    # ----------------------------------------------------------------------
    # Text extraction
    # ----------------------------------------------------------------------

    @handle_errors
    def extract_text(
            self,
            input_data: Union[str, bytes, Path],
            extension: Optional[str] = None,
            pages: Optional[Union[int, str, List[Union[int, str]]]] = None,
            ocr: bool = False,
            language_ocr: str = "eng",    
    ) -> str:
        """
        Extracts text from the provided input data based on its format and type.

        Args:
            input_data (Union[str, bytes, Path]):
                The input for extraction: a filesystem path, raw bytes, or string content.
            extension (Optional[str]):
                File extension to use when `input_data` is bytes (e.g. 'pdf', 'xlsx').
            pages (Optional[int | str | list[int | str]]):
                • For paged formats (PDF, DOCX, TIFF): one-based page numbers to extract.
                • For Excel formats (XLSX, XLS): sheet index (int), sheet name (str),
                  or a mixed list thereof.
                • If None (default), all pages/sheets are extracted.
            ocr (bool):
                Enables OCR for text extraction using Tesseract OCR. Applicable for formats
                like PDF, DOCX, and image-based files.
            language_ocr (str):
                Tesseract language code (default: 'eng').

        Returns:
            str: The extracted text content.

        Raises:
            InvalidInputError: If the input data is invalid or unsupported.

        Supported formats:
            'pdf', 'doc', 'docx', 'xlsx', 'xls', 'txt', 'csv',
            'html', 'htm', 'json', 'tif', 'tiff', 'jpg', 'jpeg',
            'png', 'gif'
        """
        
        
        return self._text_extractor.data_extractor(
            input_data,
            extension,
            pages,
            ocr,
            language_ocr,
        )

    def extract_text_azure(
            self,
            input_data: Union[str, bytes, Path],
            extension: Optional[str] = None,
            language_ocr: str = "eng",
            pages: Optional[Union[int, str, List[Union[int, str]]]] = None,
            azure_endpoint: Optional[str] = None,
            azure_key: Optional[str] = None,
            azure_model_id: str = "prebuilt-read",
            hybrid: bool = False,
    ):
        """
        Extracts text, tables, and key-value pairs from documents using
        **Azure Document Intelligence** (OCR).

        Supported formats:
        - Images: JPG, PNG, TIFF, BMP, GIF
        - PDF (direct OCR or hybrid mode with native text extraction)
        - DOCX (OCR for embedded images)

        Args:
            input_data (Union[str, bytes, Path]):
                File path, binary content, or byte stream.
            extension (Optional[str], default=None):
                File extension (required if `input_data` is a stream or bytes).
            language_ocr (str, default="eng"):
                OCR language code (ISO-639-2 or ISO-639-1).
            pages (Optional[Union[int, str, List[Union[int, str]]]], default=None):
                Pages to process. Examples:
                - `1` (only page 1)
                - `"1,3,5-7"` (specific pages)
                - `[1, 3, "5-7"]` (mixed list)
            azure_endpoint (Optional[str], default=None):
                Azure Document Intelligence endpoint.  
                Example: `"https://<resource-name>.cognitiveservices.azure.com/"`.
            azure_key (Optional[str], default=None):
                Azure API key.
            azure_model_id (str, default="prebuilt-read"):
                Azure model:
                - `"prebuilt-read"` → text only
                - `"prebuilt-layout"` → text + tables + key-value fields
            hybrid (bool, default=False):
                If True, for PDFs it runs a hybrid mode:
                - Pages with text → direct extraction via PyMuPDF
                - Pages with images → Azure OCR

        Returns:
            CloudExtractionResult:
                Object containing:
                - `text_pages`: list of text pages
                - `text`: concatenated text
                - `tables`: extracted tables
                - `pretty_tables`: tables formatted as ASCII
                - `key_value`: dictionary mapping keys to list of values

        Raises:
            RuntimeError: if the Azure module is not installed.
            AzureCredentialsError: if endpoint or key is missing/invalid.
            UnsupportedExtensionAzureError: if the file format is unsupported.
            FileProcessingError: if the file does not exist or cannot be read.

        Example:
            ```python
            import textwizard as tw

            res = tw.extract_text_azure(
                "invoice.pdf",
                language_ocr="ita",
                azure_endpoint="https://myocr.cognitiveservices.azure.com/",
                azure_key="xxxxxx",
                azure_model_id="prebuilt-layout"
            )

            print(res.text)           # concatenated text
            print(res.pretty_tables)  # tables in readable format
            print(res.key_value)      # extracted key-value pairs
            ```
        """
        try:
            from textwizard.wizard_extractors.ocr_service.azure_ocr import AzureOcr
        except ImportError:
            raise RuntimeError("To use Azure OCR, install: textwizard[azure]")

        client = AzureOcr(endpoint=azure_endpoint, key=azure_key)
        return client.extract(
            input_data,
            model_id=azure_model_id,
            extension=extension,
            language_ocr=language_ocr,
            pages=pages,
            hybrid=hybrid
        )

    # ----------------------------------------------------------------------
    # HTML cleaning
    # ----------------------------------------------------------------------
    @handle_errors
    def clean_html(
            self,
            text: str,
            remove_script: bool = None,
            remove_metadata_tags: bool = None,
            remove_flow_tags: bool = None,
            remove_sectioning_tags: bool = None,
            remove_heading_tags: bool = None,
            remove_phrasing_tags: bool = None,
            remove_embedded_tags: bool = None,
            remove_interactive_tags: bool = None,
            remove_palpable: bool = None,
            remove_doctype: bool = None,
            remove_comments: bool = None,
            remove_specific_attributes: Union[str, list, None] = None,
            remove_specific_tags: Union[str, list, None] = None,
            remove_empty_tags: bool = None,
            remove_content_tags: Union[str, list, None] = None,
            remove_tags_and_contents: Union[str, list, None] = None,
    ) -> str:
        """
         Modes
        -----
        A) No parameters provided (all None) → **Text-only extraction**
           - Returns: str (plain text)
           - Behavior: traverses DOM, skips SCRIPT_SUPPORTING tags, concatenates text with safe spacing.
    
        B) At least one parameter is True → **Structural clean (destructive)**
           - Returns: str (serialized HTML)
           - Behavior:
             * Group removals (scripts/metadata/flow/sectioning/headings/phrasing/embedded/interactive/palpable)
             * Optional removals: doctype, comments
             * Extra selectors (only in Mode B):
                 - remove_specific_tags: unwrap tags matched by names/wildcards
                 - remove_tags_and_contents: delete tags and their contents
                 - remove_content_tags: keep tag, drop inner content
                 - remove_specific_attributes: delete matching attributes
                 - remove_empty_tags: prune empty nodes after edits
             * Preserves readable spacing when deleting nodes.
    
        C) Parameters provided and all are False → **Text extraction with preservation**
           - Returns: str (mostly text, with selected tags/comments/doctype preserved inline)
           - Behavior:
             * Any group flagged False is **preserved** as markup in the output
               (e.g., remove_heading_tags=False keeps <h1>…</h6>).
             * remove_comments=False and/or remove_doctype=False preserve those nodes.



        Args:
            text (str): The HTML text to be cleaned.
            remove_script (bool, optional): Removes script tags containing executable code (e.g., <script>, <template>).
            remove_metadata_tags (bool, optional): Removes metadata tags (e.g., <link>, <meta>, <base>, <noscript>, <script>, <style>, <title>).
            remove_flow_tags (bool, optional): Removes flow content tags (e.g., <address>, <div>,<input>.).
            remove_sectioning_tags (bool, optional): Removes sectioning content tags (e.g., <article>, <aside>,<nav>.)..
            remove_heading_tags (bool, optional): Removes heading tags (e.g., <h1> to <h6>).
            remove_phrasing_tags (bool, optional): Removes phrasing content tags (e.g., <audio>, <code>,<textarea>.)..
            remove_embedded_tags (bool, optional): Removes embedded content tags (e.g., <iframe>, <embed>, <img>).
            remove_interactive_tags (bool, optional): Removes interactive content tags (e.g., <button>, <input>, <select>).
            remove_palpable (bool, optional): Removes palpable content elements (e.g., <address>, <math>, <table>).
            remove_doctype (bool, optional): Removes the document type declaration (e.g., <!DOCTYPE html>).
            remove_comments (bool, optional): Removes HTML comments.
            remove_specific_attributes (str | list, optional): Specific attributes to remove from tags. Supports wildcards.
            remove_specific_tags (str | list, optional): Specific tags to remove. Supports wildcards.
            remove_empty_tags (bool, optional): Removes empty HTML tags.
            remove_content_tags (str | list, optional): Removes the content of specified tags. Supports wildcards.
            remove_tags_and_contents (str | list, optional): Removes specified tags along with their contents. Supports wildcards.

        Returns:
            str: The cleaned HTML text.

        Raises:
            ValueError: If the input text is not a valid string.
            
        Notes
        -----
        - Wildcards for tag/attribute selectors:
            * "on*"  matches event handlers (onclick, onload, …)
            * "data-*", "aria-*"
            * Exact names or lists are accepted.
        - When DOM becomes empty after removals, returns "".
    
        """
        clean_params = {
            "html.remove_script": remove_script,
            "html.remove_metadata_tags": remove_metadata_tags,
            "html.remove_flow_tags": remove_flow_tags,
            "html.remove_sectioning_tags": remove_sectioning_tags,
            "html.remove_heading_tags": remove_heading_tags,
            "html.remove_phrasing_tags": remove_phrasing_tags,
            "html.remove_embedded_tags": remove_embedded_tags,
            "html.remove_interactive_tags": remove_interactive_tags,
            "html.remove_palpable": remove_palpable,
            "html.remove_doctype": remove_doctype,
            "html.remove_comments": remove_comments,
            "html.remove_specific_attributes": remove_specific_attributes,
            "html.remove_specific_tags": remove_specific_tags,
            "html.remove_empty_tags": remove_empty_tags,
            "html.remove_content_tags": remove_content_tags,
            "html.remove_tags_and_contents": remove_tags_and_contents,
        }

        return self._html_cleaner.clean(text, **clean_params)


    # ----------------------------------------------------------------------
    # XML cleaning
    # ----------------------------------------------------------------------
    @handle_errors
    def clean_xml(
            self,
            text: str ,
            remove_comments: bool = None,
            remove_processing_instructions: bool = None,
            remove_cdata_sections: bool = None,
            remove_empty_tags: bool = None,
            remove_namespaces: bool = None,
            remove_duplicate_siblings: bool = None,
            collapse_whitespace: bool = None,
            remove_specific_tags: Union[str, list, None] = None,
            remove_content_tags: Union[str, list, None] = None,
            remove_attributes: Union[str, list, None] = None,
            remove_declaration: bool = None,
            normalize_entities: bool = None,
    ) -> str:
        """
        Clean an XML string in one call.

        Parameters
        ----------
        text : str or bytes
            The XML to clean.
        remove_comments : bool, optional
            Remove <!-- comments -->.
        remove_processing_instructions : bool, optional
            Remove <?…?> instructions.
        remove_cdata_sections : bool, optional
            Unwrap <![CDATA[…]]> into plain text.
        remove_empty_tags : bool, optional
            Remove tags with no text, no children and no attributes.
        remove_namespaces : bool, optional
            Drop namespace prefixes and xmlns declarations.
        remove_duplicate_siblings : bool, optional
            Keep only the first identical sibling element.
        collapse_whitespace : bool, optional
            Collapse runs of whitespace into a single space.
        remove_specific_tags : str, list, optional
            Delete these tags entirely (supports wildcards).
        remove_content_tags : str, list, optional
            Keep the tag but delete its inner content.
        remove_attributes : str, list, optional
            Delete these attributes (supports wildcards).
        remove_declaration : bool, optional
            Drop the <?xml …?> declaration.
        normalize_entities : bool, optional
            Convert entities like &amp; into &.

        Returns
        -------
        str
            The cleaned XML.
        """
        clean_params = {
            "xml.remove_comments": remove_comments,
            "xml.remove_processing_instructions": remove_processing_instructions,
            "xml.remove_cdata_sections": remove_cdata_sections,
            "xml.remove_empty_tags": remove_empty_tags,
            "xml.remove_namespaces": remove_namespaces,
            "xml.remove_duplicate_siblings": remove_duplicate_siblings,
            "xml.collapse_whitespace": collapse_whitespace,
            "xml.remove_specific_tags": remove_specific_tags,
            "xml.remove_content_tags": remove_content_tags,
            "xml.remove_attributes": remove_attributes,
            "xml.remove_declaration": remove_declaration,
            "xml.normalize_entities": normalize_entities,
        }

        return self._xml_cleaner.clean(text, **clean_params)

    # ----------------------------------------------------------------------
    # CSV cleaning
    # ----------------------------------------------------------------------
    @handle_errors
    def clean_csv(
        self,
        text: str,
        delimiter: str = ",",
        quotechar: str = '"',
        escapechar: str | None = None,
        doublequote: bool = True,
        skipinitialspace: bool = False,
        lineterminator: str = "\n",
        quoting: int = csv.QUOTE_MINIMAL,
        remove_columns: Union[str, int, Iterable[Union[str, int]], None] = None,
        remove_row_index: Union[int, Iterable[int], None] = None,
        remove_values: Union[str, int, Iterable[Union[str, int]], None] = None, 
        remove_duplicates_rows: bool = False,
        trim_whitespace: bool = False,
        remove_empty_columns: bool = False,
        remove_empty_rows: bool = False,
    ) -> str:
        """
         Clean CSV text with a configurable dialect and structural operations.
    
        Dialect
        -------
        Controlled by ``delimiter``, ``quotechar``, ``escapechar``, ``doublequote``,
        ``skipinitialspace``, ``lineterminator``, and ``quoting`` (one of
        ``csv.QUOTE_MINIMAL | QUOTE_ALL | QUOTE_NONE | QUOTE_NONNUMERIC``).
        The output is serialized using this dialect.
    
        Operations
        ----------
        - ``remove_columns``: drop columns by **header name** (requires header) or **0-based index**.
        - ``remove_row_index``: drop **0-based** row indices over the parsed rows
          (if a header exists, it is row index ``0``).
        - ``remove_values``: blank out cells matching any value; supports wildcards ``*`` and ``?``.
        - ``trim_whitespace``: strip leading/trailing whitespace inside fields.
        - ``remove_duplicates_rows``: remove exact duplicate rows after cleaning.
        - ``remove_empty_columns`` / ``remove_empty_rows``: drop empty structures after all edits.
        
        Parameters
        ----------
        text
            Raw CSV data as a string.
        delimiter
            Field delimiter (default: ',').
        quotechar
            Character used to quote fields (default: '"').
        escapechar
            Character used to escape the quotechar (default: None).
        doublequote
            Controls doublequote handling (default: True).
        skipinitialspace
            Skip spaces after delimiters (default: False).
        lineterminator
            Line terminator (default: '\n').
        quoting
            Controls quoting behavior (csv module constant, default: QUOTE_MINIMAL).
        remove_columns
            Column(s) to remove by name or index.
        remove_row_index
            Row index(es) to remove.
        remove_values
            Value(s) or wildcard pattern(s) to blank out.
        remove_duplicates_rows
            Remove duplicate rows (default: False).
        trim_whitespace
            Trim whitespace inside fields (default: False).
        remove_empty_columns
            Remove columns containing only empty values (default: False).
        remove_empty_rows
            Remove rows containing only empty values (default: False).

        Returns
        -------
        str
            The cleaned CSV data.
        """
        dialect = CsvDialect(
            delimiter=delimiter,
            quotechar=quotechar,
            escapechar=escapechar,
            doublequote=doublequote,
            skipinitialspace=skipinitialspace,
            lineterminator=lineterminator,
            quoting=quoting,
        )

        flags = {
            "csv.remove_columns": remove_columns,
            "csv.remove_row_index": remove_row_index,
            "csv.remove_values": remove_values,
            "csv.remove_duplicates_rows": remove_duplicates_rows,
            "csv.trim_whitespace": trim_whitespace,
            "csv.remove_empty_columns": remove_empty_columns,
            "csv.remove_empty_rows": remove_empty_rows,
        }

        return self._csv_cleaner.clean(text, dialect=dialect, **flags)


    # ----------------------------------------------------------------------
    # NER
    # ----------------------------------------------------------------------

    def extract_entities(
            self,
            text: str,
            engine: str = "spacy",
            model: str = "en_core_web_sm",
            language: str = "en",
            device: str = "auto",
    ) -> EntitiesResult:
        """
        Perform Named-Entity Recognition (NER) on *text* and return a rich
        :class:`~textwizard.wizard_ner.EntitiesResult` object.

        Parameters
        ----------
        text : str
            The raw text to analyse.  
            **Must** be a non-empty Unicode string.
        engine : {'spacy', 'stanza', 'spacy_stanza'}, default ``"spacy"``
            • ``"spacy"`` – fastest; relies entirely on spaCy.  
            • ``"stanza"`` – often higher accuracy; pure Stanza pipeline.  
            • ``"spacy_stanza"`` – spaCy tokenizer + Stanza NER.
        model : str, default ``"en_core_web_sm"``
            spaCy model name *or* absolute path (used only when
            ``engine="spacy"``).
        language : str, default ``"en"``
            ISO-639 language code required by Stanza pipelines.
        device : {'auto', 'cpu', 'gpu'}, default ``"auto"``
            Where to run inference:  
            • ``"auto"`` – GPU if available, otherwise CPU.  
            • ``"cpu"``  – force CPU, even if a GPU is present.  
            • ``"gpu"``  – require CUDA-capable GPU, raise if not found.

        Returns
        -------
        EntitiesResult
            * **entities** – ``Dict[str, List[Entity]]`` grouped by label  
              (e.g. ``"PERSON" → [Entity(...), …]``).  
            * **full_analysis** – ``Dict[int, TokenAnalysis]`` keyed by token
              index, containing lemma, POS, dependency, etc.

        Raises
        ------
        ValidationError
            If *text* is empty or not a string.
        ValueError
            If *engine* or *device* is not among the supported options.
        RuntimeError
            If required libraries or language models are missing.

        Examples
        --------
        >>> tw = TextWizard()
        >>> res = tw.extract_entities("Barack Obama visited Paris.")
        >>> res.entities["PERSON"][0].text
        'Barack Obama'

        Switch engine / device
        ----------------------
        >>> # Stanza on CPU
        >>> tw.extract_entities(text, engine="stanza",
        ...                     language="en", device="cpu")
        >>> # spaCy-Stanza on GPU
        >>> tw.extract_entities(text, engine="spacy_stanza",
        ...                     language="en", device="gpu")
        """
        ner = WizardNER(
            engine=engine,
            model=model,
            language=language,
            device=device,
        )
        result = ner.run(text)

        # Attach the underlying NER engine so test-benchmarks can access it
        setattr(result, "_wizard_ner", ner)

        return result

    # ------------------------------------------------------------------
    # Spelling / correctness
    # ------------------------------------------------------------------
    def correctness_text(
            self,
            text: str,
            language: str = "en",
            dict_dir: Union[str, Path, None] = None,
            use_mmap: bool = False,
    ) -> Dict[str, Any]:
        """
          Spell-check text using compressed MARISA dictionaries (40+ languages).

          Parameters
          ----------
          text : str
              Input text to analyze (Unicode, non-empty).
          language : str, default "en"
              ISO-639 code or variant alias (e.g., "en", "it", "de").
              • `zh` requires the optional `jieba` package.
              • `ja` uses a dedicated lexical trie.
              See `LANG_INFO` for the supported set.
          dict_dir : str | pathlib.Path | None, optional
              Directory containing *.marisa.zst / *.marisa dictionaries.
              • If None: use the per-user data directory and **auto-download**
                missing files (no prompt).
              • If set: **no network access** – files must already exist.
          use_mmap : bool, default False
              If True, memory-map the `.marisa` file (lower RAM; slightly slower first access).
              If False, load the trie fully into RAM.

          Returns
          -------
          dict
              {"errors_count": int, "errors": list[str]}
              Note: the error list may contain duplicates if the same misspelling
              appears multiple times.

          Examples
          --------
          >>> tw.correctness_text("Thiss sentense has a typo.", language="en")
          {'errors_count': 2, 'errors': ['thiss', 'sentense']}

          >>> # Offline with local dictionaries + memory-mapping
          >>> tw.correctness_text("color colour", language="en", dict_dir="dictionaries", use_mmap=True)
          """       
        analyzer = CorrectnessAnalyzer(
            language,
            _dict_dir=dict_dir,
            use_mmap=use_mmap,
        )
        return analyzer.run(text)
    

    def lang_detect(
        self,
        text: str,
        top_k: int = 3,
        profiles_dir: Optional[Path | str] = None,
        use_mmap: bool = False,
        return_top1: bool = False,
    ):
        """
        Detect the language of *text* using a character n-gram model with gating,
        priors, and linguistic hints. Supports 161 ISO-639-1 languages.

        Parameters
        ----------
        text : str
            Input text (Unicode).
        top_k : int, default 3
            How many candidates to return (softmax-normalised probabilities).
        profiles_dir : Path | str | None
            Optional override for the profiles directory. If None, uses the
            package-bundled defaults.
        use_mmap : bool, default False
            If True, memory-map the profile trie(s) to reduce RAM usage; the very first
            access may be slightly slower. If False, load tries fully into RAM for
            maximum lookup throughput.
        return_top1 : bool, default False
            If True, return only the best language code (str). Otherwise return a list
            of (lang, prob) pairs of length ≤ top_k.

        Returns
        -------
        str | list[tuple[str, float]]
            • If ``return_top1=True`` → best language code (or ``""`` if none).
            • Else → list of ``(lang, prob)`` sorted by probability (desc).

        Notes
        -----
        - The model is loaded lazily on first call and cached on the instance.
        - Pass ``profiles_dir`` if you keep profiles outside the packaged defaults.
        """
        # lazy-load + cache (thread-safe)
        if self._lang_model is None:
            with self._lang_lock:
                if self._lang_model is None:
                    if profiles_dir is not None:
                        profiles_dir = Path(profiles_dir)
                        self._lang_model = load_model(
                            profiles_dir=profiles_dir,
                            use_mmap=use_mmap,
                        )
                    else:
                        # packaged defaults (model_io decides paths)
                        self._lang_model = load_model(use_mmap=use_mmap)

        results = _detect_lang(self._lang_model, text, top_k=top_k) or []
        if return_top1:
            return results[0][0] if results else ""
        return results

    

    def analyze_text_statistics(self,text: str) -> Dict[str, Any]:
        """
        Compute a suite of statistical metrics on the lexical distribution of a given text.

        This function serves as a convenient entry point that instantiates
        the underlying `StatisticalAnalyzer` class and returns all computed metrics
        in one shot. Tokens are extracted by lowercasing the input string and splitting 
        on whitespace.

        Implemented metrics
        -------------------
        - **entropy** (`float`):
          Shannon entropy (in bits per token) of the token‐frequency distribution:
            H = −∑_{w∈V} (f_w / N) · log₂(f_w / N),
          where N is the total number of tokens and f_w is the frequency of token w. 
          Higher values indicate more uniformity (greater lexical variety).

        - **zipf** (`dict` with keys `slope` and `r2`):
          Fit of a Zipfian model via linear regression on
            log₁₀(rank) → log₁₀(freq).
          • `slope` (`float`): the estimated slope of the regression line (rounded to 3 decimals).
            In an ideal Zipfian distribution, slope ≈ −1.  
          • `r2` (`float`): coefficient of determination (rounded to 3 decimals), 
            indicating how well the empirical frequency‐rank data align on a straight line.

        - **vocab_gini** (`float`):
          Gini coefficient of the type‐frequency distribution:
            G = (2·∑_{i=1}^m i·v_i) / (m·N) − ((m + 1) / m),
          where m = number of distinct tokens, N = total tokens, and {v_i} is the sorted list 
          of frequencies in ascending order. Ranges from 0 (perfectly uniform frequencies) to 1 
          (one token dominates).

        - **type_token_ratio** (`float`):
          Ratio of number of unique tokens (|V|) to total tokens (N):
            TTR = |V| / N.
          A simple measure of lexical richness; values closer to 1 indicate high diversity, 
          while values near 0 indicate high repetition.

        - **hapax_ratio** (`float`):
          Fraction of tokens that appear exactly once:
            Hapax Ratio = (number of types with frequency 1) / N.
          A high hapax ratio suggests many rare or unique tokens.

        - **simpson_index** (`float`):
          Simpson’s Diversity Index:
            D = 1 − ∑_{w∈V} (f_w / N)².
          Ranges from 0 to 1. Values close to 1 signal high diversity (no single token dominates), 
          values near 0 indicate that few tokens account for most occurrences.

        - **yule_k** (`float`):
          Yule’s K measure for lexical concentration:
            K = 10⁴ · (∑_{i=1}^M i²·V_i − N) / N²,
          where V_i = number of types occurring exactly i times, M = maximum observed frequency, 
          and N = total tokens. Larger K indicates lower lexical richness (heavy repetition).

        - **avg_word_length** (`float`):
          Average token length (in characters), weighted by frequency:
            (∑_{w∈V} |w|·f_w) / N.
          Gives a sense of how “long” the typical token is.

        Parameters
        ----------
        text : str
            Input text to analyze. All characters are lowercased, and tokens are defined 
            by splitting on whitespace.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing the following keys (all numeric values are rounded 
            to three decimal places):
            - `"entropy"` (`float`): Shannon entropy in bits per token.
            - `"zipf"` (`dict`): 
                • `"slope"` (`float`): Zipf regression slope.  
                • `"r2"` (`float`): Zipf regression R².  
            - `"vocab_gini"` (`float`): Gini coefficient of the type‐frequency distribution.
            - `"type_token_ratio"` (`float`): |V| / N.
            - `"hapax_ratio"` (`float`): fraction of hapax legomena (tokens with f_w = 1).
            - `"simpson_index"` (`float`): Simpson’s diversity index.
            - `"yule_k"` (`float`): Yule’s K measure of lexical concentration.
            - `"avg_word_length"` (`float`): average token length (characters).
        """
        return StatisticalAnalyzer().run(text)
    

    def text_similarity(self,
            a: str,
            b: str,
            method: str = "cosine"
            ) -> float:
        """
        Return a similarity score between *a* and *b*.

        Parameters
        ----------
        a, b : str
            Texts to compare.
        method : {"cosine", "jaccard", "levenshtein"}, default "cosine"
            * **cosine**      – cosine similarity on unigram + bigram TF vectors  
            * **jaccard**     – Jaccard index on lowercase word sets  
            * **levenshtein** – 1 − normalised edit distance

        Returns
        -------
        float
            Score in the range *0.0 – 1.0* (1.0 ≡ identical).
        """

        return TextSimilarity(method)(a, b)

    def beutifull_html(
            self,
            html: str,
            indent: int = 2,
            quote_attr_values: str = "spec",  # "legacy" | "spec" | "always"
            quote_char: str = '"',
            use_best_quote_char: bool = True,
            minimize_boolean_attributes: bool = False,
            use_trailing_solidus: bool = False,
            space_before_trailing_solidus: bool = True,
            escape_lt_in_attrs: bool = False,
            escape_rcdata: bool = False,
            resolve_entities: bool = True,
            alphabetical_attributes: bool = True,
            strip_whitespace: bool = False,
            include_doctype: bool = True,
            expand_mixed_content: bool = True,
            expand_empty_elements: bool = True,
    ) -> str:
        """
            Pretty-print raw HTML without changing its semantics.
            
            This function parses *html* with ``TWHTMLParser``, serializes the DOM with
            ``PrettyHTMLSerializer``, and indents each node by *indent* spaces per depth
            level. It never reflows RCData content (e.g., ``<script>``, ``<style>``,
            ``<textarea>``) and avoids introducing visible whitespace unless explicitly
            requested.
            
            Parameters
            ----------
            html : str
                The HTML string to format.
            indent : int, default 2
                Number of spaces per indentation level.
            quote_attr_values : {"always", "spec", "legacy"}, default "spec"
                Policy for quoting attribute values:
                  - "always": always wrap the value in quotes.
                  - "spec"  : quote only when required by the HTML5 spec
                              (whitespace, quotes, equals, angle brackets, backtick).
                  - "legacy": mimic legacy behavior; quote only for whitespace or quotes.
            quote_char : {"\"", "'"}, default '"'
                Preferred quote character when quoting is applied.
            use_best_quote_char : bool, default True
                If True, choose the quote character that minimizes escaping per attribute.
            minimize_boolean_attributes : bool, default False
                Render boolean attributes in compact form (e.g., ``disabled`` instead of
                ``disabled="disabled"``).
            use_trailing_solidus : bool, default False
                If True, write a trailing solidus on void elements (``<br />``). Purely
                cosmetic in HTML5.
            space_before_trailing_solidus : bool, default True
                If True, insert a space before the trailing solidus if it is used.
            escape_lt_in_attrs : bool, default False
                If True, escape ``<`` and ``>`` inside attribute values.
            escape_rcdata : bool, default False
                If True, escape characters inside RCData elements. Usually leave False.
            resolve_entities : bool, default True
                Replace characters with named entities when available.
            alphabetical_attributes : bool, default True
                Sort attributes alphabetically within each start tag. Useful for diffs.
            strip_whitespace : bool, default False
                Trim leading/trailing whitespace in text nodes and collapse runs of spaces
                to a single space.
            include_doctype : bool, default True
                Prepend ``<!DOCTYPE html>`` if not already present.
            expand_mixed_content : bool, default False
                If True, expand elements that contain both text and child elements so that
                each child appears on its own indented line. May introduce visible
                whitespace in inline contexts.
            expand_empty_elements : bool, default False
                If True, render empty non-void elements on two lines (open and close tag on
                separate lines).
            
            Returns
            -------
            str
                The formatted HTML.
            
            Notes
            -----
            - RCData elements are not pretty-printed internally by default to preserve
              semantics.
            - Void elements remain on a single line and are never given closing tags.
            - This formatter does not alter the DOM structure: it only affects whitespace,
              attribute ordering, quoting, and serialization cosmetics.
            
            Example
            -------
            >>> pretty = beutifull_html(
            ...     html="<body><button id='x' disabled>Go <b>now</b></button></body>",
            ...     indent=4,
            ...     quote_attr_values="always",
            ...     minimize_boolean_attributes=True,
            ...     alphabetical_attributes=True,
            ...     expand_mixed_content=True,
            ... )
            >>> print(pretty)
            <!DOCTYPE html>
            <html>
                <head>
                </head>
                <body>
                    <button disabled id="x">
                        Go
                        <b>
                            now
                        </b>
                    </button>
                </body>
            </html>
            """

        from textwizard.utils.tw_html_parser.beautify_html import beautify_html

        return beautify_html(
            html=html,
            indent=indent,
            quote_attr_values=quote_attr_values,
            quote_char=quote_char,
            use_best_quote_char=use_best_quote_char,
            minimize_boolean_attributes=minimize_boolean_attributes,
            use_trailing_solidus=use_trailing_solidus,
            space_before_trailing_solidus=space_before_trailing_solidus,
            escape_lt_in_attrs=escape_lt_in_attrs,
            escape_rcdata=escape_rcdata,
            resolve_entities=resolve_entities,
            alphabetical_attributes=alphabetical_attributes,
            strip_whitespace=strip_whitespace,
            include_doctype=include_doctype,
            expand_mixed_content=expand_mixed_content,
            expand_empty_elements=expand_empty_elements,
        )
    


    def html_to_markdown(self, html: str) -> str:
        """
        Convert HTML to Markdown using TextWizard's internal HTML parser/renderer.

        Parameters
        ----------
        html : str
            Raw HTML string to convert.

        Returns
        -------
        str
            Markdown representation of the input HTML. If the underlying parser
            cannot handle the input, the converter falls back gracefully and
            returns the original HTML string.

        """
        from textwizard.utils.tw_html_parser.html_to_md_dom import html_to_markdown_from_html
        return html_to_markdown_from_html(html)
