from playwright.async_api import Page

PAGE_SCRIPT = r"""() => {
  const toUrl = (value) => {
    try { return new URL(value, location.href).href; }
    catch { return ''; }
  };
  const isHttp = (value) => value.startsWith('http://') || value.startsWith('https://');

  const forms = Array.from(document.querySelectorAll('form')).map(form => ({
    action: form.getAttribute('action') ? toUrl(form.getAttribute('action')) : location.href,
    method: (form.getAttribute('method') || 'get').toUpperCase(),
    inputs: Array.from(form.querySelectorAll('input,textarea,select')).map(input => ({
      name: input.getAttribute('name') || '',
      type: input.getAttribute('type') || input.tagName.toLowerCase()
    })).filter(input => input.name)
  }));

  const links = Array.from(document.querySelectorAll('a[href]'))
    .map(anchor => toUrl(anchor.getAttribute('href')))
    .filter(isHttp);

  const scripts = Array.from(document.querySelectorAll('script[src]'))
    .map(script => toUrl(script.getAttribute('src')))
    .filter(isHttp);

  const params = new Set();
  const collect = (value) => {
    try {
      const parsed = new URL(value, location.href);
      parsed.searchParams.forEach((_, key) => params.add(key));
    } catch {}
  };
  collect(location.href);
  links.forEach(collect);
  forms.forEach(form => collect(form.action));

  return {
    title: document.title || location.href,
    html: document.documentElement.outerHTML || '',
    forms,
    links,
    scripts,
    params: Array.from(params),
    word_count: ((document.body && document.body.innerText) || '').trim().split(/\s+/).filter(Boolean).length
  };
}"""


async def extract_page_data(page: Page) -> dict[str, object]:
    return await page.evaluate(PAGE_SCRIPT)
