from docx import Document
from docx.oxml import parse_xml

doc = Document()
p = doc.add_paragraph()
omml = """
<m:oMathPara xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <m:oMath>
    <m:r>
      <w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>
      <m:t>TF(t, d) = </m:t>
    </m:r>
    <m:f>
      <m:fPr>
        <m:ctrlPr/>
      </m:fPr>
      <m:num>
        <m:r>
          <w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>
          <m:t>Q · D</m:t>
        </m:r>
      </m:num>
      <m:den>
        <m:r>
          <w:rPr><w:rFonts w:ascii="Cambria Math" w:hAnsi="Cambria Math"/></w:rPr>
          <m:t>||Q|| × ||D||</m:t>
        </m:r>
      </m:den>
    </m:f>
  </m:oMath>
</m:oMathPara>
"""
element = parse_xml(omml)
p._element.append(element)
doc.save('test_math.docx')
print("Saved test_math.docx")
