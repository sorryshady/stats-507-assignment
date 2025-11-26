# Implementation Timeline & Plan

**STATS 507 Final Project - Describe My Environment**

**Timeline:** Nov 25 - Dec 3, 2025 (8 days)  
**Report Writing Starts:** Dec 1, 2025  
**Submission Deadline:** Dec 3, 2025

---

## 🎯 Project Deliverables

1. **Well-documented executable codebase** (GitHub repo)
2. **2-page IEEE format report** (PDF)
3. **Runnable locally** (primary requirement)
4. **Deployed version** (optional, for demo)
5. **Jupyter notebook demo** (core functionality showcase)

---

## 📅 Day-by-Day Timeline

### **Days 1-3: Backend API (Nov 25-27)**

**Goal:** FastAPI backend fully functional and tested

#### Day 1 (Nov 25) - Backend Foundation

- [ ] Create FastAPI app structure
- [ ] Wrap `DualLoopSystem` for web use
- [ ] Implement WebSocket endpoint for camera frames
- [ ] Add REST endpoints (status, narration trigger)
- [ ] Basic error handling and logging
- [ ] Test with Postman/curl

**Deliverable:** Backend runs locally, accepts frames, returns detections

#### Day 2 (Nov 26) - Backend Integration

- [ ] Integrate with existing ML pipeline
- [ ] Handle base64 image encoding/decoding
- [ ] Add CORS middleware
- [ ] Implement narration endpoint
- [ ] Add system status endpoint
- [ ] Comprehensive error handling

**Deliverable:** Full backend API working end-to-end

#### Day 3 (Nov 27) - Backend Testing & Documentation

- [ ] Write API tests
- [ ] Add API documentation (FastAPI auto-docs)
- [ ] Create README for backend setup
- [ ] Test with sample images/videos
- [ ] Performance optimization

**Deliverable:** Production-ready backend with docs

---

### **Days 4-5: Frontend (Nov 28-29)**

**Goal:** Basic frontend with test page functional

#### Day 4 (Nov 28) - Frontend Setup & Test Page

- [ ] Initialize Next.js project
- [ ] Set up TypeScript + Tailwind
- [ ] Create basic layout and navigation
- [ ] Build interactive test page (`/test`)
- [ ] Implement WebSocket client
- [ ] Camera feed component

**Deliverable:** Test page connects to backend, shows camera feed

#### Day 5 (Nov 29) - Frontend Polish

- [ ] Add tracking overlay (bounding boxes)
- [ ] Narration panel
- [ ] Hazard alerts
- [ ] Status panel
- [ ] Error handling UI
- [ ] Mobile responsiveness

**Deliverable:** Complete test page with all features

---

### **Days 6-7: Additional Pages & Jupyter Notebook (Nov 30 - Dec 1)**

**Goal:** Complete website + notebook demo

#### Day 6 (Nov 30) - Website Pages

- [ ] Landing page (`/`)
- [ ] About page (`/about`)
- [ ] Roadmap page (`/roadmap`)
- [ ] Demo videos page (`/demo`)
- [ ] Beta badges and disclaimers
- [ ] Navigation and footer

**Deliverable:** Complete website (all pages)

#### Day 7 (Dec 1) - Jupyter Notebook Demo

- [ ] Create `demo.ipynb` notebook
- [ ] Include core functionality:
  - Load test image
  - Run YOLO detection
  - Generate BLIP caption
  - Trigger narration (if Ollama available)
  - Visualize results
- [ ] Add markdown explanations
- [ ] Test notebook runs end-to-end
- [ ] **START REPORT WRITING** (parallel)

**Deliverable:** Runnable notebook showcasing core ML pipeline

---

### **Day 8: Final Polish & Deployment (Dec 2)**

**Goal:** Everything ready for submission

#### Morning: Final Testing

- [ ] End-to-end testing (local)
- [ ] Fix any bugs
- [ ] Update all documentation
- [ ] Ensure code is well-commented

#### Afternoon: Deployment (Optional)

- [ ] Deploy backend (Railway/Render)
- [ ] Deploy frontend (Vercel)
- [ ] Test deployed version
- [ ] Update README with deployment links

#### Evening: Submission Prep

- [ ] Finalize GitHub repo structure
- [ ] Ensure all code runs locally
- [ ] Create submission checklist
- [ ] Prepare demo video (if time)

**Deliverable:** Complete project ready for submission

---

### **Day 9: Report Writing & Submission (Dec 3)**

**Goal:** Submit everything

#### Morning: Report Finalization

- [ ] Complete IEEE format report
- [ ] Add figures and visualizations
- [ ] Proofread and format check
- [ ] Export to PDF

#### Afternoon: Submission

- [ ] Push final code to GitHub
- [ ] Submit PDF report
- [ ] Submit GitHub link (TXT file)
- [ ] Verify all links work

**Deliverable:** ✅ **SUBMITTED**

---

## 🏗️ Implementation Approach

### Phase 1: Backend First (Days 1-3)

**Priority:** Critical path

**Why:** Frontend depends on backend API. Must get this working first.

**Key Decisions:**

- **Ollama:** **LOCAL** (recommended for submission)
  - ✅ Runs locally, no external dependencies
  - ✅ Demonstrates full-stack capability
  - ✅ No API costs
  - ✅ Works offline
  - ⚠️ Requires user to install Ollama (documented in README)
  - **Alternative:** Cloud option can be added later if time permits

