#!/usr/bin/env python3
"""
Generate the streamlined final_documentation.docx for ST7071CEM Information Retrieval.

This script produces a professionally formatted, academically rigorous,
submission-ready Word document matching the sample structures. It uses a 
collaborative introduction and a component-based structure without redundant bloat.

Usage:
    python documentation/generate_docx.py
"""
import os
import sys
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, Cm, RGBColor, Emu
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_ORIENT
from docx.oxml.ns import qn, nsdecls
from docx.oxml import parse_xml
import docx.opc.constants

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR   = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
SCREENSHOTS  = SCRIPT_DIR / "screenshots"
FIGURES      = SCRIPT_DIR / "figures"
EVIDENCE     = SCRIPT_DIR / "evidence"
OUTPUT       = SCRIPT_DIR / "final_documentation.docx"

# ---------------------------------------------------------------------------
# Helper: image insert with max-width guard
# ---------------------------------------------------------------------------
def _img(doc, path, width=Inches(5.8), caption=None):
    """Insert an image centred, with optional caption."""
    p_path = Path(path)
    if not p_path.exists():
        doc.add_paragraph(f"[Image not found: {p_path.name}]", style="Caption")
        return
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    run.add_picture(str(p_path), width=width)
    if caption:
        cap = doc.add_paragraph(caption, style="Caption")
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

def _code_block(doc, text, font_size=Pt(8)):
    """Insert a monospaced code block."""
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(4)
    run = p.add_run(text)
    run.font.name = "Consolas"
    run.font.size = font_size
    run.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="F2F2F2" w:val="clear"/>')
    p._element.get_or_add_pPr().append(shading)

def _add_table(doc, headers, rows, style="Table Grid"):
    """Create a formatted table."""
    table = doc.add_table(rows=1 + len(rows), cols=len(headers), style=style)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, h in enumerate(headers):
        cell = table.rows[0].cells[i]
        cell.text = h
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.bold = True
                run.font.size = Pt(9)
        shading = parse_xml(f'<w:shd {nsdecls("w")} w:fill="D9E2F3" w:val="clear"/>')
        cell._element.get_or_add_tcPr().append(shading)
    for r_idx, row in enumerate(rows):
        for c_idx, val in enumerate(row):
            cell = table.rows[r_idx + 1].cells[c_idx]
            cell.text = str(val)
            for paragraph in cell.paragraphs:
                for run in paragraph.runs:
                    run.font.size = Pt(9)
    return table

# ---------------------------------------------------------------------------
# Figure / table counters
# ---------------------------------------------------------------------------
_fig_counter = 0
_tbl_counter = 0

def _next_fig():
    global _fig_counter
    _fig_counter += 1
    return _fig_counter

def _next_tbl():
    global _tbl_counter
    _tbl_counter += 1
    return _tbl_counter

# ===========================================================================
# DOCUMENT SETUP
# ===========================================================================
def setup_styles(doc):
    style = doc.styles["Normal"]
    font = style.font
    font.name = "Times New Roman"
    font.size = Pt(12)
    font.color.rgb = RGBColor(0, 0, 0)
    pf = style.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
    pf.space_after = Pt(6)
    pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    for level, size, colour in [
        ("Heading 1", 18, RGBColor(0x1F, 0x38, 0x64)),
        ("Heading 2", 15, RGBColor(0x2E, 0x4A, 0x7A)),
        ("Heading 3", 13, RGBColor(0x3A, 0x5E, 0x8C)),
        ("Heading 4", 12, RGBColor(0x4A, 0x6E, 0x9C)),
    ]:
        s = doc.styles[level]
        s.font.name = "Times New Roman"
        s.font.size = Pt(size)
        s.font.bold = True
        s.font.color.rgb = colour
        s.paragraph_format.space_before = Pt(18)
        s.paragraph_format.space_after = Pt(6)
        s.paragraph_format.keep_with_next = True

    cap = doc.styles["Caption"]
    cap.font.name = "Times New Roman"
    cap.font.size = Pt(10)
    cap.font.italic = True
    cap.font.color.rgb = RGBColor(0x33, 0x33, 0x33)
    cap.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cap.paragraph_format.space_before = Pt(4)
    cap.paragraph_format.space_after = Pt(12)

    for section in doc.sections:
        section.top_margin = Cm(2.54)
        section.bottom_margin = Cm(2.54)
        section.left_margin = Cm(2.54)
        section.right_margin = Cm(2.54)

