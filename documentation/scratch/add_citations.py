import re
from pathlib import Path

file_path = Path("documentation/generate_docx.py")
content = file_path.read_text(encoding="utf-8")

# 1. Add imports
content = content.replace(
    "import json\nfrom pathlib import Path",
    "import json\nimport re\nimport html\nfrom pathlib import Path"
)

# 2. Add functions
functions = """
_bookmark_id_counter = 100

def add_internal_hyperlink(paragraph, text, bookmark_name):
    \"\"\"Adds a clickable internal hyperlink to a paragraph using field codes.\"\"\"
    fld_begin = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="begin"/></w:r>')
    paragraph._p.append(fld_begin)
    
    fld_instr = parse_xml(f'<w:r {nsdecls("w")}><w:instrText xml:space="preserve"> HYPERLINK \\l "{bookmark_name}" </w:instrText></w:r>')
    paragraph._p.append(fld_instr)
    
    fld_sep = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="separate"/></w:r>')
    paragraph._p.append(fld_sep)
    
    run = parse_xml(
        f'<w:r {nsdecls("w")}>'
        f'<w:rPr>'
        f'<w:color w:val="0055AA"/>'
        f'<w:b w:val="1"/>'
        f'</w:rPr>'
        f'<w:t>{html.escape(text)}</w:t>'
        f'</w:r>'
    )
    paragraph._p.append(run)
    
    fld_end = parse_xml(f'<w:r {nsdecls("w")}><w:fldChar w:fldCharType="end"/></w:r>')
    paragraph._p.append(fld_end)

def _p_cite(doc, text):
    \"\"\"Add a justified paragraph with highlighted inline citations (enclosed in [[Text|Bookmark]] or [[Text]] for unlinked).\"\"\"
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    parts = re.split(r'(\[\[.*?\]\])', text)
    for part in parts:
        if part.startswith('[[') and part.endswith(']]'):
            content = part[2:-2]
            if '|' in content:
                cite_text, bm = content.split('|', 1)
                add_internal_hyperlink(p, cite_text, bm)
            else:
                run = p.add_run(content)
                run.font.color.rgb = RGBColor(0x00, 0x55, 0xAA)
                run.font.bold = True
        else:
            p.add_run(part)

"""
content = content.replace(
    "def _img(doc, path, width=Inches(6.5), caption=None):",
    functions + "def _img(doc, path, width=Inches(6.5), caption=None):"
)

# 3. Replace the 5 paragraphs
# Gillis
content = content.replace(
    '''    doc.add_paragraph(
        "A web crawler, often known as a spider, is a software script that browses the "
        "internet in a systematic manner to identify and index web pages (Gillis, 2022). In "
        "this system, the crawler component is specifically designed to target the Coventry "
        "University PurePortal. It is a focused crawler that begins its traversal at the Centre "
        "for Healthcare and Community Transformation seed page."
    )''',
    '''    _p_cite(doc,
        "A web crawler, often known as a spider, is a software script that browses the "
        "internet in a systematic manner to identify and index web pages [[(Gillis, 2022)|REF_GILLIS]]. In "
        "this system, the crawler component is specifically designed to target the Coventry "
        "University PurePortal. It is a focused crawler that begins its traversal at the Centre "
        "for Healthcare and Community Transformation seed page."
    )'''
)

# Richardson
content = content.replace(
    '''    doc.add_paragraph(
        "The crawler implements a breadth-first search (BFS) strategy. It identifies links to "
        "individual research outputs and academic profiles, verifying that the target page "
        "belongs to the correct department before extraction. The script utilizes the requests "
        "and BeautifulSoup libraries to fetch and parse HTML content."
    )''',
    '''    _p_cite(doc,
        "The crawler implements a breadth-first search (BFS) strategy. It identifies links to "
        "individual research outputs and academic profiles, verifying that the target page "
        "belongs to the correct department before extraction. The script utilizes the requests "
        "and BeautifulSoup libraries to fetch and parse HTML content [[(Richardson, 2022)|REF_RICHARDSON]]."
    )'''
)

