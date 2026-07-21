# Coach K — UI/UX Direction Proposal

**`coach-k-ui-proposal.pdf`** — a marketing + design proposal presenting four
complete UI directions for the Coach K app (landing + Today screen), with
positioning, palettes, typography, strengths/watch-outs, and a recommendation.

## Directions
1. **Iron Forge** — dark gym + signal red (refined current DNA)
2. **Day Court** — daylight chalk + court-green athletics
3. **Film Cut** — cinematic tungsten, Dayan's photo leads
4. **Signal Strip** — high-contrast poster athletics

## Regenerate

```bash
pip install weasyprint pypdfium2   # if not present
python3 proposals/build_proposal.py
```

Outputs `proposals/coach-k-ui-proposal.pdf`. Images are embedded from
`frontend/public/images/`, so the PDF is self-contained.

## See the directions live (interactive)
- Local: `cd frontend && npm run dev` → `http://localhost:5173/?design=1`
- Deployed: `https://your-app/?design=1`
- Or Landing footer → **Preview UI directions**