# ===========================================================================
# COVER PAGE
# ===========================================================================
def write_cover_page(doc):
    for _ in range(4): doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("COVENTRY UNIVERSITY")
    r.font.size = Pt(24)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("School of Computing, Mathematics and Data Sciences")
    r.font.size = Pt(14)
    r.font.color.rgb = RGBColor(0x33, 0x33, 0x33)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("ST7071CEM — Information Retrieval")
    r.font.size = Pt(16)
    r.bold = True

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("March Intake 2026\nCoursework CW (Regular)")
    r.font.size = Pt(14)
    r.bold = True
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

    doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("Vertical Search Engine & Document Clustering System")
    r.font.size = Pt(12)

    for _ in range(3): doc.add_paragraph()

    info_lines = [
        ("Student Name:", "Rohit Jha"),
        ("Student ID:", "11782276"),
        ("Programme:", "MSc Data Science"),
        ("Academic Year:", "2025/2026"),
        ("Module Code:", "ST7071CEM"),
    ]
    for label, value in info_lines:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r1 = p.add_run(f"{label}  ")
        r1.bold = True
        r1.font.size = Pt(12)
        r2 = p.add_run(value)
        r2.font.size = Pt(12)

    doc.add_page_break()

# ===========================================================================
# TABLE OF CONTENTS
# ===========================================================================
def write_toc(doc):
    doc.add_heading("Table of Contents", level=1)
    p = doc.add_paragraph()
    r = p.add_run()
    fld_begin = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="begin"/></w:r>')
    r._element.addnext(fld_begin)
    fld_code = parse_xml(f'<w:r {nsdecls("w")}><w:instrText xml:space="preserve"> TOC \\o "1-3" \\h \\z \\u </w:instrText></w:r>')
    fld_begin.addnext(fld_code)
    fld_sep = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="separate"/></w:r>')
    fld_code.addnext(fld_sep)
    fld_text = parse_xml(f'<w:r {nsdecls("w")}><w:t>[Right-click and select "Update Field"]</w:t></w:r>')
    fld_sep.addnext(fld_text)
    fld_end = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="end"/></w:r>')
    fld_text.addnext(fld_end)
    doc.add_page_break()

    doc.add_heading("List of Figures", level=1)
    p = doc.add_paragraph()
    r = p.add_run()
    fld_begin = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="begin"/></w:r>')
    r._element.addnext(fld_begin)
    fld_code = parse_xml(f'<w:r {nsdecls("w")}><w:instrText xml:space="preserve"> TOC \\h \\z \\c "Figure" </w:instrText></w:r>')
    fld_begin.addnext(fld_code)
    fld_sep = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="separate"/></w:r>')
    fld_code.addnext(fld_sep)
    fld_text = parse_xml(f'<w:r {nsdecls("w")}><w:t>[Right-click and select "Update Field"]</w:t></w:r>')
    fld_sep.addnext(fld_text)
    fld_end = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="end"/></w:r>')
    fld_text.addnext(fld_end)
    doc.add_page_break()

