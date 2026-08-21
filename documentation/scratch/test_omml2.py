from docx import Document
from docx.oxml import parse_xml

doc = Document()
p = doc.add_paragraph()
omml = """
<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <m:oMath>
    <m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:i/></w:rPr><m:t>WCSS = </m:t></m:r>
    <m:nary>
      <m:naryPr>
        <m:chr m:val="∑"/>
        <m:limLoc m:val="undOvr"/>
        <m:subHide m:val="0"/>
        <m:supHide m:val="0"/>
      </m:naryPr>
      <m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:i/></w:rPr><m:t>i=1</m:t></m:r></m:sub>
      <m:sup><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:i/></w:rPr><m:t>K</m:t></m:r></m:sup>
      <m:e>
        <m:nary>
          <m:naryPr>
            <m:chr m:val="∑"/>
            <m:limLoc m:val="undOvr"/>
            <m:subHide m:val="0"/>
            <m:supHide m:val="1"/>
          </m:naryPr>
          <m:sub><m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:i/></w:rPr><m:t>x ∈ C_i</m:t></m:r></m:sub>
          <m:sup/>
          <m:e>
            <m:sSup>
              <m:sSupPr/>
              <m:e>
                <m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/><w:i/></w:rPr><m:t>||x - μ_i||</m:t></m:r>
              </m:e>
              <m:sup>
                <m:r><w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr><m:t>2</m:t></m:r>
              </m:sup>
            </m:sSup>
          </m:e>
        </m:nary>
      </m:e>
    </m:nary>
  </m:oMath>
</m:oMathPara>
"""
try:
    element = parse_xml(omml)
    p._element.append(element)
    doc.save('test_math2.docx')
    print("Success")
except Exception as e:
    print(f"Failed: {e}")