# Chodorow
content = content.replace(
    '''    doc.add_paragraph(
        "Once data is scraped by the crawler, it must be durably stored for indexing. "
        "The system utilizes MongoDB Atlas, a NoSQL document database, which is highly suited "
        "for the flexible schema requirements of scraped web data. Research outputs can have "
        "varying numbers of authors, missing abstracts, or different publication formats, making "
        "MongoDB's JSON-like document structure ideal."
    )''',
    '''    _p_cite(doc,
        "Once data is scraped by the crawler, it must be durably stored for indexing. "
        "The system utilizes MongoDB Atlas, a NoSQL document database, which is highly suited "
        "for the flexible schema requirements of scraped web data [[(Chodorow, 2013)|REF_CHODOROW]]. Research outputs can have "
        "varying numbers of authors, missing abstracts, or different publication formats, making "
        "MongoDB's JSON-like document structure ideal."
    )'''
)

# Manning
content = content.replace(
    '''    doc.add_paragraph(
        "The core of the retrieval system is the Vector Space Model (VSM), where documents "
        "are represented as mathematical vectors in a multidimensional space (Manning, Raghavan "
        "and Schütze, 2008). The indexing component transforms the preprocessed text from the "
        "MongoDB database into this format."
    )''',
    '''    _p_cite(doc,
        "The core of the retrieval system is the Vector Space Model (VSM), where documents "
        "are represented as mathematical vectors in a multidimensional space [[(Manning, Raghavan and Schütze, 2008)|REF_MANNING]]. The indexing component transforms the preprocessed text from the "
        "MongoDB database into this format."
    )'''
)

# Pedregosa + Jones
content = content.replace(
    '''    doc.add_paragraph(
        "The implementation utilizes Term Frequency-Inverse Document Frequency (TF-IDF) "
        "weighting via the scikit-learn library (Pedregosa et al., 2011). TF-IDF evaluates "
        "how relevant a word is to a document in a collection. The mathematical formulation is:"
    )''',
    '''    _p_cite(doc,
        "The implementation utilizes Term Frequency-Inverse Document Frequency (TF-IDF) "
        "weighting via the scikit-learn library [[(Pedregosa et al., 2011)|REF_PEDREGOSA]]. TF-IDF, originally introduced to evaluate term specificity [[(Jones, 1972)|REF_JONES]], evaluates "
        "how relevant a word is to a document in a collection. The mathematical formulation is:"
    )'''
)

# MacQueen
content = content.replace(
    '''    doc.add_paragraph(
        "The second task complements the retrieval system by implementing a document clustering "
        "and classification system. Document clustering is an unsupervised machine learning "
        "technique that groups a collection of documents into clusters based on content "
        "similarity. Using the established BBC News dataset, this component processes text into "
        "TF-IDF vectors and applies K-Means clustering (K=3) to automatically categorise "
        "documents into Economics, Entertainment, and Politics. A trained classifier allows "
        "users to submit new documents and assigns them to the appropriate cluster based on "
        "Euclidean distance."
    )''',
    '''    _p_cite(doc,
        "The second task complements the retrieval system by implementing a document clustering "
        "and classification system. Document clustering is an unsupervised machine learning "
        "technique that groups a collection of documents into clusters based on content "
        "similarity. Using the established BBC News dataset, this component processes text into "
        "TF-IDF vectors and applies K-Means clustering (K=3) [[(MacQueen, 1967)|REF_MACQUEEN]] to automatically categorise "
        "documents into Economics, Entertainment, and Politics. A trained classifier allows "
        "users to submit new documents and assigns them to the appropriate cluster based on "
        "Euclidean distance."
    )'''
)