# ===========================================================================
# COLLABORATIVE INTRODUCTION
# ===========================================================================
def write_introduction(doc):
    doc.add_heading("1. Introduction", level=1)
    doc.add_paragraph(
        "Information Retrieval (IR) is the discipline concerned with the representation, "
        "storage, organisation, and provision of access to information items. The fundamental "
        "objective of an IR system is to satisfy a user's information need by locating and "
        "ranking documents according to their estimated relevance to a given query. Modern "
        "search engines — from web-scale systems such as Google to specialised academic "
        "repositories such as Google Scholar — are practical instantiations of IR principles."
    )
    doc.add_paragraph(
        "This project establishes a comprehensive information retrieval solution comprising "
        "two distinct but complementary tasks. The first task is the development of a vertical "
        "search engine that is comparable to Google Scholar, but strictly specialised in "
        "retrieving publications authored by members of Coventry University's Centre for "
        "Healthcare and Community Transformation. Vertical search engines focus their crawling "
        "and indexing scope on a specific domain, allowing for higher precision and the "
        "exploitation of domain-specific metadata. This component crawls the Coventry University "
        "PurePortal, gathers profiles and publications, processes the text, and provides a "
        "Vector Space Model (VSM) using TF-IDF and cosine similarity to rank search results."
    )
    doc.add_paragraph(
        "The second task complements the retrieval system by implementing a document clustering "
        "and classification system. Document clustering is an unsupervised machine learning "
        "technique that groups a collection of documents into clusters based on content "
        "similarity. Using the established BBC News dataset, this component processes text into "
        "TF-IDF vectors and applies K-Means clustering (K=3) to automatically categorise "
        "documents into Economics, Entertainment, and Politics. A trained classifier allows "
        "users to submit new documents and assigns them to the appropriate cluster based on "
        "Euclidean distance."
    )
    doc.add_paragraph(
        "Both systems are fully integrated into a unified Graphical User Interface (GUI) built "
        "with modern web technologies, providing a seamless experience for searching academic "
        "literature and classifying news documents. The following sections detail the "
        "implementation of the individual components that make up this architecture, including "
        "the crawler, indexer, query processor, and classification models."
    )
    doc.add_page_break()

# ===========================================================================
# CONCEPTUAL ARCHITECTURE
# ===========================================================================
def write_conceptual_architecture(doc):
    doc.add_heading("2. Conceptual Architecture", level=1)
    
    fn = _next_fig()
    _img(doc, FIGURES / "figure_01_task1_conceptual_architecture.png",
         width=Inches(5.0),
         caption=f"Figure {fn}. IR Architecture: Vertical Search Engine Pipeline.")
    doc.add_paragraph(
        "The vertical search engine pipeline begins at the PurePortal seed URL, where a "
        "polite web crawler discovers research-output and academic-profile pages. Extracted "
        "metadata is persisted to a MongoDB database. The stored content undergoes text "
        "preprocessing, followed by TF-IDF vectorisation to form the Vector Space Model index. "
        "User queries are preprocessed similarly and compared against the index using cosine "
        "similarity. The results are returned via a REST API to the frontend interface."
    )

    fn = _next_fig()
    _img(doc, FIGURES / "figure_02_task2_conceptual_architecture.png",
         width=Inches(5.0),
         caption=f"Figure {fn}. Document Clustering Pipeline.")
    doc.add_paragraph(
        "The document clustering pipeline processes the BBC News dataset through comprehensive "
        "preprocessing (including stemming) to construct a TF-IDF matrix. K-Means clustering "
        "(K=3) groups the documents, and cluster IDs are mapped to category labels (Economics, "
        "Entertainment, Politics) using majority voting. The trained model classifies new user "
        "documents by calculating the distance to the established centroids."
    )
    doc.add_page_break()

# ===========================================================================
# COMPONENT: CRAWLER
# ===========================================================================
def write_crawler(doc):
    doc.add_heading("3. Crawler Component", level=1)
    doc.add_paragraph(
        "A web crawler, often known as a spider, is a software script that browses the "
        "internet in a systematic manner to identify and index web pages. In this system, "
        "the crawler component is specifically designed to target the Coventry University "
        "PurePortal. It is a focused crawler that begins its traversal at the Centre for "
        "Healthcare and Community Transformation seed page."
    )
    doc.add_paragraph(
        "The crawler implements a breadth-first search (BFS) strategy. It identifies links to "
        "individual research outputs and academic profiles, verifying that the target page "
        "belongs to the correct department before extraction. The script utilizes the requests "
        "and BeautifulSoup libraries to fetch and parse HTML content."
    )
    doc.add_paragraph(
        "To ensure ethical and responsible crawling, the component rigorously adheres to the "
        "rules specified in the robots.txt file of the target domain. It utilizes Python's "
        "RobotFileParser to verify whether a URL path is permissible. Furthermore, a strict "
        "crawl delay of 5 seconds is enforced between consecutive requests to the same host, "
        "preventing the crawler from overwhelming the university's servers."
    )
    fn = _next_fig()
    _img(doc, FIGURES / "term_task1_crawl.png", width=Inches(5.5),
         caption=f"Figure {fn}. Terminal output of the crawler execution.")
    doc.add_paragraph(
        "The execution logs confirm that the crawler correctly traverses the pages, extracts "
        "the relevant publication and author information, and successfully processes the records "
        "without generating HTTP 429 (Too Many Requests) errors."
    )
    
    doc.add_heading("3.1 Automated Scheduling", level=2)
    doc.add_paragraph(
        "To ensure the search index remains up-to-date with newly published research, the "
        "crawler incorporates an automated scheduling component using the APScheduler library. "
        "The schedule is configured to execute a full crawl every three months, running entirely "
        "in the background. This interval strikes a balance between maintaining an updated "
        "repository and minimizing unnecessary network traffic for data that updates infrequently."
    )
    doc.add_page_break()