**Backend Structure:**

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── api/
│   │   ├── routes/
│   │   │   ├── camera.py    # WebSocket endpoint
│   │   │   ├── narration.py # POST /api/narration/trigger
│   │   │   └── status.py    # GET /api/status
│   │   └── models.py        # Pydantic models
│   └── core/
│       └── system.py        # Wrapper around DualLoopSystem
└── requirements.txt
```

### Phase 2: Frontend (Days 4-5)

**Priority:** High

**Focus:** Test page (`/test`) first, then other pages

**Minimal Viable Frontend:**

- Test page with camera feed
- Other pages can be simpler (static content)

### Phase 3: Polish & Demo (Days 6-7)

**Priority:** Medium

**Focus:** Complete website + notebook demo

---

## 🔧 Technical Decisions

### Ollama: Local vs Cloud

**Decision: LOCAL (Primary)**

**Rationale:**

1. **Submission Requirement:** Must run locally
2. **Simplicity:** No API keys, no costs, no external dependencies
3. **Demonstration:** Shows full-stack ML capability
4. **Reliability:** No network issues during demo

**Implementation:**

- Backend checks if Ollama is running on startup
- Returns clear error if Ollama not available
- README includes Ollama setup instructions
- Status endpoint shows Ollama connection status

**Fallback:**

- If Ollama unavailable, narration endpoint returns error
- Other features (detection, tracking) still work
- Can add cloud option later if time permits

### Deployment Strategy

**Local-First Approach:**

1. **Primary:** Everything runs locally (required)
2. **Optional:** Deployed version for easy demo

**Deployment Options:**

- **Backend:** Railway or Render (free tier)
- **Frontend:** Vercel (free tier)
- **Alternative:** Single server with Docker Compose

**Note:** Deployment is optional. Local execution is mandatory.

---

## 📓 Jupyter Notebook Demo

### Purpose

Demonstrate core ML functionality without web interface complexity.

### Structure (`demo.ipynb`)

```python
# Cell 1: Setup & Imports
# Cell 2: Load Test Image
# Cell 3: YOLO Detection (with visualization)
# Cell 4: BLIP Scene Captioning
# Cell 5: Trajectory Analysis (if video)
# Cell 6: LLM Narration (if Ollama available)
# Cell 7: Summary & Results
```

### Features

- ✅ Self-contained (runs in notebook)
- ✅ Uses existing `src/` modules
- ✅ Visual outputs (images, text)
- ✅ Markdown explanations
- ✅ Works without web server

### Requirements

- Jupyter installed
- All dependencies from `requirements.txt`
- Ollama optional (graceful degradation)

---

## 📁 Final Project Structure

```
final/
├── README.md                    # Main project README
├── requirements.txt             # Python dependencies
├── demo.ipynb                   # Jupyter notebook demo
│
├── src/                         # Existing ML code (unchanged)
│   ├── main.py
│   ├── config.py
│   ├── hardware/
│   ├── reflex_loop/
│   └── cognitive_loop/
│
├── backend/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   └── core/
│   └── requirements.txt
│
├── frontend/                    # Next.js frontend
│   ├── app/
│   ├── components/
│   ├── lib/
│   └── package.json
│
├── test_images/                # Test images
├── public/                     # Static assets
│   └── demos/                  # Demo videos (if any)
│
├── docs/                       # Documentation
│   ├── API.md                  # API documentation
│   ├── SETUP.md                # Setup instructions
│   └── ARCHITECTURE.md         # System architecture
│
└── report/                     # Report files
    └── final_report.pdf        # IEEE format report
```

---

## ✅ Submission Checklist

### Code Repository

- [ ] Well-documented code (docstrings, comments)
- [ ] README with setup instructions
- [ ] Requirements files (Python + Node.js)
- [ ] `.gitignore` configured
- [ ] All code runs locally
- [ ] Jupyter notebook works
- [ ] API documentation (FastAPI auto-docs)

### Report (IEEE Format)

- [ ] 2+ pages
- [ ] IEEE template formatting
- [ ] Sections: Introduction, Method, Results, Conclusion
- [ ] Figures and visualizations
- [ ] Citations (if any)
- [ ] PDF format

### Submission Files

- [ ] PDF report
- [ ] TXT file with GitHub link
- [ ] GitHub repo is public (or shared with instructor)

---

## 🚨 Risk Mitigation

### Risk 1: Backend takes longer than expected

**Mitigation:** Focus on core endpoints first (camera, narration). Skip optional features.

### Risk 2: Frontend integration issues

**Mitigation:** Test backend thoroughly before frontend. Use Postman/curl first.

### Risk 3: Ollama setup complexity

**Mitigation:** Clear documentation. Graceful degradation if Ollama unavailable.

### Risk 4: Report writing time

**Mitigation:** Start report Dec 1 (parallel with notebook). Use existing docs as starting point.

### Risk 5: Deployment issues

**Mitigation:** Deployment is optional. Focus on local execution first.

---

## 🎯 Success Criteria

### Minimum Viable Product (MVP)

- ✅ Backend API runs locally
- ✅ Test page connects to backend
- ✅ Camera feed works
- ✅ Narration triggers work
- ✅ Jupyter notebook runs
- ✅ Report submitted

### Nice-to-Have (If Time Permits)

- ✅ All website pages complete
- ✅ Deployed version working
- ✅ Demo videos added
- ✅ Additional polish

---

## 📝 Notes

1. **Focus on Backend First:** This is the critical path. Get it working before frontend.

2. **Ollama Local:** Keep it simple. Local Ollama is sufficient for submission.

3. **Report Parallel:** Start writing report Dec 1 while finishing notebook.

4. **Local > Deployed:** Local execution is required. Deployment is bonus.

5. **Notebook Priority:** Jupyter notebook is important for easy demo. Don't skip it.

---

## 🚀 Getting Started

**Today (Nov 25):** Start with backend foundation.

**First Task:** Create FastAPI app structure and basic WebSocket endpoint.

**Next Steps:** Follow day-by-day timeline above.

---

**Ready to begin?** Let's start with backend implementation! 🎉
