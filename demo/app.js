/*
 * Retrieval demo for the University Chatbot.
 * BM25 search over the same document chunks the RAG app indexes; shows the
 * top passages instead of a generated answer (which needs a Mistral key).
 */
(function () {
  'use strict';

  var TOP_K = 3;
  var MIN_SCORE = 4.0;
  var EXAMPLES = [
    'What is the minimum attendance required?',
    'How is CGPA calculated?',
    'What are the hostel in-time rules?',
    'Can I take leave of absence?',
    'What happens if I miss an end-semester exam?',
    'Are guests allowed in the hostel?',
  ];
  var STOP = new Set(('a an the of to in on for and or is are be by with as at from that this it its can i my me ' +
    'what how when who which do does did will would should may there their they we you your about any if not ' +
    'all also has have had was were been than then into per under up out').split(' '));

  var chunks = [], docTokens = [], df = new Map(), avgLen = 0;

  function tokenize(text) {
    return text.toLowerCase().replace(/[^a-z0-9%\s]/g, ' ').split(/\s+/)
      .filter(function (w) { return w.length > 1 && !STOP.has(w); })
      .map(function (w) { return w.replace(/(ies)$/, 'y').replace(/([^s])s$/, '$1'); });
  }

  function buildIndex() {
    var total = 0;
    docTokens = chunks.map(function (c) {
      var toks = tokenize(c.text);
      total += toks.length;
      new Set(toks).forEach(function (t) { df.set(t, (df.get(t) || 0) + 1); });
      return toks;
    });
    avgLen = total / Math.max(1, chunks.length);
  }

  function search(query) {
    var q = Array.from(new Set(tokenize(query)));
    var N = chunks.length, k1 = 1.5, b = 0.75;
    var scored = docTokens.map(function (toks, i) {
      var tf = new Map();
      toks.forEach(function (t) { tf.set(t, (tf.get(t) || 0) + 1); });
      var score = 0;
      q.forEach(function (t) {
        var f = tf.get(t);
        if (!f) return;
        var idf = Math.log(1 + (N - df.get(t) + 0.5) / (df.get(t) + 0.5));
        score += idf * (f * (k1 + 1)) / (f + k1 * (1 - b + b * toks.length / avgLen));
      });
      return { i: i, score: score };
    });
    return scored.filter(function (s) { return s.score > 0; })
      .sort(function (a, b) { return b.score - a.score; }).slice(0, TOP_K);
  }

  function escapeHtml(s) {
    return s.replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }

  function highlight(text, query) {
    var html = escapeHtml(text);
    var terms = tokenize(query).filter(function (t) { return t.length > 2; });
    terms.forEach(function (t) {
      var re = new RegExp('\\b(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + '\\w*)', 'gi');
      html = html.replace(re, '<mark>$1</mark>');
    });
    return html;
  }

  var messages = document.getElementById('messages');
  function addMessage(role, html) {
    var el = document.createElement('div');
    el.className = 'msg ' + role;
    el.innerHTML = '<div class="avatar">' + (role === 'user' ? '🧑‍🎓' : '🎓') + '</div><div class="body">' + html + '</div>';
    messages.appendChild(el);
    el.scrollIntoView({ behavior: 'smooth', block: 'end' });
  }

  function answer(query) {
    addMessage('user', '<p>' + escapeHtml(query) + '</p>');
    var hits = search(query);
    if (!hits.length || hits[0].score < MIN_SCORE) {
      addMessage('bot', '<p>I cannot find that information in the official documents.</p>');
      return;
    }
    var html = '<p>Here are the most relevant sections from the official documents:</p>' +
      hits.map(function (h) {
        var c = chunks[h.i];
        return '<div class="passage"><span class="src">' + escapeHtml(c.doc) + '</span>' + highlight(c.text, query) + '</div>';
      }).join('');
    addMessage('bot', html);
  }

  var examples = document.getElementById('examples');
  EXAMPLES.forEach(function (q) {
    var b = document.createElement('button');
    b.type = 'button'; b.textContent = q;
    b.onclick = function () { answer(q); };
    examples.appendChild(b);
  });

  document.getElementById('ask').addEventListener('submit', function (e) {
    e.preventDefault();
    var input = document.getElementById('q');
    var q = input.value.trim();
    if (!q) return;
    input.value = '';
    answer(q);
  });

  addMessage('bot', '<p>Hello! I can answer questions about Academic Rules, Hostel Policy, and Mass Comm guidelines. What would you like to know?</p>');

  fetch('chunks.json').then(function (r) { return r.json(); }).then(function (data) {
    chunks = data;
    buildIndex();
  });
})();