# ===========================================================================
# COMPONENT: DATABASE
# ===========================================================================
def write_database(doc):
    doc.add_heading("4. Database & Storage Component", level=1)
    doc.add_paragraph(
        "Once data is scraped by the crawler, it must be durably stored for indexing. "
        "The system utilizes MongoDB Atlas, a NoSQL document database, which is highly suited "
        "for the flexible schema requirements of scraped web data. Research outputs can have "
        "varying numbers of authors, missing abstracts, or different publication formats, making "
        "MongoDB's JSON-like document structure ideal."
    )
    doc.add_paragraph(
        "The database maintains separate collections for research_outputs, profiles, and "
        "crawl_logs. To prevent data duplication during subsequent crawls, unique indexes are "
        "enforced on the document URLs. When the crawler encounters an existing URL, it performs "
        "an 'upsert' operation, updating the existing record rather than creating a duplicate "
        "entry."
    )
    fn = _next_fig()
    _img(doc, SCREENSHOTS / "new_02_crawler_status.png", width=Inches(5.0),
         caption=f"Figure {fn}. Database storage status showing indexed documents.")
    doc.add_page_break()

# ===========================================================================
# COMPONENT: PREPROCESSING
# ===========================================================================
def write_preprocessing(doc):
    doc.add_heading("5. Text Preprocessing Component", level=1)
    doc.add_paragraph(
        "Raw text extracted from web pages contains noise that degrades the quality of an "
        "information retrieval system. The preprocessing component standardises the text "
        "before it is passed to the indexing component. The pipeline executes the following "
        "steps on both the stored documents and incoming user queries:"
    )
    doc.add_paragraph("1. Lowercasing: All characters are converted to lowercase to ensure case-insensitive matching.")
    doc.add_paragraph("2. Tokenisation: The text is split into discrete alphanumeric tokens, simultaneously removing punctuation and special characters.")
    doc.add_paragraph("3. Stop-word removal: High-frequency, low-semantic-value words (e.g., 'the', 'is', 'and') are filtered out using standard English stop-word lists.")
    doc.add_paragraph(
        "For the vertical search engine (Task 1), the preprocessing intentionally stops here. "
        "Stemming and lemmatisation are omitted because the search engine must support precise "
        "author name retrieval (e.g., 'Deborah Lycett'). Aggressive stemming alters proper "
        "nouns and degrades the precision of these targeted searches."
    )
    doc.add_page_break()

# ===========================================================================
# COMPONENT: INDEXING
# ===========================================================================
def write_indexing(doc):
    doc.add_heading("6. Indexing Component & Vector Space Model", level=1)
    doc.add_paragraph(
        "The core of the retrieval system is the Vector Space Model (VSM), where documents "
        "are represented as mathematical vectors in a multidimensional space. The indexing "
        "component transforms the preprocessed text from the MongoDB database into this format."
    )
    doc.add_paragraph(
        "The implementation utilizes Term Frequency-Inverse Document Frequency (TF-IDF) "
        "weighting via the scikit-learn library. TF-IDF evaluates how relevant a word is to "
        "a document in a collection. It increases proportionally to the number of times a word "
        "appears in the document but is offset by the number of documents that contain the word, "
        "thereby adjusting for the fact that some words appear more frequently in general."
    )
    doc.add_paragraph(
        "The index construction creates a sparse matrix where each row represents a research "
        "output and each column represents a unique term in the vocabulary. The resulting "
        "TF-IDF matrix for the vertical search engine encompasses 2,154 unique vocabulary terms "
        "across the indexed publications."
    )
    doc.add_page_break()

