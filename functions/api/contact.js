export async function onRequestPost(context) {
  const { request, env } = context;

  const origin = request.headers.get('Origin') || '';
  const allowed = ['https://resourcehip.com', 'https://www.resourcehip.com'];
  if (env.CF_PAGES_URL) allowed.push(env.CF_PAGES_URL);

  if (!allowed.includes(origin) && !origin.startsWith('http://localhost')) {
    return Response.json({ error: 'Forbidden' }, { status: 403 });
  }

  let data;
  try {
    data = await request.json();
  } catch {
    return Response.json({ error: 'Invalid request' }, { status: 400 });
  }

  if (data.website) {
    return Response.json({ ok: true });
  }

  function sanitise(val, max) {
    return String(val || '').replace(/<[^>]*>/g, '').replace(/[\r\n]+/g, '\n').trim().slice(0, max);
  }

  function sanitiseHeader(val, max) {
    return String(val || '').replace(/<[^>]*>/g, '').replace(/[\r\n<>"\\]/g, '').trim().slice(0, max);
  }

  const name = sanitiseHeader(data.name, 100);
  const email = sanitiseHeader(data.email, 254);
  const company = sanitiseHeader(data.company, 100);
  const validReasons = ['verified-rating', 'press', 'general', ''];
  const reason = validReasons.includes(data.reason) ? data.reason : '';
  const message = sanitise(data.message, 5000);

  if (!name) return Response.json({ error: 'Name is required.' }, { status: 400 });
  if (!email || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    return Response.json({ error: 'A valid email is required.' }, { status: 400 });
  }
  if (!message) return Response.json({ error: 'Message is required.' }, { status: 400 });

  const reasonLabels = {
    'verified-rating': 'Verified Rating Enquiry',
    'press': 'Press',
    'general': 'General',
    '': 'Not specified',
  };

  const subject = reason === 'verified-rating'
    ? `[Verified Rating Enquiry] ${name}`
    : `[Contact Form] ${name}`;

  const bodyLines = [
    `Name: ${name}`,
    `Email: ${email}`,
  ];
  if (company) bodyLines.push(`Company: ${company}`);
  bodyLines.push(
    `Reason: ${reasonLabels[reason]}`,
    '',
    'Message:',
    message,
    '',
    '---',
    `IP: ${request.headers.get('CF-Connecting-IP') || 'unknown'}`,
    `Time: ${new Date().toISOString()}`,
  );

  const rawMime = [
    `From: "Resourcehip Contact Form" <contact-form@resourcehip.org>`,
    `Reply-To: "${name}" <${email}>`,
    `To: hello@resourcehip.com`,
    `Subject: ${subject}`,
    `Content-Type: text/plain; charset=utf-8`,
    ``,
    bodyLines.join('\r\n'),
  ].join('\r\n');

  try {
    const workerUrl = env.EMAIL_WORKER_URL || 'https://resourcehip-email-worker.chris-b0e.workers.dev';
    const resp = await fetch(workerUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Worker-Auth': env.WORKER_AUTH_SECRET || '',
      },
      body: JSON.stringify({
        from: 'contact-form@resourcehip.org',
        to: 'hello@resourcehip.com',
        rawMime,
      }),
    });
    if (!resp.ok) {
      const err = await resp.text();
      console.error('Email worker error:', resp.status, err);
      return Response.json(
        { error: 'Failed to send. Please email hello@resourcehip.com directly.' },
        { status: 500 },
      );
    }
  } catch (err) {
    console.error('Email send error:', err);
    return Response.json(
      { error: 'Failed to send. Please email hello@resourcehip.com directly.' },
      { status: 500 },
    );
  }

  return Response.json({ ok: true });
}
