import './Documentation.css'

const sections = [
  {
    id: 'abstract',
    num: '01',
    title: 'Abstract',
    content: (
      <>
        <p>
          <strong>DERMA.ai</strong> is a lightweight AI system designed to provide accessible preliminary skin health guidance using a standard camera.
          The system analyzes facial images to detect visible skin patterns such as <em>acne presence</em>, <em>texture irregularity</em>, <em>dark circles</em>, and <em>wrinkle indicators</em>.
          The analysis is combined with user lifestyle inputs (sleep, diet, stress) to generate structured, non-diagnostic recommendations.
        </p>
        <p>
          The goal is not medical diagnosis but <strong>early awareness and guidance</strong>, especially for users with limited dermatology access.
        </p>
      </>
    ),
  },
  {
    id: 'problem',
    num: '02',
    title: 'Problem Statement',
    content: (
      <>
        <p>Many individuals ignore early skin issues due to:</p>
        <ul>
          <li>High dermatology consultation cost</li>
          <li>Long waiting times</li>
          <li>Lack of specialists in smaller cities</li>
          <li>Reliance on random online advice</li>
        </ul>
        <p>This leads to trial-and-error skincare practices, sometimes worsening conditions.</p>
        <blockquote>
          There exists a gap between <strong>doing nothing</strong> and <strong>visiting a dermatologist</strong>.<br />
          DERMA.ai aims to bridge this gap using computer vision–based preliminary analysis.
        </blockquote>
      </>
    ),
  },
  {
    id: 'objectives',
    num: '03',
    title: 'Objectives',
    content: (
      <>
        <div className="doc-columns">
          <div>
            <h4>Primary</h4>
            <ul>
              <li>Detect visible acne patterns</li>
              <li>Analyze skin texture irregularities</li>
              <li>Identify dark circle intensity</li>
              <li>Detect wrinkle indicators</li>
              <li>Evaluate skin tone uniformity</li>
            </ul>
          </div>
          <div>
            <h4>Secondary</h4>
            <ul>
              <li>Provide structured lifestyle suggestions</li>
              <li>Offer preventive awareness</li>
              <li>Recommend professional consultation when required</li>
              <li>Maintain fast processing (&lt;5 seconds)</li>
            </ul>
          </div>
        </div>
      </>
    ),
  },
  {
    id: 'scope',
    num: '04',
    title: 'Scope of System',
    content: (
      <>
        <div className="doc-columns">
          <div className="scope-card scope-provides">
            <h4>✅ Provides</h4>
            <ul>
              <li>Preliminary skin awareness</li>
              <li>Educational recommendations</li>
              <li>Non-clinical guidance</li>
            </ul>
          </div>
          <div className="scope-card scope-not">
            <h4>⛔ Does NOT Provide</h4>
            <ul>
              <li>Medical diagnosis</li>
              <li>Prescription suggestions</li>
              <li>Disease detection</li>
            </ul>
          </div>
        </div>
      </>
    ),
  },
  {
    id: 'architecture',
    num: '05',
    title: 'System Architecture',
    content: (
      <>
        <p className="doc-subtitle">Workflow Pipeline</p>
        <div className="pipeline">
          {['User Image', 'Face Detection', 'Region Segmentation', 'Feature Extraction', 'ML Model', 'Rule Engine', 'Report'].map(
            (step, i, arr) => (
              <span key={step} className="pipeline-step">
                <span className="pipeline-label">{step}</span>
                {i < arr.length - 1 && <span className="pipeline-arrow">→</span>}
              </span>
            )
          )}
        </div>
      </>
    ),
  },
  {
    id: 'methodology',
    num: '06',
    title: 'Methodology',
    content: (
      <>
        <div className="method-grid">
          <div className="method-card">
            <h4>6.1 — Image Acquisition</h4>
            <p><strong>Input via:</strong> smartphone camera, webcam, or uploaded image</p>
            <p><strong>Constraints:</strong> frontal face, adequate lighting, minimal occlusion</p>
          </div>
          <div className="method-card">
            <h4>6.2 — Face Detection</h4>
            <p><strong>Purpose:</strong> isolate face from background</p>
            <p><strong>Method:</strong> Haar Cascade classifier</p>
            <p><strong>Output:</strong> bounding box of face region</p>
          </div>
          <div className="method-card">
            <h4>6.3 — Region Segmentation</h4>
            <p>Key regions extracted: <em>forehead, left cheek, right cheek, under-eye area</em></p>
            <p>Different skin conditions appear in different regions.</p>
          </div>
          <div className="method-card">
            <h4>6.4 — Feature Extraction</h4>
            <p>The system measures visual patterns rather than directly classifying images.</p>
            <div className="doc-columns feat-cols">
              <div>
                <strong>Texture</strong>
                <ul><li>LBP</li><li>Surface roughness</li></ul>
              </div>
              <div>
                <strong>Color</strong>
                <ul><li>HSV variance</li><li>LAB luminance</li><li>Redness intensity</li></ul>
              </div>
              <div>
                <strong>Structural</strong>
                <ul><li>Edge density</li><li>Cluster irregularities</li></ul>
              </div>
              <div>
                <strong>Contrast</strong>
                <ul><li>Under-eye darkness</li><li>Tone uniformity</li></ul>
              </div>
            </div>
          </div>
          <div className="method-card">
            <h4>6.5 — ML Models</h4>
            <p><strong>Models:</strong> SVM · Random Forest · KNN</p>
            <p><strong>Why:</strong> interpretable, low cost, suitable for small datasets, fast inference</p>
          </div>
          <div className="method-card">
            <h4>6.6 — Lifestyle Integration</h4>
            <p>User questionnaire: sleep duration, water intake, stress level, diet type, skincare habits</p>
            <p>Combines biological context with visual signals.</p>
          </div>
          <div className="method-card">
            <h4>6.7 — Recommendation Engine</h4>
            <p>Rule-based mapping of detected patterns to actionable advice.</p>
            <p className="doc-example">High texture irregularity + oily pattern → oil control suggestions</p>
            <p className="doc-example">Dark circles + low sleep → sleep improvement advice</p>
            <p><strong>Safety Rule:</strong> if abnormal severity → recommend dermatologist consultation</p>
          </div>
        </div>
      </>
    ),
  },
  {
    id: 'dataset',
    num: '07',
    title: 'Dataset',
    content: (
      <>
        <div className="doc-columns">
          <div>
            <h4>Sources</h4>
            <ul>
              <li>Public dermatology datasets</li>
              <li>Open facial image datasets</li>
              <li>Manually filtered examples</li>
            </ul>
          </div>
          <div>
            <h4>Preprocessing</h4>
            <ul>
              <li>Resizing &amp; normalization</li>
              <li>Lighting adjustment</li>
              <li>Region cropping</li>
            </ul>
          </div>
        </div>
      </>
    ),
  },
  {
    id: 'evaluation',
    num: '08',
    title: 'Evaluation Metrics',
    content: (
      <>
        <div className="metrics-row">
          {['Accuracy', 'Precision', 'Recall', 'F1 Score', 'Confusion Matrix'].map((m) => (
            <span key={m} className="metric-badge">{m}</span>
          ))}
        </div>
        <p className="doc-target">
          Target: <strong>Accuracy ≥ 85%</strong> for controlled conditions
        </p>
      </>
    ),
  },
  {
    id: 'limitations',
    num: '09',
    title: 'Limitations',
    content: (
      <ul>
        <li>Lighting sensitivity</li>
        <li>Camera quality dependence</li>
        <li>Cannot detect internal skin diseases</li>
        <li>Dataset diversity constraints</li>
        <li>Advisory only — not a medical device</li>
      </ul>
    ),
  },
  {
    id: 'ethics',
    num: '10',
    title: 'Ethical Considerations',
    content: (
      <ul>
        <li>No medical claims</li>
        <li>No beauty scoring</li>
        <li>Privacy protection — no permanent storage of images</li>
        <li>Dermatologist recommendation for severe cases</li>
      </ul>
    ),
  },
  {
    id: 'future',
    num: '11',
    title: 'Future Scope',
    content: (
      <div className="future-grid">
        {[
          { icon: '📈', label: 'Temporal skin tracking' },
          { icon: '📱', label: 'Mobile app deployment' },
          { icon: '🌍', label: 'Improved dataset diversity' },
          { icon: '💧', label: 'Hydration detection' },
          { icon: '🔴', label: 'Redness detection' },
          { icon: '🧠', label: 'Deep learning upgrade' },
        ].map((item) => (
          <div key={item.label} className="future-card">
            <span className="future-icon">{item.icon}</span>
            <span>{item.label}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'tech',
    num: '12',
    title: 'Technology Stack',
    content: (
      <div className="tech-grid">
        {[
          { label: 'Language', value: 'Python' },
          { label: 'Vision', value: 'OpenCV · Dlib' },
          { label: 'ML', value: 'Scikit-learn · NumPy' },
          { label: 'Frontend', value: 'React · Vite' },
          { label: 'Backend', value: 'Flask' },
          { label: 'Inference', value: 'Local (no cloud)' },
        ].map((t) => (
          <div key={t.label} className="tech-card">
            <span className="tech-label">{t.label}</span>
            <span className="tech-value">{t.value}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'conclusion',
    num: '13',
    title: 'Conclusion',
    content: (
      <p>
        DERMA.ai demonstrates that classical computer vision combined with machine learning can provide accessible preliminary skin guidance.
        The system focuses on <strong>awareness rather than diagnosis</strong> and emphasizes responsible AI use in healthcare-adjacent applications.
      </p>
    ),
  },
]

export default function Documentation() {
  return (
    <div className="doc-page">
      {/* ── Hero ────────────────────────────────────── */}
      <header className="doc-hero">
        <div className="doc-hero-glow" />
        <span className="doc-badge">Project Documentation</span>
        <h1>
          DERMA<span className="accent">.ai</span>
        </h1>
        <p className="doc-tagline">
          AI-Based Skin Condition Analysis Using Classical Computer Vision &amp; Machine Learning
        </p>
      </header>

      {/* ── TOC ─────────────────────────────────────── */}
      <nav className="doc-toc">
        <h3>Contents</h3>
        <ol>
          {sections.map((s) => (
            <li key={s.id}>
              <a href={`#${s.id}`}>{s.title}</a>
            </li>
          ))}
        </ol>
      </nav>

      {/* ── Sections ────────────────────────────────── */}
      <main className="doc-body">
        {sections.map((s) => (
          <section key={s.id} id={s.id} className="doc-section">
            <div className="doc-section-header">
              <span className="doc-num">{s.num}</span>
              <h2>{s.title}</h2>
            </div>
            <div className="doc-section-content">{s.content}</div>
          </section>
        ))}
      </main>

      {/* ── Footer ──────────────────────────────────── */}
      <footer className="doc-footer">
        <p>© 2026 DERMA.ai — All rights reserved</p>
      </footer>
    </div>
  )
}