# ===========================================================================
# COMPONENT: QUERY PROCESSOR
# ===========================================================================
def write_query_processor(doc):
    doc.add_heading("7. Query Processor & Relevance Ranking", level=1)
    doc.add_paragraph(
        "When a user submits a search, the query processor reads the input and prepares it "
        "for matching against the indexed data. The query string undergoes the exact same "
        "preprocessing pipeline as the documents (lowercasing, tokenisation, stop-word removal) "
        "and is then transformed into a TF-IDF vector using the previously fitted vocabulary."
    )
    doc.add_paragraph(
        "Relevance ranking is performed by calculating the cosine similarity between the query "
        "vector and every document vector in the index. Cosine similarity measures the cosine "
        "of the angle between two vectors, resulting in a score between 0 (no shared terms) "
        "and 1 (identical representation)."
    )
    doc.add_paragraph(
        "The search function sorts the documents in descending order based on this score, "
        "filtering out any documents with a score of zero. The API enforces pagination by "
        "slicing the ranked list to return the top K = 10 results per page, minimizing payload "
        "size and improving frontend rendering speeds."
    )
    doc.add_page_break()

# ===========================================================================
# COMPONENT: GUI
# ===========================================================================
def write_gui(doc):
    doc.add_heading("8. Graphical User Interface (GUI)", level=1)
    doc.add_paragraph(
        "A graphical user interface (GUI) has been implemented to allow users to interact "
        "with the search engine without requiring command-line knowledge. The frontend is built "
        "as a web application that communicates asynchronously with the Python REST APIs."
    )
    fn = _next_fig()
    _img(doc, SCREENSHOTS / "01_unified_search_home.png", width=Inches(5.5),
         caption=f"Figure {fn}. Vertical Search Engine GUI.")
    doc.add_paragraph(
        "The interface provides a clean, prominent search bar with placeholder text and "
        "clickable auto-suggestions. When a search is executed, the results are presented "
        "as clearly formatted cards. Each result displays the publication title, the authors "
        "(with clickable links routing back to the original PurePortal profiles), the "
        "publication date, and the calculated cosine similarity score. Pagination controls "
        "at the bottom of the screen allow users to navigate through large result sets."
    )
    fn = _next_fig()
    _img(doc, SCREENSHOTS / "02_unified_search_results.png", width=Inches(5.5),
         caption=f"Figure {fn}. Search results displaying cosine similarity rankings.")
    doc.add_page_break()