# 4. Replace write_references
old_refs = """def write_references(doc):
    doc.add_heading("12. References", level=1)
    refs = [
        "Aggarwal, C. C., & Zhai, C. (2012). Mining text data. Springer. https://doi.org/10.1007/978-1-4614-3223-4",
        "Baeza-Yates, R., & Ribeiro-Neto, B. (2011). Modern information retrieval: The concepts and technology behind search (2nd ed.). Addison-Wesley.",
        "Gillis, A.S. (2022). What is a web crawler? everything you need to know. TechTarget. Available at: https://www.techtarget.com/whatis/definition/crawler",
        "Greene, D., & Cunningham, P. (2006). Practical solutions to the problem of diagonal dominance in kernel document clustering. Proceedings of the 23rd International Conference on Machine Learning (ICML 2006).",
        "Harris, J. (2022). Vertical search engine. Twaino. Available at: https://www.twaino.com/en/definition/v/vertical-search-engine/",
        "Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to information retrieval. Cambridge University Press.",
        "Pedregosa, F., et al. (2011). Scikit-learn: Machine learning in Python. Journal of Machine Learning Research, 12, 2825–2830.",
        "Steinbach, M., Karypis, G., & Kumar, V. (2000). A comparison of document clustering techniques. Proceedings of the KDD Workshop on Text Mining.",
    ]
    for ref in refs:
        p = doc.add_paragraph(ref)
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.space_after = Pt(6)
    doc.add_page_break()"""

new_refs = """def write_references(doc):
    doc.add_heading("12. References", level=1)
    
    refs = [
        ("REF_CHODOROW", "Chodorow, K. (2013). MongoDB: The Definitive Guide (2nd ed.). O'Reilly Media."),
        ("REF_COVENTRY", "Coventry University. (2025). Centre for Healthcare and Community Transformation. https://pureportal.coventry.ac.uk/en/organisations/centre-for-healthcare-and-community-transformation"),
        ("REF_GILLIS", "Gillis, A. S. (2022). What is a web crawler? TechTarget. https://www.techtarget.com/whatis/definition/Web-crawler"),
        ("REF_JOLLIFFE", "Jolliffe, I. T. (2002). Principal Component Analysis (2nd ed.). Springer."),
        ("REF_JONES", "Jones, K. S. (1972). A statistical interpretation of term specificity and its application in retrieval. Journal of Documentation, 28(1), 11-21."),
        ("REF_MACQUEEN", "MacQueen, J. (1967). Some methods for classification and analysis of multivariate observations. Proceedings of the Fifth Berkeley Symposium on Mathematical Statistics and Probability, 1(14), 281-297."),
        ("REF_MANNING", "Manning, C. D., Raghavan, P., & Schütze, H. (2008). Introduction to Information Retrieval. Cambridge University Press."),
        ("REF_PEDREGOSA", "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine Learning in Python. Journal of Machine Learning Research, 12, 2825-2830."),
        ("REF_RICHARDSON", "Richardson, L. (2022). Beautiful Soup Documentation. Crummy. https://www.crummy.com/software/BeautifulSoup/bs4/doc/"),
    ]
    
    global _bookmark_id_counter
    for bm_name, ref_text in refs:
        p = doc.add_paragraph()
        p.paragraph_format.first_line_indent = Inches(-0.5)
        p.paragraph_format.left_indent = Inches(0.5)
        p.paragraph_format.space_after = Pt(6)
        
        _bookmark_id_counter += 1
        bm_start = parse_xml(f'<w:bookmarkStart {nsdecls("w")} w:id="{_bookmark_id_counter}" w:name="{bm_name}"/>')
        p._p.append(bm_start)
        
        p.add_run(ref_text)
        
        bm_end = parse_xml(f'<w:bookmarkEnd {nsdecls("w")} w:id="{_bookmark_id_counter}"/>')
        p._p.append(bm_end)

    doc.add_page_break()"""

content = content.replace(old_refs, new_refs)

file_path.write_text(content, encoding="utf-8")
print("Modifications applied successfully.")
