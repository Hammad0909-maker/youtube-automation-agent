const fs = require('node:fs/promises');

const API_KEY = process.env.TUBEALFRED_API_KEY;
if (!API_KEY) {
  console.error('Missing TUBEALFRED_API_KEY. Add it under GitHub repository Settings → Secrets and variables → Actions.');
  process.exit(1);
}

const topics = [
  'AI technology breakthrough explained',
  'space science discoveries explained',
  'human body health science facts',
];

async function searchYouTube(query) {
  const url = new URL('https://api.tubealfred.com/v1/youtube/search');
  url.searchParams.set('query', query);
  url.searchParams.set('sort', 'popularity');
  url.searchParams.set('type', 'video');
  url.searchParams.set('upload_date', 'month');

  const response = await fetch(url, {
    headers: { Authorization: `Bearer ${API_KEY}`, Accept: 'application/json' },
    signal: AbortSignal.timeout(30000),
  });

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    const message = payload.message || payload.error || `HTTP ${response.status}`;
    throw new Error(`TubeAlfred search failed for "${query}": ${message}`);
  }
  if (payload.status !== 'success' || !payload.data) {
    throw new Error(`TubeAlfred returned an unexpected response for "${query}".`);
  }

  const videos = Array.isArray(payload.data.videos) ? payload.data.videos : [];
  return videos.slice(0, 8).map((video) => ({
    title: video.title || 'Untitled video',
    url: video.url || (video.id ? `https://www.youtube.com/watch?v=${video.id}` : ''),
    channel: video.channel?.title || 'Unknown channel',
    views: video.view_count_text || 'Views unavailable',
    published: video.published_time_text || 'Date unavailable',
    duration: video.length_text || 'Duration unavailable',
  }));
}

function markdownTable(videos) {
  if (!videos.length) return '_No results were returned for this search._';
  const escape = (value) => String(value).replace(/\|/g, '\\|').replace(/\r?\n/g, ' ');
  return [
    '| Video | Channel | Views | Published | Length |',
    '|---|---|---:|---|---|',
    ...videos.map((video) => `| [${escape(video.title)}](${video.url}) | ${escape(video.channel)} | ${escape(video.views)} | ${escape(video.published)} | ${escape(video.duration)} |`),
  ].join('\n');
}

async function main() {
  const sections = [
    '# NOVARA — YouTube Topic Research',
    '',
    `Generated: ${new Date().toISOString()}`,
    '',
    '> Research aid only. Popularity is not a guarantee of future views. Check every factual claim against reliable sources, avoid copying other creators, and review the final video before publishing.',
    '',
  ];

  for (const topic of topics) {
    console.log(`Searching: ${topic}`);
    const videos = await searchYouTube(topic);
    sections.push(`## Search: ${topic}`, '', markdownTable(videos), '');
  }

  sections.push(
    '## NOVARA production checklist',
    '',
    '- [ ] Choose an original angle; do not copy another video’s script or edit.',
    '- [ ] Verify health/science/news claims with reliable primary or expert sources.',
    '- [ ] Mark uncertain or developing news clearly; do not present guesses as facts.',
    '- [ ] Create original narration and visuals; check rights for every asset.',
    '- [ ] Check title and description for misleading claims.',
    '- [ ] Watch the complete exported video and confirm narration, subtitles, and visuals match.',
    '- [ ] Human review is required. This workflow does not upload or publish videos.',
    '',
  );

  await fs.mkdir('artifacts', { recursive: true });
  const report = sections.join('\n');
  await fs.writeFile('artifacts/novara-research.md', report, 'utf8');
  await fs.writeFile('artifacts/novara-research.json', JSON.stringify({ generatedAt: new Date().toISOString(), topics }, null, 2), 'utf8');
  console.log('Research report saved to artifacts/novara-research.md');
}

main().catch((error) => {
  console.error(error.message);
  process.exit(1);
});