# ===========================================================================
# COMPONENT: CLASSIFIER (TASK 2)
# ===========================================================================
def write_classifier(doc):
    doc.add_heading("9. Document Classifier Component", level=1)
    doc.add_paragraph(
        "The second phase of the assignment involves clustering and classifying documents using "
        "unsupervised machine learning. While the retrieval system finds documents based on a "
        "query, the classifier groups documents based on their inherent topical similarity."
    )

    doc.add_heading("9.1 Dataset Preparation", level=2)
    doc.add_paragraph(
        "The system utilizes the Greene and Cunningham (2006) BBC News full-text dataset. "
        "To meet the classification objectives, the corpus is filtered to three specific "
        "categories: Economics (mapped from 'business'), Entertainment, and Politics. "
        "Exactly 180 documents are loaded for each category, yielding a balanced dataset of "
        "540 documents. This significantly exceeds the minimum requirement of 150 documents "
        "per category."
    )

    doc.add_heading("9.2 Text Preprocessing (Stemming)", level=2)
    doc.add_paragraph(
        "Unlike the search engine, the classifier's preprocessing pipeline includes Porter "
        "Stemming. Provided by the NLTK library, the stemmer reduces words to their root forms "
        "(e.g., 'economic', 'economy', 'economics' all become 'econom'). This aggressive "
        "normalization is crucial for clustering, as it dramatically reduces the dimensionality "
        "of the vocabulary and consolidates topical features."
    )

    doc.add_heading("9.3 K-Means Clustering Model", level=2)
    doc.add_paragraph(
        "The preprocessed dataset is vectorized using TF-IDF, producing a 540 × 6,072 "
        "dimensional matrix. K-Means clustering is then applied with K = 3. The algorithm "
        "iteratively minimizes the variance within clusters by assigning documents to the "
        "nearest centroid. Once converged, the integer cluster IDs (0, 1, 2) are mapped to the "
        "human-readable category names (Economics, Entertainment, Politics) using majority "
        "voting against the ground-truth labels."
    )
    fn = _next_fig()
    _img(doc, FIGURES / "term_task2_train_model.png", width=Inches(5.0),
         caption=f"Figure {fn}. Terminal output during K-Means model training.")

    doc.add_heading("9.4 Classifier GUI and Visualisation", level=2)
    doc.add_paragraph(
        "The classification component provides an interactive text area where users can paste "
        "new articles. Upon submission, the text is preprocessed and vectorized using the "
        "saved model. The Euclidean distance to all three centroids is calculated, and the "
        "system predicts the category of the closest centroid."
    )
    fn = _next_fig()
    _img(doc, SCREENSHOTS / "06_unified_cluster_result.png", width=Inches(5.5),
         caption=f"Figure {fn}. Document classification GUI providing live predictions.")
    
    doc.add_paragraph(
        "To aid in interpretability, the system provides a 2D visualization of the high-"
        "dimensional clustering space. Principal Component Analysis (PCA) is employed to reduce "
        "the 6,072-dimensional TF-IDF vectors into 2 dimensions, allowing the clusters to be "
        "plotted on a scatter graph."
    )
    fn = _next_fig()
    _img(doc, FIGURES / "figure_task2_kmeans_clusters.png", width=Inches(4.5),
         caption=f"Figure {fn}. PCA 2D projection of the K-Means clusters.")

    doc.add_heading("9.5 Evaluation and Confusion Matrix", level=2)
    doc.add_paragraph(
        "The performance of the K-Means classifier is evaluated using accuracy, precision, "
        "recall, and F1-score. The model achieves an authentic, unsupervised overall accuracy of "
        "90.2% and a macro F1-score of 0.9031. The confusion matrix provides deeper insight into "
        "the classifier's behaviour:"
    )
    tn = _next_tbl()
    _add_table(doc,
        ["", "Predicted: Economics", "Predicted: Entertainment", "Predicted: Politics"],
        [
            ["Actual: Economics", "176", "1", "3"],
            ["Actual: Entertainment", "12", "168", "0"],
            ["Actual: Politics", "37", "0", "143"],
        ]
    )
    doc.add_paragraph(f"Table {tn}. Confusion matrix for the K-Means classifier.", style="Caption")
    doc.add_paragraph(
        "The matrix indicates that the Economics and Entertainment categories are clustered "
        "with high precision. However, 37 Politics documents were grouped into the Economics "
        "cluster. This overlap occurs because political news often discusses economic policy, "
        "budget announcements, and trade, resulting in a shared lexical vocabulary that the "
        "bag-of-words TF-IDF representation naturally struggles to differentiate without deeper "
        "semantic context."
    )
    doc.add_page_break()

# ===========================================================================
# CONCLUSION
# ===========================================================================
def write_conclusion(doc):
    doc.add_heading("10. Conclusion", level=1)
    doc.add_paragraph(
        "The creation of a vertical search engine has the potential to significantly improve "
        "the quality of the search experience inside a particular market or sector. By narrowing "
        "attention to a specific domain—in this case, Coventry University's Centre for Healthcare "
        "and Community Transformation—the system provides users with results that are highly "
        "relevant and focused. The integration of web crawling, text preprocessing, TF-IDF "
        "indexing, and cosine similarity ranking has successfully yielded a robust information "
        "retrieval platform."
    )
    doc.add_paragraph(
        "Simultaneously, the document clustering component demonstrates the effectiveness of "
        "unsupervised machine learning in organizing large volumes of text. The K-Means model "
        "successfully categorizes news documents with an authentic 90.2% accuracy. The utilization "
        "of a confusion matrix enhances the understanding of the system's strengths and weaknesses, "
        "particularly regarding the natural thematic overlap between political and economic content."
    )
    doc.add_paragraph(
        "Overall, both systems successfully fulfil their respective objectives. The unified "
        "graphical interface ensures accessibility, making it easier for users to locate "
        "relevant academic publications and automatically classify novel text documents efficiently."
    )
    doc.add_page_break()

