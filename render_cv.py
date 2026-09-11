from pathlib import Path
from playwright.sync_api import sync_playwright
import fitz

root=Path(__file__).resolve().parent
out=root/'output'/'pdf'; out.mkdir(parents=True,exist_ok=True)
qa=root/'tmp'/'pdfs'; qa.mkdir(parents=True,exist_ok=True)
with sync_playwright() as p:
    browser=p.chromium.launch(channel='msedge',headless=True)
    page=browser.new_page(viewport={'width':1100,'height':1000})
    page.goto((root/'daniel_montoya_cv_visual.html').as_uri())
    page.evaluate('document.fonts.ready')
    page.pdf(path=str(out/'Daniel_Camilo_Montoya_Full_Stack.pdf'),prefer_css_page_size=True,print_background=True)
    page.screenshot(path=str(qa/'screen.png'),full_page=True)
    with page.expect_download() as download:
        page.locator('[data-export-ats]').click()
    saved=Path(download.value.path()).read_text(encoding='utf-8')
    assert 'GraphQL' in saved and 'knowledge sharing' in saved.lower()
    (root/'daniel_montoya_cv_ats.txt').write_text(saved,encoding='utf-8')
    assert '- Optimized frontend code' in saved
    assert saved.index('TECHNICAL SKILLS') < saved.index('WORK EXPERIENCE') < saved.index('KNOWLEDGE SHARING')
    assert page.locator('.avatar').is_visible()
    assert page.locator('.contact-icon').count() == 5
    page.evaluate('window.print = () => { window.printInvoked = true; }')
    page.locator('[data-export-pdf]').click()
    assert page.evaluate('window.printInvoked === true')
    assert page.locator('.contact-text').evaluate_all('(els) => els.every(e => e.scrollWidth <= e.clientWidth)')
    page.set_viewport_size({'width':390,'height':844})
    assert page.evaluate('document.documentElement.scrollWidth <= innerWidth')
    page.screenshot(path=str(qa/'mobile.png'),full_page=True)
    browser.close()
doc=fitz.open(out/'Daniel_Camilo_Montoya_Full_Stack.pdf')
print('Pages:',len(doc))
full=''
for i,page in enumerate(doc):
    text=page.get_text(); full+=text
    print('Page',i+1, 'words:',len(text.split()), 'start:',text[:110].replace('\n',' | '), 'end:',text[-100:].replace('\n',' | '))
    page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(qa/f'page-{i+1}.png')
    for block in page.get_text('blocks'):
        assert block[0]>=0 and block[1]>=0 and block[2]<=page.rect.width and block[3]<=page.rect.height
assert len(doc)==2
for term in ['6+ years','GraphQL','Mentu','Sofka','Knowledge Sharing','B2','+57 350 707 5614','96.7%','$1,500','3.8','0.08','80 ms','30%','1 MB','GitHub cost policies']:
    assert term.lower() in full.lower(), term
    assert term.lower() in saved.lower(), term
assert full.index('Independent Full-Stack Developer') < full.index('eClass') < full.index('Mentu') < full.index('Sofka')
print('Text extraction, page bounds, export and mobile width checks passed.')