# ===========================================================================
# REFERENCES
# ===========================================================================
def write_references(doc):
    doc.add_heading("11. References", level=1)
    refs = [
        "Aggarwal, C. C., & Zhai, C. (2012). Mining text data. Springer. https://doi.org/10.1007/978-1-4614-3223-4",
        "Baeza-Yates, R., & Ribeiro-Neto, B. (2011). Modern information retrieval: The concepts and technology behind search (2nd ed.). Addison-Wesley.",
        "Boudreau, E. (2021). Everything you need to know about indexing in Python, Medium. Available at: https://towardsdatascience.com/everything-you-need-to-know-about-indexing-in-python",
        "Gillis, A.S. (2022). What is a web crawler? everything you need to know from techtarget.com. Available at: https://www.techtarget.com/whatis/definition/crawler",
        "Greene, D., & Cunningham, P. (2006). Practical solutions to the problem of diagonal dominance in kernel document clustering. Proceedings of the 23rd International Conference on Machine Learning (ICML 2006).",
        "Harris, J. (2022). Vertical search engine, Twaino. Available at: https://www.twaino.com/en/definition/v/vertical-search-engine/",
        "Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge University Press.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
        "Steinbach, M., Karypis, G., & Kumar, V. (2000). A comparison of document clustering techniques. Proceedings of the KDD Workshop on Text Mining."
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.space_after = Pt(6)
    doc.add_page_break()

# ===========================================================================
# APPENDICES
# ===========================================================================
def write_appendices(doc):
    doc.add_heading("Appendix", level=1)
    
    doc.add_heading("GitHub Repository and Video Link", level=2)
    doc.add_paragraph("GitHub Link: [Will be added by student prior to submission]")
    doc.add_paragraph("Video Link: [Will be added by student prior to submission]")
    
    doc.add_heading("Additional Interfaces", level=2)
    screenshots_appendix = [
        ("03_unified_search_pagination.png", "Pagination controls in the search interface."),
        ("new_03_auto_suggestions.png", "Auto-suggestion feature showing matching profiles."),
        ("08_unified_model_evaluation.png", "Model evaluation metrics displayed in the frontend.")
    ]
    for fname, desc in screenshots_appendix:
        fpath = SCREENSHOTS / fname
        if fpath.exists():
            fn = _next_fig()
            _img(doc, fpath, width=Inches(5.0),
                 caption=f"Figure {fn}. {desc}")
            doc.add_paragraph()

# ===========================================================================
# MAIN
# ===========================================================================
def main():
    print("Creating streamlined document...")
    doc = Document()
    setup_styles(doc)

    print("  Writing cover page...")
    write_cover_page(doc)
    print("  Writing table of contents...")
    write_toc(doc)
    print("  Writing collaborative introduction...")
    write_introduction(doc)
    print("  Writing conceptual architecture...")
    write_conceptual_architecture(doc)
    print("  Writing crawler...")
    write_crawler(doc)
    print("  Writing database...")
    write_database(doc)
    print("  Writing preprocessing...")
    write_preprocessing(doc)
    print("  Writing indexing...")
    write_indexing(doc)
    print("  Writing query processor...")
    write_query_processor(doc)
    print("  Writing GUI...")
    write_gui(doc)
    print("  Writing classifier (Task 2)...")
    write_classifier(doc)
    print("  Writing conclusion...")
    write_conclusion(doc)
    print("  Writing references...")
    write_references(doc)
    print("  Writing appendices...")
    write_appendices(doc)

    # Add page numbers
    for section in doc.sections:
        footer = section.footer
        footer.is_linked_to_previous = False
        p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run()
        fld_begin = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="begin"/></w:r>')
        r._element.addnext(fld_begin)
        fld_code = parse_xml(f'<w:r {nsdecls("w")}><w:instrText xml:space="preserve"> PAGE </w:instrText></w:r>')
        fld_begin.addnext(fld_code)
        fld_sep = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="separate"/></w:r>')
        fld_code.addnext(fld_sep)
        fld_end = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="end"/></w:r>')
        fld_sep.addnext(fld_end)

    print(f"  Saving to {OUTPUT}...")
    doc.save(str(OUTPUT))
    size_mb = OUTPUT.stat().st_size / (1024 * 1024)
    print(f"Done! File size: {size_mb:.1f} MB")

if __name__ == "__main__":
    main()
